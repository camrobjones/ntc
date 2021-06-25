"""
Test NTC Views
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()

from ntc import models

"""
Test create_topic
"""

print("Running ntc.test_views.py")


class TestViews(TestCase):
    """Test the views"""

    @classmethod
    def SetUpClass(cls):
        """Create session and grab token"""
        print("\nRunning TestViews ...\n\n")

        # Create user for testing
        cls.user = User.objects.create(
            username="Tester",
            email="tester@testmail.com")
        cls.user.set_password("secret")
        cls.user.save()

        # Create client
        cls.client = Client()
        cls.profile = models.Profile.objects.create(user=cls.user)

        # Login client
        self.client.login(username='Tester', password='secret')

    def test_home_response(self):
        """Test home page responds"""
        print("test_home_response")
        self.client.login(username='Tester', password='secret')
        response = self.client.get("/ntc/")
        self.assertEqual(response.status_code, 200)

    def test_vote_response(self):
        """Test vote page responds"""
        print("test_vote_response")
        self.client.login(username='Tester', password='secret')
        response = self.client.get("/ntc/vote/")
        self.assertEqual(response.status_code, 200)

    def test_topic_response(self):
        """Test topic page responds"""
        print("test_topic_response")
        self.client.login(username='Tester', password='secret')
        profile = models.Profile.objects.create(user=cls.user)
        response = self.client.get("/ntc/vote/1/")
        self.assertEqual(response.status_code, 200)

    # API views

    def test_create_topic_response(self):
        """Test homepage responds"""
        self.client.login(username='Tester', password='secret')
        response = self.client.get("/ntc/create_topic")
        self.assertEqual(response.status_code, 200)

    # API views

    # path('check_topic_duplicates/', views.check_topic_duplicates),
    # path('search_topic', views.search_topic),
    # path('get_topic/<int:topic_id>/', views.get_topic),
    # path('next_topic/', views.next_topic),
    # path('random_topic/', views.random_topic),
    # path('submit_vote/', views.submit_vote),
    # path('submit_comment/', views.submit_comment),
    # path('submit_comment_vote/', views.submit_comment_vote)


    # def test_create_topic(self):
    #     # TODO: Use django request factory
    #     r = self.client.post(
    #         "http://127.0.0.1:8000/ntc/create_topic",
    #         # data={"csrfmiddlewaretoken": csrftoken},
    #         json={
    #             "name": "Ron Paul",
    #             "description": "Ronald Ernest Paul (born August 20, 1935) is an American author, physician, retired politician, and presidential candidate who served as the U.S. Representative for Texas's 22nd congressional district from 1976 to 1977 and again from 1979 to 1985, and for Texas's 14th congressional district from 1997 to 2013. On three occasions, he sought the presidency of the United States: as the Libertarian Party nominee in 1988 and as a candidate in the Republican primaries of 2008 and 2012.",
    #             "category": "PER",
    #             "tags": [],
    #             "url": "https://en.wikipedia.org/wiki/Ron_Paul"
    #              }
    #         )
    #     print(r)

