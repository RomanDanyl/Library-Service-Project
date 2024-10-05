from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book

BOOKS_URL = reverse("books:book-list")


def sample_book(**params):
    defaults = {
        "title": "Sample Book",
        "author": "Sample Author",
        "cover": "HARD",
        "inventory": 10,
        "daily_fee": 2.50,
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


def detail_url(book_id):
    return reverse("books:book-detail", args=[book_id])


class UnauthorizedTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_not_required_for_list(self):
        response = self.client.get(BOOKS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auth_required_for_detail_post_put_path_delete(self):
        book = sample_book()
        url = detail_url(book.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        payload = {
            "title": "book1",
            "author": "author1",
            "cover": "SOFT",
            "inventory": 3,
            "daily_fee": 2.5,
        }
        response = self.client.post(BOOKS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        payload = {
            "title": "book2",
            "author": "author2",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": 1.5,
        }
        response = self.client.put(url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        payload.update({"title": "book3"})
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAsAdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@mail.com",
            password="<PASSWORD>",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_detail_post_put_path_delete_allow(self):
        book = sample_book()
        url = detail_url(book.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payload = {
            "title": "book1",
            "author": "author1",
            "cover": "SOFT",
            "inventory": 3,
            "daily_fee": 2.5,
        }
        response = self.client.post(BOOKS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        book = Book.objects.get(id=response.data["id"])
        for key in payload:
            self.assertEqual(payload[key], getattr(book, key))

        payload = {
            "title": "book2",
            "author": "author2",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": 1.5,
        }
        response = self.client.put(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payload.update({"title": "book3"})
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
