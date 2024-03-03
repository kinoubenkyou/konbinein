from django.core import mail
from django.core.cache import cache
from mongoengine import connect, disconnect, get_connection
from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.test import APITestCase

from konbinein.settings import MONGO


class ViewSetTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        connect(**MONGO["test"])

    def tearDown(self):
        super().tearDown()
        cache.clear()
        get_connection().drop_database("test")
        disconnect()

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
        self._assert_saved_object({**filter_, "id": pk})

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
        self.assertIsNone(self.view_set.queryset.filter(id=object_.id).first())

    def _assert_email(self, body, subject, to):
        dict_ = mail.outbox[0].__dict__
        self.assertEqual(dict_["body"], body)
        self.assertEqual(dict_["from_email"], "webmaster@localhost")
        self.assertEqual(dict_["subject"], subject)
        self.assertCountEqual(dict_["to"], to)

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
        query_set = cls.view_set.queryset.filter(**filter_).distinct()
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
