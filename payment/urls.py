from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payment.views import (
    PaymentViewSet,
    CreateCheckoutSession,
    PaymentSuccessView,
    PaymentCancelView,
    PaymentSuccessTempView,
)

router = DefaultRouter()
router.register("payments", PaymentViewSet, basename="payments")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "create-checkout-session/",
        CreateCheckoutSession.as_view(),
        name="create-checkout-session",
    ),
    path(
        "payments/success/<str:session_id>/",
        PaymentSuccessView.as_view(),
        name="payment-success",
    ),
    path("payments/cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
    path("checkout/", PaymentSuccessTempView.as_view(), name="checkout-success"),
]

app_name = "payments"
