from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from rest_framework import routers

from main.view_sets.admin_organization_view_set import AdminOrganizationViewSet
from main.view_sets.admin_user_view_set import AdminUserViewSet
from main.view_sets.order_shipping_view_set import OrderShippingViewSet
from main.view_sets.order_view_set import OrderViewSet
from main.view_sets.organization_user_view_set import OrganizationUserViewSet
from main.view_sets.product_shipping_view_set import ProductShippingViewSet
from main.view_sets.product_view_set import ProductViewSet
from main.view_sets.public_user_view_set import PublicUserViewSet
from main.view_sets.staff_organization_view_set import OrganizationViewSet
from main.view_sets.staff_view_set import StaffViewSet
from main.view_sets.user_organization_view_set import UserOrganizationViewSet
from main.view_sets.user_staff_view_set import UserStaffViewSet
from main.view_sets.user_view_set import UserViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(
    r"admin/organizations", AdminOrganizationViewSet, basename="admin-organization"
)
router.register(r"admin/users", AdminUserViewSet, basename="admin-user")
router.register(
    r"organizations/(?P<organization_id>[^/.]+)/order-shippings",
    OrderShippingViewSet,
)
router.register(r"organizations/(?P<organization_id>[^/.]+)/orders", OrderViewSet)
router.register(
    r"organizations/(?P<organization_id>[^/.]+)/organizations", OrganizationViewSet
)
router.register(
    r"organizations/(?P<organization_id>[^/.]+)/users",
    OrganizationUserViewSet,
    basename="organization-user",
)
router.register(r"organizations/(?P<organization_id>[^/.]+)/products", ProductViewSet)
router.register(
    r"organizations/(?P<organization_id>[^/.]+)/product-shippings",
    ProductShippingViewSet,
)
router.register(
    r"organizations/(?P<organization_id>[^/.]+)/staffs",
    StaffViewSet,
    basename="organization-staff",
)
router.register(
    r"users/(?P<user_id>[^/.]+)/organizations",
    UserOrganizationViewSet,
    basename="user-organization",
)
router.register(
    r"users/(?P<user_id>[^/.]+)/staffs", UserStaffViewSet, basename="user-staff"
)
router.register(r"users/(?P<user_id>[^/.]+)/users", UserViewSet)
router.register(r"public/users", PublicUserViewSet, basename="public-user")
urlpatterns = router.urls + [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]
