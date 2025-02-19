# issues/forms.py
from django import forms
from .models import Issue
from django.contrib.auth import get_user_model

User = get_user_model()

# Form for regular users to create and update issues (only title and description)
class UserIssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'description', 'category']  # Only allow title and description for regular users

# Form for staff users to create, update and manage issues (includes assignee, status, and category)
class StaffIssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'description', 'assignee', 'status', 'category']  # Staff can assign and change status

    # Optionally, you can customize the widget for the 'assignee' field, for example, using a dropdown to select users
    assignee = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True),  # Staff users only, set dynamically in the view
        required=False,
        empty_label="Select Assignee"
    )

