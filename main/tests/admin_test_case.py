from main.tests.user_test_case import UserTestCase


class AdminTestCase(UserTestCase):
    is_user_system_administrator = True
