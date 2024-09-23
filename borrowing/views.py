from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingReadSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
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
