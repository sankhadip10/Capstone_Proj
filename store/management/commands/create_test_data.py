# store/management/commands/create_test_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from store.models import Collection, Product, Customer, Order, OrderItem, Cart, CartItem
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test data for Celery task testing'

    def handle(self, *args, **options):
        self.stdout.write("Creating test data...")

        try:
            with transaction.atomic():
                # Check if we have existing orders first
                if Order.objects.exists():
                    latest_order = Order.objects.select_related('customer__user').first()
                    self.stdout.write(f"📋 Found existing order #{latest_order.id}")
                    self.stdout.write(
                        f"👤 Customer: {latest_order.customer.user.first_name} {latest_order.customer.user.last_name}")
                    self.stdout.write(f"📧 Email: {latest_order.customer.user.email}")

                    self.stdout.write("\n✅ You can test with existing data:")
                    self.stdout.write(
                        f"   python manage.py test_celery_tasks --task order_confirmation --order-id {latest_order.id}")
                    return

                # Create or get test user (avoiding conflicts)
                test_username = 'celery_test_user'
                test_email = 'celery_test@example.com'

                try:
                    user = User.objects.get(username=test_username)
                    self.stdout.write("📝 Test user already exists")
                except User.DoesNotExist:
                    # Create user WITHOUT triggering signal issues
                    user = User.objects.create_user(
                        username=test_username,
                        email=test_email,
                        password='testpass123',
                        first_name='Celery',
                        last_name='TestUser'
                    )
                    self.stdout.write("✅ Created test user")

                # Ensure customer exists (handle signal race condition)
                customer, created = Customer.objects.get_or_create(
                    user=user,
                    defaults={
                        'phone': '+1234567890',
                        'membership': Customer.MEMBERSHIP_BRONZE
                    }
                )
                if created:
                    self.stdout.write("✅ Created customer profile")

                # Create test collection
                collection, created = Collection.objects.get_or_create(
                    title='Celery Test Electronics',
                    defaults={}
                )
                if created:
                    self.stdout.write("✅ Created test collection")

                # Create test products
                products_data = [
                    {'title': 'Celery Test Laptop', 'price': 999.99, 'inventory': 5},
                    {'title': 'Celery Test Phone', 'price': 699.99, 'inventory': 15},
                    {'title': 'Celery Test Tablet', 'price': 399.99, 'inventory': 8},
                ]

                created_products = []
                for product_data in products_data:
                    product, created = Product.objects.get_or_create(
                        title=product_data['title'],
                        defaults={
                            'slug': product_data['title'].lower().replace(' ', '-'),
                            'description': f"Test description for {product_data['title']}",
                            'unit_price': Decimal(str(product_data['price'])),
                            'inventory': product_data['inventory'],
                            'collection': collection
                        }
                    )
                    created_products.append(product)

                    if created:
                        self.stdout.write(f"✅ Created product: {product.title}")

                # Create test order
                order, created = Order.objects.get_or_create(
                    customer=customer,
                    defaults={
                        'payment_status': Order.PAYMENT_STATUS_COMPLETE
                    }
                )

                if created:
                    # Add order items
                    OrderItem.objects.get_or_create(
                        order=order,
                        product=created_products[0],  # Test Laptop
                        defaults={
                            'quantity': 1,
                            'unit_price': created_products[0].unit_price
                        }
                    )

                    OrderItem.objects.get_or_create(
                        order=order,
                        product=created_products[1],  # Test Phone
                        defaults={
                            'quantity': 2,
                            'unit_price': created_products[1].unit_price
                        }
                    )

                    self.stdout.write(f"✅ Created test order #{order.id} with items")
                else:
                    self.stdout.write(f"📝 Test order #{order.id} already exists")

                # Create test cart for cart functionality testing
                cart, created = Cart.objects.get_or_create(
                    defaults={}
                )

                if created and len(created_products) > 2:
                    # Add items to cart
                    CartItem.objects.get_or_create(
                        cart=cart,
                        product=created_products[2],  # Test Tablet
                        defaults={
                            'quantity': 1
                        }
                    )
                    self.stdout.write(f"✅ Created test cart {cart.id} with items")

        except Exception as e:
            self.stdout.write(f"❌ Error creating test data: {e}")

            # Try to find existing data to use instead
            self.stdout.write("\n🔍 Looking for existing data to use...")

            if Order.objects.exists():
                order = Order.objects.select_related('customer__user').first()
                self.stdout.write(f"✅ Found existing order #{order.id}")
                self.stdout.write(f"👤 Customer: {order.customer.user.first_name} {order.customer.user.last_name}")
                self.stdout.write(f"📧 Email: {order.customer.user.email}")

                self.stdout.write("\n📧 You can test with existing data:")
                self.stdout.write(
                    f"   python manage.py test_celery_tasks --task order_confirmation --order-id {order.id}")
                return
            else:
                self.stdout.write("❌ No existing orders found. Please create an order through the API first.")
                return

        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("🎉 TEST DATA READY!"))
        self.stdout.write("=" * 50)
        self.stdout.write(f"👤 Test User: {user.username} (email: {user.email})")
        self.stdout.write(f"📦 Products: {Product.objects.count()} total")
        self.stdout.write(f"🛒 Orders: {Order.objects.count()} total")
        self.stdout.write(f"🛍️ Carts: {Cart.objects.count()} total")

        latest_order = Order.objects.last()
        if latest_order:
            self.stdout.write(f"📋 Latest Order ID: {latest_order.id}")

            self.stdout.write("\n📧 Now you can test email tasks:")
            self.stdout.write(
                f"   python manage.py test_celery_tasks --task order_confirmation --order-id {latest_order.id}")
            self.stdout.write("   python manage.py test_celery_tasks --task daily_report")
            self.stdout.write("   python manage.py test_celery_tasks --task check_inventory")
        else:
            self.stdout.write("⚠️  No orders found for email testing")