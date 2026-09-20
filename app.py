import json
import requests
import os
import random
import itertools
import re
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Phụ Kiện 88 Dual-Persona Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "PK88_System_Prompt_GA_IDE.md"), "r", encoding="utf-8") as f:
    SYSTEM_INSTRUCTION = f.read()

with open(os.path.join(BASE_DIR, "PK88_Knowledge_Base.json"), "r", encoding="utf-8") as f:
    KNOWLEDGE_BASE = json.load(f)

# Load all available Gemini API keys from environment
API_KEYS = []
for key, value in os.environ.items():
    if key.startswith("GEMINI_API_KEY") and value:
        API_KEYS.append(value)

# Fallback if no specific keys are found but a general one is
if not API_KEYS and os.getenv("GEMINI_API_KEY"):
    API_KEYS.append(os.getenv("GEMINI_API_KEY"))

# Create an iterator for round-robin key rotation
print(f"DEBUG: Loaded {len(API_KEYS)} API keys")
api_key_cycle = itertools.cycle(API_KEYS) if API_KEYS else None

# Prepare system instruction context
SYSTEM_CONTEXT = SYSTEM_INSTRUCTION + "\n\nKnowledge Base:\n" + json.dumps(KNOWLEDGE_BASE, ensure_ascii=False)

class ChatRequest(BaseModel):
    message: str
    history: list = []

def get_mock_reply(message: str) -> dict:
    """Mock demo fallback when no API key is provided, intelligently answers based on Knowledge Base."""
    lower_msg = message.lower()
    
    # Check if message is for Bé 8 (Kỹ thuật)
    be_8_keywords = ["sửa", "pin", "ép kính", "màn hình", "ppf", "bảo hành", "vỏ", "hư", "lỗi", "bể", "nứt"]
    if any(k in lower_msg for k in be_8_keywords):
        services = KNOWLEDGE_BASE['roles']['be_8']['services']
        
        # Determine exact service to recommend
        matched_service = next((s for s in services if any(k in s['service'].lower() or k in s['details'].lower() for k in be_8_keywords if k in lower_msg)), services[0])
        
        reply = f"Dạ Bé 8 chào anh/chị nha! Về dịch vụ {matched_service['service']}, bên em {matched_service['details']}. Anh/chị cho Bé 8 xin dòng máy chính xác để em báo giá chuẩn và chuẩn bị sẵn linh kiện nhé!"
        
        if "bảo hành" in lower_msg:
             reply = f"Dạ Bé 8 chào anh/chị! Về chính sách bảo hành thì: {KNOWLEDGE_BASE['roles']['be_8']['warranty_policy']} Anh/chị cần hỗ trợ thêm gì ạ?"
        
        return {
            "speaker": "be_8",
            "speaker_name": "Bé 8",
            "reply": reply,
            "suggested_actions": ["Chi nhánh gần nhất", "Giá thay pin iPhone", "Báo giá dán PPF", "Chính sách bảo hành"]
        }
    
    # Check for Chi nhánh info
    if any(k in lower_msg for k in ["chi nhánh", "địa chỉ", "ở đâu", "cửa hàng", "tìm shop", "gần nhất"]):
        branches = "\n".join([f"- {b['city']}: {b['address']} ({b['note']})" for b in KNOWLEDGE_BASE['branches'][:3]]) 
        reply = f"Chị 8 gửi bạn thông tin các chi nhánh tiêu biểu bên mình nhé:\n{branches}\n\nBạn đang ở khu vực nào (Bến Tre, Mỹ Tho, Cần Thơ, Vĩnh Long, Trà Vinh) để Chị 8 chỉ đường ra cửa hàng gần nhất ạ?"
        return {
            "speaker": "chi_8",
            "speaker_name": "Chị 8",
            "reply": reply,
            "suggested_actions": ["Chi nhánh Mỹ Tho", "Chi nhánh Bến Tre", "Chi nhánh Cần Thơ", "Chi nhánh Vĩnh Long"]
        }

    # Match specific product category by keywords
    catalog = KNOWLEDGE_BASE['roles']['chi_8']['catalog']
    matched_cat = None
    
    if any(k in lower_msg for k in ["tai nghe", "tai", "headphone", "airpod", "bluetooth", "loa", "âm thanh", "sound", "type c", "type-c"]):
        matched_cat = next((c for c in catalog if "Tai nghe" in c['category']), None)
    elif any(k in lower_msg for k in ["sạc", "cáp", "củ sạc", "dây sạc", "sac", "cap", "charger"]):
        matched_cat = next((c for c in catalog if "Cáp sạc" in c['category']), None)
    elif any(k in lower_msg for k in ["ốp", "op", "case", "bao da", "magsafe"]):
        matched_cat = next((c for c in catalog if "Ốp lưng" in c['category']), None)
    elif any(k in lower_msg for k in ["kính", "cường lực", "cuong luc", "kinh", "dán màn"]):
        matched_cat = next((c for c in catalog if "Kính cường lực" in c['category']), None)
    elif any(k in lower_msg for k in ["dự phòng", "pin dự phòng", "powerbank", "chuột", "hub", "lens", "apple watch"]):
        matched_cat = next((c for c in catalog if "Phụ kiện khác" in c['category']), None)

    if matched_cat:
        products = ", ".join(matched_cat['products'][:3])
        reply = f"Dạ có nha bạn ơi! Phụ Kiện 88 đang sẵn rất nhiều mẫu {matched_cat['category']} xịn sò (ví dụ: {products}...). Bạn đang dùng dòng máy nào hay cần tìm mẫu cụ thể nào để Chị 8 tư vấn và báo giá ưu đãi nhất cho mình nè?"
        return {
            "speaker": "chi_8",
            "speaker_name": "Chị 8",
            "reply": reply,
            "suggested_actions": matched_cat['products'][:3] + ["Hotline 0833 898 688"]
        }
        
    # Default friendly greeting if general
    reply = "Dạ Chị 8 chào bạn nha! Phụ Kiện 88 chuyên cung cấp đầy đủ phụ kiện chính hãng (Ốp lưng, Cường lực, Cáp sạc nhanh, Tai nghe/Loa Bluetooth) và dịch vụ sửa chữa ép kính, thay pin lấy liền. Bạn đang quan tâm đến sản phẩm hoặc dịch vụ nào để Chị 8 hỗ trợ mình ngay nhé?"
    return {
        "speaker": "chi_8",
        "speaker_name": "Chị 8",
        "reply": reply,
        "suggested_actions": ["Cáp sạc nhanh Type-C", "Tai nghe Bluetooth", "Dán cường lực", "Báo giá thay pin"]
    }

def send_telegram_alert(lead_data, score, label):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    msg = f"🔥 [LEAD {label}] • Điểm Score: {score}đ\n"
    msg += f"- Khách hàng: {lead_data.get('customer_name', 'Chưa rõ')}\n"
    msg += f"- Số điện thoại: {lead_data.get('phone', 'Chưa rõ')}\n"
    msg += f"- Nhu cầu: {lead_data.get('need', 'Chưa rõ')}\n"
    msg += f"- Ngân sách: {lead_data.get('budget', 'Chưa rõ')}\n"
    msg += f"- Thời gian: {lead_data.get('timeline', 'Chưa rõ')}\n"
    msg += f"- Chi nhánh: {lead_data.get('branch', 'Chưa rõ')}\n"
    msg += f"\n👉 Đề xuất: Liên hệ ngay khách hàng để chốt sales!"

    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            requests.post(url, json={"chat_id": chat_id, "text": msg})
        except Exception as e:
            print(f"Telegram API Error: {e}")
    else:
        print("\n--- MẪU THÔNG BÁO TELEGRAM ---")
        print(msg)
        print("------------------------------\n")

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        # Pre-capture phone using regex as fallback
        normalized_msg = req.message.replace(' ', '').replace('.', '').replace('-', '')
        phone_match = re.search(r'(0[35789]\d{8})', normalized_msg)
        fallback_phone = phone_match.group(1) if phone_match else None

        resp_data = None
        # 1. Check Mock Mode
        if not API_KEYS:
            resp_data = get_mock_reply(req.message)
            if fallback_phone:
                resp_data["lead_info"] = {"phone": fallback_phone, "need": req.message}
        else:
            # 2. Live API Mode with Key Rotation & Fallback Retries
            last_err = None
            
            # Dynamic Real-time Date & Year Context
            now_dt = datetime.now()
            current_date_str = now_dt.strftime("%d/%m/%Y")
            current_year = now_dt.year
            
            time_context = (
                f"\n\n[THỜI GIAN HIỆN TẠI HỆ THỐNG THỜI GIAN THỰC]\n"
                f"- Hôm nay là ngày: {current_date_str} (Năm {current_year}).\n"
                f"- LƯU Ý QUAN TRỌNG: Bạn luôn luôn nhận biết mốc thời gian hiện tại là năm {current_year}.\n"
                f"- Khi khách hàng hỏi về các dòng máy điện thoại (iPhone, Samsung...), hãy dựa trên mốc thời gian hiện tại ({current_year}) để trả lời chuẩn xác nhất."
            )
            
            dynamic_system_context = SYSTEM_CONTEXT + time_context

            for _ in range(len(API_KEYS)):
                selected_key = next(api_key_cycle)
                try:
                    genai.configure(api_key=selected_key)
                    model = genai.GenerativeModel(
                        model_name="gemini-1.5-flash",
                        system_instruction=dynamic_system_context
                    )
                    
                    # Build prompt with history
                    history_text = "Conversation History:\n"
                    for msg in req.history:
                        try:
                            text = msg.get("parts", [{"text":""}])[0].get("text", "")
                            history_text += f"{msg.get('role', 'user')}: {text}\n"
                        except:
                            pass
                    
                    full_prompt = history_text + f"\nNew User Message: {req.message}\nPlease respond strictly in the required JSON format."

                    response = model.generate_content(
                        full_prompt,
                        generation_config={"response_mime_type": "application/json"}
                    )
                    
                    # Clean markdown code blocks if any
                    resp_text = response.text.strip()
                    if resp_text.startswith("```json"):
                        resp_text = resp_text[7:]
                    if resp_text.startswith("```"):
                        resp_text = resp_text[3:]
                    if resp_text.endswith("```"):
                        resp_text = resp_text[:-3]
                        
                    resp_data = json.loads(resp_text.strip())
                    break # Successfully parsed response
                except Exception as err:
                    last_err = err
                    print(f"API Key retry warning: {err}", flush=True)
                    continue
            
            if resp_data is None:
                print(f"All API keys failed or JSON parse error. Last error: {last_err}", flush=True)
                resp_data = get_mock_reply(req.message)

        # 3. Process BANT & Lead Scoring
        lead_info = resp_data.get("lead_info") or {}
        phone = lead_info.get("phone")
        phone = str(phone).strip() if phone else ""
        
        if phone == "..." or not phone:
            phone = fallback_phone
            
        if phone and len(phone) >= 9:
            lead_info["phone"] = phone
            
            # Lead Scoring Algorithm
            score = 30 # Base for having a phone
            need = lead_info.get("need", "")
            timeline = lead_info.get("timeline", "").lower()
            budget = lead_info.get("budget", "")
            branch = lead_info.get("branch", "")
            
            def is_valid(val): return val and str(val).strip() not in ["", "...", "Chưa rõ", "None"]
            
            if is_valid(need): score += 25
            if is_valid(timeline):
                if any(k in timeline for k in ["hôm nay", "24h", "gấp"]): score += 20
                elif "trong tuần" in timeline: score += 15
            if is_valid(budget): score += 15
            if is_valid(branch): score += 10
            
            if score >= 80: label = "HOT LEAD"
            elif score >= 60: label = "WARM LEAD"
            else: label = "COLD LEAD"
            
            lead_info["score"] = score
            lead_info["label"] = label
            lead_info["timestamp"] = datetime.now().isoformat()
            
            # Save to leads.json (safely handled for serverless environments)
            try:
                leads_file = os.path.join(BASE_DIR, "leads.json")
                leads = []
                if os.path.exists(leads_file):
                    try:
                        with open(leads_file, "r", encoding="utf-8") as f:
                            leads = json.load(f)
                    except json.JSONDecodeError:
                        leads = []
                        
                leads.append(lead_info)
                with open(leads_file, "w", encoding="utf-8") as f:
                    json.dump(leads, f, ensure_ascii=False, indent=4)
            except Exception as fe:
                print(f"File write skipped on serverless: {fe}", flush=True)
                
            # Send Telegram Alert
            send_telegram_alert(lead_info, score, label)
            
            # Append confirmation
            lead_capture_msg = f"Dạ Phụ Kiện 88 đã ghi nhận thông tin và số điện thoại của anh/chị. Đội ngũ tư vấn sẽ chuẩn bị máy/linh kiện và gọi lại hỗ trợ mình ngay trong 5-10 phút tới ạ!\n\n"
            resp_data["reply"] = lead_capture_msg + resp_data.get("reply", "")

        return resp_data
        
    except Exception as e:
        import traceback
        print(f"API Error: {e}", flush=True)
        traceback.print_exc()
        # Graceful degradation to mock if API fails
        resp = get_mock_reply(req.message)
        return resp

@app.get("/")
async def root():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

# Mount the static directory to serve images and other assets
app.mount("/", StaticFiles(directory=BASE_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
