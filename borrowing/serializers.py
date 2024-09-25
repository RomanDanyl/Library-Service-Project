from datetime import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.models import Book
from books.serializers import BookSerializer
from borrowing.models import Borrowing
from utils.stripe_helpers import create_stripe_session
from payment.models import Payment
from payment.serializers import PaymentSerializer


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

    def get_book_details(self, obj):
        try:
            book = Book.objects.get(id=obj.book_id)
            return BookSerializer(book).data
        except Book.DoesNotExist:
            return None

    def get_payments(self, obj):
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
            create_stripe_session(borrowing, total_amount)
        except Exception as e:
            raise ValidationError({"error": str(e)})

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
            raise serializers.ValidationError("Book is not available for borrowing.")

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
                {"error": "This borrowing has already been returned."}
            )

        borrowing.actual_return = datetime.today().date()

        book = Book.objects.get(pk=borrowing.book_id)
        book.inventory += 1
        book.save()

        borrowing.save()
        return borrowing
