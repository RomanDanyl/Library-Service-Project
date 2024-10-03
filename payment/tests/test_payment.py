from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from borrowing.models import Borrowing
from payment.models import Payment
from books.models import Book


class BorrowingPaymentTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@mail.com", password="testpass"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="SOFT",
            daily_fee=10,
            inventory=5,
        )
        self.client.force_authenticate(user=self.user)

    def test_borrowing_creates_payment(self):
        data = {
            "borrow_date": "2024-10-03",
            "expected_return": "2024-10-10",
            "book_id": self.book.id,
        }

        response = self.client.post(
            reverse("borrowings:borrowing-list"), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        borrowing_id = response.data["id"]
        borrowing = Borrowing.objects.get(id=borrowing_id)

        payment = Payment.objects.filter(borrowing_id=borrowing.id).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.type, Payment.TypeChoices.PAYMENT)
        self.assertEqual(payment.status, Payment.StatusChoices.PENDING)
        self.assertEqual(payment.money_to_pay, self.book.daily_fee * 7)
