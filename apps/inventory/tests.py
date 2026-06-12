from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.products.models import Product
from apps.inventory.models import Notification

User = get_user_model()

class NotificationClickViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            role=User.STAFF
        )
        self.product = Product.objects.create(
            name='Test Bike Brake Cable',
            selling_price=150.00,
            purchase_price=100.00,
            stock_qty=4,
            low_stock_limit=5
        )
        self.notification = Notification.objects.create(
            message='🔔 LOW STOCK: Test Bike Brake Cable has only 4 unit(s) left.',
            notification_type=Notification.LOW_STOCK,
            related_product=self.product,
            is_read=False
        )

    def test_anonymous_redirect(self):
        # When not logged in, clicking the notification should redirect to login
        response = self.client.get(reverse('inventory:notification_click', kwargs={'pk': self.notification.pk}))
        self.assertRedirects(response, f"/accounts/login/?next=/inventory/notifications/{self.notification.pk}/click/")

    def test_click_notification_marks_read_and_redirects(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')
        
        # Click the notification
        response = self.client.get(reverse('inventory:notification_click', kwargs={'pk': self.notification.pk}))
        
        # Verify redirect to the product list page with correct q parameter
        expected_url = reverse('products:product_list') + '?q=Test%20Bike%20Brake%20Cable'
        self.assertRedirects(response, expected_url)
        
        # Verify notification is marked as read
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_click_notification_without_product(self):
        # Create a notification with no related product
        notification_no_prod = Notification.objects.create(
            message='General Notification',
            notification_type=Notification.GENERAL,
            is_read=False
        )
        
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('inventory:notification_click', kwargs={'pk': notification_no_prod.pk}))
        
        # Verify redirect to notification list page
        self.assertRedirects(response, reverse('inventory:notifications'))
        
        # Verify notification is marked as read
        notification_no_prod.refresh_from_db()
        self.assertTrue(notification_no_prod.is_read)


class ProductNotificationSignalTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name='Test Bike Helmet',
            selling_price=1000.00,
            purchase_price=800.00,
            stock_qty=10,
            low_stock_limit=5
        )

    def test_stock_drops_to_low_stock_creates_notification(self):
        # Drop stock to 4 (low stock)
        self.product.stock_qty = 4
        self.product.save()

        # Verify LOW_STOCK notification is created
        notifications = Notification.objects.filter(related_product=self.product, notification_type=Notification.LOW_STOCK, is_read=False)
        self.assertEqual(notifications.count(), 1)
        self.assertIn("has only 4 unit(s) left", notifications.first().message)

    def test_stock_drops_to_out_of_stock_creates_notification_and_resolves_low_stock(self):
        # First drop to low stock to create low stock notification
        self.product.stock_qty = 4
        self.product.save()

        low_stock_notif = Notification.objects.get(related_product=self.product, notification_type=Notification.LOW_STOCK)
        self.assertFalse(low_stock_notif.is_read)

        # Now drop to out of stock
        self.product.stock_qty = 0
        self.product.save()

        # Low stock notification should be marked as read
        low_stock_notif.refresh_from_db()
        self.assertTrue(low_stock_notif.is_read)

        # Out of stock notification should be created
        out_of_stock_notif = Notification.objects.get(related_product=self.product, notification_type=Notification.OUT_OF_STOCK, is_read=False)
        self.assertIn("has 0 units left", out_of_stock_notif.message)

    def test_stock_increases_to_low_stock_resolves_out_of_stock(self):
        # Start at out of stock
        self.product.stock_qty = 0
        self.product.save()

        out_of_stock_notif = Notification.objects.get(related_product=self.product, notification_type=Notification.OUT_OF_STOCK)
        self.assertFalse(out_of_stock_notif.is_read)

        # Increase to low stock (e.g. 3)
        self.product.stock_qty = 3
        self.product.save()

        # Out of stock should be read
        out_of_stock_notif.refresh_from_db()
        self.assertTrue(out_of_stock_notif.is_read)

        # Low stock should be created
        low_stock_notif = Notification.objects.get(related_product=self.product, notification_type=Notification.LOW_STOCK, is_read=False)
        self.assertIn("has only 3 unit(s) left", low_stock_notif.message)

    def test_stock_updates_within_low_stock_updates_message(self):
        # Start at low stock 3
        self.product.stock_qty = 3
        self.product.save()

        low_stock_notif = Notification.objects.get(related_product=self.product, notification_type=Notification.LOW_STOCK, is_read=False)
        self.assertIn("has only 3 unit(s) left", low_stock_notif.message)

        # Update to low stock 4
        self.product.stock_qty = 4
        self.product.save()

        # Message should be updated
        low_stock_notif.refresh_from_db()
        self.assertIn("has only 4 unit(s) left", low_stock_notif.message)
        self.assertFalse(low_stock_notif.is_read)

    def test_stock_increased_above_limit_resolves_all_notifications(self):
        # Start at out of stock
        self.product.stock_qty = 0
        self.product.save()

        out_of_stock_notif = Notification.objects.get(related_product=self.product, notification_type=Notification.OUT_OF_STOCK)

        # Change to low stock
        self.product.stock_qty = 3
        self.product.save()

        low_stock_notif = Notification.objects.get(related_product=self.product, notification_type=Notification.LOW_STOCK, is_read=False)

        # Increase above low stock
        self.product.stock_qty = 8
        self.product.save()

        # Both should be marked as read
        out_of_stock_notif.refresh_from_db()
        low_stock_notif.refresh_from_db()
        self.assertTrue(out_of_stock_notif.is_read)
        self.assertTrue(low_stock_notif.is_read)
