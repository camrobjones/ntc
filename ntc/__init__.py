"""
NTC Main
--------
"""

from .ntc import (get_topic_by_id, get_next_topic,
                  get_random_topic, model2json, get_last_voted_topic,
                  submit_vote, create_topic,
                  create_comment, create_comment_vote,
                  get_top_20_topics, skip_topic)

from .search import keyword_search, check_topic_duplicates
