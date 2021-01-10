"""
Wikipedia
---------
Get Topic data from wikipedia
"""

# TODO: https://pypi.org/project/Wikipedia-API/
# and category search

import re
import collections
import logging

import wikipedia

logger = logging.getLogger(__name__)

"""
Constants
---------
"""
TOPIC_DATA_KEYS = {"name", "description", "category",
                   "profile", "url", "tags"}

CATEGORY_KEYWORDS = {
    "PER": ["person", "people", "ruler", "writer", "theorist",
            "philosopher", "politician", "minister", "leader"],
    "POL": ["policy", "policies", "program"],
    "GOV": ["government", "ministry", "ministries"],
    "COU": ["nation", "country", "countries"],
    "WOR": ["book", "work", "literature", "essay", "publication"],
    "PHI": ["theories", "theory", "philosophy", "philosophies",
            "ideology", "ideologies", "movement", "tradition"]
}

CATEGORY_PATTERNS = {
    k: re.compile("|".join(v)) for k, v in CATEGORY_KEYWORDS.items()
    }


"""
Functions
---------
"""


def get_wiki_description(page, max_length=980):
    """Extract the first paragraph of the wiki description and clean it"""
    content = page.content
    para = content.split("\n")[0]

    if len(para) > max_length:
        sents = para.split('. ')
        para_text = ""

        for sent in sents:
            new_para_text = " ".join([para_text, sent])
            if len(new_para_text) < max_length:
                para_text = new_para_text
            else:
                break

        para = para_text

    return para


def get_wiki_category(page):
    """Extract the category of a page from wiki"""
    categories = page.categories
    counter = collections.Counter()

    for category in categories:
        category = category.lower()

        for name, pattern in CATEGORY_PATTERNS.items():
            if re.search(pattern, category):
                counter.update([name])

    if counter:
        return counter.most_common(1)[0][0]

    logger.warning("No category matches for %r", page.title)
    return "OTH"


def create_topic_from_wiki(name):
    """Grab text from wikipedia and create a page"""
    try:
        page = wikipedia.page(name)
    except wikipedia.PageError as e:
        pages = wikipedia.search(name)
        print(e)
        print(pages)
        return None
    except wikipedia.DisambiguationError as e:
        print(e)
        return None

    data = {
        "name": page.title,
        "description": get_wiki_description(page),
        "category": get_wiki_category(page),
        "tags": [],
        "url": page.url
    }

    return data
