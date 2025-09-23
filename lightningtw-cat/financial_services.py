import os
import json
import telegram
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- Helper Function to Load Bank Codes ---
def load_bank_codes():
    """Loads bank codes from the JSON file."""
    try:
        script_dir = os.path.dirname(__file__)
        json_path = os.path.join(script_dir, 'bank_codes.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: bank_codes.json not found. Bank names will not be displayed.")
        return {}

BANK_CODES = load_bank_codes()

# --- Telegram Notification Function ---
def send_telegram_notify(message, token, chat_id):
    """Sends a message to the specified Telegram chat."""
    try:
        bot = telegram.Bot(token=token)
        bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
        print("✅ Telegram notification sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send Telegram notification: {e}")

# --- Google Sheets Integration ---
def write_to_sheets(bank_code, account, gross_amount, profit, net_amount, timestamp, from_bank):
    """Appends a new row to the specified Google Sheet."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        script_dir = os.path.dirname(__file__)
        creds_path = os.path.join(script_dir, '..', 'credentials.json') # Assumes credentials.json is in the root

        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        sheet = client.open("LightningEmpireAccounts").sheet1

        bank_name = BANK_CODES.get(bank_code, bank_code)
        row = [timestamp, bank_name, account, gross_amount, profit, net_amount, from_bank]
        sheet.append_row(row)
        print("✅ Transaction successfully logged to Google Sheets.")
    except FileNotFoundError:
        print("❌ Google Sheets Error: `credentials.json` not found in the root directory.")
    except Exception as e:
        print(f"❌ Google Sheets Error: {e}")

# --- Bank Transfer Verification ---
def verify_bank_transfer(bank_code, account, amount, from_bank="未知"):
    """Verifies bank transfer details and sends a notification."""
    token = os.getenv("COMMAND_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    expected_account = None
    if bank_code == os.getenv('BANK_CTBC_CODE'):
        expected_account = os.getenv('BANK_CTBC_ACCOUNT')
    elif bank_code == os.getenv('BANK_POST_CODE'):
        expected_account = os.getenv('BANK_POST_ACCOUNT')

    if account == expected_account:
        bank_name = BANK_CODES.get(bank_code, "未知銀行")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        profit = amount * 0.1
        net_amount = amount - profit

        msg = (
            f"⚡ <b>Lightning Empire 金流入帳確認</b>\n"
            f"🏦 銀行：{bank_name} (代碼: {bank_code})\n"
            f"💰 總金額：{amount:,.2f} NT$\n"
            f"💸 分潤 (10%)：{profit:,.2f} NT$ (轉至女神家族 Bot)\n"
            f"💵 淨額：{net_amount:,.2f} NT$\n"
            f"📅 時間：{now}\n"
            f"🔗 來源：{from_bank}\n\n"
            f"🛡️ 總司令，資金到位！帝國戰力 +{net_amount:,.2f} 💜"
        )
        send_telegram_notify(msg, token, chat_id)

        profit_share_msg = f"💸 分潤通知：{profit:,.2f} NT$ 已模擬轉帳至 AutoFinanceBot。"
        send_telegram_notify(profit_share_msg, token, chat_id)

        write_to_sheets(bank_code, account, amount, profit, net_amount, now, from_bank)
        return True
    else:
        bank_name = BANK_CODES.get(bank_code, f"代碼 {bank_code}")
        error_msg = f"❌ 帳戶不符：銀行 {bank_name} 收到一筆轉帳，但帳號 `{account}` 與設定不符。"
        send_telegram_notify(error_msg, token, chat_id)
        return False

# --- Simulation Function ---
def simulate_and_check_flow():
    """Simulates bank transfers for testing the cash flow check."""
    print("\n--- Simulating and Checking Cash Flow ---")
    ctbc_code = os.getenv('BANK_CTBC_CODE')
    ctbc_account = os.getenv('BANK_CTBC_ACCOUNT')
    post_code = os.getenv('BANK_POST_CODE')
    post_account = os.getenv('BANK_POST_ACCOUNT')

    # Simulate a valid CTBC transfer
    verify_bank_transfer(ctbc_code, ctbc_account, 50000, from_bank="模擬轉帳")
    # Simulate a valid POST transfer
    verify_bank_transfer(post_code, post_account, 30000, from_bank="模擬轉帳")
    # Simulate an invalid transfer
    verify_bank_transfer(ctbc_code, "000000000000", 100, from_bank="可疑來源")
    print("--- Simulation Complete ---\n")
