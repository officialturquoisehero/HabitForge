from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "task_date",
            "start_time",
            "end_time",
            "category",
            "reward",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Task title...",
            }),
            "description": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Optional description...",
            }),
            "task_date": forms.DateInput(attrs={
                "type": "date",
            }),
            "start_time": forms.TimeInput(attrs={
                "type": "time",
            }),
            "end_time": forms.TimeInput(attrs={
                "type": "time",
            }),
            "category": forms.Select(),
            "reward": forms.TextInput(attrs={
                "placeholder": "Optional reward...",
            }),
        }