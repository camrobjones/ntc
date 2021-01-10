"""
NTC API utils
-------------
Helper functions and wrappers for API
"""

import json
import logging
from functools import wraps

from django.http import JsonResponse
from django.utils import timezone as tz

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
