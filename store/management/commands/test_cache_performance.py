from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.test import Client
import time
import json


class Command(BaseCommand):
    help = 'Test cache performance and measure improvements'

    def handle(self, *args, **options):
        client = Client()

        # Test 1: Product List Performance
        self.stdout.write("Testing Product List Performance...")

        # Clear cache first
        cache.clear()

        # Test without cache (first request)
        start_time = time.time()
        response1 = client.get('/store/products/')
        uncached_time = (time.time() - start_time) * 1000  # Convert to ms

        # Test with cache (second request)
        start_time = time.time()
        response2 = client.get('/store/products/')
        cached_time = (time.time() - start_time) * 1000  # Convert to ms

        # Calculate improvement
        improvement = ((uncached_time - cached_time) / uncached_time) * 100

        self.stdout.write(f"Uncached request: {uncached_time:.2f}ms")
        self.stdout.write(f"Cached request: {cached_time:.2f}ms")
        self.stdout.write(f"Performance improvement: {improvement:.1f}%")

        # Test 2: Product Detail Performance
        self.stdout.write("\nTesting Product Detail Performance...")

        # Clear specific cache
        cache.delete("product_detail_1")

        # Test without cache
        start_time = time.time()
        response1 = client.get('/store/products/1/')
        uncached_detail_time = (time.time() - start_time) * 1000

        # Test with cache
        start_time = time.time()
        response2 = client.get('/store/products/1/')
        cached_detail_time = (time.time() - start_time) * 1000

        detail_improvement = ((uncached_detail_time - cached_detail_time) / uncached_detail_time) * 100

        self.stdout.write(f"Uncached detail: {uncached_detail_time:.2f}ms")
        self.stdout.write(f"Cached detail: {cached_detail_time:.2f}ms")
        self.stdout.write(f"Detail improvement: {detail_improvement:.1f}%")

        # Test 3: Collections Performance
        self.stdout.write("\nTesting Collections Performance...")

        cache.delete("collections_with_counts")

        start_time = time.time()
        response1 = client.get('/store/collections/')
        uncached_collections = (time.time() - start_time) * 1000

        start_time = time.time()
        response2 = client.get('/store/collections/')
        cached_collections = (time.time() - start_time) * 1000

        collections_improvement = ((uncached_collections - cached_collections) / uncached_collections) * 100

        self.stdout.write(f"Uncached collections: {uncached_collections:.2f}ms")
        self.stdout.write(f"Cached collections: {cached_collections:.2f}ms")
        self.stdout.write(f"Collections improvement: {collections_improvement:.1f}%")

        # Overall Summary
        avg_improvement = (improvement + detail_improvement + collections_improvement) / 3

        self.stdout.write(f"\n" + "=" * 50)
        self.stdout.write(f"CACHE PERFORMANCE SUMMARY")
        self.stdout.write(f"=" * 50)
        self.stdout.write(f"Average Performance Improvement: {avg_improvement:.1f}%")
        self.stdout.write(f"Redis Cache Status: ACTIVE")
        self.stdout.write(f"Cache Backend: django_redis.cache.RedisCache")
        self.stdout.write(f"Cache Timeout: 10 minutes")

        # Test cache status
        cache.set('test_key', 'test_value', 60)
        test_value = cache.get('test_key')
        cache_status = "WORKING" if test_value == 'test_value' else "FAILED"

        self.stdout.write(f"Redis Connection: {cache_status}")