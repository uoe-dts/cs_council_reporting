from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import Http404
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .models import Issue, Notification, Resource
from .forms import UserIssueForm, StaffIssueForm, CommentForm

User = get_user_model()

# List issues: Staff can see all, regular users can see only their own
def issue_list(request):
    if request.user.is_authenticated:
        # Get all staff members for the assignee filter
        staff_members = User.objects.filter(is_staff=True)
        
        # Start with all issues
        issues = Issue.objects.all()
        
        # Apply filters
        status = request.GET.get('status')
        category = request.GET.get('category')
        priority = request.GET.get('priority')
        assignee = request.GET.get('assignee')
        date_range = request.GET.get('date_range')
        search = request.GET.get('search')
        
        if status:
            issues = issues.filter(status=status)
        if category:
            issues = issues.filter(category=category)
        if priority:
            issues = issues.filter(priority=priority)
        if assignee:
            issues = issues.filter(assignee_id=assignee)
        if search:
            issues = issues.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
            
        # Handle date range filters
        today = timezone.now().date()
        if date_range == 'today':
            issues = issues.filter(created_at__date=today)
        elif date_range == 'week':
            week_ago = today - timedelta(days=7)
            issues = issues.filter(created_at__date__gte=week_ago)
        elif date_range == 'month':
            month_ago = today - timedelta(days=30)
            issues = issues.filter(created_at__date__gte=month_ago)
        elif date_range == 'overdue':
            issues = issues.filter(
                Q(due_date__lt=today) & 
                ~Q(status__in=['resolved', 'closed'])
            )
        
        return render(request, 'issues/issue_list.html', {
            'issues': issues,
            'staff_members': staff_members,
        })
    else:
        return render(request, 'issues/issue_list.html', {
            'issues': None,
            'staff_members': [],
        })


# View details of an issue
@login_required
def issue_detail(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    comment_form = CommentForm()
    
    # Get available resources for staff members
    available_resources = None
    if request.user.is_staff:
        available_resources = Resource.objects.filter(status='available')
    
    return render(request, 'issues/issue_detail.html', {
        'issue': issue,
        'comment_form': comment_form,
        'available_resources': available_resources,
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
            issue.status = 'open'  # Default status for new issues
            issue.save()
            return redirect('issues:issue_list')  # After creating an issue, redirect to issue list
        else:
            # If form is invalid, return to the form with errors
            return render(request, 'issues/issue_form.html', {'form': form})
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
        return redirect('issues:issue_detail', pk=issue.pk)

    if request.method == 'POST':
        if request.user.is_staff:
            form = StaffIssueForm(request.POST, instance=issue)
        else:
            form = UserIssueForm(request.POST, instance=issue)  # Regular users can only change title/description
        if form.is_valid():
            form.save()
            return redirect('issues:issue_list')  # Redirecting to the issue list page after update
    else:
        if request.user.is_staff:
            form = StaffIssueForm(instance=issue)
        else:
            form = UserIssueForm(instance=issue)

    return render(request, 'issues/issue_form.html', {'form': form, 'issue': issue})

# Delete an issue (only staff can delete)
@login_required
def issue_delete(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    
    if not request.user.is_staff:
        return redirect('issues:issue_detail', pk=issue.pk)
    
    if request.method == 'POST':
        issue.delete()
        return redirect('issues:issue_list')
    
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

@login_required
def notifications(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    # Mark all notifications as read
    notifications.update(read=True)
    return render(request, 'issues/notifications.html', {'notifications': notifications})

@login_required
def add_comment(request, issue_id):
    issue = get_object_or_404(Issue, pk=issue_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.issue = issue
            comment.author = request.user
            comment.save()
            return redirect('issues:issue_detail', pk=issue_id)
        else:
            # If form is invalid, return to the detail page with the form
            return render(request, 'issues/issue_detail.html', {
                'issue': issue,
                'comment_form': form,
                'available_resources': Resource.objects.filter(status='available') if request.user.is_staff else None
            })
    return redirect('issues:issue_detail', pk=issue_id)

@login_required
def add_resource(request, issue_id):
    if not request.user.is_staff:
        return redirect('issues:issue_detail', pk=issue_id)
    
    issue = get_object_or_404(Issue, pk=issue_id)
    if request.method == 'POST':
        resource_name = request.POST.get('resource_name')
        if resource_name:
            # Create and add the resource
            resource = Resource.objects.create(
                name=resource_name,
                type='other',  # You can add a type field in the form if needed
                status='available'
            )
            issue.resources.add(resource)
            
            # Create a notification for the issue reporter
            if issue.reporter:
                Notification.objects.create(
                    issue=issue,
                    recipient=issue.reporter,
                    message=f"A new resource '{resource_name}' has been added to your issue."
                )
    
    return redirect('issues:issue_detail', pk=issue_id)

@login_required
def remove_resource(request, issue_id, resource_id):
    if not request.user.is_staff:
        return redirect('issues:issue_detail', pk=issue_id)
    
    issue = get_object_or_404(Issue, pk=issue_id)
    resource = get_object_or_404(Resource, pk=resource_id)
    
    if request.method == 'POST':
        # Remove the resource from the issue
        issue.resources.remove(resource)
        
        # Create a notification for the issue reporter
        if issue.reporter:
            Notification.objects.create(
                issue=issue,
                recipient=issue.reporter,
                message=f"The resource '{resource.name}' has been removed from your issue."
            )
        
        # Delete the resource if it's not used by any other issues
        if not resource.issues.exists():
            resource.delete()
    
    return redirect('issues:issue_detail', pk=issue_id)