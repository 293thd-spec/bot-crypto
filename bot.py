import os
import requests

def send_telegram_message():
    # Lấy thông tin từ Variables của Railway
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    message = "✅ Tin nhắn test từ ứng dụng Python trên Railway!"

    if not token or not chat_id:
        print("Lỗi: Bạn chưa cấu hình biến TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID trên Railway!")
        return

    url = f"https://telegram.org{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Gửi tin nhắn thành công!")
        else:
            print(f"Lỗi từ Telegram: {response.text}")
    except Exception as e:
        print(f"Lỗi kết nối: {e}")

if __name__ == "__main__":
    send_telegram_message()
