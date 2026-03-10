import json
from datetime import date, time

from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TaskForm
from .models import Task


@login_required
def task_list(request):
    selected_date = request.GET.get('date')

    if selected_date:
        tasks = Task.objects.filter(owner=request.user, task_date=selected_date).order_by('start_time', 'completed', '-created_at')
        current_date = selected_date
    else:
        current_date = date.today()
        tasks = Task.objects.filter(owner=request.user, task_date=current_date).order_by('start_time', 'completed', '-created_at')

    form = TaskForm(initial={'task_date': current_date})

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'form': form,
        'today': current_date,
    })


@login_required
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.save()
            messages.success(request, f'Task "{task.title}" added.')
    return redirect(request.META.get('HTTP_REFERER', 'task_list'))


@login_required
def complete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, owner=request.user)
        if not task.completed:
            task.completed = True
            task.save()

            if task.reward:
                messages.success(
                    request,
                    f'Great job! "{task.title}" completed. Reward unlocked: {task.reward}'
                )
            else:
                messages.success(request, f'Great job! "{task.title}" completed.')
        else:
            messages.info(request, f'"{task.title}" was already completed.')

    return redirect(request.META.get('HTTP_REFERER', 'task_list'))


@login_required
def delete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, owner=request.user)
        task_title = task.title
        task.delete()
        messages.info(request, f'Task "{task_title}" deleted.')
    return redirect(request.META.get('HTTP_REFERER', 'task_list'))

@login_required
def edit_task(request, task_id):

    task = get_object_or_404(Task, id=task_id, owner=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)

        if form.is_valid():
            form.save()
            return redirect("schedule")

    else:
        form = TaskForm(instance=task)

    return render(request, "tasks/edit_task.html", {"form": form})

@login_required
def move_task(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        task_id = int(data["task_id"])
        hour = int(data["hour"])
    except (KeyError, ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"status": "error", "message": "Invalid payload"}, status=400)

    task = get_object_or_404(Task, id=task_id, owner=request.user)
    task.start_time = time(hour, 0)

    if task.end_time and task.end_time <= task.start_time:
        task.end_time = None

    task.save()

    return JsonResponse({"status": "ok"})