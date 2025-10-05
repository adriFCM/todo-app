

from django.db import models

"""
Domain model for the to-do app.

One entity: Task
- Uses a small Priority enum with human-readable labels.
- Sensible defaults so forms/views stay simple.
- SQLite (dev) or any DB backend via Django ORM.
"""

class Task(models.Model):
    class Priority(models.TextChoices):
        """
        Enum of allowed priorities.
        Stored as short codes in the DB (LOW/MED/HIGH),
        displayed as human labels (Low/Medium/High).
        """
        LOW = 'LOW', 'Low'
        MED = 'MED', 'Medium'
        HIGH = 'HIGH', 'High'

    # Short, required title. (Django adds an implicit 'id' primary key.)
    title = models.CharField(max_length=200)
    # Optional long text. 'blank=True' means form validation allows empty string.
    description = models.TextField(blank=True)
    # Optional date. 'null=True' allows NULL in DB, 'blank=True' allows empty form input.
    due_date = models.DateField(null=True, blank=True)
    # Dropdown in forms thanks to 'choices'; defaults to LOW.
    priority = models.CharField(max_length=5, choices=Priority.choices, default=Priority.LOW)
    # Tasks start not completed.
    completed = models.BooleanField(default=False)
    # Set automatically when the row is first created.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Human-friendly representation (admin, shell, logs).
        """
        return self.title

