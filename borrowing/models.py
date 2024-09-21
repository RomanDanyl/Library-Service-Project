from django.core.validators import MinValueValidator
from django.db import models


class Borrowing(models.Model):
    email = models.CharField(max_length=255)
    expected_return = models.DateField()
    actual_return = models.DateField(null=True, blank=True)
    book_id = models.IntegerField(validators=[MinValueValidator(0)])
    user_id = models.IntegerField(validators=[MinValueValidator(0)])

    def is_late(self) -> bool:
        if self.actual_return and self.actual_return > self.expected_return:
            return True
        return False
