from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static
from . import auth
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='index'),
    path('register/', auth.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),
    path('my-issues/', views.my_issues, name='my_issues'),
    path('manage-staff/', views.manage_staff, name='manage_staff'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)