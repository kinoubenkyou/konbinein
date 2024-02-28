from django.core.cache import cache
from mongoengine import connect, disconnect, get_connection
from rest_framework.test import APITestCase

from konbinein.settings import MONGO


class TestCase(APITestCase):
    def setUp(self):
        super().setUp()
        connect(**MONGO["test"])

    def tearDown(self):
        super().tearDown()
        cache.clear()
        get_connection().drop_database("test")
        disconnect()
