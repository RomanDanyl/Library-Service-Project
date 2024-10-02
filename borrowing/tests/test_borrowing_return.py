from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from borrowing.models import Borrowing
from payment.models import Payment


class BorrowingReturnTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@mail.com", password="testpass"
        )
        self.book = Book.objects.create(
            title="Test Book", author="Test Author", inventory=5, daily_fee=10
        )
        self.client.force_authenticate(user=self.user)
        self.borrowing = Borrowing.objects.create(
            borrow_date=date.today(),
            book_id=self.book.id,
            user_id=self.user.id,
            expected_return=date.today() + timedelta(days=5),
            actual_return=None,
        )
        self.url = reverse(
            "borrowings:borrowing-return-borrowing", args=[self.borrowing.id]
        )

    def test_return_on_time(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        borrowing = Borrowing.objects.get(id=self.borrowing.id)
        self.assertIsNotNone(borrowing.actual_return)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 6)

    @patch.object(Borrowing, "clean", lambda self: None)
    @patch(
        "borrowing.serializers.BorrowingReturnSerializer.validate",
        lambda self, data: data,
    )
    def test_return_late_with_fine(self):
        self.borrowing.expected_return = date.today() - timedelta(days=2)
        self.borrowing.actual_return = None
        self.borrowing.save()

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        borrowing = Borrowing.objects.get(id=self.borrowing.id)
        self.assertIsNotNone(borrowing.actual_return)

        payments = Payment.objects.filter(borrowing_id=borrowing.id)
        self.assertEqual(payments.count(), 1)
        self.assertEqual(payments[0].type, Payment.TypeChoices.FINE)
