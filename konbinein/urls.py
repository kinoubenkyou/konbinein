from rest_framework import routers

from main.views.admin_organization_view import AdminOrganizationViewSet
from main.views.order_view import OrderViewSet
from main.views.organization_personnel_view import OrganizationPersonnelViewSet
from main.views.organization_view import OrganizationViewSet
from main.views.personnel_view import PersonnelViewSet
from main.views.public_user_view import PublicUserViewSet
from main.views.user_view import UserViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(
    r"admin/organizations", AdminOrganizationViewSet, basename="admin-organization"
)
router.register(r"organizations", OrganizationViewSet)
router.register(r"organizations/(?P<organization_id>[^/.]+)/orders", OrderViewSet)
router.register(
    r"organizations/(?P<organization_id>[^/.]+)/personnels",
    OrganizationPersonnelViewSet,
    basename="organization-personnel",
)
router.register(r"users", UserViewSet)
router.register(r"users/(?P<user_id>[^/.]+)/personnels", PersonnelViewSet)
router.register(r"public/users", PublicUserViewSet, basename="public-user")
urlpatterns = router.urls
