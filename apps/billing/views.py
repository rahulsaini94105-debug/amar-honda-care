import json
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.contrib import messages
from django.db import transaction
from apps.accounts.mixins import StaffOrOwnerRequiredMixin
from apps.products.models import Product
from .models import Invoice, InvoiceItem
from .forms import InvoiceForm
from .utils import generate_invoice_pdf


class BillingPOSView(StaffOrOwnerRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'billing/pos.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['products'] = Product.objects.filter(is_active=True, stock_qty__gt=0).select_related('category')
        ctx['categories'] = Product.objects.filter(is_active=True).values_list('category__name', 'category__id').distinct()
        return ctx

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = InvoiceForm(request.POST)
        cart_data = request.POST.get('cart_data', '[]')
        try:
            cart = json.loads(cart_data)
        except json.JSONDecodeError:
            cart = []

        # Allow service-only invoices (empty cart is fine if service_charge > 0)
        service_charge = float(request.POST.get('service_charge') or 0)
        if not cart and service_charge <= 0:
            return JsonResponse(
                {'success': False, 'errors': {'__all__': ['Please add at least one product or enter a service charge.']}},
                status=400
            )

        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()

            for item in cart:
                product = get_object_or_404(Product, pk=item['product_id'])
                InvoiceItem.objects.create(
                    invoice=invoice,
                    product=product,
                    quantity=int(item['quantity']),
                    unit_price=product.selling_price,
                )
            invoice.calculate_totals()
            messages.success(request, f'Invoice #{invoice.invoice_number} created successfully!')
            return JsonResponse({'success': True, 'invoice_id': invoice.pk, 'invoice_number': invoice.invoice_number})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)


class InvoiceListView(StaffOrOwnerRequiredMixin, ListView):
    model = Invoice
    template_name = 'billing/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20

    def get_queryset(self):
        qs = Invoice.objects.select_related('created_by').all()
        q = self.request.GET.get('q')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if q:
            qs = qs.filter(invoice_number__icontains=q) | qs.filter(customer_name__icontains=q) | qs.filter(vehicle_number__icontains=q)
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        return qs


class InvoiceDetailView(StaffOrOwnerRequiredMixin, DetailView):
    model = Invoice
    template_name = 'billing/invoice_detail.html'
    context_object_name = 'invoice'


class InvoicePDFView(LoginRequiredMixin, View):
    def get(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        pdf = generate_invoice_pdf(invoice)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="Invoice_{invoice.invoice_number}.pdf"'
            return response
        return HttpResponse('Error generating PDF', status=500)
