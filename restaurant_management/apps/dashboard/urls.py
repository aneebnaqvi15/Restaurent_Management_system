from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reports/', views.reports_page, name='reports'),
    path('reports/sales-data/', views.sales_data, name='sales-data'),
    path('logout/', views.custom_logout, name='logout'),
]
