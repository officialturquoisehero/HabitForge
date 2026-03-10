from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Habit(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='habits'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='daily')
    preferred_time = models.TimeField(null=True, blank=True)
    weekly_days = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_weekly_days_list(self):
        if not self.weekly_days:
            return []
        return [int(day) for day in self.weekly_days.split(',') if day.strip().isdigit()]

    def get_weekly_days_display_list(self):
        day_names = {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: 'Saturday',
            6: 'Sunday',
        }
        return [day_names[day] for day in self.get_weekly_days_list() if day in day_names]

    def get_weekly_days_display(self):
        return ', '.join(self.get_weekly_days_display_list())

    def scheduled_on_date(self, target_date):
        if self.frequency == 'daily':
            return True
        if self.frequency == 'weekly':
            return target_date.weekday() in self.get_weekly_days_list()
        return False

    def current_streak(self):
        if self.frequency != 'daily':
            return 0

        today = timezone.localdate()
        completed_dates = set(
            self.logs.filter(completed=True).values_list('date', flat=True)
        )

        streak = 0
        check_date = today

        while check_date in completed_dates:
            streak += 1
            check_date -= timedelta(days=1)

        return streak

    def best_streak(self):
        if self.frequency != 'daily':
            return 0

        completed_dates = sorted(
            self.logs.filter(completed=True).values_list('date', flat=True)
        )

        if not completed_dates:
            return 0

        best = 1
        current = 1

        for i in range(1, len(completed_dates)):
            if completed_dates[i] == completed_dates[i - 1] + timedelta(days=1):
                current += 1
                best = max(best, current)
            elif completed_dates[i] != completed_dates[i - 1]:
                current = 1

        return best


class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField()
    completed = models.BooleanField(default=True)

    class Meta:
        unique_together = ('habit', 'date')

    def __str__(self):
        return f"{self.habit.title} - {self.date}"