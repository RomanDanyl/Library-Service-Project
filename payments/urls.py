from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payments.views import (
    PaymentViewSet,
    PaymentSuccessView,
    PaymentCancelView,
    PaymentSuccessTempView,
)

router = DefaultRouter()
router.register("payments", PaymentViewSet, basename="payments")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "payments/success/<str:session_id>/",
        PaymentSuccessView.as_view(),
        name="payments-success",
    ),
    path("payments/cancel/", PaymentCancelView.as_view(), name="payments-cancel"),
    path("checkout/", PaymentSuccessTempView.as_view(), name="checkout-success"),
]

app_name = "payments"
