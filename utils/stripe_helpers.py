from decimal import Decimal

import stripe
from django.conf import settings
from django.urls import reverse

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(
    borrowing: Borrowing, total_amount: Decimal, payment_type: str, request
) -> Payment:

    book = Book.objects.get(id=borrowing.book_id)

    if payment_type == Payment.TypeChoices.FINE:
        product_name = f"Fine for overdue borrowing of {book.title}"
    else:
        product_name = f"Borrowing for {book.title}"

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": product_name,
                    },
                    "unit_amount": int(total_amount * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=request.build_absolute_uri(reverse("payments:checkout-success"))
        + f"?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=request.build_absolute_uri(reverse("payments:payments-cancel")),
    )

    payment = Payment.objects.create(
        status=Payment.StatusChoices.PENDING,
        type=payment_type,
        session_id=checkout_session.id,
        session_url=checkout_session.url,
        borrowing_id=borrowing.id,
        money_to_pay=total_amount,
    )

    return payment
