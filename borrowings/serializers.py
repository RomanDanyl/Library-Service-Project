from datetime import datetime
from typing import Optional, Dict, List

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.models import Book
from books.serializers import BookSerializer
from borrowings.models import Borrowing
from utils.stripe_helpers import create_stripe_session
from payments.models import Payment
from payments.serializers import PaymentSerializer


FINE_MULTIPLIER = 2


class BorrowingReadSerializer(serializers.ModelSerializer):
    book_details = serializers.SerializerMethodField()
    payments = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return",
            "actual_return",
            "book_details",
            "user_id",
            "payments",
        )
        read_only_fields = ("user_id",)

    def get_book_details(self, obj: Borrowing) -> Optional[Dict]:
        try:
            book = Book.objects.get(id=obj.book_id)
            return BookSerializer(book).data
        except Book.DoesNotExist:
            return None

    def get_payments(self, obj: Borrowing) -> Optional[List]:
        try:
            payments = Payment.objects.filter(borrowing_id=obj.id)
            return PaymentSerializer(payments, many=True).data
        except Payment.DoesNotExist:
            return None


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return", "book_id", "user_id")
        read_only_fields = ("user_id",)

    def create(self, validated_data):
        book = Book.objects.get(id=validated_data["book_id"])
        book.inventory -= 1
        book.save()
        validated_data["user_id"] = self.context["request"].user.id
        borrowing = Borrowing.objects.create(**validated_data)

        borrowing_days = (borrowing.expected_return - borrowing.borrow_date).days
        total_amount = book.daily_fee * borrowing_days

        try:
            create_stripe_session(
                borrowing,
                total_amount,
                Payment.TypeChoices.PAYMENT,
                self.context["request"],
            )
        except Exception as e:
            raise ValidationError({"borrow_error": str(e)})

        return borrowing

    def validate(self, data):
        if "borrow_date" not in data or data["borrow_date"] is None:
            data["borrow_date"] = datetime.today().date()

        borrow_date = data["borrow_date"]
        expected_return = data.get("expected_return")

        if expected_return <= borrow_date:
            raise serializers.ValidationError(
                {
                    "expected_return": "Expected return date must be after the borrow date."
                }
            )

        book = Book.objects.filter(id=data["book_id"]).first()
        if not book or book.inventory <= 0:
            raise serializers.ValidationError("Book is not available for borrowings.")

        return data


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "book_id", "borrow_date", "expected_return", "actual_return"]
        read_only_fields = (
            "id",
            "borrow_date",
            "expected_return",
            "actual_return",
            "book_id",
            "user_id",
        )
        model = Borrowing

    def update(self, borrowing, validated_data):
        if borrowing.actual_return:
            raise serializers.ValidationError(
                {"error": "This borrowings has already been returned."}
            )

        borrowing.actual_return = datetime.today().date()

        book = Book.objects.get(pk=borrowing.book_id)
        book.inventory += 1
        book.save()

        borrowing.save()

        if borrowing.is_late():
            overdue_days = (borrowing.actual_return - borrowing.expected_return).days
            fine_amount = overdue_days * book.daily_fee * FINE_MULTIPLIER

            try:
                create_stripe_session(
                    borrowing,
                    fine_amount,
                    Payment.TypeChoices.FINE,
                    self.context["request"],
                )
            except Exception as e:
                raise ValidationError({"return_borrow_error": str(e)})

        return borrowing
