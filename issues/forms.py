# issues/forms.py
from django import forms
from .models import Issue, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

# Form for regular users to create and update issues (only title and description)
class UserIssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'description', 'category']  # Only allow title and description for regular users

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or title.strip() == '':
            raise forms.ValidationError("Title is required")
        return title.strip()

# Form for staff users to create, update and manage issues (includes assignee, status, and category)
class StaffIssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'description', 'assignee', 'status', 'category', 'priority']  # Staff can assign and change status

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show staff users in the assignee dropdown
        self.fields['assignee'].queryset = User.objects.filter(is_staff=True)
        self.fields['assignee'].empty_label = "Select Assignee"

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or title.strip() == '':
            raise forms.ValidationError("Title is required")
        return title.strip()

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your comment here...'}),
        }
        labels = {
            'text': 'Your Comment'
        }

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if not text or text.strip() == '':
            raise forms.ValidationError("Comment cannot be empty")
        return text.strip()

