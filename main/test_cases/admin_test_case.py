from main.test_cases.user_test_case import UserTestCase


class AdminTestCase(UserTestCase):
    is_user_system_administrator = True
