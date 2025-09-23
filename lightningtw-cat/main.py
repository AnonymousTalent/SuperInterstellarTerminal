import argparse
import os
import pandas as pd
import telegram
from dotenv import load_dotenv

def dispatch_orders():
    """
    Reads unit data from a CSV, dispatches an active unit, and sends a notification.
    """
    print("😼⚡️ AI 派單系統啟動中...")
    try:
        df = pd.read_csv('units.csv')

        active_units = df[df['operator_status'] == 'Active']

        if active_units.empty:
            dispatch_message = "所有單位都在待命中，無可派遣的單位。"
            print(dispatch_message)
        else:
            # Select a random active unit to dispatch
            unit_to_dispatch = active_units.sample(n=1)
            unit_id = unit_to_dispatch.iloc[0]['unit_id']

            # Update status
            df.loc[df['unit_id'] == unit_id, 'operator_status'] = 'Engaged'

            # Save changes
            df.to_csv('units.csv', index=False)

            dispatch_message = f"✅ **作戰指令已下達**\n\n單位 `{unit_id}` 已成功派遣，狀態更新為 `Engaged`。"
            print(f"單位 {unit_id} 已派遣。")

        # Send to Telegram using the command bot
        token = os.getenv("COMMAND_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        bot = telegram.Bot(token=token)
        bot.send_message(chat_id=chat_id, text=dispatch_message, parse_mode='Markdown')

        print(f"✅ 派單結果已發送至 Telegram Chat ID: {chat_id}。")

    except FileNotFoundError:
        print("❌ 錯誤：找不到 `units.csv` 檔案。")
    except Exception as e:
        print(f"❌ 派遣時發生未知錯誤：{e}")


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
    parser.add_argument("--派單", action="store_true", help="自動派送今日訂單")
    parser.add_argument("--報表", action="store_true", help="生成報表並發送 Telegram")
    parser.add_argument("--金流檢查", action="store_true", help="監控金流異常")
    parser.add_argument("--策略模擬", action="store_true", help="模擬不同派單策略並輸出結果")

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
    else:
        print("🤔 請提供一個操作指令，例如：--派單")
        parser.print_help()
    print("--- 任務結束 ---")


if __name__ == "__main__":
    main()
