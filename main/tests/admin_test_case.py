from main.tests.user_test_case import UserTestCase


class AdminTestCase(UserTestCase):
    is_organization_view_set = False
    is_user_system_administrator = True
    is_user_view_set = False
