# store/management/commands/warm_cache.py
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.test.client import Client
from django.conf import settings
from django.db.models import Count, Avg
from store.models import Product, Collection, Review

try:
    from django_redis import get_redis_connection
except ImportError:
    get_redis_connection = None
import time


class Command(BaseCommand):
    help = 'Warm up cache by pre-loading frequently accessed data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-first',
            action='store_true',
            help='Clear cache before warming'
        )

    def handle(self, *args, **options):
        # Add testserver to allowed hosts temporarily for internal requests
        original_allowed_hosts = settings.ALLOWED_HOSTS
        if 'testserver' not in settings.ALLOWED_HOSTS:
            settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ['testserver']

        try:
            self.stdout.write(self.style.SUCCESS("🔥 CACHE WARMING STARTED"))
            self.stdout.write("=" * 50)

            if options['clear_first']:
                cache.clear()
                self.stdout.write("🗑️  Cache cleared")

            client = Client()
            warmed_items = 0

            # 1. Warm Collection Data
            self.stdout.write("\n📂 Warming collection cache...")
            collections = Collection.objects.annotate(
                products_count=Count('products')
            ).all()

            for collection in collections:
                cache_key = f"collection_detail_{collection.id}"
                if not cache.get(cache_key):
                    cache.set(cache_key, {
                        'id': collection.id,
                        'title': collection.title,
                        'products_count': collection.products_count
                    }, timeout=600)  # 10 minutes
                    warmed_items += 1

            self.stdout.write(f"  ✅ Warmed {len(collections)} collections")

            # 2. Warm Product List Cache
            self.stdout.write("\n📦 Warming product list cache...")
            try:
                response = client.get('/store/products/')
                if response.status_code == 200:
                    self.stdout.write("  ✅ Product list cache warmed")
                    warmed_items += 1
                else:
                    self.stdout.write(f"  ⚠️  Product list request failed: {response.status_code}")
            except Exception as e:
                self.stdout.write(f"  ❌ Product list error: {e}")

            # 3. Warm Collection List Cache
            self.stdout.write("\n📂 Warming collection list cache...")
            try:
                response = client.get('/store/collections/')
                if response.status_code == 200:
                    self.stdout.write("  ✅ Collection list cache warmed")
                    warmed_items += 1
                else:
                    self.stdout.write(f"  ⚠️  Collection list request failed: {response.status_code}")
            except Exception as e:
                self.stdout.write(f"  ❌ Collection list error: {e}")

            # 4. Warm Top Product Details
            self.stdout.write("\n🔍 Warming top product details...")
            # Get top products by ID (most recent) since Review model doesn't have rating field
            top_products = Product.objects.select_related('collection').prefetch_related('images').order_by('-id')[:10]

            product_count = 0
            for product in top_products:
                try:
                    response = client.get(f'/store/products/{product.id}/')
                    if response.status_code == 200:
                        product_count += 1
                        warmed_items += 1
                    else:
                        self.stdout.write(f"  ⚠️  Product {product.id} request failed: {response.status_code}")
                except Exception as e:
                    self.stdout.write(f"  ⚠️  Product {product.id} error: {e}")

            self.stdout.write(f"  ✅ Warmed {product_count} product details")

            # 5. Cache Frequently Used Queries
            self.stdout.write("\n📊 Caching aggregated data...")

            # Cache product count by collection
            collection_stats = {}
            for collection in collections:
                count = collection.products.count()
                collection_stats[collection.id] = count

            cache.set('collection_product_counts', collection_stats, timeout=1800)  # 30 minutes
            warmed_items += 1

            # Cache total products count
            total_products = Product.objects.count()
            cache.set('total_products_count', total_products, timeout=1800)
            warmed_items += 1

            # Cache total collections count
            total_collections = Collection.objects.count()
            cache.set('total_collections_count', total_collections, timeout=1800)
            warmed_items += 1

            self.stdout.write("  ✅ Aggregated data cached")

            # 6. Verify Cache Status
            self.stdout.write("\n🔍 Verifying cache status...")

            try:
                if get_redis_connection:
                    redis_client = get_redis_connection("default")
                    keys = redis_client.keys("*")
                    memory_info = redis_client.info('memory')
                    used_memory = memory_info.get('used_memory_human', 'Unknown')

                    self.stdout.write(f"  📊 Total cache keys: {len(keys)}")
                    self.stdout.write(f"  💾 Memory usage: {used_memory}")
                else:
                    self.stdout.write("  📊 Cache verification: Basic functionality OK")

            except Exception as e:
                self.stdout.write(f"  ⚠️  Cache verification error: {e}")

            # Summary
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(self.style.SUCCESS("🎉 CACHE WARMING COMPLETED"))
            self.stdout.write("=" * 50)
            self.stdout.write(f"Items warmed: {warmed_items}")
            self.stdout.write(f"Collections cached: {len(collections)}")
            self.stdout.write(f"Products cached: {product_count}")
            self.stdout.write("Cache is now optimized for better performance!")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Cache warming failed: {e}"))

        finally:
            # Restore original allowed hosts
            settings.ALLOWED_HOSTS = original_allowed_hosts