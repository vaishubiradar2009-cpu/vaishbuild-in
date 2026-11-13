"""
====================================================================
MediCare AI - Flask Application & API Router
File: app.py
Description: Modern AI-powered healthcare web platform backend
             with Gemini API, Supabase/SQLite persistence,
             multilingual support (EN, HI, KN), and clinical guardrails.
====================================================================
"""

import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from config import Config
import db
import ai_service

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config.from_object(Config)

# Initialize local database schema & seed data if needed
with app.app_context():
    db.init_sqlite_db()

# ====================================================================
# Frontend Web Routes
# ====================================================================

@app.route('/')
def index():
    """Renders the main single-page dashboard application."""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health status and configured capabilities."""
    return jsonify({
        "status": "healthy",
        "service": "MediCare AI Platform",
        "gemini_configured": bool(Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != 'your_gemini_api_key_here'),
        "gemini_model": Config.GEMINI_MODEL,
        "database": "Supabase PostgreSQL" if Config.SUPABASE_DB_URL else "SQLite (medicare.db)",
        "supported_languages": ["en", "hi", "kn"]
    })

# ====================================================================
# 1. AI Health Chatbot Endpoints
# ====================================================================

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """
    Conversational AI Health Chatbot with safety guardrails
    and multilingual support.
    """
    data = request.get_json(silent=True) or {}
    user_message = data.get('message', '').strip()
    session_id = data.get('session_id') or str(uuid.uuid4())
    language = data.get('language', 'en').lower()

    if not user_message:
        return jsonify({"error": "Message content cannot be empty"}), 400

    if language not in ['en', 'hi', 'kn']:
        language = 'en'

    # Save user message to database
    db.save_chat_message(session_id, 'user', user_message, language)

    # Fetch recent session history for conversational context
    history = db.get_chat_history(session_id, limit=6)

    # Generate guardrailed AI response via Gemini
    ai_result = ai_service.chat_with_health_assistant(user_message, history, language)

    # Save assistant message to database
    db.save_chat_message(session_id, 'ai', ai_result['message'], language)

    return jsonify({
        "session_id": session_id,
        "reply": ai_result['message'],
        "language": ai_result['language'],
        "is_emergency": ai_result['is_emergency'],
        "disclaimer": ai_result['disclaimer'],
        "model": ai_result['model']
    })

@app.route('/api/chat/history/<session_id>', methods=['GET'])
def get_chat_history_endpoint(session_id):
    """Retrieve chat history for a session."""
    history = db.get_chat_history(session_id, limit=20)
    return jsonify({"session_id": session_id, "messages": history})

# ====================================================================
# 2. Symptom Information Checker Endpoints
# ====================================================================

@app.route('/api/symptoms/check', methods=['POST'])
def symptom_checker_endpoint():
    """
    Analyze symptoms for informational guidance and triage urgency.
    Never presents conclusions as a medical diagnosis.
    """
    data = request.get_json(silent=True) or {}
    symptoms_text = data.get('symptoms_text', '').strip()
    duration = data.get('duration', '1-2 days')
    severity = data.get('severity', 'Mild')
    age_group = data.get('age_group', 'Adult')
    language = data.get('language', 'en').lower()
    patient_name = data.get('patient_name', 'Aditi Sharma')

    if not symptoms_text:
        return jsonify({"error": "Please describe your symptoms"}), 400

    if language not in ['en', 'hi', 'kn']:
        language = 'en'

    # Execute AI symptom triage assessment
    assessment = ai_service.analyze_symptoms(
        symptoms_text=symptoms_text,
        duration=duration,
        severity=severity,
        age_group=age_group,
        language=language
    )

    # Persist assessment record to database
    assessment_id = db.save_symptom_assessment({
        "patient_id": 'c1111111-1111-1111-1111-111111111111',
        "patient_name": patient_name,
        "symptoms_text": symptoms_text,
        "duration": duration,
        "severity": severity,
        "age_group": age_group,
        "language": language,
        "ai_analysis": assessment.get('summary_explanation', ''),
        "urgency_level": assessment.get('urgency_level', 'Low'),
        "recommended_specialty": assessment.get('recommended_specialty', 'General Medicine')
    })

    assessment["id"] = assessment_id
    return jsonify(assessment)

@app.route('/api/symptoms/history', methods=['GET'])
def symptom_history_endpoint():
    """Get previous symptom assessment records."""
    history = db.get_symptom_assessments(limit=10)
    return jsonify({"assessments": history})

# ====================================================================
# 3. Doctor Appointment Booking Endpoints
# ====================================================================

@app.route('/api/doctors', methods=['GET'])
def get_doctors_endpoint():
    """List doctors, optionally filtered by medical specialty."""
    specialty = request.args.get('specialty')
    doctors = db.get_doctors(specialty=specialty)
    return jsonify({"doctors": doctors, "count": len(doctors)})

@app.route('/api/doctors/<doctor_id>', methods=['GET'])
def get_doctor_endpoint(doctor_id):
    """Retrieve details for a single doctor."""
    doctor = db.get_doctor_by_id(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404
    return jsonify({"doctor": doctor})

@app.route('/api/appointments', methods=['GET'])
def get_appointments_endpoint():
    """List scheduled patient appointments."""
    appointments = db.get_appointments()
    return jsonify({"appointments": appointments, "count": len(appointments)})

@app.route('/api/appointments', methods=['POST'])
def book_appointment_endpoint():
    """Book a new doctor appointment."""
    data = request.get_json(silent=True) or {}
    required_fields = ['doctor_id', 'patient_name', 'patient_phone', 'appointment_date', 'time_slot']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400

    result = db.create_appointment(data)
    return jsonify(result), 201

@app.route('/api/appointments/<appointment_id>/cancel', methods=['POST', 'PATCH'])
def cancel_appointment_endpoint(appointment_id):
    """Cancel an appointment."""
    success = db.cancel_appointment(appointment_id)
    if not success:
        return jsonify({"error": "Appointment not found or already cancelled"}), 404
    return jsonify({"status": "success", "message": "Appointment cancelled successfully"})

# ====================================================================
# 4. Medicine Reminders Endpoints
# ====================================================================

@app.route('/api/medicines', methods=['GET'])
def get_medicines_endpoint():
    """Retrieve active medicine reminders."""
    meds = db.get_medicines()
    return jsonify({"medicines": meds, "count": len(meds)})

@app.route('/api/medicines', methods=['POST'])
def add_medicine_endpoint():
    """Add a new medicine reminder."""
    data = request.get_json(silent=True) or {}
    if not data.get('medicine_name') or not data.get('dosage'):
        return jsonify({"error": "Medicine name and dosage are required"}), 400

    result = db.create_medicine(data)
    return jsonify(result), 201

@app.route('/api/medicines/<medicine_id>/status', methods=['PATCH'])
def update_medicine_status_endpoint(medicine_id):
    """Update medicine compliance status for today ('taken', 'skipped', 'pending')."""
    data = request.get_json(silent=True) or {}
    status = data.get('status', 'taken')
    if status not in ['taken', 'skipped', 'pending']:
        return jsonify({"error": "Invalid status value"}), 400

    success = db.update_medicine_status(medicine_id, status)
    if not success:
        return jsonify({"error": "Reminder not found"}), 404
    return jsonify({"status": "success", "medicine_id": medicine_id, "new_status": status})

@app.route('/api/medicines/<medicine_id>', methods=['DELETE'])
def delete_medicine_endpoint(medicine_id):
    """Delete a medicine reminder."""
    success = db.delete_medicine(medicine_id)
    if not success:
        return jsonify({"error": "Reminder not found"}), 404
    return jsonify({"status": "success", "message": "Reminder removed successfully"})

# ====================================================================
# 5. Health Awareness Articles Endpoints
# ====================================================================

@app.route('/api/articles', methods=['GET'])
def get_articles_endpoint():
    """Retrieve health awareness articles localized in EN, HI, or KN."""
    category = request.args.get('category')
    lang = request.args.get('lang', 'en').lower()
    if lang not in ['en', 'hi', 'kn']:
        lang = 'en'

    articles = db.get_articles(category=category, lang=lang)
    return jsonify({"articles": articles, "count": len(articles), "language": lang})

@app.route('/api/articles/<article_id>', methods=['GET'])
def get_article_endpoint(article_id):
    """Retrieve full content for a single article."""
    lang = request.args.get('lang', 'en').lower()
    if lang not in ['en', 'hi', 'kn']:
        lang = 'en'

    article = db.get_article_by_id(article_id, lang=lang)
    if not article:
        return jsonify({"error": "Article not found"}), 404
    return jsonify({"article": article, "language": lang})

# ====================================================================
# 6. Emergency Contacts & Guidelines Endpoints
# ====================================================================

@app.route('/api/emergency', methods=['GET'])
def get_emergency_endpoint():
    """Retrieve verified 24/7 emergency helplines localized in EN, HI, or KN."""
    lang = request.args.get('lang', 'en').lower()
    if lang not in ['en', 'hi', 'kn']:
        lang = 'en'

    contacts = db.get_emergency_contacts(lang=lang)
    return jsonify({
        "contacts": contacts,
        "primary_emergency_numbers": [
            {"service": "Ambulance", "number": "108", "desc": "Medical Emergency Response"},
            {"service": "National Emergency", "number": "112", "desc": "Police, Fire, Medical"},
            {"service": "Tele-MANAS", "number": "14416", "desc": "Mental Health Counseling"},
            {"service": "Maternity", "number": "102", "desc": "Janani Shishu Suraksha"}
        ],
        "language": lang
    })

# ====================================================================
# 7. Patient Health Dashboard & Vitals Endpoints
# ====================================================================

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_endpoint():
    """Unified patient dashboard summary."""
    summary = db.get_dashboard_summary()
    return jsonify(summary)

@app.route('/api/vitals', methods=['POST'])
def update_vitals_endpoint():
    """Log updated patient health vitals."""
    data = request.get_json(silent=True) or {}
    result = db.update_health_vitals(data)
    return jsonify(result), 201

# ====================================================================
# Error Handlers
# ====================================================================

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({"error": "API route not found"}), 404
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error", "detail": str(e)}), 500

if __name__ == '__main__':
    print("=" * 65)
    print("🏥 MediCare AI Healthcare Web Application Running")
    print(f"🌐 Access Web Interface: http://localhost:{Config.PORT}")
    print(f"📊 Gemini AI Configured: {bool(Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != 'your_gemini_api_key_here')}")
    print(f"🗄️ Database Backend: {'Supabase Cloud PostgreSQL' if Config.SUPABASE_DB_URL else 'SQLite Local Database'}")
    print("=" * 65)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
