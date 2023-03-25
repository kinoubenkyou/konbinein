from rest_framework import routers

from main.views.admin_organization_view import AdminOrganizationViewSet
from main.views.order_view import OrderViewSet
from main.views.organization_staff_view import OrganizationStaffViewSet
from main.views.organization_view import OrganizationViewSet
from main.views.public_user_view import PublicUserViewSet
from main.views.staff_view import StaffViewSet
from main.views.user_view import UserViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(
    r"admin/organizations", AdminOrganizationViewSet, basename="admin-organization"
)
router.register(r"organizations", OrganizationViewSet)
router.register(r"organizations/(?P<organization_id>[^/.]+)/orders", OrderViewSet)
router.register(
    r"organizations/(?P<organization_id>[^/.]+)/staffs",
    OrganizationStaffViewSet,
    basename="organization-staff",
)
router.register(r"users", UserViewSet)
router.register(r"users/(?P<user_id>[^/.]+)/staffs", StaffViewSet)
router.register(r"public/users", PublicUserViewSet, basename="public-user")
urlpatterns = router.urls
