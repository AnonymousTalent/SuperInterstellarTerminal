import os
import time
import random
import json
import requests
from datetime import datetime

# This module contains the logic for the continuous dispatch simulation.
# It's designed to be run as a background task by the main server.

# Note: In a real production app, you might use a more robust task queue
# like Celery, but for this simulation, a background thread is sufficient.

# These functions are copied from the old continuous_dispatcher.py and will be used here.

AI_NAMES = [
    "FlashArmyBot", "LightningEmpire2025Bot", "LightningEmpireBot", "LightningEmperorBot",
    "PhantomSparksTetrisBot", "LightningTetrisBot", "CommanderTetrisBot", "ThunderTetrisBot"
]
REPORT_FILE = "dispatch_report.json"
ETIQUETTE_FILE = "etiquette.json"

def send_telegram(message: str):
    """Sends a message via Telegram."""
    TELEGRAM_BOT_TOKEN = os.getenv("COMMAND_BOT_TOKEN") # Use command bot for simulation status
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram tokens not set. Skipping notification.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})
        print(f"✅ Telegram notification sent.")
    except Exception as e:
        print(f"❌ Failed to send Telegram notification: {e}")

def log_dispatch(entry: dict):
    """Logs a dispatch event to a JSON file."""
    try:
        with open(REPORT_FILE, "r") as f:
            report = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        report = []
    report.append(entry)
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)

def update_etiquette(ai_name: str, score: int):
    """Updates a local JSON file and simulates updating cloud sheets."""
    try:
        with open(ETIQUETTE_FILE, "r") as f:
            etiquette = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        etiquette = {name: 0 for name in AI_NAMES}
    etiquette[ai_name] = etiquette.get(ai_name, 0) + score
    with open(ETIQUETTE_FILE, "w") as f:
        json.dump(etiquette, f, indent=2)
    print(f"☁️ Simulating update to Google Sheets/M365 for {ai_name}: new score {etiquette[ai_name]}")

def dispatch_order(order_data: dict, platform: str, ai_name: str):
    """Simulates dispatching an order to a platform via a specific AI."""
    print(f"-> Dispatching Order {order_data['id']} to {platform} via AI {ai_name}...")
    status = "成功" if random.random() > 0.1 else "失敗"
    update_etiquette(ai_name, score=1)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "platform": platform,
        "order": order_data,
        "ai_name": ai_name,
        "status": status
    }
    log_dispatch(entry)
    message = f"[派單模擬]\nAI: {ai_name}\n平台: {platform}\n訂單: {order_data['id']}\n狀態: {status}"
    send_telegram(message)

def generate_random_order():
    """Generates a random sample order."""
    order_id = f"SIM-ORD-{random.randint(10000, 99999)}"
    amount = round(random.uniform(100.0, 2000.0), 2)
    return {"id": order_id, "item": "Simulated Item", "amount": amount}

def start_dispatch_simulation():
    """Main loop for continuous, simulated dispatching. To be run in a background thread."""
    print("🚀 Background dispatch simulation service starting...")
    send_telegram("🚀 **背景派單模擬服務已啟動**")

    while True:
        try:
            order = generate_random_order()
            ai_agent = random.choice(AI_NAMES)
            platform = random.choice(["Uber", "Foodpanda"])

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Simulating new order: {order['id']}")
            dispatch_order(order, platform, ai_agent)

            sleep_interval = random.randint(30, 90) # Longer interval for background task
            time.sleep(sleep_interval)

        except Exception as e:
            print(f"❌ Error in background simulation task: {e}")
            error_message = f"🚨 **背景模擬服務發生錯誤**\n\n`{e}`\n\n服務將在 60 秒後重試。"
            send_telegram(error_message)
            time.sleep(60)
