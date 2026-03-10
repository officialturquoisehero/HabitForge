from django import forms
from .models import Habit


class HabitForm(forms.ModelForm):
    WEEKDAY_CHOICES = [
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ]

    weekly_days = forms.MultipleChoiceField(
        choices=WEEKDAY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Habit
        fields = ['title', 'description', 'frequency', 'preferred_time', 'weekly_days']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Habit title...',
            }),
            'description': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Optional description...',
            }),
            'frequency': forms.Select(),
            'preferred_time': forms.TimeInput(attrs={
                'type': 'time',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.weekly_days:
            self.initial['weekly_days'] = self.instance.weekly_days.split(',')

    def clean(self):
        cleaned_data = super().clean()
        frequency = cleaned_data.get('frequency')
        weekly_days = cleaned_data.get('weekly_days')

        if frequency == 'weekly' and not weekly_days:
            self.add_error('weekly_days', 'Please choose at least one day for a weekly habit.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        weekly_days = self.cleaned_data.get('weekly_days', [])

        if instance.frequency == 'weekly':
            instance.weekly_days = ','.join(weekly_days)
        else:
            instance.weekly_days = ''

        if commit:
            instance.save()

        return instance