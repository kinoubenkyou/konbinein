from rest_framework import routers

from main.views import OrderViewSet, OrganizationViewSet, UserViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register("orders", OrderViewSet)
router.register("organizations", OrganizationViewSet)
router.register("users", UserViewSet)
urlpatterns = router.urls
