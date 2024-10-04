from django.db import models


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "HARD"
        SOFT = "SOFT"

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    cover = models.CharField(max_length=4, choices=CoverChoices.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        unique_together = ("title", "author")
        ordering = ["author", "title"]
