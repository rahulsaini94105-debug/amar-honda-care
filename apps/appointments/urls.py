from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('book/', views.CustomerBookingView.as_view(), name='book'),
    path('book/success/', views.BookingSuccessView.as_view(), name='booking_success'),
    path('calendar/', views.AdminCalendarView.as_view(), name='calendar'),
    path('analytics/', views.AppointmentAnalyticsView.as_view(), name='analytics'),
    
    # API endpoints
    path('api/availability/', views.MechanicAvailabilityAPIView.as_view(), name='api_availability'),
    path('api/events/', views.AppointmentEventListView.as_view(), name='api_events'),
    path('api/update/<int:pk>/', views.AppointmentUpdateAPIView.as_view(), name='api_update'),
    path('api/action/<int:pk>/', views.AppointmentActionView.as_view(), name='api_action'),
]
