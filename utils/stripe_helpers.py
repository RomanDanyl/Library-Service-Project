from decimal import Decimal

import stripe
from django.conf import settings

from books.models import Book
from borrowing.models import Borrowing
from payment.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(borrowing: Borrowing, total_amount: Decimal) -> Payment:
    book = Book.objects.get(id=borrowing.book_id)
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Borrowing for {book.title}",
                    },
                    "unit_amount": int(total_amount * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=settings.STRIPE_SUCCESS_URL,
        cancel_url=settings.STRIPE_CANCEL_URL,
    )

    payment = Payment.objects.create(
        status=Payment.StatusChoices.PENDING,
        type=Payment.TypeChoices.PAYMENT,
        borrowing_id=borrowing.id,
        session_url=checkout_session.url,
        session_id=checkout_session.id,
        money_to_pay=total_amount,
    )

    return payment
