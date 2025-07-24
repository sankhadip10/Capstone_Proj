# Create test_production_payment.py
import requests
import json

BASE_URL = "https://capstone-prod-ea68d8515465.herokuapp.com"


def test_complete_flow():
    print("🧪 Testing Production Payment Flow...")

    # Step 1: Test basic connectivity
    print("\n1. Testing basic connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/store/collections/")
        print(f"✅ Collections API: {response.status_code}")
        print(f"   Found {len(response.json())} collections")
    except Exception as e:
        print(f"❌ Connectivity failed: {e}")
        return

    # Step 2: Create test user
    print("\n2. Creating test user...")
    user_data = {
        "username": "payment_test_user",
        "email": "payment_test@example.com",
        "password": "testpass123456",
        "first_name": "Payment",
        "last_name": "Tester"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/users/", json=user_data)
        if response.status_code in [200, 201]:
            print("✅ User created successfully")
        else:
            print(f"⚠️  User creation: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"❌ User creation failed: {e}")

    # Step 3: Login
    print("\n3. Testing login...")
    login_data = {
        "username": "payment_test_user",
        "password": "testpass123456"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/jwt/create/", json=login_data)
        if response.status_code == 200:
            token = response.json()['access']
            print(f"✅ Login successful, token: {token[:20]}...")

            # Step 4: Test authenticated endpoint
            print("\n4. Testing authenticated endpoint...")
            headers = {"Authorization": f"JWT {token}"}
            response = requests.get(f"{BASE_URL}/store/orders/", headers=headers)
            print(f"✅ Orders endpoint: {response.status_code}")

            # Step 5: Test payment intent (if order exists)
            print("\n5. Testing payment intent...")
            payment_data = {"order_id": 1}  # Assuming order ID 1 exists
            response = requests.post(
                f"{BASE_URL}/payments/create-payment-intent/",
                json=payment_data,
                headers=headers
            )
            print(f"💳 Payment intent: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ Payment intent created: {response.json()}")
            else:
                print(f"⚠️  Payment response: {response.text[:200]}")

        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Login error: {e}")


if __name__ == "__main__":
    test_complete_flow()