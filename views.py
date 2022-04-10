"""
NTC Views
---------
Generally tries to pass data to ntc ASAP
"""

import logging
import json
from email.utils import parseaddr

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Exists, OuterRef
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from ntc import ntc
from ntc.api import api, get_profile, parse_request, _decode, get_user

# Get an instance of a logger
logger = logging.getLogger(__name__)

"""
HTML Views
----------
Render HTML responses
"""


def vote(request, topic_id=None):
    """The main voting view"""
    print("Request: ", request, " topic_id ", topic_id)
    context = {'user': get_user(request)}
    return render(request, "ntc/vote.html", context)


def topic(request, topic_id):
    """Return a view of the given topic"""
    profile = get_profile(request.user)

    topic_info = ntc.get_topic_by_id(profile, topic_id)
    context = {'user': get_user(request), "topic": topic_info}
    return render(request, "ntc/vote.html", context)


def home(request):
    """Homepage"""

    context = {
        "topics": ntc.get_top_20_topics(),
        "user": get_user(request)
    }

    return render(request, "ntc/home.html", context)


"""
API views
---------
Backend for api functionality
"""

"""
User views
----------
- get_user
- login
- logout
- signup
"""


def login_user(request):
    """Asynchronously log user in"""

    # Retrieve request data
    post = json.loads(request.body.decode('utf-8'), object_hook=_decode)

    # Retrieve simulation parameters
    username = post.get('username')
    password = post.get('password')

    # check if username is email
    User = get_user_model()
    if not User.objects.filter(username=username).exists():
        email_query = User.objects.filter(email=username)
        if email_query.count() == 1:
            username = email_query.first().username

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        user_data = get_user(request)
        out = {"success": True, "user": user_data}

    else:
        # Return an 'invalid login' error message.
        message = "Incorrect username or password."
        out = {"success": False, "message": message}

    return JsonResponse(out)


def logout_user(request):
    """Asynchronously log user out"""
    logout(request)
    request.COOKIES['neurons'] = []
    out = {"success": True}
    return JsonResponse(out)


def signup(request):
    """Asynchronously create new user"""

    # Retrieve request data
    post = json.loads(request.body.decode('utf-8'), object_hook=_decode)

    # Retrieve simulation parameters
    username = post.get('username')
    email = post.get('email')
    password = post.get('password')
    password_confirm = post.get('passwordConfirm')

    # Validate inputs
    errors = []
    User = get_user_model()

    out = {"success": False, "errors": errors}

    # Check username is unique
    if (User.objects.filter(username=username).exists() or
       User.objects.filter(email=username).exists()):
        errors.append("That username is already in use.")
        return JsonResponse(out)

    # Check email is valid
    parsed = parseaddr(email)[1]
    if '@' not in parsed or len(parsed) < 3:
        errors.append("Please enter a valid email address.")
        return JsonResponse(out)

    # Check email is unique
    if User.objects.filter(email=email).exists():
        errors.append("That email is already in use.")
        return JsonResponse(out)

    # Validate password
    try:
        validate_password(password)
    except ValidationError as e:
        errors += e
        return JsonResponse(out)

    # Check passwords match
    if password != password_confirm:
        errors.append("Passwords do not match.")
        return JsonResponse(out)

    # Create User
    user = User.objects.create_user(username, email, password)
    login(request, user)
    user_data = get_user(request)
    out = {"success": True, "user": user_data}

    return JsonResponse(out)


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
    try:
        topic = ntc.get_next_topic(profile)
    except IndexError:
        topic = ntc.get_last_voted_topic(profile)
        return {"success": False,
                "error": "All topics have been voted on.",
                "topic": topic,
                "handled": True}
    return {"success": True, "topic": topic}


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
def skip_topic(profile, **data):
    """Store user vote on a topic and return topic info"""

    success, errors = ntc.skip_topic(profile, data)

    if not success:
        return {'success': success, 'errors': errors}

    topic = ntc.get_next_topic(profile)

    return {"success": success, "topic": topic}


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
