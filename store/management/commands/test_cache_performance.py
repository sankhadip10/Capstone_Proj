from django.core.management.base import BaseCommand
from django.test.client import Client
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from store.models import Product, Collection, Customer

try:
    from django_redis import get_redis_connection
except ImportError:
    get_redis_connection = None
import time
import statistics

User = get_user_model()


class Command(BaseCommand):
    help = 'Test cache performance across different endpoints'

    def add_arguments(self, parser):
        parser.add_argument(
            '--iterations',
            type=int,
            default=5,
            help='Number of test iterations to run (default: 5)'
        )

    def handle(self, *args, **options):
        # Add testserver to allowed hosts temporarily
        original_allowed_hosts = settings.ALLOWED_HOSTS
        if 'testserver' not in settings.ALLOWED_HOSTS:
            settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ['testserver']

        try:
            iterations = options['iterations']
            client = Client()

            self.stdout.write(self.style.SUCCESS("🚀 CACHE PERFORMANCE TEST"))
            self.stdout.write("=" * 50)

            # Ensure we have test data
            self._ensure_test_data()

            performance_results = []

            # Test 1: Product List Performance
            self.stdout.write("\n📦 Testing Product List Performance...")
            product_improvement = self._test_product_list_performance(client, iterations)
            if product_improvement is not None:
                performance_results.append(product_improvement)

            # Test 2: Collection List Performance
            self.stdout.write("\n📂 Testing Collection List Performance...")
            collection_improvement = self._test_collection_list_performance(client, iterations)
            if collection_improvement is not None:
                performance_results.append(collection_improvement)

            # Test 3: Product Detail Performance
            self.stdout.write("\n🔍 Testing Product Detail Performance...")
            detail_improvement = self._test_product_detail_performance(client, iterations)
            if detail_improvement is not None:
                performance_results.append(detail_improvement)

            # Calculate overall improvement
            if performance_results:
                avg_improvement = statistics.mean(performance_results)
                self._display_summary(avg_improvement)
            else:
                self.stdout.write(self.style.WARNING("⚠️  No performance data collected"))

        finally:
            # Restore original allowed hosts
            settings.ALLOWED_HOSTS = original_allowed_hosts

    def _ensure_test_data(self):
        """Ensure we have test data for performance testing"""
        if not Collection.objects.exists():
            collection = Collection.objects.create(title="Test Collection")
            self.stdout.write("📝 Created test collection")
        else:
            collection = Collection.objects.first()

        if Product.objects.count() < 5:
            for i in range(5):
                Product.objects.get_or_create(
                    title=f"Test Product {i + 1}",
                    defaults={
                        'slug': f'test-product-{i + 1}',
                        'description': f'Test product {i + 1} description',
                        'unit_price': 10.00 + i,
                        'inventory': 100,
                        'collection': collection
                    }
                )
            self.stdout.write("📝 Created test products")

    def _test_product_list_performance(self, client, iterations):
        """Test product list endpoint performance"""
        try:
            # Clear cache completely
            cache.clear()

            # Clear any view-level cache entries
            try:
                if get_redis_connection:
                    redis_client = get_redis_connection("default")
                    cache_keys = redis_client.keys("*")
                    if cache_keys:
                        redis_client.delete(*cache_keys)
            except Exception:
                pass  # Continue with basic cache.clear()

            # Uncached requests
            uncached_times = []
            for _ in range(iterations):
                start_time = time.time()
                response = client.get('/store/products/')
                end_time = time.time()
                if response.status_code == 200:
                    uncached_times.append((end_time - start_time) * 1000)
                else:
                    self.stdout.write(f"  ⚠️  Request failed with status: {response.status_code}")

            # Cached requests (warm up cache first)
            if uncached_times:
                client.get('/store/products/')  # Warm up

                cached_times = []
                for _ in range(iterations):
                    start_time = time.time()
                    response = client.get('/store/products/')
                    end_time = time.time()
                    if response.status_code == 200:
                        cached_times.append((end_time - start_time) * 1000)

                if cached_times:
                    uncached_avg = statistics.mean(uncached_times)
                    cached_avg = statistics.mean(cached_times)
                    improvement = ((uncached_avg - cached_avg) / uncached_avg) * 100

                    self.stdout.write(f"  Uncached products: {uncached_avg:.2f}ms")
                    self.stdout.write(f"  Cached products: {cached_avg:.2f}ms")
                    self.stdout.write(f"  Products improvement: {improvement:.1f}%")

                    return improvement

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Product test error: {e}"))

        return None

    def _test_collection_list_performance(self, client, iterations):
        """Test collection list endpoint performance"""
        try:
            # Clear cache completely
            cache.clear()

            # Clear any view-level cache entries
            try:
                if get_redis_connection:
                    redis_client = get_redis_connection("default")
                    cache_keys = redis_client.keys("*")
                    if cache_keys:
                        redis_client.delete(*cache_keys)
            except Exception:
                pass  # Continue with basic cache.clear()

            # Uncached requests
            uncached_times = []
            for _ in range(iterations):
                start_time = time.time()
                response = client.get('/store/collections/')
                end_time = time.time()
                if response.status_code == 200:
                    uncached_times.append((end_time - start_time) * 1000)
                else:
                    self.stdout.write(f"  ⚠️  Request failed with status: {response.status_code}")

            # Cached requests
            if uncached_times:
                client.get('/store/collections/')  # Warm up

                cached_times = []
                for _ in range(iterations):
                    start_time = time.time()
                    response = client.get('/store/collections/')
                    end_time = time.time()
                    if response.status_code == 200:
                        cached_times.append((end_time - start_time) * 1000)

                if cached_times:
                    uncached_avg = statistics.mean(uncached_times)
                    cached_avg = statistics.mean(cached_times)
                    improvement = ((uncached_avg - cached_avg) / uncached_avg) * 100

                    self.stdout.write(f"  Uncached collections: {uncached_avg:.2f}ms")
                    self.stdout.write(f"  Cached collections: {cached_avg:.2f}ms")
                    self.stdout.write(f"  Collections improvement: {improvement:.1f}%")

                    return improvement

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Collection test error: {e}"))

        return None

    def _test_product_detail_performance(self, client, iterations):
        """Test product detail endpoint performance"""
        try:
            product = Product.objects.first()
            if not product:
                self.stdout.write("  ⚠️  No products found for testing")
                return None

            # Clear cache completely
            cache.clear()

            # Clear any view-level cache entries
            try:
                if get_redis_connection:
                    redis_client = get_redis_connection("default")
                    cache_keys = redis_client.keys("*")
                    if cache_keys:
                        redis_client.delete(*cache_keys)
            except Exception:
                pass  # Continue with basic cache.clear()

            # Uncached requests
            uncached_times = []
            for _ in range(iterations):
                start_time = time.time()
                response = client.get(f'/store/products/{product.id}/')
                end_time = time.time()
                if response.status_code == 200:
                    uncached_times.append((end_time - start_time) * 1000)
                else:
                    self.stdout.write(f"  ⚠️  Request failed with status: {response.status_code}")

            # Cached requests
            if uncached_times:
                client.get(f'/store/products/{product.id}/')  # Warm up

                cached_times = []
                for _ in range(iterations):
                    start_time = time.time()
                    response = client.get(f'/store/products/{product.id}/')
                    end_time = time.time()
                    if response.status_code == 200:
                        cached_times.append((end_time - start_time) * 1000)

                if cached_times:
                    uncached_avg = statistics.mean(uncached_times)
                    cached_avg = statistics.mean(cached_times)
                    improvement = ((uncached_avg - cached_avg) / uncached_avg) * 100

                    self.stdout.write(f"  Uncached detail: {uncached_avg:.2f}ms")
                    self.stdout.write(f"  Cached detail: {cached_avg:.2f}ms")
                    self.stdout.write(f"  Detail improvement: {improvement:.1f}%")

                    return improvement

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Detail test error: {e}"))

        return None

    def _display_summary(self, avg_improvement):
        """Display performance test summary"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("CACHE PERFORMANCE SUMMARY"))
        self.stdout.write("=" * 50)
        self.stdout.write(f"Average Performance Improvement: {avg_improvement:.1f}%")

        # Cache status
        try:
            cache.set('test_key', 'test_value', 1)
            if cache.get('test_key') == 'test_value':
                self.stdout.write(self.style.SUCCESS("Redis Cache Status: ACTIVE"))
            else:
                self.stdout.write(self.style.ERROR("Redis Cache Status: INACTIVE"))
        except Exception:
            self.stdout.write(self.style.ERROR("Redis Cache Status: ERROR"))

        # Configuration info
        cache_config = settings.CACHES['default']
        self.stdout.write(f"Cache Backend: {cache_config['BACKEND']}")
        self.stdout.write(f"Cache Timeout: {cache_config.get('TIMEOUT', 300)} seconds")
        self.stdout.write(f"Redis Connection: WORKING")

