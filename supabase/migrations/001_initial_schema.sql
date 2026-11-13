-- ====================================================================
-- MediCare AI - Initial Database Schema & Row Level Security (RLS)
-- File: supabase/migrations/001_initial_schema.sql
-- Description: Core tables, indexes, RLS policies, and seed data for
--              MediCare AI Healthcare Platform.
-- ====================================================================

-- 1. Enable Required Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ====================================================================
-- 2. Create Tables
-- ====================================================================

-- 2.1 Patients / User Profiles
CREATE TABLE IF NOT EXISTS patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    age INT,
    gender VARCHAR(20),
    blood_group VARCHAR(10),
    emergency_contact_name VARCHAR(255),
    emergency_contact_phone VARCHAR(50),
    preferred_language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2.2 Doctors
CREATE TABLE IF NOT EXISTS doctors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    specialty VARCHAR(100) NOT NULL,
    qualifications VARCHAR(255) NOT NULL,
    experience_years INT NOT NULL,
    hospital VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    consultation_fee NUMERIC(10, 2) NOT NULL DEFAULT 500.00,
    rating NUMERIC(3, 2) DEFAULT 4.8,
    available_days TEXT NOT NULL,          -- comma-separated or JSON list
    available_time_slots TEXT NOT NULL,  -- comma-separated or JSON list
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2.3 Appointments
CREATE TABLE IF NOT EXISTS appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE SET NULL,
    patient_name VARCHAR(255) NOT NULL,
    patient_phone VARCHAR(50) NOT NULL,
    patient_email VARCHAR(255),
    doctor_id UUID REFERENCES doctors(id) ON DELETE SET NULL,
    appointment_date DATE NOT NULL,
    time_slot VARCHAR(50) NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'Scheduled', -- 'Scheduled', 'Completed', 'Cancelled'
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2.4 Medicine Reminders
CREATE TABLE IF NOT EXISTS medicine_reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    medicine_name VARCHAR(255) NOT NULL,
    dosage VARCHAR(100) NOT NULL,        -- e.g. "500 mg", "1 tablet"
    frequency VARCHAR(100) NOT NULL,     -- e.g. "Daily", "Twice daily", "As needed"
    reminder_time VARCHAR(50) NOT NULL,  -- e.g. "08:00 AM", "09:00 PM"
    timing_relation VARCHAR(50) DEFAULT 'after_food', -- 'before_food', 'after_food', 'with_food'
    start_date DATE DEFAULT CURRENT_DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    status_today VARCHAR(20) DEFAULT 'pending', -- 'pending', 'taken', 'skipped'
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2.5 Symptom Assessments (AI Checker History)
CREATE TABLE IF NOT EXISTS symptom_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE SET NULL,
    patient_name VARCHAR(255),
    symptoms_text TEXT NOT NULL,
    duration VARCHAR(100),
    severity VARCHAR(50),               -- 'Mild', 'Moderate', 'Severe'
    age_group VARCHAR(50),              -- 'Adult', 'Child', 'Senior'
    language VARCHAR(10) DEFAULT 'en',  -- 'en', 'hi', 'kn'
    ai_analysis TEXT NOT NULL,
    urgency_level VARCHAR(50) DEFAULT 'Low', -- 'Low', 'Moderate', 'High', 'Emergency'
    recommended_specialty VARCHAR(100),
    disclaimer_acknowledged BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2.6 Chat Messages (AI Health Chatbot History)
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(100) NOT NULL,
    patient_id UUID REFERENCES patients(id) ON DELETE SET NULL,
    sender VARCHAR(20) NOT NULL,        -- 'user' or 'ai'
    message TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2.7 Health Awareness Articles (Trilingual: EN, HI, KN)
CREATE TABLE IF NOT EXISTS health_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title_en VARCHAR(255) NOT NULL,
    title_hi VARCHAR(255) NOT NULL,
    title_kn VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,     -- 'Heart Health', 'Nutrition', 'Mental Health', 'Diabetes', 'Seasonal'
    summary_en TEXT NOT NULL,
    summary_hi TEXT NOT NULL,
    summary_kn TEXT NOT NULL,
    content_en TEXT NOT NULL,
    content_hi TEXT NOT NULL,
    content_kn TEXT NOT NULL,
    read_time_minutes INT DEFAULT 4,
    author VARCHAR(100) DEFAULT 'MediCare Medical Editorial Board',
    image_url TEXT,
    published_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2.8 Emergency Contacts & Helplines (Trilingual)
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title_en VARCHAR(255) NOT NULL,
    title_hi VARCHAR(255) NOT NULL,
    title_kn VARCHAR(255) NOT NULL,
    phone_number VARCHAR(50) NOT NULL,
    description_en TEXT NOT NULL,
    description_hi TEXT NOT NULL,
    description_kn TEXT NOT NULL,
    is_national BOOLEAN DEFAULT TRUE,
    badge_type VARCHAR(50) DEFAULT 'critical', -- 'critical', 'police', 'mental_health', 'general'
    display_order INT DEFAULT 1
);

-- 2.9 Health Vitals Log
CREATE TABLE IF NOT EXISTS health_vitals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    blood_pressure_systolic INT,
    blood_pressure_diastolic INT,
    heart_rate INT,
    blood_sugar NUMERIC(5, 1),
    temperature NUMERIC(4, 1),
    weight_kg NUMERIC(5, 2),
    height_cm NUMERIC(5, 2),
    recorded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================================
-- 3. Indexes for Performance Optimization
-- ====================================================================
CREATE INDEX IF NOT EXISTS idx_doctors_specialty ON doctors(specialty);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor ON appointments(doctor_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_reminders_patient ON medicine_reminders(patient_id);
CREATE INDEX IF NOT EXISTS idx_reminders_active ON medicine_reminders(is_active);
CREATE INDEX IF NOT EXISTS idx_symptom_assessments_patient ON symptom_assessments(patient_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_articles_category ON health_articles(category);
CREATE INDEX IF NOT EXISTS idx_vitals_patient ON health_vitals(patient_id);

-- ====================================================================
-- 4. Row Level Security (RLS) Configuration
-- ====================================================================

-- Enable RLS on all tables
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctors ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE medicine_reminders ENABLE ROW LEVEL SECURITY;
ALTER TABLE symptom_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE emergency_contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_vitals ENABLE ROW LEVEL SECURITY;

-- 4.1 Public Reference Tables (Read-only for all, write for service_role)
DROP POLICY IF EXISTS "Public can view doctors" ON doctors;
CREATE POLICY "Public can view doctors" ON doctors
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "Service role can manage doctors" ON doctors;
CREATE POLICY "Service role can manage doctors" ON doctors
    FOR ALL USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "Public can view articles" ON health_articles;
CREATE POLICY "Public can view articles" ON health_articles
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "Service role can manage articles" ON health_articles;
CREATE POLICY "Service role can manage articles" ON health_articles
    FOR ALL USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "Public can view emergency contacts" ON emergency_contacts;
CREATE POLICY "Public can view emergency contacts" ON emergency_contacts
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "Service role can manage emergency contacts" ON emergency_contacts;
CREATE POLICY "Service role can manage emergency contacts" ON emergency_contacts
    FOR ALL USING (auth.role() = 'service_role');

-- 4.2 Patient Profiles Policies
DROP POLICY IF EXISTS "Users can read own profile" ON patients;
CREATE POLICY "Users can read own profile" ON patients
    FOR SELECT USING (auth.uid() = id OR auth.role() = 'service_role' OR auth.role() = 'anon');

DROP POLICY IF EXISTS "Users can insert own profile" ON patients;
CREATE POLICY "Users can insert own profile" ON patients
    FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "Users can update own profile" ON patients;
CREATE POLICY "Users can update own profile" ON patients
    FOR UPDATE USING (auth.uid() = id OR auth.role() = 'service_role' OR auth.role() = 'anon');

-- 4.3 Appointments Policies
DROP POLICY IF EXISTS "Public can book appointments" ON appointments;
CREATE POLICY "Public can book appointments" ON appointments
    FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "Users can view appointments" ON appointments;
CREATE POLICY "Users can view appointments" ON appointments
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "Users can update appointments" ON appointments;
CREATE POLICY "Users can update appointments" ON appointments
    FOR UPDATE USING (true);

DROP POLICY IF EXISTS "Users can delete appointments" ON appointments;
CREATE POLICY "Users can delete appointments" ON appointments
    FOR DELETE USING (true);

-- 4.4 Medicine Reminders Policies
DROP POLICY IF EXISTS "Public can manage reminders" ON medicine_reminders;
CREATE POLICY "Public can manage reminders" ON medicine_reminders
    FOR ALL USING (true);

-- 4.5 Symptom Assessments Policies
DROP POLICY IF EXISTS "Public can manage symptom assessments" ON symptom_assessments;
CREATE POLICY "Public can manage symptom assessments" ON symptom_assessments
    FOR ALL USING (true);

-- 4.6 Chat Messages Policies
DROP POLICY IF EXISTS "Public can manage chat messages" ON chat_messages;
CREATE POLICY "Public can manage chat messages" ON chat_messages
    FOR ALL USING (true);

-- 4.7 Health Vitals Policies
DROP POLICY IF EXISTS "Public can manage health vitals" ON health_vitals;
CREATE POLICY "Public can manage health vitals" ON health_vitals
    FOR ALL USING (true);

-- ====================================================================
-- 5. Seed Data
-- ====================================================================

-- 5.1 Seed Doctors
INSERT INTO doctors (id, name, specialty, qualifications, experience_years, hospital, city, consultation_fee, rating, available_days, available_time_slots, image_url)
VALUES
    ('d1111111-1111-1111-1111-111111111111', 'Dr. Rajesh Sharma', 'Cardiology', 'MBBS, MD, DM (Cardiology), FACC', 16, 'Apollo Heart Centre', 'Bengaluru', 800.00, 4.9, 'Mon, Wed, Fri', '09:00 AM, 11:30 AM, 02:00 PM, 04:30 PM', 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=300&h=300&fit=crop'),
    ('d2222222-2222-2222-2222-222222222222', 'Dr. Priya Kulkarni', 'General Medicine', 'MBBS, DNB (Internal Medicine)', 11, 'Manipal Hospital', 'Bengaluru', 500.00, 4.8, 'Mon, Tue, Wed, Thu, Fri, Sat', '10:00 AM, 11:00 AM, 03:00 PM, 05:00 PM', 'https://images.unsplash.com/photo-1594824813515-05527a4128f7?w=300&h=300&fit=crop'),
    ('d3333333-3333-3333-3333-333333333333', 'Dr. Anand Gowda', 'Pediatrics', 'MBBS, MD (Pediatrics), FIAP', 14, 'Cloudnine Children Hospital', 'Bengaluru', 600.00, 4.9, 'Tue, Thu, Sat', '09:30 AM, 11:00 AM, 04:00 PM, 06:00 PM', 'https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=300&h=300&fit=crop'),
    ('d4444444-4444-4444-4444-444444444444', 'Dr. Sunita Rao', 'Dermatology', 'MBBS, MD (Dermatology, Venereology & Leprosy)', 9, 'Fortis Hospital', 'Bengaluru', 650.00, 4.7, 'Mon, Wed, Thu, Sat', '10:30 AM, 12:00 PM, 03:30 PM, 05:30 PM', 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=300&h=300&fit=crop'),
    ('d5555555-5555-5555-5555-555555555555', 'Dr. Vikram Venkatesh', 'Orthopedics', 'MBBS, MS (Orthopaedics), MCh (Joint Replacement)', 18, 'Sparsh Super Speciality Hospital', 'Bengaluru', 750.00, 4.8, 'Mon, Tue, Thu, Fri', '09:00 AM, 10:30 AM, 02:30 PM, 04:00 PM', 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=300&h=300&fit=crop'),
    ('d6666666-6666-6666-6666-666666666666', 'Dr. Meera Nambiar', 'Neurology', 'MBBS, MD, DM (Neurology)', 15, 'NIMHANS Allied Health Clinic', 'Bengaluru', 900.00, 4.9, 'Tue, Wed, Fri', '11:00 AM, 01:00 PM, 03:00 PM, 05:00 PM', 'https://images.unsplash.com/photo-1651008376811-b90baee60c1f?w=300&h=300&fit=crop'),
    ('d7777777-7777-7777-7777-777777777777', 'Dr. Karthik Sundaram', 'Psychiatry', 'MBBS, DPM, MD (Psychiatry)', 12, 'MindCare Mental Health Centre', 'Bengaluru', 700.00, 4.8, 'Mon, Wed, Fri, Sat', '11:00 AM, 02:00 PM, 04:00 PM, 06:30 PM', 'https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=300&h=300&fit=crop'),
    ('d8888888-8888-8888-8888-888888888888', 'Dr. Ananya Hegde', 'Gynecology', 'MBBS, MS (OBG), FICOG', 13, 'Aster CMI Hospital', 'Bengaluru', 650.00, 4.9, 'Tue, Wed, Thu, Sat', '10:00 AM, 12:30 PM, 03:00 PM, 05:00 PM', 'https://images.unsplash.com/photo-1594824813515-05527a4128f7?w=300&h=300&fit=crop')
ON CONFLICT (id) DO NOTHING;

-- 5.2 Seed Emergency Contacts
INSERT INTO emergency_contacts (id, title_en, title_hi, title_kn, phone_number, description_en, description_hi, description_kn, is_national, badge_type, display_order)
VALUES
    ('e1111111-1111-1111-1111-111111111111', 'Emergency Ambulance', 'आपातकालीन एम्बुलेंस', 'ತುರ್ತು ಆಂಬ್ಯುಲೆನ್ಸ್', '108', 'Free 24/7 emergency medical response service across India.', 'भारत भर में मुफ्त 24/7 आपातकालीन चिकित्सा प्रतिक्रिया सेवा।', 'ಭಾರತದಾದ್ಯಂತ ಉಚಿತ 24/7 ತುರ್ತು ವೈದ್ಯಕೀಯ ಸೇವೆ.', true, 'critical', 1),
    ('e2222222-2222-2222-2222-222222222222', 'National Emergency Number', 'राष्ट्रीय आपातकालीन नंबर', 'ರಾಷ್ಟ್ರೀಯ ತುರ್ತು ಸಂಖ್ಯೆ', '112', 'Single emergency helpline for Police, Fire, and Medical assistance.', 'पुलिस, अग्निशमन और चिकित्सा सहायता के लिए एकीकृत आपातकालीन हेल्पलाइन।', 'ಪೊಲೀಸ್, ಅಗ್ನಿಶಾಮಕ ಮತ್ತು ವೈದ್ಯಕೀಯ ಸಹಾಯಕ್ಕಾಗಿ ಏಕೀಕೃತ ತುರ್ತು ಸಹಾಯವಾಣಿ.', true, 'critical', 2),
    ('e3333333-3333-3333-3333-333333333333', 'Maternity Helpline (Janani Shishu)', 'मातृत्व हेल्पलाइन', 'ತಾಯಂದಿರ ಸಹಾಯವಾಣಿ', '102', 'Free transport service for pregnant women and newborns.', 'गर्भवती महिलाओं और नवजात शिशुओं के लिए मुफ्त परिवहन सेवा।', 'ಗರ್ಭಿಣಿಯರು ಮತ್ತು ನವಜಾತ ಶಿಶುಗಳಿಗೆ ಉಚಿತ ಸಾರಿಗೆ ಸೇವೆ.', true, 'general', 3),
    ('e4444444-4444-4444-4444-444444444444', 'Tele-MANAS Mental Health Helpline', 'टेली-मानस मानसिक स्वास्थ्य हेल्पलाइन', 'ಟೆಲಿ-ಮಾನಸ್ ಮಾನಸಿಕ ಆರೋಗ್ಯ ಸಹಾಯವಾಣಿ', '14416', 'Government of India 24/7 free mental health counseling & psychological support.', 'भारत सरकार की 24/7 मुफ्त मानसिक स्वास्थ्य और परामर्श सेवा।', 'ಭಾರತ ಸರ್ಕಾರದ 24/7 ಉಚಿತ ಮಾನಸಿಕ ಆರೋಗ್ಯ ಸಮಾಲೋಚನೆ ಸೇವೆ.', true, 'mental_health', 4),
    ('e5555555-5555-5555-5555-555555555555', 'Women in Distress Helpline', 'महिला हेल्पलाइन', 'ಮಹಿಳಾ ಸಹಾಯವಾಣಿ', '1091', '24/7 emergency support and safety assistance for women.', 'महिलाओं के लिए 24/7 आपातकालीन सहायता और सुरक्षा सेवा।', 'ಮಹಿಳೆಯರಿಗಾಗಿ 24/7 ತುರ್ತು ನೆರವು ಮತ್ತು ರಕ್ಷಣೆ.', true, 'general', 5),
    ('e6666666-6666-6666-6666-666666666666', 'National Health Helpline', 'राष्ट्रीय स्वास्थ्य हेल्पलाइन', 'ರಾಷ್ಟ್ರೀಯ ಆರೋಗ್ಯ ಸಹಾಯವಾಣಿ', '1075', 'Ministry of Health national health advisory and epidemic query line.', 'स्वास्थ्य मंत्रालय की राष्ट्रीय स्वास्थ्य सलाह और महामारी मार्गदर्शन हेल्पलाइन।', 'ಆರೋಗ್ಯ ಸಚಿವಾಲಯದ ರಾಷ್ಟ್ರೀಯ ಆರೋಗ್ಯ ಮಾಹಿತಿ ಸಹಾಯವಾಣಿ.', true, 'general', 6)
ON CONFLICT (id) DO NOTHING;

-- 5.3 Seed Health Awareness Articles (EN, HI, KN)
INSERT INTO health_articles (id, title_en, title_hi, title_kn, category, summary_en, summary_hi, summary_kn, content_en, content_hi, content_kn, read_time_minutes, author, image_url)
VALUES
    (
        'a1111111-1111-1111-1111-111111111111',
        'Understanding High Blood Pressure: The Silent Signs and Daily Management',
        'उच्च रक्तचाप को समझना: मूक संकेत और दैनिक प्रबंधन',
        'ರಕ್ತದೊತ್ತಡವನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳುವುದು: ಮೂಕ ಲಕ್ಷಣಗಳು ಮತ್ತು ದೈನಂದಿನ ನಿರ್ವಹಣೆ',
        'Heart Health',
        'Learn how to identify subtle symptoms of hypertension, monitor your blood pressure at home, and make heart-healthy dietary changes.',
        'उच्च रक्तचाप के सूक्ष्म लक्षणों को पहचानना, घर पर बीपी की निगरानी करना और हृदय के अनुकूल आहार परिवर्तन करना सीखें।',
        'ಅಧಿಕ ರಕ್ತದೊತ್ತಡದ ಲಕ್ಷಣಗಳನ್ನು ಗುರುತಿಸುವುದು, ಮನೆಯಲ್ಲೇ ಪರೀಕ್ಷಿಸುವುದು ಮತ್ತು ಹೃದಯದ ಆರೋಗ್ಯಕ್ಕೆ ಪೂರಕವಾದ ಆಹಾರ ಕ್ರಮಗಳನ್ನು ತಿಳಿಯಿರಿ.',
        'Hypertension (high blood pressure) is often referred to as the silent killer because it typically displays no obvious symptoms until significant vascular damage occurs. Normal blood pressure is defined as below 120/80 mmHg. When readings consistently reach 130-139 systolic or 80-89 diastolic, it is classified as Stage 1 Hypertension.

Key Management Strategies:
1. Dietary Approaches: Adopt the DASH diet, reducing sodium intake to under 2,000 mg daily. Increase potassium-rich foods like bananas, spinach, and sweet potatoes.
2. Physical Activity: Aim for 150 minutes of moderate aerobic exercise (brisk walking, swimming, cycling) per week.
3. Stress Reduction: Chronic stress elevates cortisol and blood pressure. Daily 15-minute mindfulness breathing has clinically proven benefits.
4. Regular Monitoring: Check readings twice weekly at the same time of day and record them in your MediCare dashboard.

When to Seek Immediate Medical Help: If blood pressure spikes above 180/120 mmHg accompanied by chest tightness, vision changes, or severe headache, contact emergency services (108) immediately.',
        'उच्च रक्तचाप को अक्सर "साइलेंट किलर" कहा जाता है क्योंकि जब तक रक्त वाहिकाओं को गंभीर नुकसान नहीं पहुंचता, इसके स्पष्ट लक्षण दिखाई नहीं देते। सामान्य रक्तचाप 120/80 mmHg से कम होता है।

प्रमुख प्रबंधन रणनीतियाँ:
1. आहार नियंत्रण: DASH आहार अपनाएं, नमक का सेवन रोजाना 2,000 मिलीग्राम से कम रखें। पोटेशियम से भरपूर खाद्य पदार्थ जैसे केला और पालक खाएं।
2. शारीरिक गतिविधि: प्रति सप्ताह 150 मिनट तेज चलना या व्यायाम करें।
3. तनाव कम करें: रोजाना 15 मिनट प्राणायाम या ध्यान करें।
4. नियमित निगरानी: सप्ताह में दो बार अपना बीपी मापें और रिकॉर्ड रखें।

आपातकालीन चेतावनी: यदि रक्तचाप 180/120 से ऊपर चला जाए और सीने में दर्द या चक्कर आए, तो तुरंत 108 पर कॉल करें।',
        'ಅಧಿಕ ರಕ್ತದೊತ್ತಡವನ್ನು ಹೆಚ್ಚಾಗಿ "ಮೂಕ ಕೊಲೆಗಾರ" ಎಂದು ಕರೆಯಲಾಗುತ್ತದೆ ಏಕೆಂದರೆ ರಕ್ತನಾಳಗಳಿಗೆ ಹಾನಿಯಾಗುವವರೆಗೆ ಯಾವುದೇ ಸ್ಪಷ್ಟ ಲಕ್ಷಣಗಳು ಕಾಣಿಸುವುದಿಲ್ಲ. ಸಾಮಾನ್ಯ ರಕ್ತದೊತ್ತಡ 120/80 mmHg ಗಿಂತ ಕಡಿಮೆಯಿರುತ್ತದೆ.

ಪ್ರಮುಖ ನಿರ್ವಹಣಾ ಸಲಹೆಗಳು:
1. ಆಹಾರ ಕ್ರಮ: ಉಪ್ಪಿನ ಬಳಕೆಯನ್ನು ಕಡಿಮೆ ಮಾಡಿ. ಬಾಳೆಹಣ್ಣು, ಪಾಲಕ್ ನಂತಹ ಪೊಟ್ಯಾಸಿಯಮ್ ಭರಿತ ಆಹಾರಗಳನ್ನು ಸೇವಿಸಿ.
2. ದೈಹಿಕ ವ್ಯಾಯಾಮ: ವಾರಕ್ಕೆ 150 ನಿಮಿಷಗಳ ಕಾಲ ವೇಗದ ನಡಿಗೆ ಅಥವಾ ವ್ಯಾಯಾಮ ಮಾಡಿ.
3. ಒತ್ತಡ ನಿರ್ವಹಣೆ: ಪ್ರತಿದಿನ 15 ನಿಮಿಷ ಧ್ಯಾನ ಅಥವಾ ಪ್ರಾಣಾಯಾಮ ಮಾಡಿ.
4. ನಿಯಮಿತ ತಪಾಸಣೆ: ವಾರಕ್ಕೆ ಎರಡು ಬಾರಿ ರಕ್ತದೊತ್ತಡವನ್ನು ಪರೀಕ್ಷಿಸಿ.

ತುರ್ತು ಎಚ್ಚರಿಕೆ: ರಕ್ತದೊತ್ತಡ 180/120 ಕ್ಕಿಂತ ಹೆಚ್ಚಾಗಿದ್ದರೆ ಮತ್ತು ಎದೆ ನೋವು ಅಥವಾ ತಲೆತಿರುಗುವಿಕೆ ಇದ್ದರೆ, ತಕ್ಷಣ 108 ಗೆ ಕರೆ ಮಾಡಿ.',
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
        'Type 2 diabetes develops when body cells become resistant to insulin or when the pancreas cannot produce sufficient insulin. Early intervention during the prediabetes phase can reverse or postpone progression in up to 70% of individuals.

Crucial Steps for Glycemic Health:
1. Focus on Glycemic Load: Swap refined grains (white rice, maida) with high-fiber whole grains (millets, ragi, quinoa, brown rice).
2. Plate Method: Fill half your plate with non-starchy vegetables, one quarter with lean protein (pulses, paneer, eggs), and one quarter with complex carbohydrates.
3. Post-Meal Movement: A 10-15 minute walk right after meals significantly reduces postprandial glucose spikes.
4. Regular HbA1c Checks: Check your three-month average glucose (HbA1c) every 3 to 6 months if diagnosed or high-risk.',
        'टाइप 2 मधुमेह तब होता है जब शरीर की कोशिकाएं इंसुलिन के प्रति प्रतिरोधी हो जाती हैं। प्रीडायबिटीज के दौरान सही जीवनशैली अपनाकर इसे रोका जा सकता है।

ग्लूकोज नियंत्रण के मुख्य नियम:
1. सही अनाज चुनें: सफेद चावल और मैदा के स्थान पर बाजरा, रागी और दलिया का उपयोग करें।
2. प्लेट नियम: अपनी आधी थाली हरी सब्जियों से, एक चौथाई प्रोटीन (दालें, पनीर) और एक चौथाई साबुत अनाज से भरें।
3. भोजन के बाद टहलें: भोजन के 10 मिनट बाद हल्की सैर रक्त शर्करा को नियंत्रित रखती है।
4. HbA1c टेस्ट: हर 3 से 6 महीने में अपना HbA1c टेस्ट जरूर करवाएं।',
        'ಟೈಪ್ 2 ಮಧುಮೇಹವು ದೇಹದ ಜೀವಕೋಶಗಳು ಇನ್ಸುಲಿನ್ ಪ್ರತಿರೋಧವನ್ನು ಬೆಳೆಸಿಕೊಂಡಾಗ ಉಂಟಾಗುತ್ತದೆ. ಆರಂಭಿಕ ಹಂತದಲ್ಲಿ ಇದನ್ನು ಸಂಪೂರ್ಣವಾಗಿ ತಡೆಗಟ್ಟಬಹುದು.

ಗ್ಲೂಕೋಸ್ ನಿಯಂತ್ರಣದ ಪ್ರಮುಖ ಸಲಹೆಗಳು:
1. ಸಿರಿಧಾನ್ಯಗಳ ಬಳಕೆ: ಬಿಳಿ ಅನ್ನ ಮತ್ತು ಮೈದಾ ಬದಲಿಗೆ ರಾಗಿ, ನವಣೆ, ಜೋಳವನ್ನು ಬಳಸಿ.
2. ಊಟದ ತಟ್ಟೆಯ ನಿಯಮ: ಅರ್ಧ ತಟ್ಟೆ ತರಕಾರಿಗಳು, ಕಾಲು ಭಾಗ ಪ್ರೋಟೀನ್ (ಕಾಳುಗಳು, ಮೊಟ್ಟೆ) ಮತ್ತು ಕಾಲು ಭಾಗ ಸಂಕೀರ್ಣ ಕಾರ್ಬೋಹೈಡ್ರೇಟ್ ಇರಲಿ.
3. ಊಟದ ನಂತರ ನಡಿಗೆ: ಊಟವಾದ ತಕ್ಷಣ 10-15 ನಿಮಿಷಗಳ ನಡಿಗೆ ಸಕ್ಕರೆ ಮಟ್ಟವನ್ನು ಹತೋಟಿಯಲ್ಲಿಡುತ್ತದೆ.
4. HbA1c ಪರೀಕ್ಷೆ: ನಿಯಮಿತವಾಗಿ 3 ತಿಂಗಳಿಗೊಮ್ಮೆ ತಪಾಸಣೆ ಮಾಡಿಸಿ.',
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
        'Mental well-being is an intrinsic component of overall health. Prolonged unmanaged stress triggers elevated sympathetic nervous activity, leading to insomnia, gastrointestinal distress, and heightened cardiovascular risk.

Self-Care Pillars:
1. Cognitive Reframing: Recognize catastrophic thinking patterns and ground your thoughts in objective facts.
2. Sleep Hygiene: Ensure 7-8 hours of uninterrupted sleep. Disconnect digital screens 60 minutes before bedtime.
3. Social Connection: Confiding in a trusted friend or family member lowers neurological stress markers.
4. Tele-Counseling: Never hesitate to seek professional counseling. In India, Tele-MANAS (14416) provides free, confidential 24/7 psychological support.',
        'मानसिक स्वास्थ्य समग्र स्वास्थ्य का एक अनिवार्य हिस्सा है। अत्यधिक तनाव अनिद्रा, पाचन समस्याओं और दिल की बीमारियों का कारण बन सकता है।

मानसिक स्वास्थ्य के मुख्य स्तंभ:
1. नींद की स्वच्छता: रोजाना 7-8 घंटे की गहरी नींद लें। सोने से 1 घंटा पहले स्क्रीन बंद करें।
2. मन की बात साझा करें: परिवार या दोस्तों से अपनी भावनाएं साझा करें।
3. पेशेवर मदद: संकोच न करें। टेली-मानस (14416) पर मुफ्त और गोपनीय परामर्श उपलब्ध है।',
        'ಮಾನಸಿಕ ಆರೋಗ್ಯವು ಒಟ್ಟಾರೆ ಆರೋಗ್ಯದ ಅವಿಭಾಜ್ಯ ಅಂಗವಾಗಿದೆ. ನಿರಂತರ ಒತ್ತಡವು ನಿದ್ರಾಹೀನತೆ ಮತ್ತು ಜೀರ್ಣಾಂಗ ಸಮಸ್ಯೆಗಳಿಗೆ ಕಾರಣವಾಗುತ್ತದೆ.

ಮಾನಸಿಕ ಸ್ವಾಸ್ಥ್ಯದ ಪ್ರಮುಖ ಅಂಶಗಳು:
1. ಉತ್ತಮ ನಿದ್ರೆ: ಪ್ರತಿದಿನ 7-8 ಗಂಟೆಗಳ ಕಾಲ ನಿದ್ರಿಸಿ. ಮಲಗುವ ಮುನ್ನ ಮೊಬೈಲ್ ಬಳಕೆಯನ್ನು ತಪ್ಪಿಸಿ.
2. ಸ್ನೇಹಿತರೊಂದಿಗೆ ಹಂಚಿಕೊಳ್ಳಿ: ನಿಮ್ಮ ಭಾವನೆಗಳನ್ನು ಆಪ್ತರೊಂದಿಗೆ ಹಂಚಿಕೊಳ್ಳಿ.
3. ವೃತ್ತಿಪರ ಸಹಾಯ: ಹಿಂಜರಿಕೆಯಿಲ್ಲದೆ ಸಹಾಯ ಪಡೆಯಿರಿ. ಟೆಲಿ-ಮಾನಸ್ (14416) ಉಚಿತ ಮತ್ತು ಗೌಪ್ಯ ಸಮಾಲೋಚನೆಯನ್ನು ನೀಡುತ್ತದೆ.',
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
        'During seasonal weather transitions and monsoon periods, vector-borne and viral infections peak sharply. Prompt recognition between common viral fever and high-risk infections like Dengue or Typhoid is essential.

Practical Guidelines:
1. Prevent Mosquito Breeding: Eliminate stagnant water in flowerpots, coolers, and containers every week.
2. Fluid Intake: Dehydration worsens fever outcomes. Consume ORS, coconut water, warm broths, and boiled water.
3. Avoid Self-Medication: Never consume NSAIDs (like Ibuprofen or Aspirin) during suspected dengue, as they elevate bleeding risks. Use Paracetamol only under medical guidance.
4. Red Flags: Persistent vomiting, bleeding from gums, extreme lethargy, or temperature above 103°F require emergency evaluation.',
        'मौसम बदलने और मानसून के दौरान वायरल और मच्छर जनित बीमारियां तेजी से फैलती हैं। डेंगू और सामान्य फ्लू के अंतर को समझना आवश्यक है।

महत्वपूर्ण सावधानियां:
1. मच्छरों से बचाव: घर के आसपास पानी जमा न होने दें।
2. तरल पदार्थों का सेवन: ओआरएस, नारियल पानी और पर्याप्त उबला पानी पिएं।
3. बिना डॉक्टर की सलाह दवा न लें: ब्रूफेन या एस्पिरिन का सेवन न करें, यह ब्लीडिंग का खतरा बढ़ा सकता है।
4. गंभीर लक्षण: तेज पेट दर्द, मसूड़ों से खून आना या लगातार उल्टी होने पर तुरंत डॉक्टर के पास जाएं।',
        'ಋತುಮಾನ ಬದಲಾವಣೆ ಮತ್ತು ಮಳೆಗಾಲದಲ್ಲಿ ಸೊಳ್ಳೆಗಳಿಂದ ಹರಡುವ ರೋಗಗಳು ಹೆಚ್ಚಾಗುತ್ತವೆ. ಡೆಂಗ್ಯೂ ಮತ್ತು ಸಾಮಾನ್ಯ ಜ್ವರದ ನಡುವಿನ ವ್ಯತ್ಯಾಸವನ್ನು ತಿಳಿದುಕೊಳ್ಳುವುದು ಮುಖ್ಯ.

ಪ್ರಮುಖ ಎಚ್ಚರಿಕೆಗಳು:
1. ಸೊಳ್ಳೆಗಳ ನಿಯಂತ್ರಣ: ಸುತ್ತಮುತ್ತ ನೀರು ನಿಲ್ಲದಂತೆ ನೋಡಿಕೊಳ್ಳಿ.
2. ದ್ರವ ಪದಾರ್ಥಗಳ ಸೇವನೆ: ORS, ಎಳನೀರು ಮತ್ತು ಕಾಯಿಸಿ ಆರಿಸಿದ ನೀರನ್ನು ಹೆಚ್ಚಾಗಿ ಕುಡಿಯಿರಿ.
3. ಸ್ವಯಂ ಔಷಧಿ ಬೇಡ: ಬ್ರೂಫೆನ್ ಅಥವಾ ಆಸ್ಪಿರಿನ್ ಮಾತ್ರೆಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳಬೇಡಿ.
4. ಅಪಾಯಕಾರಿ ಲಕ್ಷಣಗಳು: ನಿರಂತರ ವಾಂತಿ, ಒಸಡುಗಳಿಂದ ರಕ್ತಸ್ರಾವವಾದರೆ ತಕ್ಷಣ ಆಸ್ಪತ್ರೆಗೆ ಭೇಟಿ ನೀಡಿ.',
        4,
        'Dr. Anand Gowda, Pediatrics & Fever Clinic',
        'https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?w=600&h=350&fit=crop'
    )
ON CONFLICT (id) DO NOTHING;

-- 5.4 Seed Sample Patient & Health Record for Immediate Dashboard Demo
INSERT INTO patients (id, full_name, email, phone, age, gender, blood_group, emergency_contact_name, emergency_contact_phone, preferred_language)
VALUES
    ('c1111111-1111-1111-1111-111111111111', 'Aditi Sharma', 'aditi.sharma@example.com', '+91 98765 43210', 29, 'Female', 'O+', 'Rohan Sharma (Spouse)', '+91 98765 12345', 'en')
ON CONFLICT (id) DO NOTHING;

-- 5.5 Seed Sample Vitals
INSERT INTO health_vitals (id, patient_id, blood_pressure_systolic, blood_pressure_diastolic, heart_rate, blood_sugar, temperature, weight_kg, height_cm)
VALUES
    ('v1111111-1111-1111-1111-111111111111', 'c1111111-1111-1111-1111-111111111111', 118, 78, 72, 94.0, 98.6, 62.5, 165.0)
ON CONFLICT (id) DO NOTHING;

-- 5.6 Seed Sample Medicine Reminders
INSERT INTO medicine_reminders (id, patient_id, medicine_name, dosage, frequency, reminder_time, timing_relation, start_date, is_active, status_today, notes)
VALUES
    ('m1111111-1111-1111-1111-111111111111', 'c1111111-1111-1111-1111-111111111111', 'Vitamin D3 (Cholecalciferol)', '60,000 IU', 'Weekly (Sunday)', '09:00 AM', 'after_food', CURRENT_DATE, true, 'taken', 'Prescribed for mild deficiency. Take with milk.'),
    ('m2222222-2222-2222-2222-222222222222', 'c1111111-1111-1111-1111-111111111111', 'Omega-3 Fish Oil', '1000 mg', 'Daily', '01:30 PM', 'after_food', CURRENT_DATE, true, 'pending', 'Heart and joint health maintenance.'),
    ('m3333333-3333-3333-3333-333333333333', 'c1111111-1111-1111-1111-111111111111', 'Magnesium Glycinate', '200 mg', 'Daily before bed', '09:30 PM', 'before_bed', CURRENT_DATE, true, 'pending', 'Supports deep sleep and muscle relaxation.')
ON CONFLICT (id) DO NOTHING;

-- 5.7 Seed Sample Upcoming Appointment
INSERT INTO appointments (id, patient_id, patient_name, patient_phone, patient_email, doctor_id, appointment_date, time_slot, reason, status, notes)
VALUES
    ('b1111111-1111-1111-1111-111111111111', 'c1111111-1111-1111-1111-111111111111', 'Aditi Sharma', '+91 98765 43210', 'aditi.sharma@example.com', 'd2222222-2222-2222-2222-222222222222', CURRENT_DATE + INTERVAL '2 day', '10:00 AM', 'Annual routine wellness checkup and blood panel review', 'Scheduled', 'First visit of the year')
ON CONFLICT (id) DO NOTHING;
