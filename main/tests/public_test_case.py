from rest_framework.test import APITestCase


class PublicTestCase(APITestCase):
    is_organization_view_set = False
    is_user_view_set = False
