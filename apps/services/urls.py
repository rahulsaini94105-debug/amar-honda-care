from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.ServiceListView.as_view(), name='service_list'),
    path('add/', views.ServiceCreateView.as_view(), name='service_create'),
    path('<int:pk>/', views.ServiceDetailView.as_view(), name='service_detail'),
    path('<int:pk>/update/', views.ServiceUpdateView.as_view(), name='service_update'),
    path('<int:pk>/checklist/', views.UpdateChecklistView.as_view(), name='update_checklist'),
    path('history/', views.VehicleHistoryView.as_view(), name='vehicle_history'),
    path('types/', views.ServiceTypeListView.as_view(), name='service_type_list'),
    path('types/add/', views.ServiceTypeCreateView.as_view(), name='service_type_create'),
]
