from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    """
    ModelForm for creating/updating Task objects.

    Why a ModelForm?
    - Centralizes validation and widgets (UX) for this form.
    - Keeps business rules close to the model (required/choices).
    - Makes `due_date` optional, but strictly DD/MM/YYYY when provided.
    """
    # Optional long text field; render as a multi-line <textarea>.
    description = forms.CharField(
        required=False, # user can leave this blank
        widget=forms.Textarea(attrs={
            "rows": 6, # initial visible height of the textarea
            "placeholder": "Optional notes about the task…" # helpful hint
        })
    )
    # Optional date; if provided must parse as DD/MM/YYYY.
    due_date = forms.DateField(
        required=False, # allow empty (matches model null/blank)
        input_formats=['%d/%m/%Y'],  # enforce day/month/year parsing
        widget=forms.DateInput(
            format='%d/%m/%Y', # render back to user in the same format
            attrs={'placeholder': 'DD/MM/YYYY', 'inputmode': 'numeric', 'autocomplete': 'off'}
        ),
        error_messages={'invalid': "Invalid date format. Please use DD/MM/YYYY"},  # friendly validation message
    )

    class Meta:
        model = Task
        # Only expose editable fields in the form.
        # (title required by model; priority renders as a <select> from TextChoices)
        fields = ['title', 'description', 'due_date', 'priority']
