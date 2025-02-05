from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from issues.models import Issue
from comments.models import Comment

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