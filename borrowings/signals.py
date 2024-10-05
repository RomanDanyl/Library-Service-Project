import asyncio

from django.db.models.signals import post_save
from django.dispatch import receiver

from books.models import Book
from utils.telegram_helpers import send_telegram_message
from borrowings.models import Borrowing


@receiver(post_save, sender=Borrowing)
def send_borrowing_notification(sender, instance, created, **kwargs):
    if created:
        book = Book.objects.get(pk=instance.book_id)
        message = (
            f"New Borrowing created:\n"
            f"Id: {instance.id}\n"
            f"Book: {instance.book_id}, {book.title}\n"
            f"User: {instance.user_id}\n"
        )
        asyncio.run(send_telegram_message(message))
