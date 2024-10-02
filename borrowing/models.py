from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return = models.DateField()
    actual_return = models.DateField(null=True, blank=True)
    book_id = models.IntegerField(validators=[MinValueValidator(0)])
    user_id = models.IntegerField(validators=[MinValueValidator(0)])

    def is_late(self) -> bool:
        if self.actual_return and self.actual_return > self.expected_return:
            return True
        return False

    def clean(self):
        if self.actual_return:
            if self.actual_return < self.borrow_date:
                raise ValidationError(
                    "Actual return date must be after the borrow date."
                )
        if self.expected_return < self.borrow_date:
            raise ValidationError("Expected return date must be after the borrow date.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Borrowing of {self.borrow_date} (Expected: {self.expected_return})"
