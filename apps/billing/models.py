from django.db import models
from django.utils import timezone
from decimal import Decimal


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=15, blank=True)
    vehicle_number = models.CharField(max_length=20, blank=True)
    vehicle_model = models.CharField(max_length=100, blank=True)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=[
        ('CASH', 'Cash'), ('UPI', 'UPI'), ('CARD', 'Card'), ('CREDIT', 'Credit')
    ], default='CASH')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, related_name='invoices'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"INV-{self.invoice_number} | {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            today = timezone.now()
            date_str = today.strftime('%Y%m%d')
            last = Invoice.objects.filter(invoice_number__startswith=f'AHC{date_str}').count()
            self.invoice_number = f'AHC{date_str}{str(last + 1).zfill(4)}'
        super().save(*args, **kwargs)

    def calculate_totals(self):
        items_total = sum(item.total_price for item in self.items.all())
        parts_total = sum(part.total_price for part in self.parts.all())
        self.subtotal = items_total + Decimal(str(self.service_charge)) + parts_total
        self.gst_amount = (self.subtotal * self.gst_percent) / 100
        self.grand_total = self.subtotal + self.gst_amount - self.discount
        self.save()


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, related_name='invoice_items')
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class SparePart(models.Model):
    """Predefined spare parts catalog that mechanics commonly replace."""
    name = models.CharField(max_length=150)
    default_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ServiceBillPart(models.Model):
    """A spare part (predefined or custom) attached to an invoice."""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='parts')
    spare_part = models.ForeignKey(
        SparePart, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='bill_items'
    )
    custom_name = models.CharField(max_length=150, blank=True)  # for manual/custom parts
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['id']

    def __str__(self):
        name = self.spare_part.name if self.spare_part else self.custom_name
        return f"{name} x {self.quantity} = ₹{self.total_price}"

    @property
    def part_name(self):
        return self.spare_part.name if self.spare_part else self.custom_name

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
