from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from main.factories.organization_factory import OrganizationFactory
from main.factories.personnel_factory import PersonnelFactory
from main.tests.views import TokenAuthenticatedTestCase


class PersonnelViewSetTestCase(TokenAuthenticatedTestCase):
    def test_create(self):
        path = reverse("personnel-list")
        data = {"organization": OrganizationFactory.create().id}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_post_agreeing(self):
        personnel = PersonnelFactory.create(user=self.user)
        path = reverse("personnel-agreeing", kwargs={"pk": personnel.id})
        response = self.client.post(path, {}, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
