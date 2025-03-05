from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),
    path('issue-trends/', views.issue_trends, name='issue_trends'),
    path('category-analysis/', views.category_analysis, name='category_analysis'),
    path('geographic-analysis/', views.geographic_analysis, name='geographic_analysis'),
    path('cost-analysis/', views.cost_analysis, name='cost_analysis'),
] 