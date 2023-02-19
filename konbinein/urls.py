from rest_framework import routers

from main.views import (
    OrderViewSet,
    OrganizationPersonnelViewSet,
    OrganizationViewSet,
    PersonnelViewSet,
    UserViewSet,
)

router = routers.SimpleRouter(trailing_slash=False)
router.register("orders", OrderViewSet)
router.register("organizations", OrganizationViewSet)
router.register(
    r"organizations/(?P<organization_id>[^/.]+)/personnels",
    OrganizationPersonnelViewSet,
    basename="organization_personnel",
)
router.register("users", UserViewSet)
router.register("personnels", PersonnelViewSet)
urlpatterns = router.urls
