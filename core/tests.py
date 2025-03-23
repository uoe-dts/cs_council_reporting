from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class CoreTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

    def test_home_page(self):
        """Test that home page loads properly"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')

    def test_login(self):
        """Test user login functionality"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertTrue(response.url.startswith(reverse('index')))

    def test_profile_view(self):
        """Test that profile page is accessible when logged in"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')

    def test_profile_update(self):
        """Test that users can update their profile"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'updated@example.com',
            'update_profile': 'Save Changes'
        }
        response = self.client.post(reverse('profile'), data)
        self.assertEqual(response.status_code, 302)
        
        updated_user = User.objects.get(username='testuser')
        self.assertEqual(updated_user.email, 'updated@example.com')
        self.assertEqual(updated_user.first_name, 'Test')

    def test_staff_management(self):
        """Test that only superusers can access staff management"""
        # Test with regular user
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('manage_staff'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

        # Test with admin user
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('manage_staff'))
        self.assertEqual(response.status_code, 200)

    def test_registration(self):
        """Test user registration"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newuserpass123',
            'password2': 'newuserpass123'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_logout(self):
        """Test user logout functionality"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        self.assertTrue(response.url.startswith(reverse('index')))

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')

    def test_duplicate_registration(self):
        """Test registration with existing username"""
        data = {
            'username': 'testuser',  # Already exists
            'email': 'new@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with that username already exists')

    def test_profile_unauthorized_access(self):
        """Test that profile page is not accessible when not logged in"""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_password_mismatch_registration(self):
        """Test registration with mismatched passwords"""
        data = {
            'username': 'newuser2',
            'email': 'new2@example.com',
            'password1': 'pass123',
            'password2': 'differentpass123'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser2').exists())
