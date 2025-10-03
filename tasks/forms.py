from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    # Force DD/MM/YYYY parsing & display
    due_date = forms.DateField(
        input_formats=['%d/%m/%Y'],          # parse as day/month/year
        widget=forms.DateInput(
            format='%d/%m/%Y',               # render as day/month/year
            attrs={'placeholder': 'DD/MM/YYYY'}
        ),
        error_messages={
            'invalid': "Please use DD/MM/YYYY.",
            'required': "Due date is required."
        },
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority']
