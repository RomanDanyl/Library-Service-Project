from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payment.views import PaymentViewSet, CreateCheckoutSession

router = DefaultRouter()
router.register("payments", PaymentViewSet, basename="payments")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "create-checkout-session/",
        CreateCheckoutSession.as_view(),
        name="create-checkout-session",
    ),
]

app_name = "payments"
