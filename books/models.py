from django.core.validators import MinValueValidator
from django.db import models


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "HARD"
        SOFT = "SOFT"

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    cover = models.CharField(max_length=4, choices=CoverChoices.choices)
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    daily_fee = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"{self.title} by {self.author}"
