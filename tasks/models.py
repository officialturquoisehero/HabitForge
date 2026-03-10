from django.conf import settings
from django.db import models


class Task(models.Model):
    CATEGORY_CHOICES = [
        ("study", "Study"),
        ("personal", "Personal"),
        ("health", "Health"),
        ("university", "University"),
        ("business", "Business"),
        ("sports", "Sports"),
        ("entertainment", "Entertainment"),
        ("other", "Other"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="other",
    )
    reward = models.CharField(max_length=200, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title