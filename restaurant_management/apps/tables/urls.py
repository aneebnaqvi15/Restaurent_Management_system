# apps/tables/urls.py
from django.urls import path
from . import views

app_name = 'tables'

urlpatterns = [
    # API endpoints
    path('api/reservations/', views.create_reservation, name='api_create_reservation'),
    
    # Template views
    path('', views.TableListView.as_view(), name='table-list'),
    path('create/', views.TableCreateView.as_view(), name='table-create'),
    path('<int:pk>/update/', views.TableUpdateView.as_view(), name='table-update'),
    path('<int:pk>/delete/', views.TableDeleteView.as_view(), name='table-delete'),
    path('reservations/create/', views.reservation_form, name='reservation-create'),
]