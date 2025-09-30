

from django.db import models

class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MED = 'MED', 'Medium'
        HIGH = 'HIGH', 'High'

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=5, choices=Priority.choices, default=Priority.MED)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

