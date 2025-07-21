from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Inspect current cache contents'

    def handle(self, *args, **options):
        # Test cache connection
        try:
            cache.set('connection_test', 'success', 10)
            test_result = cache.get('connection_test')
            if test_result == 'success':
                self.stdout.write(self.style.SUCCESS('✅ Redis cache connection: WORKING'))
            else:
                self.stdout.write(self.style.ERROR('❌ Redis cache connection: FAILED'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Redis error: {e}'))
            return

        # Show cache keys (Redis-specific)
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")

            keys = redis_conn.keys("*")
            self.stdout.write(f"\n📊 Current cache keys ({len(keys)} total):")

            for key in keys[:10]:  # Show first 10 keys
                key_str = key.decode() if isinstance(key, bytes) else str(key)
                ttl = redis_conn.ttl(key)
                self.stdout.write(f"  🔑 {key_str} (TTL: {ttl}s)")

            if len(keys) > 10:
                self.stdout.write(f"  ... and {len(keys) - 10} more keys")

        except ImportError:
            self.stdout.write("⚠️  django-redis not available for key inspection")
        except Exception as e:
            self.stdout.write(f"⚠️  Could not inspect keys: {e}")

        self.stdout.write(f"\n💾 Cache Configuration:")
        self.stdout.write(f"  Backend: django_redis.cache.RedisCache")
        self.stdout.write(f"  Timeout: 10 minutes")
        self.stdout.write(f"  Location: redis://redis:6379/2")
