from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.products.models import Product
from apps.inventory.models import StockLog
from apps.billing.models import Invoice, InvoiceItem

User = get_user_model()

class InvoiceDeleteViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username='owneruser',
            password='testpassword',
            role=User.OWNER
        )
        self.staff = User.objects.create_user(
            username='staffuser',
            password='testpassword',
            role=User.STAFF
        )
        self.mechanic = User.objects.create_user(
            username='mechuser',
            password='testpassword',
            role=User.MECHANIC
        )
        self.product = Product.objects.create(
            name='Test Product',
            selling_price=100.00,
            purchase_price=80.00,
            stock_qty=10,
            low_stock_limit=2
        )
        # Create an invoice
        self.invoice = Invoice.objects.create(
            customer_name='John Doe',
            customer_phone='1234567890',
            service_charge=50.00,
            created_by=self.owner
        )
        # Create invoice item (simulating sale which reduced stock initially)
        # Note: we need to manually adjust stock in setup to match the initial sale reduction
        # since signals might or might not have run depending on how we created it.
        # Let's see: signals.py listens to post_save of InvoiceItem.
        # If we save InvoiceItem, it reduces stock of Product.
        self.item = InvoiceItem.objects.create(
            invoice=self.invoice,
            product=self.product,
            quantity=3,
            unit_price=100.00
        )
        # Reload product to ensure we get the reduced stock if signals ran
        self.product.refresh_from_db()

    def test_anonymous_user_cannot_delete(self):
        response = self.client.post(reverse('billing:invoice_delete', kwargs={'pk': self.invoice.pk}))
        # Redirects to login
        self.assertRedirects(response, f"/accounts/login/?next=/billing/invoices/{self.invoice.pk}/delete/")
        # Invoice still exists
        self.assertTrue(Invoice.objects.filter(pk=self.invoice.pk).exists())

    def test_mechanic_user_cannot_delete(self):
        self.client.login(username='mechuser', password='testpassword')
        response = self.client.post(reverse('billing:invoice_delete', kwargs={'pk': self.invoice.pk}))
        # Permission Denied (403)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Invoice.objects.filter(pk=self.invoice.pk).exists())

    def test_owner_user_can_delete_and_restores_stock(self):
        self.client.login(username='owneruser', password='testpassword')
        
        initial_stock = self.product.stock_qty
        item_qty = self.item.quantity
        
        response = self.client.post(reverse('billing:invoice_delete', kwargs={'pk': self.invoice.pk}))
        
        # Should redirect to invoice list
        self.assertRedirects(response, reverse('billing:invoice_list'))
        
        # Invoice is deleted
        self.assertFalse(Invoice.objects.filter(pk=self.invoice.pk).exists())
        
        # Product stock is restored
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_qty, initial_stock + item_qty)
        
        # StockLog of type RETURN is created
        stock_log = StockLog.objects.filter(product=self.product, change_type=StockLog.RETURN).first()
        self.assertIsNotNone(stock_log)
        self.assertEqual(stock_log.quantity_change, item_qty)
        self.assertIn(f"Delete Invoice #{self.invoice.invoice_number}", stock_log.note)


class InvoicePDFViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username='owneruser',
            password='testpassword',
            role=User.OWNER
        )
        self.mechanic = User.objects.create_user(
            username='mechuser',
            password='testpassword',
            role=User.MECHANIC
        )
        self.invoice = Invoice.objects.create(
            customer_name='Jane Doe',
            customer_phone='0987654321',
            service_charge=150.00,
            created_by=self.owner
        )

    def test_anonymous_user_cannot_view_pdf(self):
        response = self.client.get(reverse('billing:invoice_pdf', kwargs={'pk': self.invoice.pk}))
        # Redirects to login
        self.assertRedirects(response, f"/accounts/login/?next=/billing/invoices/{self.invoice.pk}/pdf/")

    def test_logged_in_user_can_view_pdf(self):
        self.client.login(username='mechuser', password='testpassword')
        response = self.client.get(reverse('billing:invoice_pdf', kwargs={'pk': self.invoice.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn(f'inline; filename="Invoice_{self.invoice.invoice_number}.pdf"', response['Content-Disposition'])
        
        # Check that it's a valid PDF (PDF files start with %PDF)
        pdf_content = response.content
        self.assertTrue(pdf_content.startswith(b'%PDF'))

