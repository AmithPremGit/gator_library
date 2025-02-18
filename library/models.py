from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    availability_status = models.CharField(
        max_length=5,
        choices=[('Yes', 'Available'), ('No', 'Not Available')],
        default='Yes'
    )
    parent_id = models.IntegerField(null=True, blank=True)
    left_id = models.IntegerField(null=True, blank=True)
    right_id = models.IntegerField(null=True, blank=True)
    borrowed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='borrowed_books'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['book_id']

    def __str__(self):
        return f"{self.title} (ID: {self.book_id})"

    def save(self, *args, **kwargs):
        print(f"DEBUG: Saving book {self.book_id}")
        super().save(*args, **kwargs)


class Reservation(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    patron = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='book_reservations'
    )
    priority = models.IntegerField(
        choices=[
            (1, 'Low'),
            (2, 'Medium'),
            (3, 'High')
        ],
        default=1
    )
    reservation_time = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-priority', 'reservation_time']

    def __str__(self):
        return f"{self.patron.username}'s reservation for {self.book.title}"