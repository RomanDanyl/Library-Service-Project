import stripe
from django.conf import settings
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

    def post(self, request, *args, **kwargs):
        borrowing_id = kwargs.get("borrowing_id")
        borrowing = Borrowing.objects.get(id=borrowing_id)
        book = Book.objects.get(id=borrowing.book_id)
        borrowing_days = (borrowing.expected_return - borrowing.borrow_date).days

        total_amount = book.daily_fee * borrowing_days
        total_amount_in_cents = int(total_amount * 100)

        try:
            payment = create_stripe_session(borrowing, total_amount_in_cents)
            return Response(
                {"id": payment.session_id, "url": payment.session_url},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
