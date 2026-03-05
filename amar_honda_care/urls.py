"""Amar Honda Care URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('', include('apps.reports.urls', namespace='reports')),  # dashboard at /
    path('products/', include('apps.products.urls', namespace='products')),
    path('billing/', include('apps.billing.urls', namespace='billing')),
    path('inventory/', include('apps.inventory.urls', namespace='inventory')),
    path('purchases/', include('apps.purchases.urls', namespace='purchases')),
    path('services/', include('apps.services.urls', namespace='services')),
    # REST API
    path('api/v1/', include('apps.api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
