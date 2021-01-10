"""
Heavy lifting for ntc app
-------------------------
- Data Processing and storage
- Validation for model creation
- Querying utils
"""

import random
import logging
from statistics import mean
from copy import deepcopy

from django.core.exceptions import ValidationError
from django.db.models import Q, Count
from django.utils.text import slugify

from ntc import models

logger = logging.getLogger(__name__)

"""
Utils
-----
General purpose tools
"""


def model2json(obj):
    """Serialize a model as JSON"""
    obj = deepcopy(obj)
    data = obj.__dict__
    data.pop('_state', None)
    return data


def generate_topic_slug(topic):
    """Create a legal, unique slug for the topic"""

    # Find the max_length of the slug
    max_length = models.Topic._meta.get_field('slug').max_length - 1

    # Generate slug from topic name
    slug = slugify(topic.name, allow_unicode=True)[:max_length]

    # Check if any other objects have the same name
    objects = models.Topic.objects.filter(name=topic.name).exclude(
        pk=topic.id)

    if objects.exists():
        suffix = f"-{objects.count()}"

        # Ensure slug not too long including suffix
        slug = slug[:max_length - len(suffix)] + suffix

    return slug


"""
Retrieve
--------
check_topic_duplicates
"""


def get_topic_info(topic, profile):
    """Get info about a specific topic"""

    # Retrieve topic votes
    votes = topic.vote_set.exclude(profile=profile)
    votes = list(votes.values('profile_id', 'x', 'y'))

    # Get user vote
    user_vote = topic.vote_set.filter(
        profile=profile).values('x', 'y').first()

    # Calculate mean position
    if len(votes) > 2:
        mean_x = mean([vote['x'] for vote in votes])
        mean_y = mean([vote['y'] for vote in votes])
        mean_vote = {"x": mean_x, "y": mean_y}
    else:
        mean_vote = {}

    # Retrieve comments
    comments = list(topic.comment_set.all().values())

    data = model2json(topic)
    data['info'] = {"votes": votes,
                    "user_vote": user_vote,
                    "mean_vote": mean_vote,
                    "comments": comments}

    return data


def rank_topics_for_user(profile):
    """Rank topics in order of popularity and relevance to user"""
    # TODO: Estimate relevance for user

    # Exclude topics the user has voted on
    topics = models.Topic.objects.exclude(vote__profile=profile)

    # Order by popularity
    topics = topics.annotate(no_votes=Count('vote'))
    return topics.order_by('-no_votes')


def get_topic_by_id(profile, topic_id):
    """Retrieve topic with specified id"""
    topic = models.Topic.objects.get(id=topic_id)
    return get_topic_info(topic, profile)


def get_next_topic(profile):
    """Return the top ranked unseen topic for the user"""
    topics = rank_topics_for_user(profile)
    return get_topic_info(topics[0], profile)


def get_random_topic(profile):
    """Return a random topic"""
    max_id = models.Topic.objects.last().pk

    while True:
        topic_id = random.randint(1, max_id)
        topic = models.Topic.objects.filter(pk=topic_id)
        if topic.exists():
            return get_topic_info(topic.get(), profile)


"""
Data storage
------------
Store new data in db
"""


def add_tag_to_topic(tag, topic):
    """Add tags to topic"""

    # Get or create the tag object
    created, tag = models.Tag.objects.get_or_create(
        name=tag,
        default={"profile": topic.profile}
    )

    topic.tags.add(tag)


def create_topic(data):
    """Create new topic object"""
    # TODO: Refactor as class based validator/factory

    # initialise output
    out = {"success": False, "errors": {}, "topic": None}

    # Remove tags
    tags = data.pop('tags', [])

    # Create topic object
    topic = models.Topic(**data)
    topic.slug = generate_topic_slug(topic)

    # Validate the model and gather errors
    try:
        topic.full_clean()
    except ValidationError as e:
        out['errors'].update(e.message_dict)

    if out['errors']:
        return out

    topic.save()

    # Add tags
    for tag in tags:
        add_tag_to_topic(tag, topic)

    out['success'] = True
    out['topic'] = topic

    return out


def submit_vote(profile, data):
    """Submit a users vote on a topic"""

    # Retrieve topic
    topic = models.Topic.objects.get(pk=data['topic_id'])

    # Get or create vote
    vote, created = models.Vote.objects.get_or_create(
        profile=profile,
        topic=topic,
        defaults={
            "x": data['x'],
            "y": data['y']
        })

    return True, []


def create_comment(profile, topic_id, text, parent=None):
    """Submit a users vote on a topic"""
    data = {"success": False, "errors": {}}

    # Retrieve topic
    topic = models.Topic.objects.get(pk=topic_id)

    # Get or create vote
    comment = models.Comment(
        profile=profile,
        topic=topic,
        text=text,
        parent=parent
        )

    try:
        comment.full_clean()
    except ValidationError as e:
        data['errors'].update(e.message_dict)
        return data

    comment.save()

    data['success'] = True

    return data


def create_comment_vote(profile, comment_id, value):
    """Submit a users vote on a topic"""
    data = {"success": False, "errors": {}}

    # Retrieve topic
    comment = models.Comment.objects.get(pk=comment_id)

    # Get or create vote
    comment_vote, created = models.CommentVote.objects.get_or_create(
        profile=profile,
        comment=comment,
        defaults={
            "value": value
        })

    comment_vote.value = int(value)

    try:
        comment_vote.full_clean()
    except ValidationError as e:
        data['errors'].update(e.message_dict)
        return data

    comment_vote.save()

    comment.vote_count()
    comment.save()

    data['success'] = True

    return data


"""
Data validation
---------------
"""


class Validator():
    """Base class to validate model input"""
    errors = {}
    error_count = 0
    valid_keys = set()

    def __init__(self, data):
        self.data = data
        self.keys = set(data.keys())


def validate_topic_data(data):
    """Check if topic data is valid"""
    errors = {}
    error_count = 0

    # Check name errors
    return data
