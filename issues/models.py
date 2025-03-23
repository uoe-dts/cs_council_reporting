# issues/models.py
from django.db import models
from django.conf import settings  # to reference AUTH_USER_MODEL
from django.utils import timezone
from django.urls import reverse

# Issue status choices
STATUS_CHOICES = [
    ('open', 'Open'),
    ('in_progress', 'In Progress'),
    ('resolved', 'Resolved'),
    ('closed', 'Closed'),
]

# Issue category choices
CATEGORY_CHOICES = [
    ('roads', 'Roads & Infrastructure'),
    ('environment', 'Environment'),
    ('safety', 'Community Safety'),
    ('other', 'Other'),
]

class Notification(models.Model):
    issue = models.ForeignKey('Issue', on_delete=models.CASCADE, related_name='notifications')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username} - {self.issue.title}"

class Resource(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)  # e.g., 'vehicle', 'equipment', 'personnel'
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired')
    ], default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    def get_type_display(self):
        return self.type.replace('_', ' ').title()

class Issue(models.Model):
    title = models.CharField(max_length=200)  # Title of the issue
    description = models.TextField()  # Detailed description of the issue
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='reported_issues'
    )  # User who reported the issue
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='assigned_issues'
    )  # User who is assigned to resolve the issue
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')  # Current status of the issue
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')  # Category of the issue
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='medium')
    resources = models.ManyToManyField(Resource, blank=True, related_name='issues')
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the issue was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when the issue was last updated
    resolved_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(
        upload_to='issue_images/',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    class Meta:
        ordering = ['-created_at']  # Order issues by creation date (newest first)
        indexes = [
            models.Index(fields=['status', 'category']),
            models.Index(fields=['created_at']),
        ]

    def get_absolute_url(self):
        return reverse('issue_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        # Check if this is an existing issue
        if self.pk:
            old_instance = Issue.objects.get(pk=self.pk)
            
            # Check for status change
            if old_instance.status != self.status:
                # Notify reporter of status change
                if self.reporter:
                    Notification.objects.create(
                        issue=self,
                        recipient=self.reporter,
                        message=f"Your issue '{self.title}' status has been changed to {self.get_status_display()}"
                    )
                
                # Notify assignee if status is changed to in_progress
                if self.status == 'in_progress' and self.assignee:
                    Notification.objects.create(
                        issue=self,
                        recipient=self.assignee,
                        message=f"You have been assigned to issue '{self.title}'"
                    )
            
            # Check for assignee change
            if old_instance.assignee != self.assignee:
                if self.assignee:
                    Notification.objects.create(
                        issue=self,
                        recipient=self.assignee,
                        message=f"You have been assigned to issue '{self.title}'"
                    )
                if old_instance.assignee:
                    Notification.objects.create(
                        issue=self,
                        recipient=old_instance.assignee,
                        message=f"You have been unassigned from issue '{self.title}'"
                    )

        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)

    def calculate_response_time(self):
        if self.resolved_at:
            return self.resolved_at - self.created_at
        return timezone.now() - self.created_at

    def get_status_color(self):
        status_colors = {
            'open': 'danger',
            'in_progress': 'warning',
            'resolved': 'success',
            'closed': 'secondary'
        }
        return status_colors.get(self.status, 'secondary')

    @property
    def is_overdue(self):
        if self.status in ['open', 'in_progress']:
            # Consider an issue overdue if it's been open for more than 7 days
            return (timezone.now() - self.created_at).days > 7
        return False

    def assign_to(self, user):
        self.assignee = user
        self.status = 'in_progress'
        self.save()

    def resolve(self):
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()

    def reopen(self):
        self.status = 'open'
        self.resolved_at = None
        self.save()

class Comment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.issue.title}'