import os
import json
import telegram
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

BANK_CODES = {}

def load_bank_codes():
    """Loads bank codes from the JSON file."""
    global BANK_CODES
    try:
        script_dir = os.path.dirname(__file__)
        json_path = os.path.join(script_dir, '..', 'bank_codes.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            BANK_CODES = json.load(f)
    except FileNotFoundError:
        print("❌ Error: bank_codes.json not found.")

def send_telegram_notify(message, token, chat_id):
    """Sends a message to the specified Telegram chat."""
    try:
        bot = telegram.Bot(token=token)
        bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
        print("✅ Telegram notification sent.")
    except Exception as e:
        print(f"❌ Failed to send Telegram notification: {e}")

def write_to_sheets(bank_code, account, gross_amount, profit, net_amount, timestamp, from_bank):
    """Appends a new row to the specified Google Sheet."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_path = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')

        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        sheet_name = os.getenv('GOOGLE_SHEET_NAME', 'LightningEmpireAccounts')
        sheet = client.open(sheet_name).sheet1

        bank_name = BANK_CODES.get(bank_code, bank_code)
        row = [timestamp, bank_name, account, gross_amount, profit, net_amount, from_bank]
        sheet.append_row(row)
        print("✅ Transaction successfully logged to Google Sheets.")
    except FileNotFoundError:
        print(f"❌ Google Sheets Error: `{creds_path}` not found.")
    except Exception as e:
        print(f"❌ Google Sheets Error: {e}")

def verify_and_process_transfer(bank_code, account, amount, from_bank="未知"):
    """Verifies a bank transfer, calculates profit share, and logs everything."""
    load_bank_codes() # Ensure codes are loaded
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
            f"⚡ <b>金流入帳確認</b>\n"
            f"🏦 銀行: {bank_name} ({bank_code})\n"
            f"💰 總額: {amount:,.2f} NT$\n"
            f"💸 分潤 (10%): {profit:,.2f} NT$\n"
            f"💵 淨額: {net_amount:,.2f} NT$\n"
            f"📅 時間: {now}\n"
            f"🔗 來源: {from_bank}"
        )
        send_telegram_notify(msg, token, chat_id)

        write_to_sheets(bank_code, account, amount, profit, net_amount, now, from_bank)
        return True
    else:
        bank_name = BANK_CODES.get(bank_code, f"代碼 {bank_code}")
        error_msg = f"❌ 帳戶不符: 銀行 {bank_name} 收到一筆轉帳，但帳號 `{account}` 與設定不符。"
        send_telegram_notify(error_msg, token, chat_id)
        return False