from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from habits.models import Habit, HabitLog
from tasks.forms import TaskForm
from tasks.models import Task


@login_required
def home(request):
    today = date.today()
    week_ago = today - timedelta(days=6)
    month_ago = today - timedelta(days=29)

    all_habits = list(
        Habit.objects.filter(owner=request.user, is_active=True).order_by('-created_at')
    )

    habits = [habit for habit in all_habits if habit.scheduled_on_date(today)]

    for habit in habits:
        habit.streak = habit.current_streak()
        habit.best_streak_value = habit.best_streak()

    tasks_today = Task.objects.filter(
        owner=request.user,
        task_date=today
    ).order_by('start_time', 'completed', '-created_at')

    completed_habit_ids = set(
        HabitLog.objects.filter(
            habit__owner=request.user,
            date=today,
            completed=True
        ).values_list('habit_id', flat=True)
    )

    total_habits = len(habits)
    completed_habits_today = len([habit for habit in habits if habit.id in completed_habit_ids])

    total_tasks_today = tasks_today.count()
    completed_tasks_today = tasks_today.filter(completed=True).count()

    total_items_today = total_habits + total_tasks_today
    completed_items_today = completed_habits_today + completed_tasks_today
    progress_percent = int((completed_items_today / total_items_today) * 100) if total_items_today > 0 else 0

    habits_completed_week = HabitLog.objects.filter(
        habit__owner=request.user,
        completed=True,
        date__gte=week_ago,
        date__lte=today
    ).count()

    tasks_completed_week = Task.objects.filter(
        owner=request.user,
        completed=True,
        task_date__gte=week_ago,
        task_date__lte=today
    ).count()

    habits_completed_month = HabitLog.objects.filter(
        habit__owner=request.user,
        completed=True,
        date__gte=month_ago,
        date__lte=today
    ).count()

    tasks_completed_month = Task.objects.filter(
        owner=request.user,
        completed=True,
        task_date__gte=month_ago,
        task_date__lte=today
    ).count()

    habit_stats = []
    for habit in all_habits:
        completed_count = HabitLog.objects.filter(
            habit=habit,
            completed=True,
            date__gte=week_ago,
            date__lte=today
        ).count()

        habit_stats.append({
            'habit': habit,
            'completed_count': completed_count,
            'streak': habit.current_streak(),
            'best_streak': habit.best_streak(),
        })

    most_consistent_habit = max(habit_stats, key=lambda x: x['completed_count']) if habit_stats else None
    most_skipped_habit = min(habit_stats, key=lambda x: x['completed_count']) if habit_stats else None
    longest_streak_habit = max(habit_stats, key=lambda x: x['streak']) if habit_stats else None
    best_streak_habit = max(habit_stats, key=lambda x: x['best_streak']) if habit_stats else None

    if progress_percent == 100 and total_items_today > 0:
        feedback_message = "Perfect day. You completed all of today’s habits and tasks."
    elif progress_percent >= 70:
        feedback_message = "Nice work. You are handling today’s schedule really well."
    elif progress_percent >= 40:
        feedback_message = "Solid progress. You’re moving through today’s plan."
    else:
        feedback_message = "A small step still counts. Start with one habit or task and build momentum."

    chart_labels = []
    chart_habits_data = []
    chart_tasks_data = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        chart_labels.append(day.strftime('%a'))

        daily_habits = HabitLog.objects.filter(
            habit__owner=request.user,
            completed=True,
            date=day
        ).count()

        daily_tasks = Task.objects.filter(
            owner=request.user,
            completed=True,
            task_date=day
        ).count()

        chart_habits_data.append(daily_habits)
        chart_tasks_data.append(daily_tasks)

    context = {
        'today': today,
        'habits': habits,
        'tasks_today': tasks_today,
        'completed_habit_ids': completed_habit_ids,
        'total_habits': total_habits,
        'completed_habits_today': completed_habits_today,
        'total_tasks_today': total_tasks_today,
        'completed_tasks_today': completed_tasks_today,
        'progress_percent': progress_percent,
        'habits_completed_week': habits_completed_week,
        'tasks_completed_week': tasks_completed_week,
        'habits_completed_month': habits_completed_month,
        'tasks_completed_month': tasks_completed_month,
        'most_consistent_habit': most_consistent_habit,
        'most_skipped_habit': most_skipped_habit,
        'longest_streak_habit': longest_streak_habit,
        'best_streak_habit': best_streak_habit,
        'feedback_message': feedback_message,
        'task_form': TaskForm(initial={'task_date': today}),
        'chart_labels': chart_labels,
        'chart_habits_data': chart_habits_data,
        'chart_tasks_data': chart_tasks_data,
    }

    return render(request, 'dashboard/home.html', context)

@login_required
def analysis_view(request):
    today = date.today()
    week_ago = today - timedelta(days=6)
    month_ago = today - timedelta(days=29)

    habits = list(Habit.objects.filter(owner=request.user, is_active=True))
    tasks_week = Task.objects.filter(
        owner=request.user,
        task_date__gte=week_ago,
        task_date__lte=today
    )
    tasks_month = Task.objects.filter(
        owner=request.user,
        task_date__gte=month_ago,
        task_date__lte=today
    )

    for habit in habits:
        habit.streak = habit.current_streak()
        habit.best_streak_value = habit.best_streak()

    total_habit_logs_week = HabitLog.objects.filter(
        habit__owner=request.user,
        date__gte=week_ago,
        date__lte=today
    ).count()
    completed_habit_logs_week = HabitLog.objects.filter(
        habit__owner=request.user,
        completed=True,
        date__gte=week_ago,
        date__lte=today
    ).count()

    total_tasks_week = tasks_week.count()
    completed_tasks_week = tasks_week.filter(completed=True).count()

    total_habit_logs_month = HabitLog.objects.filter(
        habit__owner=request.user,
        date__gte=month_ago,
        date__lte=today
    ).count()
    completed_habit_logs_month = HabitLog.objects.filter(
        habit__owner=request.user,
        completed=True,
        date__gte=month_ago,
        date__lte=today
    ).count()

    total_tasks_month = tasks_month.count()
    completed_tasks_month = tasks_month.filter(completed=True).count()

    weekly_habit_percent = int((completed_habit_logs_week / total_habit_logs_week) * 100) if total_habit_logs_week else 0
    weekly_task_percent = int((completed_tasks_week / total_tasks_week) * 100) if total_tasks_week else 0
    monthly_habit_percent = int((completed_habit_logs_month / total_habit_logs_month) * 100) if total_habit_logs_month else 0
    monthly_task_percent = int((completed_tasks_month / total_tasks_month) * 100) if total_tasks_month else 0

    habit_stats = []
    for habit in habits:
        weekly_completed = HabitLog.objects.filter(
            habit=habit,
            completed=True,
            date__gte=week_ago,
            date__lte=today
        ).count()

        monthly_completed = HabitLog.objects.filter(
            habit=habit,
            completed=True,
            date__gte=month_ago,
            date__lte=today
        ).count()

        habit_stats.append({
            'habit': habit,
            'weekly_completed': weekly_completed,
            'monthly_completed': monthly_completed,
            'streak': habit.streak,
            'best_streak': habit.best_streak_value,
        })

    most_consistent_habit = max(habit_stats, key=lambda x: x['weekly_completed']) if habit_stats else None
    most_skipped_habit = min(habit_stats, key=lambda x: x['weekly_completed']) if habit_stats else None
    longest_streak_habit = max(habit_stats, key=lambda x: x['streak']) if habit_stats else None
    best_streak_habit = max(habit_stats, key=lambda x: x['best_streak']) if habit_stats else None

    if weekly_task_percent >= 80 and weekly_habit_percent >= 80:
        overall_feedback = "Excellent consistency. You are really locked in this week."
    elif weekly_task_percent >= 50 or weekly_habit_percent >= 50:
        overall_feedback = "Good momentum. You are building a solid routine."
    else:
        overall_feedback = "This week looks light, but that is fixable. Start small and stack wins."

    sorted_habit_stats = sorted(habit_stats, key=lambda x: x['weekly_completed'], reverse=True)[:8]
    habit_chart_labels = [item['habit'].title for item in sorted_habit_stats]
    habit_chart_values = [item['weekly_completed'] for item in sorted_habit_stats]

    today_tasks = Task.objects.filter(owner=request.user, task_date=today)
    tasks_completed_today = today_tasks.filter(completed=True).count()
    tasks_remaining_today = today_tasks.filter(completed=False).count()

    today_habits = [habit for habit in habits if habit.scheduled_on_date(today)]
    today_habit_ids = [habit.id for habit in today_habits]

    habits_completed_today = HabitLog.objects.filter(
        habit_id__in=today_habit_ids,
        date=today,
        completed=True
    ).count()

    total_habits_today = len(today_habits)
    habits_remaining_today = max(total_habits_today - habits_completed_today, 0)

    completion_chart_values = [
        tasks_completed_today,
        tasks_remaining_today,
        habits_completed_today,
        habits_remaining_today
    ]
    completion_chart_labels = [
        "Tasks Completed",
        "Tasks Remaining",
        "Habits Completed",
        "Habits Remaining"
    ]

    # 365-day heatmap
    heatmap_days = []
    month_labels = []
    start_day = today - timedelta(days=364)

    start_day = today - timedelta(days=364)

    heatmap_days = []
    month_labels = []

    for i in range(365):
        target_day = start_day + timedelta(days=i)

        # month label
        if target_day.day == 1:
            month_labels.append(target_day.strftime("%b"))
        else:
            month_labels.append("")

        daily_score = (
                HabitLog.objects.filter(
                    habit__owner=request.user,
                    date=target_day,
                    completed=True
                ).count()
                +
                Task.objects.filter(
                    owner=request.user,
                    task_date=target_day,
                    completed=True
                ).count()
        )

        if daily_score == 0:
            level = 0
        elif daily_score <= 2:
            level = 1
        elif daily_score <= 4:
            level = 2
        elif daily_score <= 6:
            level = 3
        else:
            level = 4

        heatmap_days.append({
            "date": target_day,
            "count": daily_score,
            "level": level
        })

    context = {
        'today': today,
        'weekly_habit_percent': weekly_habit_percent,
        'weekly_task_percent': weekly_task_percent,
        'monthly_habit_percent': monthly_habit_percent,
        'monthly_task_percent': monthly_task_percent,
        'completed_habit_logs_week': completed_habit_logs_week,
        'completed_tasks_week': completed_tasks_week,
        'completed_habit_logs_month': completed_habit_logs_month,
        'completed_tasks_month': completed_tasks_month,
        'most_consistent_habit': most_consistent_habit,
        'most_skipped_habit': most_skipped_habit,
        'longest_streak_habit': longest_streak_habit,
        'best_streak_habit': best_streak_habit,
        'habit_stats': habit_stats,
        'overall_feedback': overall_feedback,
        'habit_chart_labels': habit_chart_labels,
        'habit_chart_values': habit_chart_values,
        'completion_chart_values': completion_chart_values,
        'completion_chart_labels': completion_chart_labels,
        'heatmap_days': heatmap_days,
        "month_labels": month_labels,
    }

    return render(request, 'dashboard/analysis.html', context)

@login_required
def schedule_view(request):
    selected_date = request.GET.get('date')

    if selected_date:
        current_date = date.fromisoformat(selected_date)
    else:
        current_date = date.today()

    tasks = Task.objects.filter(
        owner=request.user,
        task_date=current_date
    ).order_by('start_time', 'created_at')

    habits = Habit.objects.filter(
        owner=request.user,
        is_active=True
    ).order_by('preferred_time', 'created_at')

    scheduled_habits = []
    unscheduled_habits = []

    for habit in habits:
        if habit.scheduled_on_date(current_date):
            if habit.preferred_time:
                scheduled_habits.append(habit)
            else:
                unscheduled_habits.append(habit)

    hour_slots = []
    for hour in range(6, 24):
        hour_tasks = []
        hour_habits = []

        for task in tasks:
            if task.start_time and task.start_time.hour == hour:
                hour_tasks.append(task)

        for habit in scheduled_habits:
            if habit.preferred_time and habit.preferred_time.hour == hour:
                hour_habits.append(habit)

        hour_slots.append({
            'hour': hour,
            'label': f"{hour:02d}:00",
            'tasks': hour_tasks,
            'habits': hour_habits,
        })

    unscheduled_tasks = tasks.filter(start_time__isnull=True)

    completed_habit_ids = set(
        HabitLog.objects.filter(
            habit__owner=request.user,
            date=current_date,
            completed=True
        ).values_list('habit_id', flat=True)
    )

    return render(request, 'dashboard/schedule.html', {
        'current_date': current_date,
        'hour_slots': hour_slots,
        'unscheduled_tasks': unscheduled_tasks,
        'unscheduled_habits': unscheduled_habits,
        'completed_habit_ids': completed_habit_ids,
    })