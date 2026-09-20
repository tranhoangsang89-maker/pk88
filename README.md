# Phụ Kiện 88 - Dual-Persona AI Chatbot 🤖📱

Hệ thống Trợ lý ảo AI tư vấn bán hàng & hỗ trợ kỹ thuật tự động cho **Phụ Kiện 88**, tích hợp 2 nhân vật: **Chị 8** (Bán hàng & Chăm sóc khách hàng) và **Bé 8** (Kỹ thuật viên sửa chữa).

---

## 🌟 Tính năng chính

- 🤖 **Dual-Persona AI**: Tự động chuyển đổi phản hồi linh hoạt giữa Chị 8 & Bé 8 dựa trên loại câu hỏi của khách hàng.
- ⚡ **Gemini API Integration**: Sử dụng mô hình Google Gemini AI phản hồi tự nhiên, chuẩn mực theo dữ liệu Knowledge Base của shop.
- 🔔 **Telegram Lead Alert**: Tự động nhận diện nhu cầu mua hàng/sửa chữa và gửi thông báo số điện thoại Lead trực tiếp về Telegram của chủ shop.
- 🔄 **API Key Round-Robin**: Hỗ trợ xoay vòng tự động nhiều API Key Gemini để tránh chạm hạn ngạch (rate limit).
- 🎨 **Giao diện hiện đại**: Thiết kế Mobile-first chuẩn Dark/Gold Chrome sang trọng.

---

## 🛠️ Cấu trúc thư mục

```text
├── api/
│   └── index.py            # Entrypoint cho Vercel Serverless Function
├── app.py                  # Backend FastAPI & Logic Chatbot
├── index.html              # Giao diện Web Chatbot Mobile-first
├── vercel.json             # File cấu hình deploy Vercel
├── PK88_Knowledge_Base.json# Dữ liệu bảng giá linh kiện & máy
├── PK88_System_Prompt_GA_IDE.md # System Prompt hướng dẫn tính cách AI
├── requirements.txt        # Các thư viện Python cần thiết
├── .gitignore              # Đã cấu hình ẩn file .env chứa thông tin nhạy cảm
└── Procfile                # Cấu hình Web Service (Render/Heroku)
```

---

## 🚀 Hướng dẫn Deploy lên Vercel (Miễn phí)

1. **Push dự án này lên GitHub của bạn.**
2. Truy cập [Vercel.com](https://vercel.com) $\rightarrow$ Chọn **Add New Project** $\rightarrow$ Import Repository từ GitHub.
3. Cấu hình **Environment Variables** trên Vercel:
   - `GEMINI_API_KEY`: Key Gemini AI của bạn (hoặc `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`...)
   - `TELEGRAM_BOT_TOKEN`: Token của Telegram Bot (dùng để gửi thông báo Lead)
   - `TELEGRAM_CHAT_ID`: Chat ID Telegram của bạn
4. Chọn **Deploy**. Vercel sẽ khởi tạo ứng dụng và cấp cho bạn đường link demo dạng: `https://<ten-du-an>.vercel.app`.

---

## 💻 Khởi chạy ở Local (Chạy thử máy cá nhân)

```bash
# 1. Cài đặt các thư viện
pip install -r requirements.txt

# 2. Tạo file .env với thông tin:
GEMINI_API_KEY=your_gemini_api_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# 3. Khởi chạy ứng dụng
python app.py
```
Mở trình duyệt truy cập: `http://localhost:8000`
