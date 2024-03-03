from main.tests.view_sets.authenticated_test_case import AuthenticatedTestCase


class UserTestCase(AuthenticatedTestCase):
    def _path(self, action, kwargs):
        kwargs["user_id"] = self.user.id
        return super()._path(action, kwargs)
