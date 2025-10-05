from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .forms import TaskForm


def task_list(request):
    """
    Render the task list with search, filters, and safe sorting.
    - Reads query params from the URL (?q=&status=&priority=&sort=)
    - Applies filters to the queryset
    - Uses a whitelist for sorting to avoid invalid/unsafe fields
    """
    # Read query parameters with sensible defaults
    q = (request.GET.get("q") or "").strip()
    sort = request.GET.get("sort") or "created_at"
    status = request.GET.get("status") or "all"       # all|open|done
    priority = request.GET.get("priority") or "all"   # all|LOW|MED|HIGH
     # Start with all tasks
    tasks = Task.objects.all()
    # Text search across title and description (case-insensitive)
    if q:
        tasks = tasks.filter(Q(title__icontains=q) | Q(description__icontains=q))
    # Status filter maps to the 'completed' boolean
    if status == "open":
        tasks = tasks.filter(completed=False)
    elif status == "done":
        tasks = tasks.filter(completed=True)

    # Priority filter must be a valid enum value (LOW/MED/HIGH)
    if priority in Task.Priority.values:
        tasks = tasks.filter(priority=priority)

    # ---- Safe sorting (whitelist) ----
    # Only allow these fields to be used in order_by to prevent errors/abuse
    allowed_fields = {"created_at", "due_date", "priority", "completed", "title"}
    raw = sort

    # Preserve optional leading "-" for descending order
    sign = "-" if sort.startswith("-") else ""
    field = sort.lstrip("-")
    # Fallback to a safe default if an invalid sort field is provided
    if field not in allowed_fields:
        sign, field = "", "created_at"

    # Apply ordering
    tasks = tasks.order_by(f"{sign}{field}")

    # Render the template, passing current filter/sort values so the UI stays in sync
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
    """
    Create a new task.
    - GET: show empty TaskForm
    - POST: validate + save then redirect to list (PRG pattern)
    TaskForm enforces: due_date optional, but if provided must be DD/MM/YYYY.
    """
    if request.method == "POST":
        form = TaskForm(request.POST) #bind POST data for validation
        if form.is_valid():
            form.save()  #persist to DB via the model
            return redirect("task_list") #Post-Redirect-Get
    else:
        form = TaskForm()
    return render(request, "tasks/task_form.html", {"form": form, "mode": "Create"})


def task_update(request, pk):
    """
    Update an existing task.
    - 404 if pk does not exist
    - Reuses TaskForm for consistent validation and rendering
    """
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task) # bind to existing instance
        if form.is_valid():
            form.save()
            return redirect("task_list")
    else:
        form = TaskForm(instance=task) # prefill form GET
    return render(request, "tasks/task_form.html", {"form": form, "mode": "Update"})


def task_delete(request, pk):
    """
    Delete a task with a confirmation step.
    - GET: show confirm page
    - POST: perform deletion and redirect (PRG)
    """
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        task.delete()
        return redirect("task_list")
    return render(request, "tasks/task_confirm_delete.html", {"task": task})



def task_toggle(request, pk):
    """
    Toggle the 'completed' flag.
    IMPORTANT: Only mutate on POST. GET should never change state.
    Always redirect back to the list (PRG) after handling.
    """
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        task.completed = not task.completed
        task.save()
    return redirect("task_list")
