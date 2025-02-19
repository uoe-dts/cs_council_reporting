# issues/models.py
from django.db import models
from django.conf import settings  # to reference AUTH_USER_MODEL
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.urls import reverse

# Issue status choices
STATUS_CHOICES = [
    ('Open', 'Open'),
    ('In Progress', 'In Progress'),
    ('Pending Review', 'Pending Review'),
    ('Resolved', 'Resolved'),
    ('Closed', 'Closed'),
]

# Issue category choices
CATEGORY_CHOICES = [
    ('Pothole', 'Pothole'),
    ('Lighting', 'Lighting'),
    ('Fly-tipping', 'Fly-tipping'),
    ('Blocked Drain', 'Blocked Drain'),
    ('Graffiti', 'Graffiti'),
    ('Anti-Social Behaviour', 'Anti-Social Behaviour'),
    ('Other', 'Other')
]

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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')  # Current status of the issue
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='Other')  # Category of the issue
    priority = models.CharField(
        max_length=10,
        choices=[
            ('Low', 'Low'),
            ('Medium', 'Medium'),
            ('High', 'High'),
            ('Urgent', 'Urgent'),
        ],
        default='Medium'
    )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the issue was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when the issue was last updated
    resolved_at = models.DateTimeField(null=True, blank=True)
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    resolution_notes = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    requires_attention = models.BooleanField(default=False)
    related_issues = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='related_to'
    )
    tags = models.CharField(max_length=200, blank=True)
    image = models.ImageField(
        upload_to='issue_images/',
        null=True,
        blank=True
    )
    risk_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Risk level from 1 to 5"
    )

    def __str__(self):
        return f"{self.title} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']  # Order issues by creation date (newest first)
        indexes = [
            models.Index(fields=['status', 'category']),
            models.Index(fields=['created_at']),
            models.Index(fields=['priority']),
        ]

    def get_absolute_url(self):
        return reverse('issue_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        if self.status == 'Resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)

    def calculate_response_time(self):
        if self.resolved_at:
            return self.resolved_at - self.created_at
        return timezone.now() - self.created_at

    def get_status_color(self):
        status_colors = {
            'Open': 'danger',
            'In Progress': 'warning',
            'Pending Review': 'info',
            'Resolved': 'success',
            'Closed': 'secondary'
        }
        return status_colors.get(self.status, 'secondary')

    def get_priority_color(self):
        priority_colors = {
            'Low': 'success',
            'Medium': 'info',
            'High': 'warning',
            'Urgent': 'danger'
        }
        return priority_colors.get(self.priority, 'secondary')

    @property
    def is_overdue(self):
        if self.status in ['Open', 'In Progress']:
            # Consider an issue overdue if it's been open for more than 7 days
            return (timezone.now() - self.created_at).days > 7
        return False

    def assign_to(self, user):
        self.assignee = user
        self.status = 'In Progress'
        self.save()

    def resolve(self, notes=None):
        self.status = 'Resolved'
        self.resolved_at = timezone.now()
        if notes:
            self.resolution_notes = notes
        self.save()

    def reopen(self):
        self.status = 'Open'
        self.resolved_at = None
        self.save()