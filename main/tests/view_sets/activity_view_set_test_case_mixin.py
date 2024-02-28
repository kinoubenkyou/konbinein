from main.tests.view_sets.view_set_test_case_mixin import ViewSetTestCaseMixin


class ActivityViewSetTestCaseMixin(ViewSetTestCaseMixin):
    def _act_and_assert_create_test(self, data, filter_):
        super()._act_and_assert_create_test(data, filter_)
        instance_id = self.query_set.filter(**filter_).first().id
        self._assert_saved_activity("create", data, instance_id)

    def _act_and_assert_destroy_test(self, pk):
        super()._act_and_assert_destroy_test(pk)
        self._assert_saved_activity("destroy", {}, pk)

    def _act_and_assert_update_test(self, data, filter_, pk):
        super()._act_and_assert_update_test(data, filter_, pk)
        self._assert_saved_activity("update", data, pk)

    def _assert_saved_activity(self, action, data, instance_id):
        user = self.user
        self.assertEqual(
            len(
                self.view_set.activity_class.objects(
                    action=action,
                    instance_id=instance_id,
                    user_id=user.id,
                    user_name=user.name,
                    **data
                )
            ),
            1,
        )
