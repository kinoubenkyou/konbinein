from main.tests.view_sets.view_set_test_case_mixin import ViewSetTestCaseMixin


class UserViewSetTestCaseMixin(ViewSetTestCaseMixin):
    def _path(self, action, kwargs):
        kwargs["user_id"] = self.user.id
        return super()._path(action, kwargs)
