import os
import random
import requests

def get_new_orders():
    """
    Simulates a call to an external delivery platform API to get new orders.
    """
    api_key = os.getenv("DELIVERY_PLATFORM_API_KEY")
    if not api_key:
        print("❌ API Client Error: DELIVERY_PLATFORM_API_KEY is not set.")
        return None

    print(f"📞 Contacting delivery platform API with key: ...{api_key[-4:]}")

    # MOCK API RESPONSE
    mock_orders = [
        {"order_id": f"ORD-{random.randint(10000, 99999)}", "customer_address": "台中市西屯區逢甲路100號", "items": ["珍珠奶茶", "雞排"], "total_price": 150},
        {"order_id": f"ORD-{random.randint(10000, 99999)}", "customer_address": "台中市北區三民路三段129號", "items": ["牛肉麵"], "total_price": 180},
    ]

    num_new_orders = random.randint(0, len(mock_orders))
    if num_new_orders == 0:
        print("👍 No new orders at the moment.")
        return []

    print(f"✅ Found {num_new_orders} new orders.")
    return mock_orders[:num_new_orders]