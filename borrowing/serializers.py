from datetime import datetime

from rest_framework import serializers

from books.models import Book
from books.serializers import BookSerializer
from borrowing.models import Borrowing


class BorrowingReadSerializer(serializers.ModelSerializer):
    book_details = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return",
            "actual_return",
            "book_details",
            "user_id",
        )

    def get_book_details(self, obj):
        try:
            book = Book.objects.get(id=obj.book_id)
            return BookSerializer(book).data
        except Book.DoesNotExist:
            return None


class BorrowingCreateSerializer(
    BorrowingReadSerializer,
    serializers.ModelSerializer,
):
    class Meta:
        model = Borrowing
        fields = ("expected_return", "book_id")
        read_only_fields = ("user_id",)

    def create(self, validated_data):
        book = Book.objects.get(id=validated_data["book_id"])
        book.inventory -= 1
        book.save()
        validated_data["user_id"] = self.context["request"].user.id
        borrowing = Borrowing.objects.create(**validated_data)
        return borrowing

    def validate(self, data):
        if "borrow_date" not in data or data["borrow_date"] is None:
            data["borrow_date"] = datetime.now().date()

        borrow_date = data["borrow_date"]
        expected_return = data.get("expected_return")
        actual_return = data.get("actual_return")

        if expected_return <= borrow_date:
            raise serializers.ValidationError(
                {
                    "expected_return": "Expected return date must be after the borrow date."
                }
            )

        if actual_return and borrow_date:
            if actual_return <= borrow_date:
                raise serializers.ValidationError(
                    {
                        "actual_return": "Actual return date must be after the borrow date."
                    }
                )

        book = Book.objects.filter(id=data["book_id"]).first()
        if not book or book.inventory <= 0:
            raise serializers.ValidationError("Book is not available for borrowing.")

        return data
