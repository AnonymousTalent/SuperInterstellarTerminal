import argparse
import os
import pandas as pd
import telegram
import api_client
from dotenv import load_dotenv
from phishing_detector import PhishingDetector, get_mock_features

def dispatch_orders():
    """
    Fetches new orders from the delivery platform API and processes them.
    """
    print("😼⚡️ AI 派單系統啟動中...")

    new_orders = api_client.get_new_orders()

    if new_orders is None:
        # This case handles API key errors from the client
        dispatch_message = "❌ **派單失敗**\n\n無法連接到外送平台 API。請檢查您的 API 金鑰設定。"
    elif not new_orders:
        # This case handles when there are no new orders
        dispatch_message = "👍 **目前無新訂單**\n\n系統將持續監控。"
    else:
        # This is the success case
        print("以下是從平台獲取的新訂單：")
        for order in new_orders:
            print(f"  - 訂單ID: {order['order_id']}, 地址: {order['customer_address']}")

        # Here, you would add the logic to assign these orders to drivers/units.
        # For now, we just confirm that we received them.

        dispatch_message = f"✅ **收到 {len(new_orders)} 筆新訂單**\n\n已從平台成功拉取訂單，準備進行 AI 派單。詳情請查看系統後台。"

    # Send a summary to Telegram using the command bot
    token = os.getenv("COMMAND_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    bot = telegram.Bot(token=token)
    bot.send_message(chat_id=chat_id, text=dispatch_message, parse_mode='Markdown')

    print(f"✅ 派單系統狀態更新已發送至 Telegram Chat ID: {chat_id}。")


def generate_report():
    """
    Reads order data from a CSV, calculates a summary, and sends it to Telegram.
    """
    print("📊 正在生成報表...")
    try:
        df = pd.read_csv('dummy_orders.csv')

        # Calculate metrics
        completed_orders = df[df['status'] == 'completed']
        total_orders = len(df)
        completed_count = len(completed_orders)
        total_revenue = completed_orders['revenue'].sum()

        # Format the report message
        report_message = (
            f"📊 **小閃電貓每日戰報** ⚡\n\n"
            f"總訂單數：{total_orders}\n"
            f"完成訂單數：{completed_count}\n"
            f"總收益：${total_revenue:,.2f} 💰\n\n"
            f"幹得不錯，總司令！😼"
        )

        print("報表內容：\n" + report_message)

        # Send to Telegram
        token = os.getenv("REPORT_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        bot = telegram.Bot(token=token)
        bot.send_message(chat_id=chat_id, text=report_message, parse_mode='Markdown')

        print(f"✅ 報表已成功發送至 Telegram Chat ID: {chat_id}。")

    except FileNotFoundError:
        print("❌ 錯誤：找不到 `dummy_orders.csv` 檔案。")
    except Exception as e:
        print(f"❌ 產生報表時發生未知錯誤：{e}")


def check_cash_flow():
    """Placeholder function for checking cash flow."""
    print("💰 正在檢查金流...")
    # TODO: Add logic to monitor payments and detect anomalies.
    print("✅ 金流檢查完成，無異常。")

def simulate_strategy():
    """Placeholder function for simulating strategies."""
    print("💎 正在進行策略模擬...")
    # TODO: Add logic for simulating dispatch strategies and calculating ROI.
    print("✅ 策略模擬完成。")

def scan_for_phishing():
    """
    Initializes the PhishingDetector model and performs a mock scan.
    """
    print("🛡️ 啟動 AI 反釣魚掃描模組...")

    # Initialize the model
    detector = PhishingDetector()
    print("✅ AI 模型載入成功。")

    # Simulate scanning a URL
    # In a real application, you would pass a real URL, extract its features,
    # and then feed the feature tensor to the model.
    mock_url_features = get_mock_features()
    prediction = detector.predict_url(mock_url_features)

    scan_result_message = f"掃描模擬完成。\n- 模擬 URL 特徵: [Tensor of size {mock_url_features.shape}]\n- AI 判斷結果: **{prediction}**"
    print(scan_result_message)

    # Send result to Telegram
    token = os.getenv("COMMAND_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    bot = telegram.Bot(token=token)
    bot.send_message(chat_id=chat_id, text=f"🛡️ **反釣魚系統報告**\n\n{scan_result_message}", parse_mode='Markdown')

    print(f"✅ 掃描結果已發送至 Telegram。")


def main():
    """Main function to parse arguments and run tasks."""
    # Load environment variables from .env file
    load_dotenv()

    # Check for required environment variables
    report_bot_token = os.getenv("REPORT_BOT_TOKEN")
    command_bot_token = os.getenv("COMMAND_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    api_key = os.getenv("DELIVERY_PLATFORM_API_KEY")

    if not all([report_bot_token, command_bot_token, telegram_chat_id, api_key]):
        print("❌ 錯誤：必要的環境變數尚未在 .env 檔案中完全設定。")
        print("請複製 .env.example 為 .env，並填寫所有金鑰 (REPORT_BOT_TOKEN, COMMAND_BOT_TOKEN, TELEGRAM_CHAT_ID, DELIVERY_PLATFORM_API_KEY)。")
        return

    parser = argparse.ArgumentParser(description="小閃電貓⚡ AI 雷霆助理")
    parser.add_argument("--派單", action="store_true", help="從平台 API 拉取新訂單並準備派送")
    parser.add_argument("--報表", action="store_true", help="生成每日戰報並發送 Telegram")
    parser.add_argument("--金流檢查", action="store_true", help="監控金流異常 (尚未實現)")
    parser.add_argument("--策略模擬", action="store_true", help="模擬不同派單策略 (尚未實現)")
    parser.add_argument("--反釣魚掃描", action="store_true", help="啟動 AI 模型掃描可疑連結")

    args = parser.parse_args()

    print("--- ⚡ 小閃電貓任務啟動 ⚡ ---")
    if args.派單:
        dispatch_orders()
    elif args.報表:
        generate_report()
    elif args.金流檢查:
        check_cash_flow()
    elif args.策略模擬:
        simulate_strategy()
    elif args.反釣魚掃描:
        scan_for_phishing()
    else:
        print("🤔 請提供一個操作指令，例如：--派單")
        parser.print_help()
    print("--- 任務結束 ---")


if __name__ == "__main__":
    main()
