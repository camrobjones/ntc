"""
NTC Views
---------
Generally tries to pass data to ntc ASAP
"""

import logging

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Exists, OuterRef

from ntc import ntc
from ntc.api import api, get_profile, parse_request

# Get an instance of a logger
logger = logging.getLogger(__name__)

"""
HTML Views
----------
Render HTML responses
"""

# Todo: 3 -> 1 function


def vote(request, topic_id=None):
    """The main voting view"""
    return render(request, "ntc/vote.html")


def topic(request, topic_id):
    """Return a view of the given topic"""
    profile = get_profile(request.user)

    topic_info = ntc.get_topic_by_id(profile, topic_id)
    return render(request, "ntc/vote.html", {"topic": topic_info})


def home(request):
    """Homepage"""
    return vote(request)


"""
API views
---------
Backend for api functionality
"""


"""
Retrieve
--------
- get_topic
- next_topic
- random_topic

# Consolidate topic getters

"""


@api
def get_topic(profile, topic_id):
    """Find and return an unseen topic for the user"""
    print(f"Calling get_topic with profile={profile}, topic_id={topic_id}")
    topic = ntc.get_topic_by_id(profile, topic_id)
    return {"topic": topic}


@api
def next_topic(profile):
    """Find and return an unseen topic for the user"""
    topic = ntc.get_next_topic(profile)
    return {"topic": topic}


@api
def random_topic(profile):
    """Return a random unseen topic to the user"""
    topic = ntc.get_random_topic(profile)

    return {"topic": topic}


"""
Search
------

"""


@api
def search_topic(profile, query):
    """Search for a topic using query and return relevant results"""

    results = ntc.keyword_search(query, max_n=None)

    # Add seen info
    results = results.annotate(
        voted=Exists(
            profile.vote_set.filter(
                topic=OuterRef('pk'))
            )
        )

    results = results[:10]

    results = [ntc.model2json(res) for res in results]

    return {"results": results, "query": query}


def check_topic_duplicates(request):
    """Check for similar topics to a new submission"""
    data = parse_request(request)
    match = ntc.check_topic_duplicates(data["queries"])

    count, message = 0, ""

    if match.exists():

        count = match.count()
        s = "s" if count > 1 else ""

        message = f"We found {count} other similar topic{s}. "
        message += "Make sure to check them out before creating a new topic."

    topics = [ntc.model2json(match) for match in match]

    out = {"count": count, "topics": topics, "message": message}

    return JsonResponse(out)


"""
Create
--------
- create_topic
- submit_vote

"""


def create_topic(request):
    """Validate input and create topic"""
    logger.info("Request recieved at create_topic")

    # Extract submission data from request object
    data = parse_request(request)
    data['profile'] = get_profile(request.user)
    print(data)

    # Attempt to create topic
    data = ntc.create_topic(data)

    print(data)

    if data['topic']:
        data['topic'] = ntc.model2json(data['topic'])

    return JsonResponse(data)


@api
def submit_vote(profile, **data):
    """Store user vote on a topic and return topic info"""

    success, errors = ntc.submit_vote(profile, data)

    if not success:
        return {'success': success, 'errors': errors}

    topic_info = ntc.get_topic_by_id(profile, data["topic_id"])

    return {'success': success, 'topic': topic_info}


@api
def submit_comment(profile, topic_id, text, parent=None):
    """Submit a new comment on a topic"""

    data = ntc.create_comment(profile, topic, text, parent)

    data['topic'] = ntc.get_topic_by_id(profile, topic_id)

    return data


@api
def submit_comment_vote(profile, comment_id, value):
    """Submit a vote on a comment"""
    data = ntc.create_comment_vote(profile, comment_id, value)

    return data
