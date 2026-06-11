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
