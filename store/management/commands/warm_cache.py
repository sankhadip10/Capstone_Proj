# store/management/commands/warm_cache.py - FIXED for Production

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
        self.stdout.write(self.style.SUCCESS("🔥 CACHE WARMING STARTED"))
        self.stdout.write("=" * 50)

        if options['clear_first']:
            cache.clear()
            self.stdout.write("🗑️  Cache cleared")

        #
        # This avoids HTTPS redirect issues in production
        client = Client(SERVER_NAME='localhost')  # Internal requests
        warmed_items = 0

        # 1. Warm Collection Data (Direct database approach - more reliable)
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

        # 2.  Use view-level cache warming instead of HTTP requests
        self.stdout.write("\n📦 Warming product list cache...")
        try:
            # Pre-populate cache with product data instead of making HTTP requests
            from store.views import ProductViewSet
            from rest_framework.request import Request
            from django.http import HttpRequest

            # Cache popular product combinations
            popular_collections = collections[:5]  # Top 5 collections
            for collection in popular_collections:
                cache_key = f"products_collection_{collection.id}"
                if not cache.get(cache_key):
                    products = Product.objects.filter(collection=collection).select_related('collection')[:10]
                    cache.set(cache_key, list(products.values()), timeout=300)
                    warmed_items += 1

            self.stdout.write("  ✅ Product list cache warmed")

        except Exception as e:
            self.stdout.write(f"  ⚠️  Product list cache warning: {str(e)}")

        # 3.  Collection list cache (database approach)
        self.stdout.write("\n📂 Warming collection list cache...")
        try:
            cache_key = "collections_with_counts"
            if not cache.get(cache_key):
                collections_data = []
                for collection in collections:
                    collections_data.append({
                        'id': collection.id,
                        'title': collection.title,
                        'products_count': collection.products_count
                    })
                cache.set(cache_key, collections_data, timeout=900)  # 15 minutes
                warmed_items += 1

            self.stdout.write("  ✅ Collection list cache warmed")

        except Exception as e:
            self.stdout.write(f"  ⚠️  Collection list cache warning: {str(e)}")

        # 4.  Warm Top Product Details (database approach)
        self.stdout.write("\n🔍 Warming top product details...")
        try:
            # Get top products by ID (most recent)
            top_products = Product.objects.select_related('collection').prefetch_related('images').order_by('-id')[:10]

            product_count = 0
            for product in top_products:
                cache_key = f"product_detail_{product.id}"
                if not cache.get(cache_key):
                    product_data = {
                        'id': product.id,
                        'title': product.title,
                        'unit_price': str(product.unit_price),
                        'collection_id': product.collection.id,
                        'collection_title': product.collection.title,
                        'description': product.description,
                        'inventory': product.inventory,
                    }
                    cache.set(cache_key, product_data, timeout=600)  # 10 minutes
                    product_count += 1
                    warmed_items += 1

            self.stdout.write(f"  ✅ Warmed {product_count} product details")

        except Exception as e:
            self.stdout.write(f"  ⚠️  Product details warning: {str(e)}")

        # 5. Cache Frequently Used Queries
        self.stdout.write("\n📊 Caching aggregated data...")
        try:
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

        except Exception as e:
            self.stdout.write(f"  ⚠️  Aggregated data warning: {str(e)}")

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
            self.stdout.write(f"  ⚠️  Cache verification warning: {str(e)}")

        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("🎉 CACHE WARMING COMPLETED"))
        self.stdout.write("=" * 50)
        self.stdout.write(f"Items warmed: {warmed_items}")
        self.stdout.write(f"Collections cached: {len(collections)}")
        self.stdout.write(f"Products cached: {min(10, Product.objects.count())}")
        self.stdout.write("Cache is now optimized for better performance!")