from main.tests.view_sets.authenticated_test_case import AuthenticatedTestCase


class AdminTestCase(AuthenticatedTestCase):
    is_user_system_administrator = True
