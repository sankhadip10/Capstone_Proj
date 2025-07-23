# locustfiles/enhanced_browse_products.py
from locust import HttpUser, task, between
from random import randint, choice
import json


class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        """Setup that runs when user starts"""
        # Create a cart for this user session
        response = self.client.post('/store/carts/')
        if response.status_code == 201:
            result = response.json()
            self.cart_id = result['id']
        else:
            self.cart_id = None

    @task(10)  # High weight - most common action
    def view_products(self):
        """Browse products by collection"""
        collection_id = randint(1, 6)
        self.client.get(
            f'/store/products/?collection_id={collection_id}',
            name='/store/products/?collection_id=[id]'
        )

    @task(8)  # Second most common
    def view_product_detail(self):
        """View individual product details"""
        product_id = randint(1, 100)  # Adjust range based on your data
        self.client.get(
            f'/store/products/{product_id}/',
            name='/store/products/[id]/'
        )

    @task(6)
    def search_products(self):
        """Search for products"""
        search_terms = ['laptop', 'phone', 'computer', 'tablet', 'camera']
        search_term = choice(search_terms)
        self.client.get(
            f'/store/products/?search={search_term}',
            name='/store/products/?search=[term]'
        )

    @task(4)
    def view_collections(self):
        """Browse all collections"""
        self.client.get('/store/collections/')

    @task(3)
    def add_to_cart(self):
        """Add items to cart"""
        if self.cart_id:
            product_id = randint(1, 50)
            quantity = randint(1, 3)

            response = self.client.post(
                f'/store/carts/{self.cart_id}/items/',
                json={
                    'product_id': product_id,
                    'quantity': quantity
                },
                name='/store/carts/[id]/items/'
            )

    @task(2)
    def view_cart(self):
        """Check cart contents"""
        if self.cart_id:
            self.client.get(
                f'/store/carts/{self.cart_id}/',
                name='/store/carts/[id]/'
            )

    @task(1)
    def update_cart_item(self):
        """Update cart item quantity"""
        if self.cart_id:
            # First get cart items
            response = self.client.get(f'/store/carts/{self.cart_id}/')
            if response.status_code == 200:
                cart_data = response.json()
                if cart_data.get('items'):
                    item = choice(cart_data['items'])
                    new_quantity = randint(1, 5)

                    self.client.patch(
                        f'/store/carts/{self.cart_id}/items/{item["id"]}/',
                        json={'quantity': new_quantity},
                        name='/store/carts/[id]/items/[id]/'
                    )


class AuthenticatedUser(HttpUser):
    """User that logs in and performs authenticated actions"""
    wait_time = between(2, 8)

    def on_start(self):
        """Login and setup"""
        # Try to register a user (might fail if exists, that's OK)
        user_data = {
            'username': f'loadtest_user_{randint(1000, 9999)}',
            'email': f'loadtest_{randint(1000, 9999)}@example.com',
            'password': 'loadtest123',
            'first_name': 'Load',
            'last_name': 'Test'
        }

        register_response = self.client.post('/auth/users/', json=user_data)

        # Login
        login_response = self.client.post('/auth/jwt/create/', json={
            'username': user_data['username'],
            'password': user_data['password']
        })

        if login_response.status_code == 200:
            token = login_response.json()['access']
            self.client.headers.update({'Authorization': f'JWT {token}'})
            self.authenticated = True

            # Create cart
            cart_response = self.client.post('/store/carts/')
            if cart_response.status_code == 201:
                self.cart_id = cart_response.json()['id']
        else:
            self.authenticated = False
            self.cart_id = None

    @task(5)
    def browse_as_authenticated_user(self):
        """Browse products as logged-in user"""
        if self.authenticated:
            product_id = randint(1, 50)
            self.client.get(f'/store/products/{product_id}/')

    @task(3)
    def add_items_and_create_order(self):
        """Add items to cart and create order"""
        if self.authenticated and self.cart_id:
            # Add some items
            for _ in range(randint(1, 3)):
                product_id = randint(1, 20)
                self.client.post(
                    f'/store/carts/{self.cart_id}/items/',
                    json={
                        'product_id': product_id,
                        'quantity': randint(1, 2)
                    }
                )

            # Create order
            order_response = self.client.post(
                '/store/orders/',
                json={'cart_id': self.cart_id},
                name='/store/orders/'
            )

            if order_response.status_code in [200, 201]:
                # Create new cart for next order
                cart_response = self.client.post('/store/carts/')
                if cart_response.status_code == 201:
                    self.cart_id = cart_response.json()['id']

    @task(2)
    def view_my_orders(self):
        """Check order history"""
        if self.authenticated:
            self.client.get('/store/orders/')

    @task(1)
    def view_customer_profile(self):
        """Check customer profile"""
        if self.authenticated:
            self.client.get('/store/customers/me/')


# Additional specialized user for API stress testing
class APIStressUser(HttpUser):
    """High-frequency API testing"""
    wait_time = between(0.1, 1)  # Very fast requests

    @task(20)
    def rapid_product_requests(self):
        """Rapid product listing requests"""
        page = randint(1, 5)
        self.client.get(f'/store/products/?page={page}')

    @task(10)
    def rapid_collection_requests(self):
        """Rapid collection requests"""
        self.client.get('/store/collections/')

    @task(5)
    def rapid_cart_creation(self):
        """Rapid cart creation/deletion"""
        response = self.client.post('/store/carts/')
        if response.status_code == 201:
            cart_id = response.json()['id']
            # Immediately delete it
            self.client.delete(f'/store/carts/{cart_id}/')


# Performance testing for caching
class CacheTestUser(HttpUser):
    """Test caching performance"""
    wait_time = between(0.5, 2)

    @task(15)
    def test_product_caching(self):
        """Repeatedly request same products to test caching"""
        # Request popular products repeatedly
        popular_products = [1, 2, 3, 4, 5]
        product_id = choice(popular_products)
        self.client.get(f'/store/products/{product_id}/')

    @task(10)
    def test_collection_caching(self):
        """Test collection list caching"""
        self.client.get('/store/collections/')

    @task(5)
    def test_filtered_products(self):
        """Test filtered product caching"""
        collection_id = choice([1, 2, 3])
        self.client.get(f'/store/products/?collection_id={collection_id}')

# # Basic load test (your current file)
# locust -f locustfiles/browse_products.py --host=http://localhost:8000
#
# # Enhanced testing with multiple user types
# locust -f locustfiles/enhanced_browse_products.py --host=http://localhost:8000
#
# # Specific user type testing
# locust -f locustfiles/enhanced_browse_products.py WebsiteUser --host=http://localhost:8000
# locust -f locustfiles/enhanced_browse_products.py AuthenticatedUser --host=http://localhost:8000


# Testing different Scenarios
# Test caching performance
# locust -f locustfiles/enhanced_browse_products.py CacheTestUser --host=http://localhost:8000
#
# # Stress test APIs
# locust -f locustfiles/enhanced_browse_products.py APIStressUser --host=http://localhost:8000
#
# # Mixed load (simulates real users)
# locust -f locustfiles/enhanced_browse_products.py --host=http://localhost:8000


# Recommended test scenarions
# Light load
# locust -f locustfiles/browse_products.py --host=http://localhost:8000 -u 10 -r 2 -t 60s
#
# # Medium load
# locust -f locustfiles/browse_products.py --host=http://localhost:8000 -u 50 -r 5 -t 300s
#
# # Heavy load (be careful!)
# locust -f locustfiles/browse_products.py --host=http://localhost:8000 -u 100 -r 10 -t 600s
