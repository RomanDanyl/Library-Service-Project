from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from borrowing.models import Borrowing


class BorrowingFilterIsActiveTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@mail.com", password="testpass"
        )
        self.client.force_authenticate(user=self.user)
        self.book = Book.objects.create(
            title="Test Book", author="Test Author", inventory=5, daily_fee=10
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date=date.today(),
            book_id=self.book.id,
            user_id=self.user.id,
            expected_return=date.today() + timedelta(days=5),
            actual_return=None,
        )

    def test_filter_active_borrowings(self):
        url = reverse("borrowings:borrowing-list") + "?is_active=true"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        self.borrowing.actual_return = date.today()
        self.borrowing.save()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)


class BorrowingFilterTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="user@mail.com", password="testpass"
        )
        self.staff_user = get_user_model().objects.create_user(
            email="staff@mail.com", password="testpass", is_staff=True
        )

        self.book1 = Book.objects.create(
            title="Book One", author="Author A", cover="HARD", inventory=5, daily_fee=10
        )
        self.book2 = Book.objects.create(
            title="Book Two", author="Author B", cover="SOFT", inventory=3, daily_fee=15
        )

        self.borrowing1 = Borrowing.objects.create(
            user_id=self.user.id,
            book_id=self.book1.id,
            borrow_date=date.today(),
            expected_return=date.today() + timedelta(days=5),
        )
        self.borrowing2 = Borrowing.objects.create(
            user_id=self.user.id,
            book_id=self.book2.id,
            borrow_date=date.today(),
            expected_return=date.today() + timedelta(days=5),
        )
        self.borrowing3 = Borrowing.objects.create(
            user_id=self.staff_user.id,
            book_id=self.book1.id,
            borrow_date=date.today(),
            expected_return=date.today() + timedelta(days=5),
        )

    def test_filter_by_user_id_as_staff(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.get(
            reverse("borrowings:borrowing-list"), {"user_id": self.user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["id"], self.borrowing1.id)
        self.assertEqual(response.data["results"][1]["id"], self.borrowing2.id)

    def test_filter_by_user_id_as_non_staff(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("borrowings:borrowing-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["id"], self.borrowing1.id)
        self.assertEqual(response.data["results"][1]["id"], self.borrowing2.id)

    def test_filter_by_user_id_non_existent(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.get(
            reverse("borrowings:borrowing-list"), {"user_id": 999}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data["results"]), 0)
