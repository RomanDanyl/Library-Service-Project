import stripe
from django.conf import settings

from books.models import Book
from payment.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(borrowing, total_amount):
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
                    "unit_amount": int(total_amount * 100),  # Stripe працює з центами
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=settings.STRIPE_SUCCESS_URL,
        cancel_url=settings.STRIPE_CANCEL_URL,
    )

    # Створюємо платіж в базі даних
    payment = Payment.objects.create(
        status=Payment.StatusChoices.PENDING,
        type=Payment.TypeChoices.PAYMENT,
        borrowing_id=borrowing.id,
        session_url=checkout_session.url,
        session_id=checkout_session.id,
        money_to_pay=total_amount,
    )

    return payment
