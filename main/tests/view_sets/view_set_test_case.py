from django.core import mail
from django.core.cache import cache
from django.db.models import QuerySet
from mongoengine import get_connection
from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.test import APITestCase


class ViewSetTestCase(APITestCase):
    maxDiff = None

    def tearDown(self):
        super().tearDown()
        cache.clear()
        get_connection().drop_database("test")

    def _act_and_assert_action_response_status(self, action, data, pk):
        response = self.client.post(self._action_path(action, pk), data, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def _act_and_assert_action_validation_test(self, action, data, expected, pk):
        response = self.client.post(self._action_path(action, pk), data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), expected)

    def _act_and_assert_create_test(self, data, filter_):
        self._act_and_assert_create_test_response_status(data)
        self._assert_saved_object(filter_)
        self._assert_saved_activity(data, filter_)

    def _act_and_assert_create_test_response_status(self, data):
        response = self.client.post(self._list_path(), data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def _act_and_assert_create_validation_test(self, data, expected):
        response = self.client.post(self._list_path(), data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), expected)

    def _act_and_assert_destroy_test(self, object_):
        self._act_and_assert_destroy_test_response_status(object_.id)
        self._assert_destroyed_object(object_)

    def _act_and_assert_destroy_test_response_status(self, pk):
        response = self.client.delete(self._detail_path(pk), format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def _act_and_assert_list_test(self, data):
        response = self.client.get(self._list_path(), data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(
            response.json()["results"], self._expected_data_list(data)
        )

    def _act_and_assert_retrieve_test(self, pk):
        response = self.client.get(self._detail_path(pk), format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertCountEqual(response.json(), self._expected_data_list({"id": pk})[0])

    def _act_and_assert_update_test(self, data, filter_, pk):
        self._act_and_assert_update_test_response_status(data, pk)
        filter_ = {**filter_, "id": pk}
        self._assert_saved_object(filter_)
        self._assert_saved_activity(data, filter_)

    def _act_and_assert_update_test_response_status(self, data, pk):
        response = self.client.put(self._detail_path(pk), data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def _act_and_assert_update_validation_test(self, data, expected, pk):
        response = self.client.put(self._detail_path(pk), data, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), expected)

    def _action_path(self, action, pk):
        kwargs = {}
        if pk is not None:
            kwargs["pk"] = pk
        return self._path(action, kwargs)

    def _assert_destroyed_object(self, object_):
        self.assertFalse(self.view_set.queryset.filter(id=object_.id).exists())

    def _assert_email(self, body, subject, to):
        dict_ = mail.outbox[0].__dict__
        self.assertEqual(dict_["body"], body)
        self.assertEqual(dict_["from_email"], "webmaster@localhost")
        self.assertEqual(dict_["subject"], subject)
        self.assertCountEqual(dict_["to"], to)

    def _assert_saved_activity(self, data, filter_):
        object_ = self.view_set.queryset.filter(**filter_).get()
        query_set = self.view_set.activity_class.objects.filter(
            creator_id=getattr(self, "user", None) and self.user.id,
            creator_organization_id=getattr(self, "organization", None)
            and self.organization.id,
            creator_type=self.view_set.activity_type,
            data=data,
            object_id=object_.id,
            organization_id=getattr(object_, "organization_id", None),
            user_id=getattr(object_, "user_id", None),
        )
        self.assertEqual(query_set.count(), 1)

    def _assert_saved_object(self, filter_):
        self.assertEqual(self.view_set.queryset.filter(**filter_).count(), 1)

    def _detail_path(self, pk):
        return self._path("detail", {"pk": pk})

    @classmethod
    def _expected_data_list(cls, request_query):
        filter_ = {
            key: value
            for key, value in request_query.items()
            if key not in ["limit", "offset", "ordering"]
        }
        query_set = cls.view_set.queryset.filter(**filter_)
        if isinstance(query_set, QuerySet):
            query_set = query_set.distinct()
        if "ordering" in request_query:
            query_set = query_set.order_by(request_query["ordering"])
        offset = request_query.get("offset", 0)
        return [
            cls._serializer_data(object_)
            for object_ in query_set[
                offset : (
                    (request_query["limit"] + offset)
                    if "limit" in request_query
                    else None
                )
            ]
        ]

    def _list_path(self):
        return self._path("list", {})

    def _path(self, action, kwargs):
        return reverse(f"{self.basename}-{action}", kwargs=kwargs)
