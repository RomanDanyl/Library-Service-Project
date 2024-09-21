from django.shortcuts import render
from rest_framework import mixins
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.viewsets import GenericViewSet

from books.models import Book
from books.serializers import BookSerializer


class BookViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action == "list":
            permission_classes = [AllowAny]
        elif self.action != "list":
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
