import json
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.db import transaction
from apps.accounts.mixins import OwnerRequiredMixin, StaffOrOwnerRequiredMixin
from apps.products.models import Product
from .models import Supplier, PurchaseOrder, PurchaseItem
from .forms import SupplierForm, PurchaseOrderForm


class SupplierListView(OwnerRequiredMixin, ListView):
    model = Supplier
    template_name = 'purchases/supplier_list.html'
    context_object_name = 'suppliers'


class SupplierCreateView(OwnerRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'purchases/supplier_form.html'
    success_url = reverse_lazy('purchases:supplier_list')

    def form_valid(self, form):
        messages.success(self.request, 'Supplier added!')
        return super().form_valid(form)


class SupplierUpdateView(OwnerRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'purchases/supplier_form.html'
    success_url = reverse_lazy('purchases:supplier_list')


class PurchaseOrderListView(StaffOrOwnerRequiredMixin, ListView):
    model = PurchaseOrder
    template_name = 'purchases/po_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        return PurchaseOrder.objects.select_related('supplier', 'created_by').all()


class PurchaseOrderCreateView(StaffOrOwnerRequiredMixin, CreateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'purchases/po_form.html'
    success_url = reverse_lazy('purchases:po_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['products'] = Product.objects.filter(is_active=True)
        ctx['low_stock_products'] = [p for p in ctx['products'] if p.is_low_stock or p.is_out_of_stock]
        return ctx

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = PurchaseOrderForm(request.POST)
        items_data = request.POST.get('items_data', '[]')
        try:
            items = json.loads(items_data)
        except json.JSONDecodeError:
            items = []

        if not items:
            messages.error(request, 'Please add at least one item.')
            return self.form_invalid(form)

        if form.is_valid():
            po = form.save(commit=False)
            po.created_by = request.user
            po.save()
            for item in items:
                product = get_object_or_404(Product, pk=item['product_id'])
                PurchaseItem.objects.create(
                    purchase_order=po,
                    product=product,
                    quantity=int(item['quantity']),
                    unit_cost=float(item['unit_cost']),
                )
            po.calculate_total()
            messages.success(request, f'Purchase Order PO-{po.pk} created!')
            return JsonResponse({'success': True, 'po_id': po.pk})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)


class PurchaseOrderDetailView(StaffOrOwnerRequiredMixin, DetailView):
    model = PurchaseOrder
    template_name = 'purchases/po_detail.html'
    context_object_name = 'order'


class ReceivePurchaseOrderView(OwnerRequiredMixin, View):
    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        if po.status == PurchaseOrder.PENDING:
            po.status = PurchaseOrder.RECEIVED
            po.save()
            messages.success(request, f'PO-{po.pk} marked as received. Stock updated!')
        return JsonResponse({'success': True})
