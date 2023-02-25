from rest_framework import routers

from main.views.order_view import OrderViewSet
from main.views.organization_personnel_view import OrganizationPersonnelViewSet
from main.views.organization_view import OrganizationViewSet
from main.views.personnel_view import PersonnelViewSet
from main.views.user_view import UserViewSet

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
