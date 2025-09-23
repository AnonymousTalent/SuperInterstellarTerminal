import os
import random

def get_new_orders():
    """
    Simulates a call to an external delivery platform API to get new orders.

    In a real-world scenario, this function would use libraries like 'requests'
    to make an HTTP GET request to the platform's API endpoint.

    Returns:
        A list of dictionaries, where each dictionary represents a new order.
        Returns None if the API key is not configured.
    """
    api_key = os.getenv("DELIVERY_PLATFORM_API_KEY")

    if not api_key:
        print("❌ API Client Error: DELIVERY_PLATFORM_API_KEY is not set in .env file.")
        return None

    print(f"📞 Contacting delivery platform API with key: ...{api_key[-4:]}")

    # --- MOCK API RESPONSE ---
    # This section simulates the data that would be returned by a real API.
    mock_orders = [
        {"order_id": f"ORD-{random.randint(1000, 9999)}", "customer_address": "台中市西屯區逢甲路100號", "items": ["珍珠奶茶", "雞排"], "total_price": 150},
        {"order_id": f"ORD-{random.randint(1000, 9999)}", "customer_address": "台中市北區三民路三段129號", "items": ["牛肉麵"], "total_price": 180},
        {"order_id": f"ORD-{random.randint(1000, 9999)}", "customer_address": "台中市南屯區公益路二段51號", "items": ["披薩", "可樂"], "total_price": 600},
    ]

    # Simulate a random number of new orders
    num_new_orders = random.randint(0, len(mock_orders))

    if num_new_orders == 0:
        print("👍 No new orders at the moment.")
        return []

    print(f"✅ Found {num_new_orders} new orders.")
    return mock_orders[:num_new_orders]
