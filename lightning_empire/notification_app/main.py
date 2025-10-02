import os
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 若用 webhook，需 pip install flask (Pydroid3 支援)
app = Flask(__name__)

# 從 .env 讀取帳戶
BANK_CTBC_CODE = os.getenv("BANK_CTBC_CODE", "822")
BANK_CTBC_ACCOUNT = os.getenv("BANK_CTBC_ACCOUNT", "484540302460")
BANK_POST_CODE = os.getenv("BANK_POST_CODE", "700")
BANK_POST_ACCOUNT = os.getenv("BANK_POST_ACCOUNT", "00210091602429")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")

# 收益分配比例
MY_SHARE = 0.25 # 你收益
SYSTEM_SHARE = 0.75 # 系統保管/分紅

def send_telegram_notify(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"⚠️ Telegram 未設定：{message}")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("✅ Telegram 通知送出成功")
        else:
            print(f"❌ Telegram 錯誤：{response.text}")
    except Exception as e:
        print(f"❌ Telegram 連線失敗：{e}")

def send_line_notify(message: str):
    if not LINE_NOTIFY_TOKEN:
        print(f"⚠️ LINE Notify 未設定：{message}")
        return
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"}
    data = {"message": message}
    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            print("✅ LINE 通知送出成功")
        else:
            print(f"❌ LINE 錯誤：{response.text}")
    except Exception as e:
        print(f"❌ LINE 連線失敗：{e}")

def notify_all(message: str):
    send_telegram_notify(message)
    send_line_notify(message)

def verify_bank_transfer(bank_code, account, amount, from_bank="未知"):
    banks = {
        BANK_CTBC_CODE: f"中信 {BANK_CTBC_ACCOUNT}",
        BANK_POST_CODE: f"郵政 {BANK_POST_ACCOUNT}"
    }
    if bank_code in banks and account == banks[bank_code].split()[-1]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        my_amount = round(amount * MY_SHARE, 2)
        system_amount = round(amount * SYSTEM_SHARE, 2)
        msg = f"⚡ <b>Lightning Empire 金流入帳確認</b>\n" \
              f"🏦 銀行：{banks[bank_code]} (代碼: {bank_code})\n" \
              f"💰 原始金額：{amount:,} NT$\n" \
              f"📅 時間：{now}\n" \
              f"🔗 來源：{from_bank}\n\n" \
              f"💎 收益拆分：\n" \
              f" 👑 你的收益 25% → {my_amount:,} NT$\n" \
              f" 🛡️ 系統保管 75% → {system_amount:,} NT$\n" \
              f"🛡️ 總司令，資金到位！帝國戰力 +{amount} 💜"
        notify_all(msg)
        return {"my_share": my_amount, "system_share": system_amount}
    else:
        error_msg = f"❌ 帳戶不符：預期 {banks.get(bank_code, '未知')}，收到 {account}"
        notify_all(error_msg)
        return None

@app.route("/bank_webhook", methods=["POST"])
def bank_webhook():
    data = request.json
    bank_code = data.get("bank_code")
    account = data.get("account")
    amount = data.get("amount", 0)
    from_bank = data.get("from_bank", "未知")
    result = verify_bank_transfer(bank_code, account, amount, from_bank)
    return jsonify(result or {"status": "error"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)