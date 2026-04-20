import os

# Debug: In ra để xem Railway đã nhận diện được biến chưa
token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

print(f"Token hiện tại: {token}")
print(f"Chat ID hiện tại: {chat_id}")

if not token or not chat_id:
    print("Lỗi: Không tìm thấy biến môi trường!")
    # Dừng chương trình nếu thiếu biến
