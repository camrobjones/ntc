"""
Test NTC Views
"""

import requests

from django.test import TestCase

from ntc import views, models

"""
Test create_topic
"""


class TestCreateTopic(TestCase):
    """Test the create topic view"""

    @classmethod
    def SetUpClass(cls):
        """Create session and grab token"""
        URL = 'http://127.0.0.1:8000/spyke'

        cls.client = requests.session()

        # Retrieve the CSRF token first
        cls.client.get(URL)  # sets cookie
        if 'csrftoken' in cls.client.cookies:
            # Django 1.6 and up
            csrftoken = cls.client.cookies['csrftoken']

        cls.client.headers.update({"X-CSRFToken": csrftoken})

    def test_create_topic(self):
        # TODO: Use django request factory
        r = self.client.post(
            "http://127.0.0.1:8000/ntc/create_topic",
            # data={"csrfmiddlewaretoken": csrftoken},
            json={
                "name": "Ron Paul",
                "description": "Ronald Ernest Paul (born August 20, 1935) is an American author, physician, retired politician, and presidential candidate who served as the U.S. Representative for Texas's 22nd congressional district from 1976 to 1977 and again from 1979 to 1985, and for Texas's 14th congressional district from 1997 to 2013. On three occasions, he sought the presidency of the United States: as the Libertarian Party nominee in 1988 and as a candidate in the Republican primaries of 2008 and 2012.",
                "category": "PER",
                "tags": [],
                "url": "https://en.wikipedia.org/wiki/Ron_Paul"
                 }
            )
        print(r)

