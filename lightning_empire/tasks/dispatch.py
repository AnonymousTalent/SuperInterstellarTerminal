import os
import telegram
from services import api_client

def run_dispatch():
    """
    Fetches new orders from the delivery platform API and processes them.
    Returns a dictionary with the status and a message.
    """
    print("😼⚡️ AI 派單系統啟動中...")
    command_bot_token = os.getenv("COMMAND_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    new_orders = api_client.get_new_orders()

    if new_orders is None:
        dispatch_message = "❌ **派單失敗**\n\n無法連接到外送平台 API。請檢查您的 API 金鑰設定。"
        result = {"status": "error", "message": "API key not configured."}
    elif not new_orders:
        dispatch_message = "👍 **目前無新訂單**\n\n系統將持續監控。"
        result = {"status": "no_orders", "message": dispatch_message}
    else:
        print(f"以下是從平台獲取的新訂單： {new_orders}")
        dispatch_message = f"✅ **收到 {len(new_orders)} 筆新訂單**\n\n已從平台成功拉取訂單，準備進行 AI 派單。"
        result = {"status": "completed", "orders_received": len(new_orders), "message": dispatch_message}

    bot = telegram.Bot(token=command_bot_token)
    bot.send_message(chat_id=telegram_chat_id, text=dispatch_message, parse_mode='Markdown')

    return result