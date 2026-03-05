from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard_alt'),
    path('sales/', views.SalesReportView.as_view(), name='sales_report'),
    path('product-sales/', views.ProductSalesReportView.as_view(), name='product_sales_report'),
    path('profit/', views.ProfitReportView.as_view(), name='profit_report'),
    path('chart-data/', views.ChartDataAPIView.as_view(), name='chart_data'),
]
