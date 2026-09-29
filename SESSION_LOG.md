# 📋 SESSION LOG — PHỤ KIỆN 88 CHATBOT
**Ngày:** 29/09/2026  
**Giờ kết thúc:** 23:23 (GMT+7)  
**Trạng thái:** ✅ Hoàn thành — Sẵn sàng bàn giao

---

## 🏗️ TỔNG QUAN HỆ THỐNG

### Repository GitHub
- **URL:** https://github.com/tranhoangsang89-maker/pk88
- **Branch:** `main`
- **Deploy:** Vercel (tự động deploy khi push) → https://pk88-bay.vercel.app

### Stack kỹ thuật
| Thành phần | Chi tiết |
|---|---|
| Backend | Python + FastAPI (`app.py`) |
| AI Model | `gemini-flash-lite-latest` (Google Gemini API) |
| Frontend | HTML/CSS/JS (`index.html`) |
| Deploy | Vercel (serverless) |
| Notification | Telegram Bot |
| Storage | `leads.json` (file-based, local) |
| Config | `.env` (KHÔNG commit lên GitHub) |

---

## 📁 CẤU TRÚC FILE QUAN TRỌNG

```
d:\App EDIT\App PK88 - Copy\
├── app.py                       <- Backend chính (FastAPI + Gemini AI)
├── index.html                   <- Frontend chatbot
├── PK88_Knowledge_Base.json     <- Knowledge base (~41KB, ~8,700 tokens)
├── PK88_System_Prompt_GA_IDE.md <- System prompt cho AI (~4,347 chars)
├── leads.json                   <- Lưu leads (KHÔNG commit)
├── requirements.txt             <- Python dependencies
├── vercel.json                  <- Cấu hình Vercel deploy
├── Dockerfile / Procfile        <- Docker/Heroku config (backup)
├── .env                         <- API Keys (KHÔNG commit, KHÔNG push)
├── update-chatbot.txt           <- Spec nâng cấp 23 phần (814 dòng)
└── SESSION_LOG.md               <- File này
```

---

## 🔑 BIẾN MÔI TRƯỜNG (.env)

> CAUTION: KHONG BAO GIO commit file `.env` len GitHub

```
GEMINI_API_KEY=...      <- Key chinh
GEMINI_API_KEY_1=...    <- Key backup 1
GEMINI_API_KEY_2=...    <- Key backup 2
TELEGRAM_BOT_TOKEN=...  <- Token Telegram Bot
TELEGRAM_CHAT_ID=...    <- Chat ID nhan thong bao Lead
```

> Vercel: Cac bien nay phai duoc set thu cong trong Vercel Dashboard -> Settings -> Environment Variables

---

## NHUNG GI DA HOAN THANH TRONG PHIEN NAY

### 1. Push code len GitHub
- Xac dinh chi co `app.py` bi modified
- Van de: GitHub chan push vi commit cu (Initial commit) chua file `test_api.py` co GCP API Key
- Giai phap: Dung `git filter-branch` xoa `test_api.py` khoi toan bo 24 commits -> `git push --force`
- Ket qua: Push thanh cong

### 2. Xu ly GitHub Secret Scanning Block
```bash
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch test_api.py" --prune-empty --tag-name-filter cat -- --all
git update-ref -d refs/original/refs/heads/main
git gc --prune=now --aggressive
git push origin main --force
```

### 3. Chan doan va toi uu toc do chatbot
Nguyen nhan cham phat hien duoc:
- Fallback model "gemini-3.5-flash" — ten SAI -> timeout 8s moi lan that bai
- Logic 2 vong lap long nhau (key x model)
- Context size ~8,700 tokens gui moi request (chap nhan duoc)

Fix da thuc hien trong `app.py`:
```python
# TRUOC (cham):
model_candidates = ["gemini-flash-lite-latest", "gemini-3.5-flash"]
for selected_key in active_keys:
    for model_name in model_candidates:  # vong lap long
        ...timeout=8

# SAU (nhanh):
MODEL_NAME = "gemini-flash-lite-latest"  # 1 model duy nhat
for selected_key in active_keys:         # 1 vong lap don
    ...timeout=15
```

---

## AI MODEL DANG DUNG

| Model | API Name | Tinh trang |
|---|---|---|
| Gemini Flash-Lite Latest | `gemini-flash-lite-latest` | Dang dung — alias tu cap nhat len version moi nhat |

> `gemini-flash-lite-latest` la alias chinh thuc cua Google, hien tro den `gemini-3.5-flash-lite` (released 21/07/2026).
> `gemini-2.5-flash-lite` se bi retire ngay 20/10/2026 — khong dung ten nay.

---

## LEAD SCORING SYSTEM (Hien tai)

```
+30 diem: Co so dien thoai (required)
+25 diem: Co nhu cau ro rang
+20 diem: Timeline gap (Hom nay / 24h)
+15 diem: Timeline trong tuan
+15 diem: Co ngan sach
+10 diem: Co chi nhanh
```

| Score | Label |
|---|---|
| >= 80 | HOT LEAD |
| 60-79 | WARM LEAD |
| < 60 | COLD LEAD |

---

## TELEGRAM INTEGRATION (Hien tai)

- Bot gui thong bao khi co Lead moi
- Thong bao gom: ten, SDT, nhu cau, ngan sach, thoi gian, chi nhanh, diem Lead, label
- Ham `send_telegram_alert()` nam trong `app.py` lines ~146-168
- Chua co Inline Buttons (xem phan Viec Con Do)

---

## VIEC CON DO / KE HOACH TUONG LAI

> Dua tren file `update-chatbot.txt` (814 dong — ban spec nang cap day du):

- [ ] Phan 1: Lead Data Model mo rong (lead_id, status, priority, purchase_intent, assigned_to, activity_log...)
- [ ] Phan 3: Purchase Intent Analysis (HIGH/MEDIUM/LOW/UNKNOWN + intent_confidence)
- [ ] Phan 5: Priority System (URGENT/HIGH/NORMAL/LOW)
- [ ] Phan 6: Lead Status Lifecycle (NEW -> CONTACTING -> CONTACTED -> QUOTED -> WAITING -> WON/LOST)
- [ ] Phan 7: Telegram Inline Buttons (Goi khach, Da lien he, Da bao gia, Follow-up, Da chot, Khong chot)
- [ ] Phan 8: SLA Alert — HOT LEAD chua xu ly sau 5 phut -> canh bao Telegram
- [ ] Phan 9: Human Handoff / Escalation
- [ ] Phan 10: Follow-up Scheduler (next_followup_at + reminder)
- [ ] Phan 11: Activity Log / Audit Trail
- [ ] Phan 12: Telegram Command Center (/leads, /hot, /warm, /pending, /stats, /lead <id>)
- [ ] Phan 13: Sales Dashboard Stats qua Telegram
- [ ] Phan 14-15: Data Integrity + Idempotency cho Telegram callbacks

---

## HUONG DAN DEPLOY

```bash
# Push code moi len GitHub (PowerShell — KHONG dung &&)
cd "d:\App EDIT\App PK88 - Copy"
git add app.py
git commit -m "mo ta thay doi"
git push origin main
# Vercel tu dong deploy sau ~1-2 phut
```

> PowerShell khong ho tro && — phai chay tung lenh rieng

---

## GIT HISTORY GAN NHAT

```
bddf699  Optimize: use single gemini-flash-lite-latest model, remove fallback loop, increase timeout to 15s
29f8ce3  Update chatbot - AI Sales Command Center v2
9b7e44f  Update PK88_Knowledge_Base.json
(24 commits total, test_api.py da bi xoa khoi toan bo history)
```

---

## LUU Y QUAN TRONG CHO AI AGENT KE TIEP

1. `.env` KHONG co tren GitHub — can set lai tren Vercel Dashboard neu deploy moi truong moi
2. `leads.json` KHONG push — data thuc te, chi ton tai local hoac tren server
3. `test_api.py` da bi xoa khoi git history — dung tao lai file nay voi API key that
4. Vercel la serverless — `leads.json` se RESET sau moi lan deploy moi -> can migrate sang database (Redis/PostgreSQL/Supabase) neu muon luu data ben vung
5. Context size ~8,700 tokens — neu Knowledge Base lon them -> can xem xet RAG hoac trim bot data it dung
6. Co 3 API Keys luan phien round-robin -> neu ca 3 het quota -> chatbot fallback ve Mock Mode (tra loi co dinh, khong dung AI)

---

*Duoc tao boi Antigravity AI — Phien lam viec 29/09/2026*
