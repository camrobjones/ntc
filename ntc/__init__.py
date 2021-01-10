"""
NTC Main
--------
"""

from .ntc import (get_topic_by_id, get_next_topic,
                  get_random_topic, model2json,
                  submit_vote, create_topic,
                  create_comment, create_comment_vote)

from .search import keyword_search, check_topic_duplicates
