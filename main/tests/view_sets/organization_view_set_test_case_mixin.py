from main.tests.view_sets.view_set_test_case_mixin import ViewSetTestCaseMixin


class OrganizationViewSetTestCaseMixin(ViewSetTestCaseMixin):
    def _path(self, action, kwargs):
        kwargs["organization_id"] = self.organization.id
        return super()._path(action, kwargs)
