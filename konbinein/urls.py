from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from rest_framework import routers

from main.view_sets.admin_organization_view_set import AdminOrganizationViewSet
from main.view_sets.admin_user_view_set import AdminUserViewSet
from main.view_sets.order_shipping_view_set import OrderShippingViewSet
from main.view_sets.order_view_set import OrderViewSet
from main.view_sets.organization_organization_view_set import (
    OrganizationOrganizationViewSet,
)
from main.view_sets.organization_staff_view_set import OrganizationStaffViewSet
from main.view_sets.organization_user_view_set import OrganizationUserViewSet
from main.view_sets.product_shipping_view_set import ProductShippingViewSet
from main.view_sets.product_view_set import ProductViewSet
from main.view_sets.public_user_view_set import PublicUserViewSet
from main.view_sets.user_organization_view_set import UserOrganizationViewSet
from main.view_sets.user_staff_view_set import UserStaffViewSet
from main.view_sets.user_user_view_set import UserUserViewSet

router = routers.SimpleRouter(trailing_slash=False)
# Admin
router.register(
    "admin/organizations", AdminOrganizationViewSet, basename="admin-organization"
)
router.register("admin/users", AdminUserViewSet, basename="admin-user")
# Organization
router.register(
    "organizations/(?P<organization_id>[^/.]+)/order-shippings", OrderShippingViewSet
)
router.register("organizations/(?P<organization_id>[^/.]+)/orders", OrderViewSet)
router.register(
    "organizations/(?P<organization_id>[^/.]+)/organizations",
    OrganizationOrganizationViewSet,
    basename="organization-organization",
)
router.register(
    "organizations/(?P<organization_id>[^/.]+)/product-shippings",
    ProductShippingViewSet,
)
router.register("organizations/(?P<organization_id>[^/.]+)/products", ProductViewSet)
router.register(
    "organizations/(?P<organization_id>[^/.]+)/staffs",
    OrganizationStaffViewSet,
    basename="organization-staff",
)
router.register(
    "organizations/(?P<organization_id>[^/.]+)/users",
    OrganizationUserViewSet,
    basename="organization-user",
)
# Public
router.register("public/users", PublicUserViewSet, basename="public-user")
# User
router.register(
    "users/(?P<user_id>[^/.]+)/organizations",
    UserOrganizationViewSet,
    basename="user-organization",
)
router.register(
    "users/(?P<user_id>[^/.]+)/staffs", UserStaffViewSet, basename="user-staff"
)
router.register(
    "users/(?P<user_id>[^/.]+)/users", UserUserViewSet, basename="user-user"
)
urlpatterns = router.urls + [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]
