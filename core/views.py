from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField, Q
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash, get_user_model
from issues.models import Issue, Comment
from .forms import UserProfileForm

User = get_user_model()

def home(request):
    # Get statistics
    total_issues = Issue.objects.count()
    resolved_issues = Issue.objects.filter(status='resolved').count()
    
    # Calculate average resolution time for resolved issues
    resolved_issues_with_time = Issue.objects.filter(status='resolved').annotate(
        resolution_time=ExpressionWrapper(
            F('updated_at') - F('created_at'),
            output_field=DurationField()
        )
    )
    avg_resolution_time = resolved_issues_with_time.aggregate(
        avg_time=Avg('resolution_time')
    )['avg_time']
    
    # Get active users (users who reported issues in the last 30 days)
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    active_users = Issue.objects.filter(
        created_at__gte=thirty_days_ago
    ).values('reporter').distinct().count()
    
    context = {
        'total_issues': total_issues,
        'resolved_issues': resolved_issues,
        'avg_resolution_time': avg_resolution_time,
        'active_users': active_users,
    }
    return render(request, 'core/index.html', context)

def contact(request):
    return render(request, 'core/contact.html')

@login_required
def profile(request):
    form = UserProfileForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            form = UserProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect('profile')
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been updated successfully.')
                return redirect('profile')
    
    return render(request, 'core/profile.html', {
        'form': form,
        'password_form': password_form
    })

@login_required
def my_issues(request):
    issues = Issue.objects.filter(reporter=request.user).order_by('-created_at')
    return render(request, 'core/my_issues.html', {'issues': issues})

def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def manage_staff(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        user_ids = request.POST.getlist('user_ids')
        
        if action == 'make_staff':
            User.objects.filter(id__in=user_ids).update(is_staff=True)
            messages.success(request, f'Successfully promoted {len(user_ids)} user(s) to staff members.')
        elif action == 'remove_staff':
            User.objects.filter(id__in=user_ids).update(is_staff=False)
            messages.success(request, f'Successfully removed staff status from {len(user_ids)} user(s).')
        
        return redirect('manage_staff')

    # Get search query
    search_query = request.GET.get('search', '')
    
    # Get filter
    filter_type = request.GET.get('filter', 'all')
    
    # Base queryset
    users = User.objects.all()
    
    # Apply search if provided
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Apply filter
    if filter_type == 'staff':
        users = users.filter(is_staff=True)
    elif filter_type == 'non_staff':
        users = users.filter(is_staff=False)
    
    # Get statistics
    total_users = User.objects.count()
    staff_count = User.objects.filter(is_staff=True).count()
    non_staff_count = User.objects.filter(is_staff=False).count()
    
    context = {
        'users': users,
        'search_query': search_query,
        'filter_type': filter_type,
        'total_users': total_users,
        'staff_count': staff_count,
        'non_staff_count': non_staff_count,
    }
    
    return render(request, 'core/manage_staff.html', context)