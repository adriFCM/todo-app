from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    due_date = forms.DateField(
        required=False,                    
        input_formats=['%d/%m/%Y'],         
        widget=forms.DateInput(
            format='%d/%m/%Y',
            attrs={
                'placeholder': 'DD/MM/YYYY',
                'inputmode': 'numeric',     
                'autocomplete': 'off'
            }
        ),
        error_messages={
            'invalid': "Invalid date format. Please use DD/MM/YYYY",
        },
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority']
