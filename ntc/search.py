"""
Searching
---------
"""

import numpy as np
from functools import reduce

from django.contrib.postgres.search import (SearchQuery, SearchRank,
                                            SearchVector, TrigramSimilarity)

from ntc import models
from django.db.models import Q, Count

"""
Utils
-----
"""


def weight2alpha(weight):
    """Convert numeric weights to alpha"""
    opts = ["A", "B", "C", "D"]
    if weight in opts:
        return weight

    idx = (np.abs(np.array([1, 0.4, 0.2, 0.1]) - weight)).argmin()
    return opts[idx]


"""
Query class
-------
"""


class Query():

    def __init__(self, term, fields=None, weights=None,
                 trigram=False):

        # Get defaults
        fields = fields or ("name", "description")

        # Enforce list type
        if not isinstance(fields, (list, tuple)):
            fields = [fields]

        weights = weights or [1] * len(fields)

        # Enforce list type
        if not isinstance(weights, (list, tuple)):
            weights = [weights]

        # Ensure weights and fields are same length
        if len(weights) != len(fields):
            raise ValueError("len(weights) must be equal to len(fields) or 0.")

        self.term = term
        self.fields = fields
        self.weights = weights
        self.trigram = trigram

        self.generate_query()

    def generate_query(self):
        """Generate db query"""
        if self.trigram:
            self.query = self.generate_trigram(
                self.fields, self.term, self.weights)
        else:
            self.query = self.generate_search_rank(
                self.fields, self.term, self.weights)
        return self.query

    def generate_trigram(self, fields, term, weights):
        """Generate trigrams from queries"""
        trigrams = [TrigramSimilarity(field, term) for field in fields]
        trigram = np.dot(trigrams, weights)
        return trigram

    def generate_search_rank(self, fields, term, weights=None):
        """Helper func to generate trigrams for queries"""

        # Ensure numeric weights
        weights = list(map(weight2alpha, weights))

        search_vectors = []
        for (field, weight) in zip(fields, weights):
            search_vectors.append(SearchVector(field, weight=weight))

        search_vector = reduce(lambda x: x + x, search_vectors)
        search_query = SearchQuery(term)

        # Create rank annotation & add to dict
        return SearchRank(search_vector, search_query)


def build_query(term, fields=None, weights=None, trigram=None):
    """Helper function to build query"""
    query = Query(term, fields, weights, trigram)
    return query.query


def build_queries(queries):
    """Builds queries for each value in the dictionary

    Parameters
    ----------
    queries : dict
        Dictionary of name:params pairs
    """

    for name, query in queries.items():
        queries[name] = build_query(**query)

    queries["total_score"] = sum(queries.values())

    return queries


def search(queries, min_score=0.1, max_n=None):
    """Search for a topic by name"""
    # Annotate with query
    topics = models.Topic.objects.annotate(**queries)

    # Filter
    topics = topics.filter(total_score__gte=min_score)

    # Sort
    # TODO: Order by verified and votes
    topics = topics.order_by('-total_score')

    # Limit
    if max_n:
        topics = topics[:max_n]

    return topics


def keyword_search(term, max_n=5, min_score=0.1):
    """Easy access function to search topics by keyword"""

    query_data = {
        "name_literal": {
            "term": term,
            "fields": "name",
            "trigram": False
            },
        "name_trigram": {
            "term": term,
            "fields": "name",
            "trigram": True
            },
        "description_score": {
            "term": term,
            "fields": "description",
            "trigram": False,
            "weights": 0.4
            },
        }

    queries = build_queries(query_data)

    results = search(queries, min_score=min_score, max_n=None)

    results = results.order_by(
        '-name_literal', '-name_trigram', '-total_score')

    if max_n:
        results = results[:max_n]

    return results


def check_topic_duplicates(data, max_n=3):
    """Check database for similar topics"""

    # query = Q(url=data['url']) or Q(name__icontains=data['name'])
    # match = models.Topic.objects.filter(query)
    queries = build_queries(data)
    match = search(queries, max_n=None)
    match = match.filter(
        Q(name_score__gte=0.8) |
        Q(url_score__gte=0.9) |
        Q(description_score__gte=0.4) |
        Q(total_score__gte=2.5))

    return match[:max_n]


"""
WIP
---

"""


class Search():
    """Perform queries on database of topics"""
    queries = {
        "name": "",
        "url": "",
        "description": "",
        "category": ""
    }

    config = {
        "max_n": None,
        "min_n": 0,
        "trigram": True,
        "weights": None,
        "fields": None,
        "disjunctive": True,
    }

    results = []

    def __init__(self, queries={}, config={}, **kwargs):
        """Create new search instance"""

        # Store params on object
        self.queries.update(queries)
        self.config.update(config)

        # Get direct arguments from kwargs
        for k, v in kwargs.items():
            if k in self.queries:
                self.queries[k] = v

            if k in self.config:
                self.queries[k] = v

    def search_by_field(self):
        """Perform a query and store the result"""
        queries = []
        for field, query in self.queries.items():
            # TODO: Generic query bot
            if query:
                queries.append(Q())
