from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import Http404
from .models import Issue
from .forms import UserIssueForm, StaffIssueForm
from comments.forms import CommentForm

User = get_user_model()

# List issues: Staff can see all, regular users can see only their own
def issue_list(request):
    if request.user.is_authenticated:
        # Exclude closed issues for all users
        issues = Issue.objects.exclude(status='Closed')  # All users (staff or regular) see all issues except closed ones
        
        if request.user.is_staff:
            users = User.objects.filter(is_staff=True)  # Get all staff users for assignment if needed
        else:
            users = []  # Regular users won't see staff users in the form
        
        return render(request, 'issues/issue_list.html', {'issues': issues, 'users': users})
    else:
        return render(request, 'issues/issue_list.html', {'issues': None, 'users': []})


# View details of an issue
def issue_detail(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    comment_form = CommentForm()

    return render(request, 'issues/issue_detail.html', {
        'issue': issue,
        'comment_form': comment_form,
    })

# Create a new issue
@login_required
def issue_create(request):
    if request.method == 'POST':
        if request.user.is_staff:
            form = StaffIssueForm(request.POST)
        else:
            form = UserIssueForm(request.POST)
        
        if form.is_valid():
            issue = form.save(commit=False)
            issue.reporter = request.user  # Set the logged-in user as the reporter
            issue.status = 'Open'  # Default status for new issues
            issue.save()
            return redirect('issue_list')  # After creating an issue, redirect to issue list
    
    else:
        if request.user.is_staff:
            form = StaffIssueForm()
        else:
            form = UserIssueForm()

    return render(request, 'issues/issue_form.html', {'form': form})

# Edit an issue
@login_required
def issue_edit(request, pk):
    issue = get_object_or_404(Issue, pk=pk)

    # Allow only staff or the reporter to edit
    if not (request.user.is_staff or issue.reporter == request.user):
        return redirect('issue_detail', pk=issue.pk)

    if request.method == 'POST':
        if request.user.is_staff:
            form = StaffIssueForm(request.POST, instance=issue)
        else:
            form = UserIssueForm(request.POST, instance=issue)  # Regular users can only change title/description
        if form.is_valid():
            form.save()
            return redirect('issue_list')  # Redirecting to the issue list page after update
    else:
        if request.user.is_staff:
            form = StaffIssueForm(instance=issue)
        else:
            form = UserIssueForm(instance=issue)

    return render(request, 'issues/issue_edit.html', {'form': form, 'issue': issue})

# Delete an issue (only staff can delete)
@login_required
def issue_delete(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    
    if not request.user.is_staff:
        return redirect('issue_detail', pk=issue.pk)
    
    if request.method == 'POST':
        issue.delete()
        return redirect('issue_list')
    
    return render(request, 'issues/issue_confirm_delete.html', {'issue': issue})

# Filter issues by category
@login_required
def issue_category(request, category=None):
    if category:
        issues = Issue.objects.filter(category=category)
    else:
        issues = Issue.objects.all()

    categories = Issue.CATEGORY_CHOICES  # Retrieve categories from model
    return render(request, 'issues/issue_category_list.html', {'issues': issues, 'categories': categories})