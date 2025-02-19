# issues/urls.py

from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.issue_list, name='issue_list'),  # Issue list page
    path('new/', views.issue_create, name='issue_create'),  # Page to create new issues
    path('<int:pk>/', views.issue_detail, name='issue_detail'),  # Issue details page
    path('<int:pk>/edit/', views.issue_edit, name='issue_edit'),  # Page to edit an issue
    path('<int:pk>/delete/', views.issue_delete, name='issue_delete'),  # Page to delete an issue
    path('category/<str:category>/', views.issue_category, name='issue_category'),  # Filter by category
    path('comments/', include('comments.urls')),  # Include the comments URLs
]