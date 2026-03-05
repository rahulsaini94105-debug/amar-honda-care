from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.InventoryDashboardView.as_view(), name='dashboard'),
    path('stock-history/', views.StockHistoryView.as_view(), name='stock_history'),
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/mark-read/', views.MarkNotificationReadView.as_view(), name='mark_all_read'),
    path('notifications/<int:pk>/read/', views.MarkNotificationReadView.as_view(), name='mark_read'),
]
