from rest_framework import routers

from main.views import OrderViewSet, OrganizationViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register("orders", OrderViewSet)
router.register("organizations", OrganizationViewSet)
urlpatterns = router.urls
