from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing


class BorrowingCreateTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@mail.com", password="testpass"
        )

        self.client.force_authenticate(user=self.user)
        self.url = reverse("borrowings:borrowing-list")

    def test_create_borrowing(self):
        book = Book.objects.create(
            title="Test Book",
            author="test author",
            cover="HARD",
            inventory=5,
            daily_fee=10.50,
        )
        data = {
            "book_id": book.id,
            "expected_return": date.today() + timedelta(days=5),
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        borrowing = Borrowing.objects.get(book_id=book.id)
        self.assertEqual(borrowing.book_id, book.id)
        self.assertEqual(borrowing.user_id, self.user.id)
        book.refresh_from_db()
        self.assertEqual(book.inventory, 4)
