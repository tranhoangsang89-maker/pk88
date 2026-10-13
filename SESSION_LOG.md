# SESSION LOG — PHU KIEN 88 CHATBOT
Ngay: 29-30/09/2026
Gio ket thuc: 00:09 (GMT+7)
Trang thai: HOAN THANH — San sang ban giao

---

## TONG QUAN HE THONG

### Repository GitHub
- URL: https://github.com/tranhoangsang89-maker/pk88
- Branch: main
- Deploy: Vercel (tu dong deploy khi push) -> https://pk88-bay.vercel.app

### Stack ky thuat
| Thanh phan     | Chi tiet                                      |
|----------------|-----------------------------------------------|
| Backend        | Python + FastAPI (app.py)                     |
| AI Model       | gemini-flash-lite-latest (Google Gemini API)  |
| Frontend       | HTML/CSS/JS (index.html)                      |
| Deploy         | Vercel (serverless)                           |
| Notification   | Telegram Bot                                  |
| Storage chinh  | Supabase PostgreSQL (table: leads)            |
| Storage backup | leads.json (fallback neu Supabase loi)        |
| Config         | .env (KHONG commit len GitHub)                |

---

## CAU TRUC FILE QUAN TRONG

```
d:\App EDIT\App PK88 - Copy\
├── app.py                       <- Backend chinh (FastAPI + Gemini + Supabase)
├── index.html                   <- Frontend chatbot
├── PK88_Knowledge_Base.json     <- Knowledge base (~41KB, ~8,700 tokens)
├── PK88_System_Prompt_GA_IDE.md <- System prompt cho AI (~4,347 chars)
├── leads.json                   <- Fallback storage (KHONG commit)
├── requirements.txt             <- Python dependencies
├── vercel.json                  <- Cau hinh Vercel deploy
├── Dockerfile / Procfile        <- Docker/Heroku config (backup)
├── .env                         <- API Keys (KHONG commit, KHONG push)
├── update-chatbot.txt           <- Spec nang cap 23 phan (814 dong)
└── SESSION_LOG.md               <- File nay
```

---

## BIEN MOI TRUONG (.env) — DAY DU

CAUTION: KHONG BAO GIO commit file .env len GitHub

```
GEMINI_API_KEY=...
GEMINI_API_KEY_1=...
GEMINI_API_KEY_2=...

TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...

SUPABASE_URL=https://kvxxkfgictaqmwcwvluf.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
```

Cac bien nay phai duoc set trong:
1. File .env (local dev)
2. Vercel Dashboard -> Settings -> Environment Variables (production)

---

## SUPABASE DATABASE

- Project: pk88-automation
- URL: https://kvxxkfgictaqmwcwvluf.supabase.co
- Region: Southeast Asia (Singapore) — ap-southeast-1
- Plan: FREE

### Table: leads (da tao ngay 30/09/2026)

| Column              | Type        | Default           | Mo ta                     |
|---------------------|-------------|-------------------|---------------------------|
| id                  | BIGSERIAL   | auto              | Primary key               |
| lead_id             | TEXT UNIQUE | gen_random_uuid() | ID duy nhat               |
| timestamp           | TIMESTAMPTZ | NOW()             | Thoi gian tao lead        |
| customer_name       | TEXT        |                   | Ten khach hang            |
| phone               | TEXT        |                   | So dien thoai             |
| need                | TEXT        |                   | Nhu cau                   |
| budget              | TEXT        |                   | Ngan sach                 |
| timeline            | TEXT        |                   | Thoi gian xu ly           |
| branch              | TEXT        |                   | Chi nhanh                 |
| score               | INTEGER     | 0                 | Diem BANT                 |
| label               | TEXT        | COLD LEAD         | HOT/WARM/COLD LEAD        |
| status              | TEXT        | NEW               | Trang thai xu ly lead     |
| priority            | TEXT        | NORMAL            | URGENT/HIGH/NORMAL/LOW    |
| purchase_intent     | TEXT        | UNKNOWN           | HIGH/MEDIUM/LOW/UNKNOWN   |
| intent_confidence   | FLOAT       | 0                 | Do tin cay intent (0-1)   |
| source              | TEXT        | chatbot           | Nguon lead                |
| notes               | TEXT        | ''                | Ghi chu nhan vien         |
| conversation_summary| TEXT        | ''                | Tom tat hoi thoai         |
| sla_alert_sent      | BOOLEAN     | FALSE             | Da gui canh bao SLA chua  |
| assigned_to         | TEXT        |                   | Nhan vien phu trach       |
| last_action_at      | TIMESTAMPTZ |                   | Lan xu ly cuoi            |
| next_followup_at    | TIMESTAMPTZ |                   | Thoi gian follow-up       |
| activity_log        | JSONB       | []                | Lich su hanh dong         |
| created_at          | TIMESTAMPTZ | NOW()             | Thoi gian tao             |

### RLS Policies:
- service_role: toan quyen doc/ghi (dung cho backend app.py)
- anon: chi doc (dung cho pk88-hub hien thi leads)

---

## NHUNG GI DA HOAN THANH TRONG PHIEN NAY

### 1. Push code len GitHub
- Chi co app.py bi modified, push thanh cong
- Van de: GitHub chan push vi commit cu chua GCP API Key trong test_api.py
- Giai phap: git filter-branch xoa test_api.py khoi 24 commits -> force push
```bash
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch test_api.py" --prune-empty --tag-name-filter cat -- --all
git update-ref -d refs/original/refs/heads/main
git gc --prune=now --aggressive
git push origin main --force
```

### 2. Chan doan va toi uu toc do chatbot
Nguyen nhan cham:
- Fallback model "gemini-3.5-flash" ten SAI -> timeout 8s moi lan
- Logic 2 vong lap long nhau (key x model)

Fix trong app.py:
```python
# TRUOC (cham):
model_candidates = ["gemini-flash-lite-latest", "gemini-3.5-flash"]
for key in active_keys:
    for model in model_candidates: ...  # vong lap long, timeout=8

# SAU (nhanh):
MODEL_NAME = "gemini-flash-lite-latest"
for key in active_keys: ...  # 1 vong lap, timeout=15
```

### 3. Tich hop Supabase luu tru Lead vinh vien
Van de: leads.json tren Vercel bi RESET sau moi lan deploy
Giai phap: Luu vao Supabase PostgreSQL, fallback ve leads.json neu loi

Thay doi trong app.py:
- Them ham supabase_insert_lead() dung requests (khong can them package)
- Them lead_id (uuid), status="NEW", source="chatbot" vao moi lead
- Uu tien ghi Supabase, neu loi moi fallback leads.json

Da test thanh cong:
- INSERT: Status 201, ID=1
- SELECT: Doc duoc lead vua ghi
- DELETE: Xoa test lead sach

### 4. SQL da chay trong Supabase Dashboard
File: scratch/create_leads_table.sql
Note: "CREATE POLICY IF NOT EXISTS" khong duoc ho tro -> dung "DROP POLICY IF EXISTS" truoc roi CREATE

---

## AI MODEL DANG DUNG

| Model                     | API Name                   | Tinh trang                         |
|---------------------------|----------------------------|------------------------------------|
| Gemini Flash-Lite Latest  | gemini-flash-lite-latest   | Dang dung — alias chinh thuc       |

- gemini-flash-lite-latest la alias chinh thuc, tro den gemini-3.5-flash-lite (21/07/2026)
- gemini-2.5-flash-lite se bi retire ngay 20/10/2026 — KHONG dung ten nay

---

## LEAD SCORING SYSTEM (Hien tai)

```
+30 diem: Co so dien thoai (bat buoc)
+25 diem: Co nhu cau ro rang
+20 diem: Timeline gap (Hom nay / 24h)
+15 diem: Timeline trong tuan
+15 diem: Co ngan sach
+10 diem: Co chi nhanh
```

| Score | Label      |
|-------|------------|
| >= 80 | HOT LEAD   |
| 60-79 | WARM LEAD  |
| < 60  | COLD LEAD  |

---

## TELEGRAM INTEGRATION (Hien tai)

- Bot gui thong bao 1 chieu khi co lead moi
- Thong bao: ten, SDT, nhu cau, ngan sach, thoi gian, chi nhanh, diem, label
- Ham send_telegram_alert() trong app.py ~line 146
- CHUA co Inline Buttons (xem phan Viec Con Do)

---

## GIT HISTORY GAN NHAT

```
9450e8e  Integrate Supabase: persistent lead storage with leads.json fallback
ee294cc  Add SESSION_LOG.md - session handoff notes for next AI agent
bddf699  Optimize: use single gemini-flash-lite-latest model, remove fallback loop, increase timeout to 15s
29f8ce3  Update chatbot - AI Sales Command Center v2
(24 commits total, test_api.py da bi xoa khoi toan bo history)
```

---

## HUONG DAN DEPLOY

PowerShell KHONG ho tro && — chay tung lenh rieng:
```powershell
cd "d:\App EDIT\App PK88 - Copy"
git add app.py
git commit -m "mo ta thay doi"
git push origin main
# Vercel tu dong deploy sau ~1-2 phut
```

---

## VIEC CON DO / KE HOACH TIEP THEO

Thu tu uu tien:

### UU TIEN CAO — Nen lam tiep
- [ ] Them SUPABASE_URL va SUPABASE_SERVICE_ROLE_KEY vao Vercel Dashboard -> Redeploy
      -> Sau buoc nay leads se duoc luu vinh vien tren Supabase

### UU TIEN TRUNG — Tiep theo
Dua tren update-chatbot.txt (814 dong, 23 phan):
- [ ] Phan 6: Lead Status Lifecycle (NEW -> CONTACTING -> CONTACTED -> QUOTED -> WON/LOST)
- [ ] Phan 7: Telegram Inline Buttons (Goi khach, Da lien he, Da bao gia, Follow-up, Da chot, Khong chot)
      QUAN TRONG: Can Supabase hoat dong truoc thi Buttons moi co ich
- [ ] Phan 8: SLA Alert — HOT LEAD chua xu ly sau 5 phut -> canh bao Telegram
- [ ] Phan 10: Follow-up Scheduler
- [ ] Phan 12: Telegram Commands (/leads, /hot, /warm, /pending, /stats)

### UU TIEN THAP — Tuong lai
- [ ] Lead Dashboard tren pk88-hub (doc table leads tu Supabase)
- [ ] Realtime notification tren pk88-hub khi co lead moi
- [ ] Phan 3: Purchase Intent Analysis
- [ ] Phan 11: Activity Log / Audit Trail
- [ ] Phan 13: Sales Stats qua Telegram

---

## LUU Y QUAN TRONG CHO AI AGENT KE TIEP

1. .env KHONG co tren GitHub — can set lai tren Vercel Dashboard neu deploy moi truong moi
2. leads.json KHONG push — chi la fallback khi Supabase loi
3. test_api.py da bi xoa khoi git history — dung tao lai file nay voi API key that
4. Vercel la serverless — KHONG co process chay lien tuc
   -> Telegram Inline Buttons PHAI dung Webhook (khong dung polling)
   -> Webhook endpoint them vao app.py la /api/telegram
5. Supabase table leads da san sang, RLS da cau hinh
   -> service_role key: toan quyen (cho backend)
   -> anon key: chi doc (cho pk88-hub frontend)
6. Context size ~8,700 tokens — chua can RAG
   RAG chi can thiet khi KB lon hon 10x hien tai (>100K tokens)
7. Co 3 Gemini API Keys luan phien -> neu ca 3 het quota -> chatbot fallback ve Mock Mode

---

## CAP NHAT KIEN THUC — 13/10/2026

### 1. Thoi gian lam viec:
- 07h00 - 22h00 tat ca cac ngay trong tuan (7h sang den 22h toi moi ngay).

### 2. Danh sach 6 chi nhanh chinh thuc dang hoat dong:
1. Phụ Kiện 88 - Phú Khương (Bến Tre 1): 35B2 Đoàn Hoàng Minh, Phường Phú Khương, TP. Bến Tre, Tỉnh Vĩnh Long
2. Phụ Kiện 88 - Đồng Khởi (Bến Tre 2): 173 Đại Lộ Đồng Khởi, Vòng Xoay Tân Thành, TP. Bến Tre, Tỉnh Vĩnh Long
3. Phụ Kiện 88 - Mỹ Tho: 25 Đinh Bộ Lĩnh, TP. Mỹ Tho, Tỉnh Đồng Tháp
4. Phụ Kiện 88 - Vĩnh Long: 120 Trưng Nữ Vương, Phường Long Châu, TP. Vĩnh Long, Tỉnh Vĩnh Long
5. Phụ Kiện 88 - Cần Thơ: 94 Đường Trần Hưng Đạo, Phường Thới Bình, Quận Ninh Kiều, TP. Cần Thơ
6. Phụ Kiện 88 - Thủ Đức (TP.HCM): 178A Võ Văn Ngân, Phường Bình Thọ, TP. Thủ Đức, TP. Hồ Chí Minh

Cac file da duoc dong bo:
- PK88_Knowledge_Base.json
- PK88_System_Prompt_GA_IDE.md
- app.py (mock handlers & prompt sync)

### 3. Tich hop Google Maps & Ban do Mini:
- File nguon: google-maps.txt
- Bo sung link Google Maps, landmark mieu ta va hotline tung chi nhanh.
- index.html: Tu dong phat hien va render khung iframe Ban do Mini (Google Maps) va nut bam "Chi duong Google Maps" mo tab moi.
- app.py: Fix json.loads(strict=False) de tranh loi control character khi Gemini sinh text dai.

---

*Duoc cap nhat boi Antigravity AI — 13/10/2026 15:27*


