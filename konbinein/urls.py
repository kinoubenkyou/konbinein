from rest_framework import routers

from main.views import OrderViewSet

router = routers.SimpleRouter()
router.register("orders", OrderViewSet)
urlpatterns = router.urls
