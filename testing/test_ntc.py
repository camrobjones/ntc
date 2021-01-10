"""
Tests for ntc
"""

from django.test import TestCase
from django.utils import timezone as tz
from django.contrib.auth import get_user_model

from ntc import ntc
from ntc import models
from ntc.testing.test_data import topic_data


# class TestValidateTopicData(TestCase):
#     """Test topic data validation"""

#     @classmethod
#     def setUpClass(cls):
#         super(TestValidateTopicData, cls).setUpClass()

#         data_clean = topic_data['clean']
#         data_error = topic_data['error']

#         cls.clean_valid, cls.clean_out = ntc.validate_topic_data(data_clean)
#         cls.error_valid, cls.error_out = ntc.validate_topic_data(data_error)

#     def test_clean_no_error(self):
#         """Ensure no errors passed for clean data"""
#         self.assertTrue(self.clean_valid)
#         self.assertEqual(self.clean_out['error_count'], 0)
#         self.assertFalse(self.clean_out['errors'])

#     def test_invalid_error(self):
#         """Ensure errors data is flagged as invalid"""
#         self.assertTrue(self.error_valid)
#         self.assertTrue(self.error_out['error_count'] > 0)

#     def test_name_len_error(self):
#         """Ensure 'Name Too Long' error raised"""

#         # Check name key is in errors
#         self.assertIn('name', self.error_out['errors'])

#         name_errors = self.error_out['errors']['name']

#         self.assertIn("Name Too Long", name_errors)


class TestCreateTopic(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestCreateTopic, cls).setUpClass()

        # Create a user
        User = get_user_model()
        cls.user = User.objects.create(
            username="Tester",
            email="a@g.com")
        cls.profile = models.Profile.objects.create(user=cls.user)

    def setUp(self):

        data = topic_data()
        self.data = data['clean']
        self.errors = data['error']

        self.data['profile'] = self.profile

    def test_create_valid_topic(self):
        """Test valid data successfully creates a topic"""

        clean_topic = ntc.create_topic(self.data)

        self.assertTrue(clean_topic['success'])

    def test_name_error(self):
        """Check error is thrown for name length"""
        self.data['name'] = self.errors['name']

        topic = ntc.create_topic(self.data)

        self.assertFalse(topic['success'])
        self.assertTrue(topic['errors']['name'])

    def test_description_error(self):
        """Check error is thrown for name length"""
        self.data['description'] = self.errors['description']

        topic = ntc.create_topic(self.data)

        self.assertFalse(topic['success'])
        self.assertTrue(topic['errors']['description'])

    def test_category_error(self):
        """Check error is thrown for name length"""
        self.data['category'] = self.errors['category']

        topic = ntc.create_topic(self.data)

        self.assertFalse(topic['success'])
        self.assertTrue(topic['errors']['category'])

    def test_url_error(self):
        """Check error is thrown for name length"""
        self.data['url'] = self.errors['url']

        topic = ntc.create_topic(self.data)

        self.assertFalse(topic['success'])
        self.assertTrue(topic['errors']['url'])


class TestSearch(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSearch, cls).setUpClass()

        # Create a user
        User = get_user_model()
        cls.user = User.objects.create(
            username="SearchTester",
            email="searchtester@testmail.com")
        cls.profile = models.Profile.objects.create(user=cls.user)

        topic1 = ntc.create_topic(
            {"name": "topic1",
             "description": "Unusual word",
             "category": "PER",
             "profile": cls.profile})

        cls.topic1 = topic1['topic']

        topic2 = ntc.create_topic(
            {"name": "zebedee",
             "description": "Common word",
             "category": "PHI",
             "profile": cls.profile})

        cls.topic2 = topic2['topic']

    def test_search(self):
        """Test search functionality"""
        res = ntc.search('topic')
        print(res)

    def test_search_name(self):
        """Test search functionality"""
        res = ntc.search('zebedee')
        print(res)

    def test_search_description(self):
        """Test search description"""
        res = ntc.search('unusual')
        print(res)



