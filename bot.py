import os
import requests

# Lấy biến và xóa khoảng trắng/dấu ngoặc dư thừa nếu có
TOKEN = str(os.getenv("TELEGRAM_BOT_TOKEN", "")).strip().replace('"', '')
CHAT_ID = str(os.getenv("TELEGRAM_CHAT_ID", "")).strip().replace('"', '')

print(f"DEBUG: Token đang dùng: {TOKEN[:10]}...") # Chỉ in 1 phần để bảo mật
print(f"DEBUG: Chat ID đang dùng: {CHAT_ID}")

if not TOKEN or not CHAT_ID:
    print("❌ Vẫn không tìm thấy biến! Hãy kiểm tra lại tab Variables trên Railway.")
else:
    # Thử gửi tin nhắn ngay khi khởi động
    url = f"https://telegram.org{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": "🔔 Railway đã kết nối Telegram thành công!"}
    
    res = requests.post(url, data=payload)
    print(f"Kết quả gửi thử: {res.json()}")
