from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.BillingPOSView.as_view(), name='pos'),
    path('service-types/', views.GetServiceTypesView.as_view(), name='service_types'),
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:pk>/pdf/', views.InvoicePDFView.as_view(), name='invoice_pdf'),
]
