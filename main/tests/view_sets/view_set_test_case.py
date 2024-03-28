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

from main.shortcuts import OBSCURE_ACTIVITY_DATA_KEYS


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
        object_ = self._assert_and_get_saved_object(data, filter_)
        self._assert_saved_activity(data, object_)

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

    def _act_and_assert_list_test(self, request_query):
        response = self.client.get(self._list_path(), request_query, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        if "ordering" in request_query:
            self.assertEqual(
                response.json()["results"], self._expected_data_list(request_query)
            )
        else:
            self.assertCountEqual(
                response.json()["results"], self._expected_data_list(request_query)
            )

    def _act_and_assert_retrieve_test(self, pk):
        response = self.client.get(self._detail_path(pk), format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.json(), self._expected_data_list({"id": pk})[0])

    def _act_and_assert_update_test(self, data, filter_, pk):
        self._act_and_assert_update_test_response_status(data, pk)
        filter_ = {**filter_, "id": pk}
        object_ = self._assert_and_get_saved_object(data, filter_)
        self._assert_saved_activity(data, object_)

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

    def _assert_and_get_saved_object(self, data, filter_):
        objects = list(self._get_query_set().filter(**filter_))
        self.assertEqual(len(objects), 1)
        return objects[0]

    def _assert_destroyed_object(self, object_):
        self.assertFalse(self._get_query_set().filter(id=object_.id).exists())

    def _assert_email(self, body, subject, to):
        dict_ = mail.outbox[0].__dict__
        self.assertEqual(dict_["body"], body)
        self.assertEqual(dict_["from_email"], "webmaster@localhost")
        self.assertEqual(dict_["subject"], subject)
        self.assertCountEqual(dict_["to"], to)

    def _assert_saved_activity(self, request_data, object_):
        data = {
            key: value
            for key, value in request_data.items()
            if key not in OBSCURE_ACTIVITY_DATA_KEYS
        }
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

    def _detail_path(self, pk):
        return self._path("detail", {"pk": pk})

    def _expected_data_list(self, request_query):
        filter_ = {
            key: value
            for key, value in request_query.items()
            if key not in ["limit", "offset", "ordering"]
        }
        query_set = self._get_query_set().filter(**filter_)
        if isinstance(query_set, QuerySet):
            query_set = query_set.distinct()
        if "ordering" in request_query:
            query_set = query_set.order_by(request_query["ordering"])
        start_at = request_query.get("offset", 0)
        end_at = (
            (start_at + request_query["limit"]) if "limit" in request_query else None
        )
        return [
            self._get_serializer_data(object_) for object_ in query_set[start_at:end_at]
        ]

    def _list_path(self):
        return self._path("list", {})

    def _path(self, action, kwargs):
        return reverse(f"{self.basename}-{action}", kwargs=kwargs)
