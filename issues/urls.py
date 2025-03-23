# issues/urls.py

from . import views
from django.urls import path

app_name = 'issues'

urlpatterns = [
    path('', views.issue_list, name='issue_list'),  # Issue list page
    path('new/', views.issue_create, name='issue_create'),  # Page to create new issues
    path('<int:pk>/', views.issue_detail, name='issue_detail'),  # Issue details page
    path('<int:pk>/edit/', views.issue_edit, name='issue_edit'),  # Page to edit an issue
    path('<int:pk>/delete/', views.issue_delete, name='issue_delete'),  # Page to delete an issue
    path('category/<str:category>/', views.issue_category, name='issue_category'),  # Filter by category
    path('notifications/', views.notifications, name='notifications'),
    path('<int:issue_id>/comment/', views.add_comment, name='add_comment'),  # Add comment to an issue
    path('<int:issue_id>/add-resource/', views.add_resource, name='add_resource'),
    path('<int:issue_id>/remove-resource/<int:resource_id>/', views.remove_resource, name='remove_resource'),  # Remove resource from an issue
]