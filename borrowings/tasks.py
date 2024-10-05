from celery import shared_task
from django.utils import timezone

from utils.telegram_helpers import send_telegram_message
from borrowings.models import Borrowing

import asyncio


@shared_task
def check_overdue_borrowings() -> None:
    today = timezone.now().date()
    tomorrow = today + timezone.timedelta(days=1)
    overdue_borrowings = Borrowing.objects.filter(
        expected_return__lte=tomorrow, actual_return__isnull=True
    )

    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            message = (
                f"Borrowing {borrowing.id} overdue!\n"
                f"Book: {borrowing.book_id}\n"
                f"User: {borrowing.user_id}\n"
                f"Expected return date: {borrowing.expected_return}"
            )
            asyncio.run(send_telegram_message(message))
    else:
        asyncio.run(send_telegram_message("No borrowings overdue today!"))
