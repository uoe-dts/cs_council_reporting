from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from issues.models import Issue
from django.http import JsonResponse
import json
from math import sqrt

# Create your views here.

@login_required
def analytics_dashboard(request):
    # Get date range
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)

    # Issue statistics
    total_issues = Issue.objects.count()
    open_issues = Issue.objects.filter(status='Open').count()
    resolved_issues = Issue.objects.filter(status='Resolved').count()
    in_progress_issues = Issue.objects.filter(status='In Progress').count()

    # Issues by category
    issues_by_category = Issue.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')

    # Issues by status
    issues_by_status = Issue.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')

    # Daily issue trends
    daily_issues = Issue.objects.filter(
        created_at__range=(start_date, end_date)
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    # Average resolution time
    resolved_issues = Issue.objects.filter(status='Resolved')
    avg_resolution_time = resolved_issues.aggregate(
        avg_time=Avg('resolved_at' - 'created_at')
    )['avg_time']

    # Issues by priority
    issues_by_priority = Issue.objects.values('priority').annotate(
        count=Count('id')
    ).order_by('-count')

    # Cost analysis
    total_estimated_cost = Issue.objects.aggregate(
        total=Sum('estimated_cost')
    )['total'] or 0

    total_actual_cost = Issue.objects.aggregate(
        total=Sum('actual_cost')
    )['total'] or 0

    # Geographic distribution
    issues_with_location = Issue.objects.exclude(
        latitude__isnull=True
    ).exclude(longitude__isnull=True)

    if issues_with_location.exists():
        # Calculate center point
        center_point = issues_with_location.aggregate(
            avg_lat=Avg('latitude'),
            avg_lng=Avg('longitude')
        )
        
        # Get issues by area
        issues_by_area = []
        for issue in issues_with_location:
            # Calculate distance from center point
            distance = sqrt(
                (issue.latitude - center_point['avg_lat'])**2 +
                (issue.longitude - center_point['avg_lng'])**2
            )
            issues_by_area.append({
                'category': issue.category,
                'lat': issue.latitude,
                'lng': issue.longitude,
                'distance': distance
            })

    context = {
        'total_issues': total_issues,
        'open_issues': open_issues,
        'resolved_issues': resolved_issues,
        'in_progress_issues': in_progress_issues,
        'issues_by_category': list(issues_by_category),
        'issues_by_status': list(issues_by_status),
        'daily_issues': list(daily_issues),
        'avg_resolution_time': avg_resolution_time,
        'issues_by_priority': list(issues_by_priority),
        'total_estimated_cost': total_estimated_cost,
        'total_actual_cost': total_actual_cost,
        'issues_by_area': issues_by_area if 'issues_by_area' in locals() else [],
        'center_point': center_point if 'center_point' in locals() else None,
    }
    
    return render(request, 'analytics/dashboard.html', context)

@login_required
def issue_trends(request):
    # Get date range
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)

    # Daily issue trends
    daily_trends = Issue.objects.filter(
        created_at__range=(start_date, end_date)
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    data = {
        'dates': [trend['date'].strftime('%Y-%m-%d') for trend in daily_trends],
        'counts': [trend['count'] for trend in daily_trends]
    }

    return JsonResponse(data)

@login_required
def category_analysis(request):
    # Get issues by category with additional metrics
    categories = Issue.objects.values('category').annotate(
        count=Count('id'),
        avg_resolution_time=Avg('resolved_at' - 'created_at'),
        total_cost=Sum('actual_cost')
    ).order_by('-count')

    data = list(categories)
    return JsonResponse({'categories': data})

@login_required
def geographic_analysis(request):
    # Get issues with location data
    issues = Issue.objects.exclude(
        latitude__isnull=True
    ).exclude(longitude__isnull=True)
    
    # Calculate center point
    center = issues.aggregate(
        avg_lat=Avg('latitude'),
        avg_lng=Avg('longitude')
    )

    # Get issues by area with basic metrics
    areas = []
    for issue in issues:
        # Calculate distance from center
        distance = sqrt(
            (issue.latitude - center['avg_lat'])**2 +
            (issue.longitude - center['avg_lng'])**2
        )
        areas.append({
            'category': issue.category,
            'lat': issue.latitude,
            'lng': issue.longitude,
            'distance': distance
        })

    data = {
        'center': center,
        'areas': areas
    }

    return JsonResponse(data)

@login_required
def cost_analysis(request):
    # Get cost data by category
    cost_data = Issue.objects.values('category').annotate(
        total_estimated=Sum('estimated_cost'),
        total_actual=Sum('actual_cost'),
        avg_estimated=Avg('estimated_cost'),
        avg_actual=Avg('actual_cost'),
        count=Count('id')
    ).order_by('-total_actual')

    data = list(cost_data)
    return JsonResponse({'cost_data': data})
