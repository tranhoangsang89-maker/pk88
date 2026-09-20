\================================================================================

BỘ MÃ NGUỒN CHATBOT PHỤ KIỆN 88 (CHỊ 8 & BÉ 8\) CHO GOOGLE ANTIGRAVITY IDE (GA IDE)

\================================================================================

&nbsp;

1\. FILE: app.py (FastAPI Backend Dual-Persona)

\--------------------------------------------------------------------------------

import json

import os

from fastapi import FastAPI, HTTPException

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

import google.generativeai as genai

&nbsp;

app \= FastAPI(title="Phụ Kiện 88 Dual-Persona Chatbot API")

&nbsp;

app.add\_middleware(

&nbsp;&nbsp;&nbsp;&nbsp;CORSMiddleware,

&nbsp;&nbsp;&nbsp;&nbsp;allow\_origins=\["\*"\],

&nbsp;&nbsp;&nbsp;&nbsp;allow\_credentials=True,

&nbsp;&nbsp;&nbsp;&nbsp;allow\_methods=\["\*"\],

&nbsp;&nbsp;&nbsp;&nbsp;allow\_headers=\["\*"\],

)

&nbsp;

BASE\_DIR \= os.path.dirname(os.path.abspath(\_\_file\_\_))

with open(os.path.join(BASE\_DIR, "system\_prompt.txt"), "r", encoding="utf-8") as f:

&nbsp;&nbsp;&nbsp;&nbsp;SYSTEM\_INSTRUCTION \= f.read()

&nbsp;

with open(os.path.join(BASE\_DIR, "knowledge\_base.json"), "r", encoding="utf-8") as f:

&nbsp;&nbsp;&nbsp;&nbsp;KNOWLEDGE\_BASE \= json.load(f)

&nbsp;

GEMINI\_API\_KEY \= os.getenv("GEMINI\_API\_KEY", "")

if GEMINI\_API\_KEY:

&nbsp;&nbsp;&nbsp;&nbsp;genai.configure(api\_key=GEMINI\_API\_KEY)

&nbsp;

model \= genai.GenerativeModel(

&nbsp;&nbsp;&nbsp;&nbsp;model\_name="gemini-1.5-flash",

&nbsp;&nbsp;&nbsp;&nbsp;system\_instruction=SYSTEM\_INSTRUCTION \+ "\\n\\nKnowledge Base:\\n" \+ json.dumps(KNOWLEDGE\_BASE, ensure\_ascii=False)

)

&nbsp;

class ChatRequest(BaseModel):

&nbsp;&nbsp;&nbsp;&nbsp;message: str

&nbsp;&nbsp;&nbsp;&nbsp;history: list \= \[\]

&nbsp;

@app.post("/api/chat")

async def chat\_endpoint(req: ChatRequest):

&nbsp;&nbsp;&nbsp;&nbsp;try:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if not GEMINI\_API\_KEY:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lower \= req.message.lower()

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if any(k in lower for k in \["sửa", "pin", "ép kính", "màn hình", "ppf", "bảo hành"\]):

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"speaker": "be\_8",

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"speaker\_name": "Bé 8",

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"reply": f"Dạ Bé 8 chào anh/chị nha\! Về dịch vụ '{req.message}', bên em có nhận làm lấy liền 15 phút tại 35 Đoàn Hoàng Minh (Bến Tre), 25 Đinh Bộ Lĩnh (Mỹ Tho), Vĩnh Long và Cần Thơ. Anh/chị cho Bé 8 xin dòng máy chính xác để em báo giá chuẩn và chuẩn bị sẵn linh kiện nhé\!",

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"suggested\_actions": \["Chi nhánh gần nhất", "Giá thay pin iPhone", "Báo giá dán PPF"\]

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return {

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"speaker": "chi\_8",

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"speaker\_name": "Chị 8",

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"reply": f"Chị 8 chào bạn nha\! Phụ Kiện 88 đang có rất nhiều mẫu phụ kiện xịn xò cho '{req.message}', đặc biệt là ốp lưng Magsafe và cáp sạc nhanh chống chai pin. Bạn đang xài dòng máy nào để Chị 8 gợi ý mẫu đẹp nhất cho nè?",

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"suggested\_actions": \["Xem ốp lưng hot", "Cáp sạc nhanh 4-in-1", "Khuyến mãi hôm nay"\]

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}

&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;response \= model.generate\_content(

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;req.message,

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;generation\_config={"response\_mime\_type": "application/json"}

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return json.loads(response.text)

&nbsp;&nbsp;&nbsp;&nbsp;except Exception as e:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise HTTPException(status\_code=500, detail=str(e))

&nbsp;

if \_\_name\_\_ \== "\_\_main\_\_":

&nbsp;&nbsp;&nbsp;&nbsp;import uvicorn

&nbsp;&nbsp;&nbsp;&nbsp;uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

&nbsp;

&nbsp;

\================================================================================

2\. FILE: index.html (Giao diện Demo Chat Widget nhúng web chuẩn mobile)

\--------------------------------------------------------------------------------

(Dùng giao diện TailwindCSS tông Vàng \- Đen, tự động nhận diện avatar Chị 8 & Bé 8 theo speaker phản hồi, test trực tiếp offline hoặc qua API).

Mở file index.html trên bất kỳ trình duyệt nào để trải nghiệm ngay.

&nbsp;