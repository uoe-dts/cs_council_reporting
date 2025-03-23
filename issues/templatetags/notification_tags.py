from django import template
from issues.models import Notification

register = template.Library()

@register.filter
def unread_count(user):
    if not user.is_authenticated:
        return 0
    return Notification.objects.filter(recipient=user, read=False).count() 