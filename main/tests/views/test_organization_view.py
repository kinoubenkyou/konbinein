from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from main.factories.organization_factory import OrganizationFactory
from main.factories.personnel_factory import PersonnelFactory
from main.factories.user_factory import UserFactory
from main.tests.views import TokenAuthenticatedTestCase


class OrganizationPersonnelViewSetTestCase(TokenAuthenticatedTestCase):
    def test_create(self):
        organization = OrganizationFactory.create()
        PersonnelFactory.create(
            does_organization_agree=True,
            does_user_agree=True,
            organization=organization,
            user=self.user,
        )
        path = reverse(
            "organization_personnel-list", kwargs={"organization_id": organization.id}
        )
        data = {"user": UserFactory.create().id}
        response = self.client.post(path, data, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_post_agreeing(self):
        organization = OrganizationFactory.create()
        PersonnelFactory.create(
            does_organization_agree=True,
            does_user_agree=True,
            organization=organization,
            user=self.user,
        )
        personnel = PersonnelFactory.create(organization=organization)
        path = reverse(
            "organization_personnel-agreeing",
            kwargs={"organization_id": organization.id, "pk": personnel.id},
        )
        response = self.client.post(path, {}, format="json")
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)


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
