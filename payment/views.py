import stripe
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import viewsets, status
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from books.models import Book
from borrowing.models import Borrowing
from utils.stripe_helpers import create_stripe_session
from payment.models import Payment
from payment.serializers import PaymentSerializer


class PaymentViewSet(ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_borrowings = Borrowing.objects.filter(user_id=user.id)
        user_borrowings_ids = user_borrowings.values_list("id", flat=True)
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(borrowing_id__in=user_borrowings_ids)


stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def post(self, request, *args, **kwargs):
        borrowing_id = kwargs.get("borrowing_id")
        borrowing = Borrowing.objects.get(id=borrowing_id)
        book = Book.objects.get(id=borrowing.book_id)
        borrowing_days = (borrowing.expected_return - borrowing.borrow_date).days

        total_amount = book.daily_fee * borrowing_days

        try:
            payment = create_stripe_session(
                borrowing, total_amount, Payment.TypeChoices.PAYMENT, request
            )
            return Response(
                {"id": payment.session_id, "url": payment.session_url},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentSuccessTempView(APIView):
    def get(self, request):
        session_id = request.GET.get("session_id")
        if session_id:
            return redirect(
                reverse("payments:payment-success", kwargs={"session_id": session_id})
            )
        return Response(
            {"error": "Session ID not found."}, status=status.HTTP_400_BAD_REQUEST
        )


class PaymentSuccessView(APIView):
    serializer_class = PaymentSerializer

    def get(self, request, session_id):
        try:
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == "paid":
                try:
                    payment = Payment.objects.get(session_id=session_id)
                    payment.status = Payment.StatusChoices.PAID
                    payment.save()
                    return Response({"message": "Payment successful."})
                except Payment.DoesNotExist:
                    return Response({"error": "Payment not found."}, status=404)
            else:
                return Response({"message": "Payment not completed."}, status=400)

        except stripe.error.StripeError as e:
            return Response({"stripe_error": str(e)}, status=500)
        except Exception as e:
            return Response({"other_error": str(e)}, status=500)


class PaymentCancelView(APIView):
    serializer_class = PaymentSerializer

    def get(self, request):
        return Response(
            {"message": "Payment was cancelled. You can pay again within 24 hours."}
        )
