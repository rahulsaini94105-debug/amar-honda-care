from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.billing.models import Invoice

User = get_user_model()

class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            role=User.OWNER
        )
        # 1. Invoice in the last 2 months (e.g. 10 days ago)
        self.inv_recent = Invoice.objects.create(
            customer_name='Recent Customer',
            grand_total=1500.00,
            created_by=self.user
        )
        self.inv_recent.created_at = timezone.now() - timedelta(days=10)
        self.inv_recent.save()
        
        # 2. Invoice older than 2 months (e.g. 70 days ago)
        self.inv_old = Invoice.objects.create(
            customer_name='Old Customer',
            grand_total=2500.00,
            created_by=self.user
        )
        self.inv_old.created_at = timezone.now() - timedelta(days=70)
        self.inv_old.save()

    def test_dashboard_context_has_invoice_groups(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('reports:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Verify the context keys exist
        self.assertIn('invoices_last_2_months', response.context)
        self.assertIn('invoices_before_2_months', response.context)
        self.assertIn('invoices_last_2_months_count', response.context)
        self.assertIn('invoices_before_2_months_count', response.context)
        
        # Verify correctness of data
        last_2_months = list(response.context['invoices_last_2_months'])
        before_2_months = list(response.context['invoices_before_2_months'])
        
        self.assertEqual(len(last_2_months), 1)
        self.assertEqual(last_2_months[0].customer_name, 'Recent Customer')
        self.assertEqual(response.context['invoices_last_2_months_count'], 1)
        
        self.assertEqual(len(before_2_months), 1)
        self.assertEqual(before_2_months[0].customer_name, 'Old Customer')
        self.assertEqual(response.context['invoices_before_2_months_count'], 1)
