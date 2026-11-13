# 🏥 MediCare AI — Modern AI-Powered Healthcare Web Platform

**MediCare AI** is a modern, responsive, and ethical healthcare web platform engineered with **HTML, CSS, JavaScript, Python Flask, Google Gemini API, and Supabase Cloud PostgreSQL (with local SQLite fallback)**.

The platform provides evidence-based health guidance, symptom triage, doctor appointment scheduling, medication adherence tracking, localized health awareness articles, and emergency first-aid protocols in **English, Hindi (हिंदी), and Kannada (ಕನ್ನಡ)**.

---

## 🌟 Core Features

- **💬 AI Health Chatbot (Google Gemini API)**: Empathetic, conversational healthcare assistant with clinical guardrails and dynamic multilingual generation in English, Hindi, and Kannada.
- **🔍 Symptom Information Checker**: Interactive triage assessing duration, severity, and age group to generate urgency classifications (*Low, Moderate, High, Emergency*), recommended medical specialties, comfort measures, and questions for doctor consultations.
- **📅 Doctor Appointment Booking**: Directory of verified medical specialists (Cardiology, Pediatrics, Dermatology, General Medicine, Orthopedics, Neurology, Psychiatry, Gynecology) with doctor ratings, consultation fees, and real-time slot booking.
- **⏰ Medicine Reminders & Compliance Tracker**: Daily medication scheduling with dosage tracking, meal relation indicators (*before/after/with food*), mark-taken/skip actions, and adherence score tracking.
- **📊 Patient Health Dashboard**: Unified dashboard aggregating vitals (Blood Pressure, Heart Rate, Fasting Blood Sugar, Weight/BMI), adherence scores, next appointments, and recent symptom assessments.
- **📰 Health Awareness Articles**: Medically reviewed educational articles available in **English, Hindi, and Kannada** with category filters and search.
- **🌐 Trilingual Localization (EN, HI, KN)**: Instant language switching across all UI elements, headings, buttons, forms, and AI outputs.
- **🚨 24/7 Emergency Helplines & First Aid**: Direct SOS dialer for Ambulance (`108`), National Emergency (`112`), Tele-MANAS (`14416`), Maternity (`102`), plus step-by-step interactive First Aid guides (Adult CPR, Heimlich Choking Relief, Severe Bleeding, and Stroke FAST protocol).
- **🔒 Patient Privacy & Non-Diagnosis Guarantee**: MediCare AI strictly presents all AI-generated content as informational guidance only and enforces prominent clinical disclaimers.

---

## 🎨 UI Design System

- **Palette**: Clean clinical White (`#ffffff`), Medical Blue (`#0284c7`, `#0369a1`), and Healthcare Teal (`#0d9488`, `#14b8a6`).
- **Typography**: Inter (Google Fonts) with optimal legibility and accessible color contrast.
- **Responsive**: Fully responsive across mobile, tablet, laptop, and ultra-wide displays.
- **Components**: Glassmorphism navigation, animated emergency pulse alerts, status pills, interactive modals, and non-blocking toast notifications.

---

## 📂 Project Architecture

```
medicare-ai/
├── app.py                          # Main Flask application & REST API router
├── config.py                       # Configuration loader (.env, Supabase, Gemini)
├── db.py                           # Unified database layer (Supabase PostgreSQL & SQLite)
├── ai_service.py                   # Gemini AI integration, prompts, and safety tripwires
├── requirements.txt                # Python dependencies
├── package.json                    # Node.js dependencies for Supabase migration runner
├── .env.example                    # Environment variable template
├── README.md                       # Complete documentation and setup manual
├── scripts/
│   ├── migrate.js                  # Node.js migration runner applying 001_initial_schema.sql
│   └── migrate.py                  # Python migration runner
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql  # Complete PostgreSQL schema, RLS policies, and seed data
├── templates/
│   └── index.html                  # Single-page dashboard web application
└── static/
    ├── css/
    │   └── styles.css              # Modern responsive CSS design system (Blue/Teal/White)
    └── js/
        ├── translations.js         # Complete EN, HI, KN translation dictionary
        ├── api.js                  # Frontend API client
        ├── chatbot.js              # AI Health Chatbot controller
        ├── symptom_checker.js      # Symptom triage assessment controller
        ├── appointments.js         # Doctor booking & filter controller
        ├── reminders.js            # Medicine reminders controller
        ├── articles.js             # Health articles controller
        ├── emergency.js            # Emergency hotlines & first aid controller
        └── app.js                  # Main controller, tab router & language switcher
```

---

## 🗄️ Supabase Cloud PostgreSQL Schema & RLS

The database is built on PostgreSQL with Row Level Security (RLS) enabled on all tables:

1. **`patients`**: User demographics, preferred language, emergency contacts.
2. **`doctors`**: Specialist profiles, hospital affiliations, consultation fees, ratings, available time slots.
3. **`appointments`**: Patient bookings linked to doctors with dates, times, and status.
4. **`medicine_reminders`**: Medication names, dosages, timings, meal relations, and compliance status.
5. **`symptom_assessments`**: Triage assessment logs with severity and urgency scores.
6. **`chat_messages`**: Chat history indexed by session ID.
7. **`health_articles`**: Curated articles in English, Hindi, and Kannada.
8. **`emergency_contacts`**: Verified 24/7 helplines in English, Hindi, and Kannada.
9. **`health_vitals`**: Patient vitals log (Blood Pressure, Heart Rate, Blood Sugar, BMI).

---

## 🚀 Setup & Installation Guide

### 1. Prerequisites
- **Python 3.10+**
- *(Optional)* **Node.js 18+** (for Node migration script)
- A **Google Gemini API Key** (Free tier available at [Google AI Studio](https://aistudio.google.com/app/apikey))
- A free **Supabase Project** (Create at [supabase.com](https://supabase.com))

---

### 2. Clone and Configure Environment

```bash
# Navigate to the project root directory
cd medicare-ai

# Copy the environment template
cp .env.example .env
```

Edit `.env` and fill in your keys:

```ini
# Flask Settings
FLASK_SECRET_KEY=your_secret_session_key
PORT=5000

# Google Gemini API Key
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Supabase Cloud PostgreSQL
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_secret_key

# Supabase PostgreSQL Connection String (Pooler or Direct URI)
# Found in: Supabase Dashboard -> Project Settings -> Database -> Connection string -> URI
SUPABASE_DB_URL=postgresql://postgres.yourprojectid:yourpassword@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
```

> **Note**: If `SUPABASE_DB_URL` is omitted, MediCare AI automatically initializes and runs on a local SQLite database (`medicare.db`) with zero configuration!

---

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Apply Database Migrations to Supabase

You can apply `supabase/migrations/001_initial_schema.sql` to your Supabase Cloud PostgreSQL database using any of the following 3 methods:

#### Method A: Node.js Migration Runner (Service Role Key)
```bash
# Install migration dependencies
npm install

# Run migration
npm run migrate
```

#### Method B: Python Migration Runner
```bash
python scripts/migrate.py
```

#### Method C: Supabase Web Dashboard (Easiest)
1. Go to your **Supabase Project Dashboard**: `https://supabase.com/dashboard`
2. In the left navigation, click on **SQL Editor**.
3. Click **New Query**.
4. Open `supabase/migrations/001_initial_schema.sql`, copy its entire content, paste it into the editor, and click **Run**.
5. All tables, Row Level Security (RLS) policies, and seed data will be created instantly.

---

### 5. Launch the Application

```bash
python app.py
```

Open your browser and navigate to:
```
http://localhost:5000
```

---

## 🌐 Multilingual Support (English, Hindi, Kannada)

| Feature | English | Hindi (हिंदी) | Kannada (ಕನ್ನಡ) |
|---|---|---|---|
| **Chatbot** | Full Gemini reasoning | Fluent Hindi responses | Fluent Kannada responses |
| **Symptom Checker** | Triage report in EN | Triage report in HI | Triage report in KN |
| **Articles** | Native English content | Native Hindi content | Native Kannada content |
| **Emergency Helplines** | English descriptions | Hindi descriptions | Kannada descriptions |
| **UI Labels & Forms** | English | हिन्दी | ಕನ್ನಡ |

Click the language selector in the top-right navbar at any time to switch languages on-the-fly.

---

## 🚨 Emergency Protocols & Helplines

The platform integrates direct click-to-call links (`tel:108`) for national emergency services:
- **108**: Emergency Ambulance & Critical Medical Response
- **112**: National Unified Emergency (Police, Fire, Medical)
- **14416**: Tele-MANAS 24/7 Free Mental Health Counseling
- **102**: Janani Shishu Suraksha Maternity Helpline
- **1091**: Women in Distress Emergency Support
- **1075**: National Health Query Helpline

---

## 🔒 Patient Privacy & Ethical Guardrails

- **Zero Diagnostic Claims**: The AI system prompt strictly forbids asserting medical diagnoses (e.g. *"You have condition X"*). Instead, it frames observations as informational possibilities for consultation with a licensed doctor.
- **No Prescription Authority**: The AI will never prescribe prescription medications, antibiotics, or regulated pharmaceuticals.
- **Emergency Tripwire**: If user input contains acute distress keywords (e.g. crushing chest pain, difficulty breathing, slurred speech, acute trauma), the UI displays high-priority emergency alerts instructing immediate contact with **108** or **112**.
- **Prominent Disclaimers**: Displayed persistently across the top banner, chat responses, symptom checker reports, and the footer.

---

## 🚢 Production Deployment Steps

### Deploy to Render / Railway / Heroku

1. **Push repository to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of MediCare AI"
   git remote add origin https://github.com/your-username/medicare-ai.git
   git push -u origin main
   ```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com) -> **New Web Service**.
   - Connect your GitHub repository.
   - **Environment**: Python 3.
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app` (or `python app.py`)
   - In **Environment Variables**, add:
     - `GEMINI_API_KEY`
     - `SUPABASE_DB_URL`
     - `FLASK_SECRET_KEY`

3. **Deploy on Railway**:
   - Go to [railway.app](https://railway.app) -> **New Project from GitHub**.
   - Add environment variables in the Railway dashboard.
   - Railway will automatically detect Flask and deploy your web service.

---

## 📄 License
This project is licensed under the MIT License.
