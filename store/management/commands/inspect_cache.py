from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings

try:
    from django_redis import get_redis_connection
except ImportError:
    get_redis_connection = None


class Command(BaseCommand):
    help = 'Inspect Redis cache status and configuration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🔍 CACHE INSPECTION REPORT"))
        self.stdout.write("=" * 50)

        # Check cache configuration
        cache_config = settings.CACHES['default']
        self.stdout.write(f"💾 Cache Backend: {cache_config['BACKEND']}")
        self.stdout.write(f"📍 Location: {cache_config['LOCATION']}")
        self.stdout.write(f"⏰ Default Timeout: {cache_config.get('TIMEOUT', 300)} seconds")

        # Test cache connection
        try:
            cache.set('connection_test', 'success', 10)
            test_value = cache.get('connection_test')
            if test_value == 'success':
                self.stdout.write(self.style.SUCCESS("✅ Cache Connection: WORKING"))
            else:
                self.stdout.write(self.style.ERROR("❌ Cache Connection: FAILED"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Cache Connection Error: {e}"))
            return

        # Get Redis client for detailed inspection
        try:
            if get_redis_connection:
                # Use django_redis method
                redis_client = get_redis_connection("default")
            else:
                # Fallback method
                self.stdout.write("⚠️  django_redis not available, using basic cache info")
                cache_info = {
                    'total_keys': 'Unknown',
                    'memory_usage': 'Unknown'
                }
                self.stdout.write(f"\n📊 Cache Status: Active")
                self.stdout.write("📭 Key inspection not available without django_redis")
                return

            # Get all keys
            keys = redis_client.keys("*")
            self.stdout.write(f"\n📊 Total Cache Keys: {len(keys)}")

            if keys:
                self.stdout.write("\n🔑 Cache Keys:")
                for i, key in enumerate(keys[:10]):  # Show first 10 keys
                    try:
                        key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
                        ttl = redis_client.ttl(key)
                        if ttl > 0:
                            self.stdout.write(f"  📝 {key_str} (TTL: {ttl}s)")
                        elif ttl == -1:
                            self.stdout.write(f"  📝 {key_str} (No expiry)")
                        else:
                            self.stdout.write(f"  📝 {key_str} (Expired)")
                    except Exception as e:
                        self.stdout.write(f"  ⚠️  Key {i + 1} inspection error: {e}")

                if len(keys) > 10:
                    self.stdout.write(f"  ... and {len(keys) - 10} more keys")
            else:
                self.stdout.write("  📭 No keys found in cache")

            # Memory usage and server info
            try:
                info = redis_client.info()
                memory_info = redis_client.info('memory')

                used_memory = memory_info.get('used_memory_human', 'Unknown')
                redis_version = info.get('redis_version', 'Unknown')
                connected_clients = info.get('connected_clients', 'Unknown')

                self.stdout.write(f"\n💾 Redis Memory Usage: {used_memory}")
                self.stdout.write(f"🔧 Redis Version: {redis_version}")
                self.stdout.write(f"👥 Connected Clients: {connected_clients}")

            except Exception as e:
                self.stdout.write(f"\n⚠️  Could not get Redis info: {e}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Redis detailed inspection failed: {e}"))

            # Fallback: Show basic cache functionality
            self.stdout.write("\n📝 Basic Cache Test:")
            try:
                # Test basic cache operations
                test_key = 'test_functionality'
                test_value = 'test_data_12345'

                cache.set(test_key, test_value, 30)
                retrieved = cache.get(test_key)

                if retrieved == test_value:
                    self.stdout.write("  ✅ Set/Get operations: WORKING")
                else:
                    self.stdout.write("  ❌ Set/Get operations: FAILED")

                cache.delete(test_key)
                after_delete = cache.get(test_key)

                if after_delete is None:
                    self.stdout.write("  ✅ Delete operation: WORKING")
                else:
                    self.stdout.write("  ❌ Delete operation: FAILED")

            except Exception as cache_test_error:
                self.stdout.write(f"  ❌ Basic cache test failed: {cache_test_error}")

        self.stdout.write("\n" + "=" * 50)
