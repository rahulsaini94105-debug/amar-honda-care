from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from apps.accounts.mixins import OwnerRequiredMixin, StaffOrOwnerRequiredMixin
from .models import Product, Category
from .forms import ProductForm, CategoryForm


class ProductListView(StaffOrOwnerRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 24

    def get_queryset(self):
        qs = Product.objects.select_related('category').filter(is_active=True)
        q = self.request.GET.get('q')
        category = self.request.GET.get('category')
        stock_filter = self.request.GET.get('stock')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(barcode__icontains=q))
        if category:
            qs = qs.filter(category_id=category)
        if stock_filter == 'low':
            qs = [p for p in qs if p.is_low_stock]
        elif stock_filter == 'out':
            qs = [p for p in qs if p.is_out_of_stock]
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        selected_cat = self.request.GET.get('category', '')
        selected_stock = self.request.GET.get('stock', '')
        # Pre-compute flags so template uses plain booleans, no == string comparisons
        ctx['categories'] = [
            {'id': cat.id, 'name': cat.name, 'is_selected': str(cat.id) == selected_cat}
            for cat in Category.objects.all()
        ]
        ctx['stock_low_selected'] = selected_stock == 'low'
        ctx['stock_out_selected'] = selected_stock == 'out'
        ctx['low_stock_count'] = sum(1 for p in Product.objects.filter(is_active=True) if p.is_low_stock)
        ctx['out_of_stock_count'] = sum(1 for p in Product.objects.filter(is_active=True) if p.is_out_of_stock)
        return ctx


class ProductCreateView(OwnerRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:product_list')

    def form_valid(self, form):
        messages.success(self.request, f'Product "{form.instance.name}" added successfully!')
        return super().form_valid(form)


class ProductUpdateView(OwnerRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:product_list')

    def form_valid(self, form):
        messages.success(self.request, f'Product "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


class ProductDetailView(StaffOrOwnerRequiredMixin, DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'


class ProductDeleteView(OwnerRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')

    def form_valid(self, form):
        messages.success(self.request, 'Product deleted successfully!')
        return super().form_valid(form)


# Category Views
class CategoryListView(OwnerRequiredMixin, ListView):
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'


class CategoryCreateView(OwnerRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('products:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Category created!')
        return super().form_valid(form)


class CategoryUpdateView(OwnerRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('products:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Category updated!')
        return super().form_valid(form)
