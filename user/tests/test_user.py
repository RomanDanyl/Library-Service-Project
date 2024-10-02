from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model


class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "email": "testuser@example.com",
            "password": "testpass123",
        }
        self.user = get_user_model().objects.create_user(**self.user_data)

    def test_create_user(self):
        """Test creating a new user"""
        response = self.client.post(
            reverse("user:create"),
            {
                "email": "newuser@example.com",
                "password": "newpass123",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(get_user_model().objects.count(), 2)
        self.assertEqual(
            get_user_model().objects.get(id=2).email, "newuser@example.com"
        )

    def test_create_user_with_existing_email(self):
        """Test creating a user with existing email fails"""
        response = self.client.post(reverse("user:create"), self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticate_user(self):
        """Test authenticating a user"""
        response = self.client.post(reverse("user:token_obtain_pair"), self.user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_authenticate_invalid_user(self):
        """Test authenticating a user with wrong credentials"""
        response = self.client.post(
            reverse("user:token_obtain_pair"),
            {
                "email": "wronguser@example.com",
                "password": "wrongpass",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manage_user(self):
        """Test retrieving and updating the authenticated user"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("user:manage"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

        response = self.client.patch(
            reverse("user:manage"),
            {
                "email": "updateduser@example.com",
                "password": "updatedpass123",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "updateduser@example.com")
