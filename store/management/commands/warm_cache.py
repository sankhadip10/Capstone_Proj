from django.core.management.base import BaseCommand
from django.core.cache import cache
from store.models import Product, Collection
from store.serializers import CollectionSerializer, ProductSerializer


class Command(BaseCommand):
    help = 'Warm up the cache with frequently accessed data'

    def handle(self, *args, **options):
        # Warm up collections cache
        collections = Collection.objects.annotate(products_count=Count('products')).all()
        collections_data = CollectionSerializer(collections, many=True).data
        cache.set("collections_with_counts", collections_data, 900)

        # Warm up first page of products
        products = Product.objects.prefetch_related('images').all()[:10]
        products_data = ProductSerializer(products, many=True).data
        cache.set("products_list_first_page", products_data, 300)

        self.stdout.write(
            self.style.SUCCESS('Cache warmed successfully!')
        )