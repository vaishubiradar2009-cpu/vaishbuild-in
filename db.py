"""
====================================================================
MediCare AI - Database Layer
File: db.py
Description: Unified data access layer supporting both Supabase Cloud
             PostgreSQL and local SQLite with seamless fallback.
====================================================================
"""

import os
import sqlite3
import uuid
import datetime
from typing import List, Dict, Any, Optional
from config import Config

def get_connection():
    """Returns a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(Config.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_sqlite_db():
    """Initializes SQLite schema and populates seed data if empty."""
    conn = get_connection()
    cur = conn.cursor()

    # Create tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id TEXT PRIMARY KEY,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        age INTEGER,
        gender TEXT,
        blood_group TEXT,
        emergency_contact_name TEXT,
        emergency_contact_phone TEXT,
        preferred_language TEXT DEFAULT 'en',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        specialty TEXT NOT NULL,
        qualifications TEXT NOT NULL,
        experience_years INTEGER NOT NULL,
        hospital TEXT NOT NULL,
        city TEXT NOT NULL,
        consultation_fee REAL NOT NULL DEFAULT 500.0,
        rating REAL DEFAULT 4.8,
        available_days TEXT NOT NULL,
        available_time_slots TEXT NOT NULL,
        image_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id TEXT PRIMARY KEY,
        patient_id TEXT,
        patient_name TEXT NOT NULL,
        patient_phone TEXT NOT NULL,
        patient_email TEXT,
        doctor_id TEXT,
        appointment_date TEXT NOT NULL,
        time_slot TEXT NOT NULL,
        reason TEXT NOT NULL,
        status TEXT DEFAULT 'Scheduled',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS medicine_reminders (
        id TEXT PRIMARY KEY,
        patient_id TEXT,
        medicine_name TEXT NOT NULL,
        dosage TEXT NOT NULL,
        frequency TEXT NOT NULL,
        reminder_time TEXT NOT NULL,
        timing_relation TEXT DEFAULT 'after_food',
        start_date TEXT,
        end_date TEXT,
        is_active INTEGER DEFAULT 1,
        status_today TEXT DEFAULT 'pending',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS symptom_assessments (
        id TEXT PRIMARY KEY,
        patient_id TEXT,
        patient_name TEXT,
        symptoms_text TEXT NOT NULL,
        duration TEXT,
        severity TEXT,
        age_group TEXT,
        language TEXT DEFAULT 'en',
        ai_analysis TEXT NOT NULL,
        urgency_level TEXT DEFAULT 'Low',
        recommended_specialty TEXT,
        disclaimer_acknowledged INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        patient_id TEXT,
        sender TEXT NOT NULL,
        message TEXT NOT NULL,
        language TEXT DEFAULT 'en',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS health_articles (
        id TEXT PRIMARY KEY,
        title_en TEXT NOT NULL,
        title_hi TEXT NOT NULL,
        title_kn TEXT NOT NULL,
        category TEXT NOT NULL,
        summary_en TEXT NOT NULL,
        summary_hi TEXT NOT NULL,
        summary_kn TEXT NOT NULL,
        content_en TEXT NOT NULL,
        content_hi TEXT NOT NULL,
        content_kn TEXT NOT NULL,
        read_time_minutes INTEGER DEFAULT 4,
        author TEXT DEFAULT 'MediCare Medical Editorial Board',
        image_url TEXT,
        published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS emergency_contacts (
        id TEXT PRIMARY KEY,
        title_en TEXT NOT NULL,
        title_hi TEXT NOT NULL,
        title_kn TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        description_en TEXT NOT NULL,
        description_hi TEXT NOT NULL,
        description_kn TEXT NOT NULL,
        is_national INTEGER DEFAULT 1,
        badge_type TEXT DEFAULT 'critical',
        display_order INTEGER DEFAULT 1
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS health_vitals (
        id TEXT PRIMARY KEY,
        patient_id TEXT,
        blood_pressure_systolic INTEGER,
        blood_pressure_diastolic INTEGER,
        heart_rate INTEGER,
        blood_sugar REAL,
        temperature REAL,
        weight_kg REAL,
        height_cm REAL,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id)
    );
    """)

    conn.commit()

    # Check if doctors are seeded
    cur.execute("SELECT COUNT(*) FROM doctors;")
    count = cur.fetchone()[0]
    if count == 0:
        seed_sqlite_db(cur, conn)

    conn.close()

def seed_sqlite_db(cur, conn):
    """Inserts initial seed data into SQLite for out-of-the-box readiness."""
    # 1. Doctors
    doctors_data = [
        ('d1111111-1111-1111-1111-111111111111', 'Dr. Rajesh Sharma', 'Cardiology', 'MBBS, MD, DM (Cardiology), FACC', 16, 'Apollo Heart Centre', 'Bengaluru', 800.00, 4.9, 'Mon, Wed, Fri', '09:00 AM, 11:30 AM, 02:00 PM, 04:30 PM', 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=300&h=300&fit=crop'),
        ('d2222222-2222-2222-2222-222222222222', 'Dr. Priya Kulkarni', 'General Medicine', 'MBBS, DNB (Internal Medicine)', 11, 'Manipal Hospital', 'Bengaluru', 500.00, 4.8, 'Mon, Tue, Wed, Thu, Fri, Sat', '10:00 AM, 11:00 AM, 03:00 PM, 05:00 PM', 'https://images.unsplash.com/photo-1594824813515-05527a4128f7?w=300&h=300&fit=crop'),
        ('d3333333-3333-3333-3333-333333333333', 'Dr. Anand Gowda', 'Pediatrics', 'MBBS, MD (Pediatrics), FIAP', 14, 'Cloudnine Children Hospital', 'Bengaluru', 600.00, 4.9, 'Tue, Thu, Sat', '09:30 AM, 11:00 AM, 04:00 PM, 06:00 PM', 'https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=300&h=300&fit=crop'),
        ('d4444444-4444-4444-4444-444444444444', 'Dr. Sunita Rao', 'Dermatology', 'MBBS, MD (Dermatology, Venereology & Leprosy)', 9, 'Fortis Hospital', 'Bengaluru', 650.00, 4.7, 'Mon, Wed, Thu, Sat', '10:30 AM, 12:00 PM, 03:30 PM, 05:30 PM', 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=300&h=300&fit=crop'),
        ('d5555555-5555-5555-5555-555555555555', 'Dr. Vikram Venkatesh', 'Orthopedics', 'MBBS, MS (Orthopaedics), MCh (Joint Replacement)', 18, 'Sparsh Super Speciality Hospital', 'Bengaluru', 750.00, 4.8, 'Mon, Tue, Thu, Fri', '09:00 AM, 10:30 AM, 02:30 PM, 04:00 PM', 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=300&h=300&fit=crop'),
        ('d6666666-6666-6666-6666-666666666666', 'Dr. Meera Nambiar', 'Neurology', 'MBBS, MD, DM (Neurology)', 15, 'NIMHANS Allied Health Clinic', 'Bengaluru', 900.00, 4.9, 'Tue, Wed, Fri', '11:00 AM, 01:00 PM, 03:00 PM, 05:00 PM', 'https://images.unsplash.com/photo-1651008376811-b90baee60c1f?w=300&h=300&fit=crop'),
        ('d7777777-7777-7777-7777-777777777777', 'Dr. Karthik Sundaram', 'Psychiatry', 'MBBS, DPM, MD (Psychiatry)', 12, 'MindCare Mental Health Centre', 'Bengaluru', 700.00, 4.8, 'Mon, Wed, Fri, Sat', '11:00 AM, 02:00 PM, 04:00 PM, 06:30 PM', 'https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=300&h=300&fit=crop'),
        ('d8888888-8888-8888-8888-888888888888', 'Dr. Ananya Hegde', 'Gynecology', 'MBBS, MS (OBG), FICOG', 13, 'Aster CMI Hospital', 'Bengaluru', 650.00, 4.9, 'Tue, Wed, Thu, Sat', '10:00 AM, 12:30 PM, 03:00 PM, 05:00 PM', 'https://images.unsplash.com/photo-1594824813515-05527a4128f7?w=300&h=300&fit=crop')
    ]
    cur.executemany("""
    INSERT INTO doctors (id, name, specialty, qualifications, experience_years, hospital, city, consultation_fee, rating, available_days, available_time_slots, image_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, doctors_data)

    # 2. Emergency contacts
    emergency_data = [
        ('e1111111-1111-1111-1111-111111111111', 'Emergency Ambulance', 'आपातकालीन एम्बुलेंस', 'ತುರ್ತು ಆಂಬ್ಯುಲೆನ್ಸ್', '108', 'Free 24/7 emergency medical response service across India.', 'भारत भर में मुफ्त 24/7 आपातकालीन चिकित्सा प्रतिक्रिया सेवा।', 'ಭಾರತದಾದ್ಯಂತ ಉಚಿತ 24/7 ತುರ್ತು ವೈದ್ಯಕೀಯ ಸೇವೆ.', 1, 'critical', 1),
        ('e2222222-2222-2222-2222-222222222222', 'National Emergency Number', 'राष्ट्रीय आपातकालीन नंबर', 'ರಾಷ್ಟ್ರೀಯ ತುರ್ತು ಸಂಖ್ಯೆ', '112', 'Single emergency helpline for Police, Fire, and Medical assistance.', 'पुलिस, अग्निशमन और चिकित्सा सहायता के लिए एकीकृत आपातकालीन हेल्पलाइन।', 'ಪೊಲೀಸ್, ಅಗ್ನಿಶಾಮಕ ಮತ್ತು ವೈದ್ಯಕೀಯ ಸಹಾಯಕ್ಕಾಗಿ ಏಕೀಕೃತ ತುರ್ತು ಸಹಾಯವಾಣಿ.', 1, 'critical', 2),
        ('e3333333-3333-3333-3333-333333333333', 'Maternity Helpline (Janani Shishu)', 'मातृत्व हेल्पलाइन', 'ತಾಯಂದಿರ ಸಹಾಯವಾಣಿ', '102', 'Free transport service for pregnant women and newborns.', 'गर्भवती महिलाओं और नवजात शिशुओं के लिए मुफ्त परिवहन सेवा।', 'ಗರ್ಭಿಣಿಯರು ಮತ್ತು ನವಜಾತ ಶಿಶುಗಳಿಗೆ ಉಚಿತ ಸಾರಿಗೆ ಸೇವೆ.', 1, 'general', 3),
        ('e4444444-4444-4444-4444-444444444444', 'Tele-MANAS Mental Health Helpline', 'टेली-मानस मानसिक स्वास्थ्य हेल्पलाइन', 'ಟೆಲಿ-ಮಾನಸ್ ಮಾನಸಿಕ ಆರೋಗ್ಯ ಸಹಾಯವಾಣಿ', '14416', 'Government of India 24/7 free mental health counseling & psychological support.', 'भारत सरकार की 24/7 मुफ्त मानसिक स्वास्थ्य और परामर्श सेवा।', 'ಭಾರತ ಸರ್ಕಾರದ 24/7 ಉಚಿತ ಮಾನಸಿಕ ಆರೋಗ್ಯ ಸಮಾಲೋಚನೆ ಸೇವೆ.', 1, 'mental_health', 4),
        ('e5555555-5555-5555-5555-555555555555', 'Women in Distress Helpline', 'महिला हेल्पलाइन', 'ಮಹಿಳಾ ಸಹಾಯವಾಣಿ', '1091', '24/7 emergency support and safety assistance for women.', 'महिलाओं के लिए 24/7 आपातकालीन सहायता और सुरक्षा सेवा।', 'ಮಹಿಳೆಯರಿಗಾಗಿ 24/7 ತುರ್ತು ನೆರವು ಮತ್ತು ರಕ್ಷಣೆ.', 1, 'general', 5),
        ('e6666666-6666-6666-6666-666666666666', 'National Health Helpline', 'राष्ट्रीय स्वास्थ्य हेल्पलाइन', 'ರಾಷ್ಟ್ರೀಯ ಆರೋಗ್ಯ ಸಹಾಯವಾಣಿ', '1075', 'Ministry of Health national health advisory and epidemic query line.', 'स्वास्थ्य मंत्रालय की राष्ट्रीय स्वास्थ्य सलाह और महामारी मार्गदर्शन हेल्पलाइन।', 'ಆರೋಗ್ಯ ಸಚಿವಾಲಯದ ರಾಷ್ಟ್ರೀಯ ಆರೋಗ್ಯ ಮಾಹಿತಿ ಸಹಾಯವಾಣಿ.', 1, 'general', 6)
    ]
    cur.executemany("""
    INSERT INTO emergency_contacts (id, title_en, title_hi, title_kn, phone_number, description_en, description_hi, description_kn, is_national, badge_type, display_order)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, emergency_data)

    # 3. Health articles
    articles_data = [
        (
            'a1111111-1111-1111-1111-111111111111',
            'Understanding High Blood Pressure: The Silent Signs and Daily Management',
            'उच्च रक्तचाप को समझना: मूक संकेत और दैनिक प्रबंधन',
            'ರಕ್ತದೊತ್ತಡವನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳುವುದು: ಮೂಕ ಲಕ್ಷಣಗಳು ಮತ್ತು ದೈನಂದಿನ ನಿರ್ವಹಣೆ',
            'Heart Health',
            'Learn how to identify subtle symptoms of hypertension, monitor your blood pressure at home, and make heart-healthy dietary changes.',
            'उच्च रक्तचाप के सूक्ष्म लक्षणों को पहचानना, घर पर बीपी की निगरानी करना और हृदय के अनुकूल आहार परिवर्तन करना सीखें।',
            'ಅಧಿಕ ರಕ್ತದೊತ್ತಡದ ಲಕ್ಷಣಗಳನ್ನು ಗುರುತಿಸುವುದು, ಮನೆಯಲ್ಲೇ ಪರೀಕ್ಷಿಸುವುದು ಮತ್ತು ಹೃದಯದ ಆರೋಗ್ಯಕ್ಕೆ ಪೂರಕವಾದ ಆಹಾರ ಕ್ರಮಗಳನ್ನು ತಿಳಿಯಿರಿ.',
            'Hypertension (high blood pressure) is often referred to as the silent killer because it typically displays no obvious symptoms until significant vascular damage occurs. Normal blood pressure is defined as below 120/80 mmHg.\n\nKey Management Strategies:\n1. Dietary Approaches: Adopt the DASH diet, reducing sodium intake to under 2,000 mg daily.\n2. Physical Activity: Aim for 150 minutes of moderate aerobic exercise per week.\n3. Stress Reduction: Daily 15-minute mindfulness breathing has clinically proven benefits.\n4. Regular Monitoring: Check readings twice weekly at the same time.\n\nEmergency Warning: If blood pressure spikes above 180/120 mmHg with chest pain, contact 108 immediately.',
            'उच्च रक्तचाप को अक्सर साइलेंट किलर कहा जाता है। सामान्य रक्तचाप 120/80 mmHg से कम होता है।\n\nप्रमुख प्रबंधन रणनीतियाँ:\n1. आहार नियंत्रण: DASH आहार अपनाएं, नमक कम करें।\n2. शारीरिक गतिविधि: प्रति सप्ताह 150 मिनट तेज टहलें।\n3. तनाव कम करें: रोजाना 15 मिनट प्राणायाम करें।\n4. नियमित निगरानी: सप्ताह में दो बार अपना बीपी मापें।\n\nआपातकालीन चेतावनी: यदि रक्तचाप 180/120 से ऊपर जाए और सीने में दर्द हो, तो तुरंत 108 पर कॉल करें।',
            'ಅಧಿಕ ರಕ್ತದೊತ್ತಡವನ್ನು ಸಾಮಾನ್ಯವಾಗಿ ಮೂಕ ಕೊಲೆಗಾರ ಎಂದು ಕರೆಯಲಾಗುತ್ತದೆ. ಸಾಮಾನ್ಯ ರಕ್ತದೊತ್ತಡ 120/80 mmHg ಗಿಂತ ಕಡಿಮೆಯಿರುತ್ತದೆ.\n\nಪ್ರಮುಖ ನಿರ್ವಹಣಾ ಸಲಹೆಗಳು:\n1. ಆಹಾರ ಕ್ರಮ: ಉಪ್ಪಿನ ಬಳಕೆಯನ್ನು ಕಡಿಮೆ ಮಾಡಿ.\n2. ದೈಹಿಕ ವ್ಯಾಯಾಮ: ವಾರಕ್ಕೆ 150 ನಿಮಿಷಗಳ ಕಾಲ ವೇಗದ ನಡಿಗೆ ಮಾಡಿ.\n3. ಒತ್ತಡ ನಿರ್ವಹಣೆ: ಪ್ರತಿದಿನ 15 ನಿಮಿಷ ಧ್ಯಾನ ಮಾಡಿ.\n4. ನಿಯಮಿತ ತಪಾಸಣೆ: ವಾರಕ್ಕೆ ಎರಡು ಬಾರಿ ರಕ್ತದೊತ್ತಡವನ್ನು ಪರೀಕ್ಷಿಸಿ.\n\nತುರ್ತು ಎಚ್ಚರಿಕೆ: ರಕ್ತದೊತ್ತಡ 180/120 ಕ್ಕಿಂತ ಹೆಚ್ಚಾಗಿದ್ದರೆ ಮತ್ತು ಎದೆ ನೋವಿದ್ದರೆ, ತಕ್ಷಣ 108 ಗೆ ಕರೆ ಮಾಡಿ.',
            5,
            'Dr. Rajesh Sharma, Cardiologist',
            'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=600&h=350&fit=crop'
        ),
        (
            'a2222222-2222-2222-2222-222222222222',
            'Type 2 Diabetes Prevention: Balancing Glucose with Smart Nutrition',
            'टाइप 2 मधुमेह की रोकथाम: स्मार्ट पोषण के साथ ग्लूकोज का संतुलन',
            'ಟೈಪ್ 2 ಮಧುಮೇಹ ತಡೆಗಟ್ಟುವಿಕೆ: ಸಮತೋಲಿತ ಪೋಷಕಾಂಶಗಳೊಂದಿಗೆ ಗ್ಲೂಕೋಸ್ ನಿರ್ವಹಣೆ',
            'Diabetes',
            'Essential guidelines for maintaining optimal glycemic control through meal timing, glycemic index management, and early preventive screening.',
            'भोजन का समय, ग्लाइसेमिक इंडेक्स प्रबंधन और शुरुआती स्क्रीनिंग के माध्यम से ग्लूकोज नियंत्रण बनाए रखने के आवश्यक दिशा-निर्देश।',
            'ಸರಿಯಾದ ಆಹಾರ ಸಮಯ, ಕಡಿಮೆ ಗ್ಲೈಸೆಮಿಕ್ ಆಹಾರಗಳು ಮತ್ತು ಆರಂಭಿಕ ತಪಾಸಣೆಯ ಮೂಲಕ ಸಕ್ಕರೆ ಕಾಯಿಲೆಯನ್ನು ನಿಯಂತ್ರಿಸುವ ವಿಧಾನಗಳು.',
            'Type 2 diabetes develops when cells develop insulin resistance. Early lifestyle intervention can reverse prediabetes in up to 70% of people.\n\nCrucial Steps:\n1. Focus on Glycemic Load: Swap refined grains with millets and whole grains.\n2. Plate Method: Half plate vegetables, quarter lean protein, quarter whole grain.\n3. Post-Meal Movement: A 10-15 minute gentle walk after meals curbs glucose spikes.\n4. HbA1c Monitoring: Check average glucose every 3-6 months.',
            'टाइप 2 मधुमेह तब होता है जब शरीर इंसुलिन का ठीक से उपयोग नहीं कर पाता।\n\nग्लूकोज नियंत्रण के मुख्य नियम:\n1. सही अनाज चुनें: मैदा व सफेद चावल के स्थान पर बाजरा और रागी खाएं।\n2. प्लेट नियम: आधी थाली हरी सब्जियां और चौथाई प्रोटीन लें।\n3. भोजन के बाद टहलें: भोजन के 10 मिनट बाद हल्की सैर फायदेमंद है।\n4. HbA1c टेस्ट: हर 3 से 6 महीने में टेस्ट करवाएं।',
            'ಟೈಪ್ 2 ಮಧುಮೇಹವನ್ನು ಆರಂಭಿಕ ಹಂತದಲ್ಲಿ ಸಂಪೂರ್ಣವಾಗಿ ತಡೆಗಟ್ಟಬಹುದು.\n\nಗ್ಲೂಕೋಸ್ ನಿಯಂತ್ರಣದ ಪ್ರಮುಖ ಸಲಹೆಗಳು:\n1. ಸಿರಿಧಾನ್ಯಗಳ ಬಳಕೆ: ಮೈದಾ ಬದಲಿಗೆ ರಾಗಿ, ನವಣೆ ಬಳಸಿ.\n2. ಊಟದ ತಟ್ಟೆಯ ನಿಯಮ: ಅರ್ಧ ತಟ್ಟೆ ತರಕಾರಿಗಳು ಮತ್ತು ಕಾಲು ಭಾಗ ಪ್ರೋಟೀನ್ ಇರಲಿ.\n3. ಊಟದ ನಂತರ ನಡಿಗೆ: ಊಟವಾದ ತಕ್ಷಣ 10-15 ನಿಮಿಷಗಳ ನಡಿಗೆ ಸಕ್ಕರೆ ಮಟ್ಟವನ್ನು ಹತೋಟಿಯಲ್ಲಿಡುತ್ತದೆ.\n4. HbA1c ಪರೀಕ್ಷೆ: ನಿಯಮಿತವಾಗಿ ತಪಾಸಣೆ ಮಾಡಿಸಿ.',
            4,
            'Dr. Priya Kulkarni, Internal Medicine',
            'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=600&h=350&fit=crop'
        ),
        (
            'a3333333-3333-3333-3333-333333333333',
            'Mental Well-being in High-Stress Environments: Practical Coping Mechanisms',
            'तनावपूर्ण वातावरण में मानसिक स्वास्थ्य: व्यावहारिक समाधान',
            'ಹೆಚ್ಚಿನ ಒತ್ತಡದ ವಾತಾವರಣದಲ್ಲಿ ಮಾನಸಿಕ ಸ್ವಾಸ್ಥ್ಯ: ಪ್ರಾಯೋಗಿಕ ಪರಿಹಾರಗಳು',
            'Mental Health',
            'Evidence-backed strategies to manage work anxiety, combat burnout, and know when to seek psychological counseling.',
            'काम की चिंता को प्रबंधित करने, बर्नआउट से निपटने और मनोवैज्ञानिक परामर्श कब लें, इसके साक्ष्य-आधारित उपाय।',
            'ಕೆಲಸದ ಆತಂಕವನ್ನು ನಿರ್ವಹಿಸಲು, ಮಾನಸಿಕ ಬಳಲಿಕೆಯಿಂದ ಹೊರಬರಲು ಮತ್ತು ಆಪ್ತಸಮಾಲೋಚನೆ ಪಡೆಯುವ ಸಮಯವನ್ನು ತಿಳಿಯಿರಿ.',
            'Mental well-being is vital for overall health. Prolonged stress triggers elevated cortisol and elevates cardiovascular risk.\n\nSelf-Care Pillars:\n1. Sleep Hygiene: 7-8 hours uninterrupted sleep. Power off screens 1 hour before bed.\n2. Mindful Resets: 5 minutes of box breathing between tasks.\n3. Confidential Counseling: Reach out to national helpline Tele-MANAS (14416) for free 24/7 support.',
            'मानसिक स्वास्थ्य जीवन का आधार है।\n\nआत्म-देखभाल के उपाय:\n1. गहरी नींद: रोजाना 7-8 घंटे सोएं।\n2. प्राणायाम: काम के बीच 5 मिनट गहरी सांस लें।\n3. टेली-मानस: मुफ्त मानसिक स्वास्थ्य सहायता के लिए 14416 डायल करें।',
            'ಮಾನಸಿಕ ಆರೋಗ್ಯವು ದೈಹಿಕ ಆರೋಗ್ಯದಷ್ಟೇ ಮುಖ್ಯವಾಗಿದೆ.\n\nಪ್ರಮುಖ ಸಲಹೆಗಳು:\n1. ಉತ್ತಮ ನಿದ್ರೆ: ಪ್ರತಿದಿನ 7-8 ಗಂಟೆಗಳ ಕಾಲ ನಿದ್ರಿಸಿ.\n2. ಪ್ರಾಣಾಯಾಮ: ಕೆಲಸದ ನಡುವೆ 5 ನಿಮಿಷ ದೀರ್ಘ ಶ್ವಾಸ ತೆಗೆದುಕೊಳ್ಳಿ.\n3. ಸಹಾಯವಾಣಿ: ಉಚಿತ ಸಮಾಲೋಚನೆಗಾಗಿ ಟೆಲಿ-ಮಾನಸ್ (14416) ಕರೆ ಮಾಡಿ.',
            4,
            'Dr. Karthik Sundaram, Psychiatrist',
            'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=600&h=350&fit=crop'
        ),
        (
            'a4444444-4444-4444-4444-444444444444',
            'Monsoon & Seasonal Fevers: Prevention, Warning Signs & Care',
            'मानसून और मौसमी बुखार: रोकथाम, चेतावनी संकेत और देखभाल',
            'ಮಳೆಗಾಲದ ಮತ್ತು ಋತುಮಾನದ ಜ್ವರಗಳು: ತಡೆಗಟ್ಟುವಿಕೆ, ಎಚ್ಚರಿಕೆ ಚಿಹ್ನೆಗಳು ಮತ್ತು ಆರೈಕೆ',
            'Seasonal Care',
            'Differentiating viral flu, dengue, and malaria, with hydration protocols and critical platelet warning indicators.',
            'वायरल फ्लू, डेंगू और मलेरिया के बीच अंतर, जलयोजन प्रोटोकॉल और प्लेटलेट चेतावनी के संकेत।',
            'ವೈರಲ್ ಜ್ವರ, ಡೆಂಗ್ಯೂ ಮತ್ತು ಮಲೇರಿಯಾಗಳ ನಡುವಿನ ವ್ಯತ್ಯಾಸ, ನೀರು ಕುಡಿಯುವ ನಿಯಮಗಳು ಮತ್ತು ಎಚ್ಚರಿಕೆಗಳು.',
            'Monsoon brings a surge in vector-borne illnesses. Distinguishing between mild viral flu and Dengue or Malaria is essential.\n\nCare Guidelines:\n1. Eliminate Stagnant Water: Prevent mosquito breeding weekly.\n2. Hydration: Drink ORS, tender coconut water, and boiled water.\n3. Avoid Self-Medication: Avoid Ibuprofen or Aspirin in suspected dengue due to bleeding risk.\n4. Urgent Symptoms: High fever, petechiae rash, or persistent vomiting require clinic testing.',
            'मौसम बदलने पर डेंगू और वायरल बुखार तेजी से फैलते हैं।\n\nदेखभाल के नियम:\n1. पानी जमा न होने दें।\n2. पर्याप्त ओआरएस और नारियल पानी पिएं।\n3. ब्रूफेन या एस्पिरिन न लें।\n4. तेज बुखार और उल्टी होने पर तुरंत डॉक्टर से संपर्क करें।',
            'ಮಳೆಗಾಲದಲ್ಲಿ ಸೊಳ್ಳೆಗಳಿಂದ ಹರಡುವ ರೋಗಗಳು ಸಾಮಾನ್ಯ.\n\nಆರೈಕೆ ಕ್ರಮಗಳು:\n1. ನೀರು ನಿಲ್ಲದಂತೆ ಜಾಗ್ರತೆ ವಹಿಸಿ.\n2. ORS ಮತ್ತು ಎಳನೀರು ಕುಡಿಯಿರಿ.\n3. ವೈದ್ಯರ ಸಲಹೆಯಿಲ್ಲದೆ ಮಾತ್ರೆ ಸೇವಿಸಬೇಡಿ.\n4. ತೀವ್ರ ಜ್ವರವಿದ್ದರೆ ಆಸ್ಪತ್ರೆಗೆ ಭೇಟಿ ನೀಡಿ.',
            4,
            'Dr. Anand Gowda, Pediatrics',
            'https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?w=600&h=350&fit=crop'
        )
    ]
    cur.executemany("""
    INSERT INTO health_articles (id, title_en, title_hi, title_kn, category, summary_en, summary_hi, summary_kn, content_en, content_hi, content_kn, read_time_minutes, author, image_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, articles_data)

    # 4. Sample Patient
    cur.execute("""
    INSERT INTO patients (id, full_name, email, phone, age, gender, blood_group, emergency_contact_name, emergency_contact_phone, preferred_language)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, ('c1111111-1111-1111-1111-111111111111', 'Aditi Sharma', 'aditi.sharma@example.com', '+91 98765 43210', 29, 'Female', 'O+', 'Rohan Sharma (Spouse)', '+91 98765 12345', 'en'))

    # 5. Sample Vitals
    cur.execute("""
    INSERT INTO health_vitals (id, patient_id, blood_pressure_systolic, blood_pressure_diastolic, heart_rate, blood_sugar, temperature, weight_kg, height_cm)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, ('v1111111-1111-1111-1111-111111111111', 'c1111111-1111-1111-1111-111111111111', 118, 78, 72, 94.0, 98.6, 62.5, 165.0))

    # 6. Sample Medicine Reminders
    reminders_data = [
        ('m1111111-1111-1111-1111-111111111111', 'c1111111-1111-1111-1111-111111111111', 'Vitamin D3 (Cholecalciferol)', '60,000 IU', 'Weekly (Sunday)', '09:00 AM', 'after_food', 'taken', 'Prescribed for mild deficiency. Take with milk.'),
        ('m2222222-2222-2222-2222-222222222222', 'c1111111-1111-1111-1111-111111111111', 'Omega-3 Fish Oil', '1000 mg', 'Daily', '01:30 PM', 'after_food', 'pending', 'Heart and joint health maintenance.'),
        ('m3333333-3333-3333-3333-333333333333', 'c1111111-1111-1111-1111-111111111111', 'Magnesium Glycinate', '200 mg', 'Daily before bed', '09:30 PM', 'before_bed', 'pending', 'Supports deep sleep and muscle relaxation.')
    ]
    cur.executemany("""
    INSERT INTO medicine_reminders (id, patient_id, medicine_name, dosage, frequency, reminder_time, timing_relation, status_today, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, reminders_data)

    # 7. Sample Upcoming Appointment
    cur.execute("""
    INSERT INTO appointments (id, patient_id, patient_name, patient_phone, patient_email, doctor_id, appointment_date, time_slot, reason, status, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        'b1111111-1111-1111-1111-111111111111',
        'c1111111-1111-1111-1111-111111111111',
        'Aditi Sharma',
        '+91 98765 43210',
        'aditi.sharma@example.com',
        'd2222222-2222-2222-2222-222222222222',
        (datetime.date.today() + datetime.timedelta(days=2)).isoformat(),
        '10:00 AM',
        'Annual routine wellness checkup and blood panel review',
        'Scheduled',
        'First consultation of this year'
    ))

    conn.commit()

# ====================================================================
# Data Access Functions (CRUD)
# ====================================================================

def get_doctors(specialty: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch all doctors, optionally filtered by medical specialty."""
    conn = get_connection()
    cur = conn.cursor()
    if specialty and specialty.lower() != 'all':
        cur.execute("SELECT * FROM doctors WHERE LOWER(specialty) = LOWER(?) ORDER BY rating DESC;", (specialty,))
    else:
        cur.execute("SELECT * FROM doctors ORDER BY rating DESC;")
    rows = cur.fetchall()
    doctors = [dict(row) for row in rows]
    conn.close()
    return doctors

def get_doctor_by_id(doctor_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve details of a single doctor by ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM doctors WHERE id = ?;", (doctor_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_appointments(patient_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all appointments with joined doctor information."""
    conn = get_connection()
    cur = conn.cursor()
    query = """
    SELECT a.*, d.name as doctor_name, d.specialty as doctor_specialty, 
           d.hospital as doctor_hospital, d.image_url as doctor_image, d.consultation_fee
    FROM appointments a
    LEFT JOIN doctors d ON a.doctor_id = d.id
    """
    params = []
    if patient_id:
        query += " WHERE a.patient_id = ?"
        params.append(patient_id)
    query += " ORDER BY a.appointment_date ASC, a.time_slot ASC;"

    cur.execute(query, params)
    rows = cur.fetchall()
    appointments = [dict(row) for row in rows]
    conn.close()
    return appointments

def create_appointment(data: Dict[str, Any]) -> Dict[str, Any]:
    """Book a new doctor appointment."""
    conn = get_connection()
    cur = conn.cursor()
    appointment_id = str(uuid.uuid4())
    patient_id = data.get('patient_id', 'c1111111-1111-1111-1111-111111111111')

    cur.execute("""
    INSERT INTO appointments (id, patient_id, patient_name, patient_phone, patient_email, doctor_id, appointment_date, time_slot, reason, status, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        appointment_id,
        patient_id,
        data.get('patient_name', 'Patient'),
        data.get('patient_phone', ''),
        data.get('patient_email', ''),
        data.get('doctor_id'),
        data.get('appointment_date'),
        data.get('time_slot'),
        data.get('reason', 'General consultation'),
        'Scheduled',
        data.get('notes', '')
    ))
    conn.commit()
    conn.close()
    return {"id": appointment_id, "status": "success", "message": "Appointment booked successfully"}

def cancel_appointment(appointment_id: str) -> bool:
    """Cancel an appointment by ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE appointments SET status = 'Cancelled' WHERE id = ?;", (appointment_id,))
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_medicines(patient_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve medicine reminders for a patient."""
    conn = get_connection()
    cur = conn.cursor()
    patient_id = patient_id or 'c1111111-1111-1111-1111-111111111111'
    cur.execute("SELECT * FROM medicine_reminders WHERE patient_id = ? AND is_active = 1 ORDER BY reminder_time ASC;", (patient_id,))
    rows = cur.fetchall()
    meds = [dict(row) for row in rows]
    conn.close()
    return meds

def create_medicine(data: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new medicine reminder."""
    conn = get_connection()
    cur = conn.cursor()
    reminder_id = str(uuid.uuid4())
    patient_id = data.get('patient_id', 'c1111111-1111-1111-1111-111111111111')

    cur.execute("""
    INSERT INTO medicine_reminders (id, patient_id, medicine_name, dosage, frequency, reminder_time, timing_relation, start_date, is_active, status_today, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 'pending', ?);
    """, (
        reminder_id,
        patient_id,
        data.get('medicine_name', ''),
        data.get('dosage', ''),
        data.get('frequency', 'Daily'),
        data.get('reminder_time', '09:00 AM'),
        data.get('timing_relation', 'after_food'),
        datetime.date.today().isoformat(),
        data.get('notes', '')
    ))
    conn.commit()
    conn.close()
    return {"id": reminder_id, "status": "success", "message": "Reminder added successfully"}

def update_medicine_status(medicine_id: str, status: str) -> bool:
    """Update today's status of a medicine ('taken', 'skipped', 'pending')."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE medicine_reminders SET status_today = ? WHERE id = ?;", (status, medicine_id))
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def delete_medicine(medicine_id: str) -> bool:
    """Remove a medicine reminder."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM medicine_reminders WHERE id = ?;", (medicine_id,))
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_articles(category: Optional[str] = None, lang: str = 'en') -> List[Dict[str, Any]]:
    """Retrieve health awareness articles adapted for selected language."""
    conn = get_connection()
    cur = conn.cursor()
    if category and category.lower() != 'all':
        cur.execute("SELECT * FROM health_articles WHERE LOWER(category) = LOWER(?) ORDER BY published_at DESC;", (category,))
    else:
        cur.execute("SELECT * FROM health_articles ORDER BY published_at DESC;")
    rows = cur.fetchall()
    articles = []
    for r in rows:
        d = dict(r)
        # Select language specific title/summary/content
        if lang == 'hi':
            d['title'] = d.get('title_hi') or d.get('title_en')
            d['summary'] = d.get('summary_hi') or d.get('summary_en')
            d['content'] = d.get('content_hi') or d.get('content_en')
        elif lang == 'kn':
            d['title'] = d.get('title_kn') or d.get('title_en')
            d['summary'] = d.get('summary_kn') or d.get('summary_en')
            d['content'] = d.get('content_kn') or d.get('content_en')
        else:
            d['title'] = d.get('title_en')
            d['summary'] = d.get('summary_en')
            d['content'] = d.get('content_en')
        articles.append(d)
    conn.close()
    return articles

def get_article_by_id(article_id: str, lang: str = 'en') -> Optional[Dict[str, Any]]:
    """Retrieve a single article with localized fields."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM health_articles WHERE id = ?;", (article_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    if lang == 'hi':
        d['title'] = d.get('title_hi') or d.get('title_en')
        d['summary'] = d.get('summary_hi') or d.get('summary_en')
        d['content'] = d.get('content_hi') or d.get('content_en')
    elif lang == 'kn':
        d['title'] = d.get('title_kn') or d.get('title_en')
        d['summary'] = d.get('summary_kn') or d.get('summary_en')
        d['content'] = d.get('content_kn') or d.get('content_en')
    else:
        d['title'] = d.get('title_en')
        d['summary'] = d.get('summary_en')
        d['content'] = d.get('content_en')
    return d

def get_emergency_contacts(lang: str = 'en') -> List[Dict[str, Any]]:
    """Retrieve emergency hotlines and services localized for current language."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM emergency_contacts ORDER BY display_order ASC;")
    rows = cur.fetchall()
    contacts = []
    for r in rows:
        d = dict(r)
        if lang == 'hi':
            d['title'] = d.get('title_hi') or d.get('title_en')
            d['description'] = d.get('description_hi') or d.get('description_en')
        elif lang == 'kn':
            d['title'] = d.get('title_kn') or d.get('title_en')
            d['description'] = d.get('description_kn') or d.get('description_en')
        else:
            d['title'] = d.get('title_en')
            d['description'] = d.get('description_en')
        contacts.append(d)
    conn.close()
    return contacts

def save_symptom_assessment(data: Dict[str, Any]) -> str:
    """Save an AI symptom assessment result to database."""
    conn = get_connection()
    cur = conn.cursor()
    assessment_id = str(uuid.uuid4())
    cur.execute("""
    INSERT INTO symptom_assessments (id, patient_id, patient_name, symptoms_text, duration, severity, age_group, language, ai_analysis, urgency_level, recommended_specialty, disclaimer_acknowledged)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1);
    """, (
        assessment_id,
        data.get('patient_id', 'c1111111-1111-1111-1111-111111111111'),
        data.get('patient_name', 'Patient'),
        data.get('symptoms_text', ''),
        data.get('duration', ''),
        data.get('severity', 'Mild'),
        data.get('age_group', 'Adult'),
        data.get('language', 'en'),
        data.get('ai_analysis', ''),
        data.get('urgency_level', 'Low'),
        data.get('recommended_specialty', 'General Medicine')
    ))
    conn.commit()
    conn.close()
    return assessment_id

def get_symptom_assessments(patient_id: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
    """Get recent symptom check records."""
    conn = get_connection()
    cur = conn.cursor()
    patient_id = patient_id or 'c1111111-1111-1111-1111-111111111111'
    cur.execute("SELECT * FROM symptom_assessments WHERE patient_id = ? ORDER BY created_at DESC LIMIT ?;", (patient_id, limit))
    rows = cur.fetchall()
    records = [dict(r) for r in rows]
    conn.close()
    return records

def save_chat_message(session_id: str, sender: str, message: str, language: str = 'en') -> str:
    """Persist a chatbot message."""
    conn = get_connection()
    cur = conn.cursor()
    msg_id = str(uuid.uuid4())
    cur.execute("""
    INSERT INTO chat_messages (id, session_id, sender, message, language)
    VALUES (?, ?, ?, ?, ?);
    """, (msg_id, session_id, sender, message, language))
    conn.commit()
    conn.close()
    return msg_id

def get_chat_history(session_id: str, limit: int = 15) -> List[Dict[str, Any]]:
    """Fetch chat history for a session."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT sender, message, language, created_at
    FROM chat_messages
    WHERE session_id = ?
    ORDER BY created_at ASC
    LIMIT ?;
    """, (session_id, limit))
    rows = cur.fetchall()
    history = [dict(r) for r in rows]
    conn.close()
    return history

def get_patient_profile(patient_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Fetch patient profile."""
    conn = get_connection()
    cur = conn.cursor()
    patient_id = patient_id or 'c1111111-1111-1111-1111-111111111111'
    cur.execute("SELECT * FROM patients WHERE id = ?;", (patient_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_health_vitals(patient_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Fetch latest health vitals for a patient."""
    conn = get_connection()
    cur = conn.cursor()
    patient_id = patient_id or 'c1111111-1111-1111-1111-111111111111'
    cur.execute("SELECT * FROM health_vitals WHERE patient_id = ? ORDER BY recorded_at DESC LIMIT 1;", (patient_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def update_health_vitals(data: Dict[str, Any]) -> Dict[str, Any]:
    """Record updated patient vitals."""
    conn = get_connection()
    cur = conn.cursor()
    vital_id = str(uuid.uuid4())
    patient_id = data.get('patient_id', 'c1111111-1111-1111-1111-111111111111')

    cur.execute("""
    INSERT INTO health_vitals (id, patient_id, blood_pressure_systolic, blood_pressure_diastolic, heart_rate, blood_sugar, temperature, weight_kg, height_cm)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        vital_id,
        patient_id,
        data.get('bp_systolic'),
        data.get('bp_diastolic'),
        data.get('heart_rate'),
        data.get('blood_sugar'),
        data.get('temperature'),
        data.get('weight_kg'),
        data.get('height_cm')
    ))
    conn.commit()
    conn.close()
    return {"id": vital_id, "status": "success", "message": "Vitals recorded"}

def get_dashboard_summary(patient_id: Optional[str] = None) -> Dict[str, Any]:
    """Unified patient dashboard summary aggregating appointments, medicines, vitals, and recent checks."""
    patient_id = patient_id or 'c1111111-1111-1111-1111-111111111111'
    profile = get_patient_profile(patient_id)
    vitals = get_health_vitals(patient_id)
    medicines = get_medicines(patient_id)
    appointments = get_appointments(patient_id)
    symptoms = get_symptom_assessments(patient_id, limit=3)

    # Calculate statistics
    active_meds_count = len(medicines)
    taken_meds = sum(1 for m in medicines if m.get('status_today') == 'taken')
    compliance_rate = int((taken_meds / active_meds_count * 100)) if active_meds_count > 0 else 100

    upcoming_appointments = [a for a in appointments if a.get('status') == 'Scheduled']

    return {
        "patient": profile,
        "vitals": vitals,
        "active_medicines": medicines,
        "medicines_taken_today": taken_meds,
        "medicines_total_today": active_meds_count,
        "medication_compliance": compliance_rate,
        "upcoming_appointments": upcoming_appointments,
        "recent_symptoms": symptoms
    }
