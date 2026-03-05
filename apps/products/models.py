from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    barcode = models.CharField(max_length=100, blank=True, unique=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_qty = models.IntegerField(default=0)
    low_stock_limit = models.IntegerField(default=5)
    unit = models.CharField(max_length=20, default='Pcs')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def profit_margin(self):
        if self.purchase_price:
            return self.selling_price - self.purchase_price
        return 0

    @property
    def is_low_stock(self):
        return 0 < self.stock_qty <= self.low_stock_limit

    @property
    def is_out_of_stock(self):
        return self.stock_qty <= 0
