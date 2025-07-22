from django.core.management.base import BaseCommand
from store.tasks import (
    send_order_confirmation_email,
    generate_daily_sales_report,
    cleanup_abandoned_carts,
    check_inventory_levels
)
from store.models import Order


class Command(BaseCommand):
    help = 'Test Celery tasks manually'

    def add_arguments(self, parser):
        parser.add_argument('--task', type=str, help='Specific task to test')
        parser.add_argument('--order-id', type=int, help='Order ID for testing')

    def handle(self, *args, **options):
        task = options.get('task')

        if task == 'order_confirmation':
            order_id = options.get('order_id')
            if not order_id:
                # Get the latest order
                latest_order = Order.objects.first()
                if latest_order:
                    order_id = latest_order.id
                else:
                    self.stdout.write("No orders found")
                    return

            self.stdout.write(f"Testing order confirmation email for order {order_id}")
            result = send_order_confirmation_email.delay(order_id)
            self.stdout.write(f"Task ID: {result.id}")

        elif task == 'daily_report':
            self.stdout.write("Testing daily sales report")
            result = generate_daily_sales_report.delay()
            self.stdout.write(f"Task ID: {result.id}")

        elif task == 'cleanup_carts':
            self.stdout.write("Testing cart cleanup")
            result = cleanup_abandoned_carts.delay()
            self.stdout.write(f"Task ID: {result.id}")

        elif task == 'check_inventory':
            self.stdout.write("Testing inventory check")
            result = check_inventory_levels.delay()
            self.stdout.write(f"Task ID: {result.id}")

        else:
            self.stdout.write("Available tasks:")
            self.stdout.write("  --task order_confirmation [--order-id X]")
            self.stdout.write("  --task daily_report")
            self.stdout.write("  --task cleanup_carts")
            self.stdout.write("  --task check_inventory")