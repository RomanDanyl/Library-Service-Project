from drf_spectacular.utils import OpenApiParameter, extend_schema_view, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingReadSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "is_active",
                str,
                description="Filter by active status (true/false)",
                required=False,
            ),
            OpenApiParameter(
                "user_id",
                int,
                description="Filter by users ID (only for staff users)",
                required=False,
            ),
        ]
    )
)
class BorrowingViewSet(
    ListModelMixin, CreateModelMixin, RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        is_active = self.request.query_params.get("is_active", None)
        queryset = self.queryset

        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                user_id = self.request.query_params.get("user_id", None)
                if user_id:
                    queryset = queryset.filter(user_id=user_id)
            else:
                queryset = queryset.filter(user_id=self.request.user.id)

            if is_active:
                if is_active.lower() == "true":
                    queryset = queryset.filter(actual_return__isnull=True)
                elif is_active.lower() == "false":
                    queryset = queryset.exclude(actual_return__isnull=True)
        return queryset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return BorrowingReadSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "return_borrowing":
            return BorrowingReturnSerializer

        return BorrowingReadSerializer

    @action(
        methods=["post"],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path="return",
    )
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        serializer = self.get_serializer(borrowing, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
