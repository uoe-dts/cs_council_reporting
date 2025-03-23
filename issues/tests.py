from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Issue, Comment
from django.utils import timezone

User = get_user_model()

class IssueTests(TestCase):
    def setUp(self):
        # Create users
        self.staff_user = User.objects.create_user(
            username='staff_test',
            password='testpass123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='user_test',
            password='testpass123'
        )
        
        # Create a test issue
        self.issue = Issue.objects.create(
            title='Test Issue',
            description='Test Description',
            reporter=self.regular_user,
            status='open',
            category='roads',
            priority='medium'
        )
        
        # Set up client
        self.client = Client()

    def test_issue_creation(self):
        """Test that an issue can be created with valid data"""
        self.client.login(username='user_test', password='testpass123')
        
        data = {
            'title': 'New Issue',
            'description': 'New Description',
            'category': 'environment',
            'priority': 'high'
        }
        
        response = self.client.post(reverse('issues:issue_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Issue.objects.filter(title='New Issue').exists())

    def test_issue_list_view(self):
        """Test that the issue list view shows all issues"""
        self.client.login(username='user_test', password='testpass123')
        response = self.client.get(reverse('issues:issue_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Issue')

    def test_issue_detail_view(self):
        """Test that the issue detail view shows correct information"""
        self.client.login(username='user_test', password='testpass123')
        response = self.client.get(reverse('issues:issue_detail', args=[self.issue.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Issue')
        self.assertContains(response, 'Test Description')

    def test_staff_issue_update(self):
        """Test that staff can update issues"""
        self.client.login(username='staff_test', password='testpass123')
        
        data = {
            'title': 'Updated Issue',
            'description': 'Updated Description',
            'category': 'roads',
            'priority': 'high',
            'status': 'in_progress'
        }
        
        response = self.client.post(
            reverse('issues:issue_edit', args=[self.issue.pk]),
            data
        )
        self.assertEqual(response.status_code, 302)
        
        updated_issue = Issue.objects.get(pk=self.issue.pk)
        self.assertEqual(updated_issue.title, 'Updated Issue')
        self.assertEqual(updated_issue.status, 'in_progress')

    def test_comment_creation(self):
        """Test that users can comment on issues"""
        self.client.login(username='user_test', password='testpass123')
        
        data = {
            'text': 'Test Comment'
        }
        
        response = self.client.post(
            reverse('issues:add_comment', args=[self.issue.pk]),
            data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(text='Test Comment').exists())

    def test_unauthorized_access(self):
        """Test that unauthorized users cannot edit issues"""
        self.client.login(username='user_test', password='testpass123')
        
        # Try to edit someone else's issue
        other_issue = Issue.objects.create(
            title='Other Issue',
            description='Other Description',
            reporter=self.staff_user,
            status='open'
        )
        
        data = {
            'title': 'Hacked Issue',
            'description': 'Hacked Description',
            'category': 'other',
            'priority': 'low'
        }
        
        response = self.client.post(
            reverse('issues:issue_edit', args=[other_issue.pk]),
            data
        )
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_issue_status_workflow(self):
        """Test the issue status workflow"""
        self.client.login(username='staff_test', password='testpass123')
        
        # Test status transitions
        statuses = ['in_progress', 'resolved', 'closed']
        for status in statuses:
            data = {
                'title': self.issue.title,
                'description': self.issue.description,
                'category': self.issue.category,
                'priority': self.issue.priority,
                'status': status
            }
            
            response = self.client.post(
                reverse('issues:issue_edit', args=[self.issue.pk]),
                data
            )
            self.assertEqual(response.status_code, 302)
            
            updated_issue = Issue.objects.get(pk=self.issue.pk)
            self.assertEqual(updated_issue.status, status)

    def test_issue_deletion(self):
        """Test that staff can delete issues"""
        self.client.login(username='staff_test', password='testpass123')
        
        # Create a new issue to delete
        issue_to_delete = Issue.objects.create(
            title='Issue to Delete',
            description='Will be deleted',
            reporter=self.regular_user,
            status='open'
        )
        
        response = self.client.post(
            reverse('issues:issue_delete', args=[issue_to_delete.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Issue.objects.filter(pk=issue_to_delete.pk).exists())

    def test_issue_category_filter(self):
        """Test filtering issues by category"""
        self.client.login(username='user_test', password='testpass123')
        
        # Create issues in different categories
        Issue.objects.create(
            title='Road Issue',
            description='Road problem',
            reporter=self.regular_user,
            category='roads',
            status='open'
        )
        Issue.objects.create(
            title='Environment Issue',
            description='Environment problem',
            reporter=self.regular_user,
            category='environment',
            status='open'
        )
        
        response = self.client.get(reverse('issues:issue_category', args=['roads']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Road Issue')
        self.assertNotContains(response, 'Environment Issue')

    def test_empty_comment(self):
        """Test that empty comments are not allowed"""
        self.client.login(username='user_test', password='testpass123')
        
        data = {
            'text': ''
        }
        
        response = self.client.post(
            reverse('issues:add_comment', args=[self.issue.pk]),
            data
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Comment.objects.filter(text='').exists())

    def test_issue_priority_update(self):
        """Test updating issue priority"""
        self.client.login(username='staff_test', password='testpass123')
        
        data = {
            'title': self.issue.title,
            'description': self.issue.description,
            'category': self.issue.category,
            'priority': 'high',
            'status': self.issue.status
        }
        
        response = self.client.post(
            reverse('issues:issue_edit', args=[self.issue.pk]),
            data
        )
        self.assertEqual(response.status_code, 302)
        
        updated_issue = Issue.objects.get(pk=self.issue.pk)
        self.assertEqual(updated_issue.priority, 'high')

    def test_issue_creation_validation(self):
        """Test issue creation with invalid data"""
        self.client.login(username='user_test', password='testpass123')
        
        data = {
            'title': '',  # Empty title
            'description': 'Test Description',
            'category': 'roads',
            'priority': 'medium'
        }
        
        response = self.client.post(reverse('issues:issue_create'), data)
        self.assertEqual(response.status_code, 200)  # Should stay on the form page
        self.assertFormError(response, 'form', 'title', 'This field is required.')
