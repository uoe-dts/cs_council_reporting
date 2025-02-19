from django.contrib import admin
from .models import Issue

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'category', 'priority', 'created_at', 'updated_at')
    list_filter = ('status', 'category', 'priority', 'created_at')
    search_fields = ('title', 'description', 'address')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'status', 'category', 'priority')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'address')
        }),
        ('Assignment', {
            'fields': ('reporter', 'assignee')
        }),
        ('Costs', {
            'fields': ('estimated_cost', 'actual_cost')
        }),
        ('Additional Information', {
            'fields': ('resolution_notes', 'is_public', 'requires_attention', 'risk_level')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at')
        }),
    )