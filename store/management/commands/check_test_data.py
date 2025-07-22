# store/management/commands/check_test_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Count
from store.models import Collection, Product, Customer, Order, OrderItem, Cart, CartItem

User = get_user_model()


class Command(BaseCommand):
    help = 'Check existing data for Celery testing'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Checking existing data for testing...")

        # Check users
        user_count = User.objects.count()
        self.stdout.write(f"👥 Users: {user_count}")

        # Check customers
        customer_count = Customer.objects.count()
        self.stdout.write(f"👤 Customers: {customer_count}")

        # Check products
        product_count = Product.objects.count()
        self.stdout.write(f"📦 Products: {product_count}")

        # Check orders
        order_count = Order.objects.count()
        self.stdout.write(f"🛒 Orders: {order_count}")

        if order_count > 0:
            # Show recent orders
            recent_orders = Order.objects.select_related('customer__user').prefetch_related('items__product')[:3]

            self.stdout.write("\n📋 Recent Orders:")
            for order in recent_orders:
                try:
                    customer_name = f"{order.customer.user.first_name} {order.customer.user.last_name}"
                    items_count = order.items.count()
                    self.stdout.write(
                        f"  Order #{order.id} - {customer_name} - {items_count} items - {order.payment_status}")
                except Exception as e:
                    self.stdout.write(f"  Order #{order.id} - Error reading details: {e}")

            # Get the latest order for testing
            latest_order = Order.objects.select_related('customer__user').last()

            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(self.style.SUCCESS("✅ READY FOR TESTING!"))
            self.stdout.write("=" * 50)

            try:
                customer_name = f"{latest_order.customer.user.first_name} {latest_order.customer.user.last_name}"
                self.stdout.write(f"📋 Latest Order: #{latest_order.id}")
                self.stdout.write(f"👤 Customer: {customer_name}")
                self.stdout.write(f"📧 Email: {latest_order.customer.user.email}")
                self.stdout.write(f"💳 Status: {latest_order.get_payment_status_display()}")

                self.stdout.write("\n🧪 Test Commands:")
                self.stdout.write(
                    f"   python manage.py test_celery_tasks --task order_confirmation --order-id {latest_order.id}")
                self.stdout.write("   python manage.py test_celery_tasks --task daily_report")
                self.stdout.write("   python manage.py test_celery_tasks --task check_inventory")
                self.stdout.write("   python manage.py test_celery_tasks --task cleanup_carts")

            except Exception as e:
                self.stdout.write(f"❌ Error reading order details: {e}")
                self.stdout.write(
                    f"🧪 Try with order ID: python manage.py test_celery_tasks --task order_confirmation --order-id {latest_order.id}")

        else:
            self.stdout.write("\n❌ No orders found!")
            self.stdout.write("💡 You need to create an order first:")
            self.stdout.write("   1. Go to your API: http://localhost:8000/store/")
            self.stdout.write("   2. Create a cart, add items, and place an order")
            self.stdout.write("   3. Or use your existing admin panel")

        # Check carts
        cart_count = Cart.objects.count()
        self.stdout.write(f"\n🛍️  Carts: {cart_count}")

        if cart_count > 0:
            carts_with_items = Cart.objects.prefetch_related('items').annotate(item_count=Count('items')).filter(
                item_count__gt=0)[:3]
            if carts_with_items.exists():
                self.stdout.write("🛍️  Carts with items:")
                for cart in carts_with_items:
                    self.stdout.write(f"  Cart {cart.id} - {cart.item_count} items")