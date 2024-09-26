from decimal import Decimal

import stripe
from django.conf import settings
from django.urls import reverse

from books.models import Book
from borrowing.models import Borrowing
from payment.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(
    borrowing: Borrowing, total_amount: Decimal, request
) -> Payment:
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
        success_url=request.build_absolute_uri(reverse("payments:checkout-success"))
        + f"?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=request.build_absolute_uri(reverse("payments:payment-cancel")),
    )

    payment = Payment.objects.create(
        status=Payment.StatusChoices.PENDING,
        type=Payment.TypeChoices.PAYMENT,
        session_id=checkout_session.id,
        session_url=checkout_session.url,
        borrowing_id=borrowing.id,
        money_to_pay=total_amount,
    )
    print(f"id: {payment.session_id}")

    return payment
