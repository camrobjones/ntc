"""
NTC API utils
-------------
Helper functions and wrappers for API
"""

import json
import logging
from functools import wraps
from itertools import count, filterfalse
import re

from django.http import JsonResponse
from django.utils import timezone as tz
from django.contrib.auth import get_user_model, login

from ntc import models

logger = logging.getLogger(__name__)


"""
Utils
-----
General purpose tools
"""


def _decode(obj):
    """Helper function to decode JSON floats and ints as numeric"""
    if isinstance(obj, str):
        # First attempt to parse as float
        try:
            return float(obj)
        except ValueError:
            # Then try int
            try:
                return int(obj)
            except ValueError:
                # Then accept string
                return obj
    elif isinstance(obj, dict):
        return {k: _decode(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_decode(v) for v in obj]
    else:
        return obj


def parse_request(request, method=None):
    """Parse args from request"""
    data = {}

    if method is not None:
        if request.method != method:

            raise AttributeError(
                f"request method incorrect: {request.method}")

    if request.method == "GET":
        data.update(request.GET.dict())

    if request.method == "POST":
        data.update(request.POST.dict())

        body = request.body.decode('utf-8')

        if body is not None:
            data.update(json.loads(body, object_hook=_decode))

    return data


"""
Users
-----
"""

"""Guest Users"""


def generate_guest_username():
    """Generate a unique guest username."""
    # Get User model
    User = get_user_model()

    # Find all names starting with guest
    guests = User.objects.filter(username__startswith="guest")

    # Get just usernames
    guest_names = [x[0] for x in guests.values_list("username")]

    # Find the appended numbers
    guest_matches = [re.match("guest([0-9]+)$", n) for n in guest_names]
    guest_nos = [int(m.groups()[0]) for m in guest_matches if m]

    # Get the smallest int not in the list
    new_no = next(filterfalse(set(guest_nos).__contains__, count(1)))

    # Create new guest name with low int
    return f"guest{new_no}"


def create_guest_user():
    """Create a guest user."""
    # Get user model
    User = get_user_model()

    # generate username
    username = generate_guest_username()
    email = f"{username}@guest.com"
    password = User.objects.make_random_password()

    user = User.objects.create_user(username, email, password, guest=True)

    return user


def get_profile(user):
    """Get or create profile for user"""
    profile = models.Profile.objects.filter(user=user)

    # Return object if it exists
    if profile.exists():
        return profile.get()

    # Otherwise create and validate object
    profile = models.Profile(user=user)
    profile.full_clean()
    profile.save()

    return profile


def get_user(request, create_guest=True):
    """Retrieve user data from request"""
    user = request.user
    if not user.is_authenticated:
        if not create_guest:
            return {"is_authenticated": False}

        user = create_guest_user()
        login(request, user)

    profile = get_profile(user)

    data = profile.data

    # if not user.guest:
    data["is_authenticated"] = True

    return data


def get_api_data(request, kwargs):
    """Combine data sources"""
    data = parse_request(request)

    profile = get_profile(request.user)

    # Aggregate data
    data.update(kwargs)
    data['profile'] = profile

    return data


"""
API call wrapper
----------------
"""


def api(func):
    """Wrapper for API calls"""

    @wraps(func)
    def api_inner(request, **kwargs):
        """Wrapper inner call"""
        start = tz.now()

        data = get_api_data(request, kwargs)
        print(data)
        # Call function
        result = func(**data)

        out = {"success": True, "message": ""}
        out.update(result)

        delta = (tz.now() - start).total_seconds()
        logger.info("Response returned for %s in %.3fs",
                    func.__name__, delta)

        return JsonResponse(out)

    return api_inner


def create_topic(request):
    """Validate input and create topic"""
    logger.info("Request recieved at create_topic")

    # Extract submission data from request object
    data = parse_request(request)
    data['profile'] = ntc.get_profile(request.user)
    print(data)

    # Attempt to create topic
    data = ntc.create_topic(data)

    print(data)

    if data['topic']:
        data['topic'] = ntc.model2json(data['topic'])

    return JsonResponse(data)
