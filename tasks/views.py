from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import Task
from .forms import TaskForm


def task_list(request):
    q = (request.GET.get("q") or "").strip()
    sort = request.GET.get("sort") or "created_at"
    status = request.GET.get("status") or "all"       # all|open|done
    priority = request.GET.get("priority") or "all"   # all|LOW|MED|HIGH

    tasks = Task.objects.all()

    if q:
        tasks = tasks.filter(Q(title__icontains=q) | Q(description__icontains=q))

    if status == "open":
        tasks = tasks.filter(completed=False)
    elif status == "done":
        tasks = tasks.filter(completed=True)

    if priority in Task.Priority.values:
        tasks = tasks.filter(priority=priority)

    # Whitelist sort fields (preserve optional leading "-")
    allowed_fields = {"created_at", "due_date", "priority", "completed", "title"}
    raw = sort
    sign = "-" if sort.startswith("-") else ""
    field = sort.lstrip("-")
    if field not in allowed_fields:
        sign, field = "", "created_at"

    tasks = tasks.order_by(f"{sign}{field}")

    return render(
        request,
        "tasks/task_list.html",
        {
            "tasks": tasks,
            "q": q,
            "sort": f"{sign}{field}",
            "status": status,
            "priority": priority,
        },
    )


def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("task_list")
    else:
        form = TaskForm()
    return render(request, "tasks/task_form.html", {"form": form, "mode": "Create"})


def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("task_list")
    else:
        form = TaskForm(instance=task)
    return render(request, "tasks/task_form.html", {"form": form, "mode": "Update"})


def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        task.delete()
        return redirect("task_list")
    return render(request, "tasks/task_confirm_delete.html", {"task": task})



def task_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        task.completed = not task.completed
        task.save()
    return redirect("task_list")
