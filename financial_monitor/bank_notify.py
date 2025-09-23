import os
import json
import telegram
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request, jsonify
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Environment Variables ---
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
BANK_CTBC_CODE = os.getenv('BANK_CTBC_CODE', '822')
BANK_CTBC_ACCOUNT = os.getenv('BANK_CTBC_ACCOUNT')
BANK_POST_CODE = os.getenv('BANK_POST_CODE', '700')
BANK_POST_ACCOUNT = os.getenv('BANK_POST_ACCOUNT')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')

# Initialize Flask App
app = Flask(__name__)

# --- Helper Function to Load Bank Codes ---
def load_bank_codes():
    """Loads bank codes from the JSON file."""
    try:
        # Construct path relative to this script's location
        script_dir = os.path.dirname(__file__)
        json_path = os.path.join(script_dir, 'bank_codes.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: bank_codes.json not found. Bank names will not be displayed.")
        return {}

BANK_CODES = load_bank_codes()

# --- Telegram Notification Function ---
def send_telegram_notify(message):
    """Sends a message to the specified Telegram chat."""
    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='HTML'
        )
        print("✅ Telegram notification sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send Telegram notification: {e}")

# --- Google Sheets Integration ---
def write_to_sheets(bank_code, account, gross_amount, profit, net_amount, timestamp, from_bank):
    """Appends a new row to the specified Google Sheet."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # The credentials file should be in the parent directory of this script's directory
        script_dir = os.path.dirname(__file__)
        creds_path = os.path.join(script_dir, '..', 'credentials.json')

        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)

        # Open the sheet by name (you can also use URL)
        sheet = client.open("LightningEmpireAccounts").sheet1

        # Prepare the row data
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
    # This function will be expanded in later steps

    # Determine the expected account number based on the bank code
    if bank_code == BANK_CTBC_CODE:
        expected_account = BANK_CTBC_ACCOUNT
    elif bank_code == BANK_POST_CODE:
        expected_account = BANK_POST_ACCOUNT
    else:
        expected_account = None

    if account == expected_account:
        bank_name = BANK_CODES.get(bank_code, "未知銀行")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Calculate 10% profit share
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
        send_telegram_notify(msg)

        # Simulate sending the profit share
        profit_share_msg = f"💸 分潤通知：{profit:,.2f} NT$ 已模擬轉帳至 AutoFinanceBot。"
        send_telegram_notify(profit_share_msg)

        # Write to Google Sheets
        write_to_sheets(bank_code, account, amount, profit, net_amount, now, from_bank)

        return True
    else:
        bank_name = BANK_CODES.get(bank_code, f"代碼 {bank_code}")
        error_msg = f"❌ 帳戶不符：銀行 {bank_name} 收到一筆轉帳，但帳號 `{account}` 與設定不符。"
        send_telegram_notify(error_msg)
        return False

# --- Flask Webhook Route ---
@app.route('/webhook/bank', methods=['POST'])
def bank_webhook():
    """Webhook to receive bank transfer notifications."""
    # Implement webhook secret verification
    if request.headers.get('X-Webhook-Secret') != WEBHOOK_SECRET:
        return jsonify({"status": "error", "message": "無效簽名"}), 403

    data = request.json
    bank_code = data.get('bank_code')
    account = data.get('account')
    amount = data.get('amount')
    from_bank = data.get('from_bank', 'Webhook')

    if not all([bank_code, account, amount]):
        return jsonify({"status": "error", "message": "缺少必要參數"}), 400

    verify_bank_transfer(bank_code, account, float(amount), from_bank)
    return jsonify({"status": "success"}), 200

# --- Simulation Function ---
def simulate_transfer():
    """Simulates a bank transfer for testing purposes."""
    print("\n--- Simulating Transfers ---")
    # Simulate CTBC transfer
    verify_bank_transfer(BANK_CTBC_CODE, BANK_CTBC_ACCOUNT, 50000, from_bank="模擬轉帳")
    # Simulate POST transfer
    verify_bank_transfer(BANK_POST_CODE, BANK_POST_ACCOUNT, 30000, from_bank="模擬轉帳")
    print("--- Simulation Complete ---\n")

if __name__ == '__main__':
    # Ensure all required environment variables are set
    if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, BANK_CTBC_ACCOUNT, BANK_POST_ACCOUNT, WEBHOOK_SECRET]):
        print("❌ 錯誤：請在 .env 檔案中設定所有必要的環境變數。")
    else:
        simulate_transfer()
        # To run the web server, uncomment the line below
        # app.run(host='0.0.0.0', port=5000)
