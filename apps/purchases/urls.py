from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    path('', views.PurchaseOrderListView.as_view(), name='po_list'),
    path('create/', views.PurchaseOrderCreateView.as_view(), name='po_create'),
    path('<int:pk>/', views.PurchaseOrderDetailView.as_view(), name='po_detail'),
    path('<int:pk>/receive/', views.ReceivePurchaseOrderView.as_view(), name='po_receive'),
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_update'),
]
