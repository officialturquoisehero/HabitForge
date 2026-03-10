from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import HabitForm
from .models import Habit, HabitLog


@login_required
def habit_list(request):
    habits = list(Habit.objects.filter(owner=request.user, is_active=True).order_by('-created_at'))
    today = date.today()

    completed_habit_ids = set(
        HabitLog.objects.filter(
            habit__owner=request.user,
            date=today,
            completed=True
        ).values_list('habit_id', flat=True)
    )

    for habit in habits:
        habit.streak = habit.current_streak()
        habit.best_streak_value = habit.best_streak()

    return render(request, 'habits/habit_list.html', {
        'habits': habits,
        'completed_habit_ids': completed_habit_ids,
    })


@login_required
def add_habit(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.owner = request.user
            habit.save()
            messages.success(request, f'Habit "{habit.title}" added.')
            return redirect('habit_list')
    else:
        form = HabitForm()

    return render(request, 'habits/add_habit.html', {'form': form})


@login_required
def edit_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, owner=request.user)

    if request.method == 'POST':
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            messages.success(request, f'Habit "{habit.title}" updated.')
            return redirect('habit_list')
    else:
        form = HabitForm(instance=habit)

    return render(request, 'habits/edit_habit.html', {
        'form': form,
        'habit': habit,
    })


@login_required
def delete_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, owner=request.user)

    if request.method == 'POST':
        habit_title = habit.title
        habit.delete()
        messages.info(request, f'Habit "{habit_title}" deleted.')
        return redirect('habit_list')

    return render(request, 'habits/delete_habit.html', {'habit': habit})


@login_required
def complete_habit(request, habit_id):
    if request.method == 'POST':
        habit = get_object_or_404(Habit, id=habit_id, owner=request.user)
        today = date.today()

        log, created = HabitLog.objects.get_or_create(
            habit=habit,
            date=today,
            defaults={'completed': True}
        )

        if created:
            messages.success(request, f'Nice! "{habit.title}" completed for today.')
        else:
            messages.info(request, f'"{habit.title}" was already completed today.')

    return redirect(request.META.get('HTTP_REFERER', 'habit_list'))