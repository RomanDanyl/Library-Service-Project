from rest_framework import routers

from borrowing.views import BorrowingViewSet


app_name = "borrowings"

router = routers.DefaultRouter()
router.register("borrowings", BorrowingViewSet)

urlpatterns = router.urls
