"""
====================================================================
MediCare AI - Google Gemini AI Service Layer
File: ai_service.py
Description: Clinical guardrails, multilingual prompt engineering,
             AI health chatbot, and symptom triage assessment using
             the Gemini API (google-genai SDK).
====================================================================
"""

import os
import json
import re
from typing import Dict, Any, List, Optional
from config import Config

# Language-specific disclaimers
DISCLAIMERS = {
    'en': (
        "⚠️ Medical Disclaimer: MediCare AI provides informational guidance only and is not a substitute "
        "for professional medical advice, clinical diagnosis, or treatment. Always consult a qualified "
        "physician for personal health concerns. In an emergency, call 108 or 112 immediately."
    ),
    'hi': (
        "⚠️ चिकित्सा अस्वीकरण: मेडीकेयर एआई केवल सूचनात्मक मार्गदर्शन प्रदान करता है और यह पेशेवर "
        "चिकित्सा सलाह, नैदानिक निदान या उपचार का विकल्प नहीं है। व्यक्तिगत स्वास्थ्य संबंधी चिंताओं के लिए "
        "हमेशा योग्य डॉक्टर से परामर्श लें। आपात स्थिति में तुरंत 108 या 112 पर कॉल करें।"
    ),
    'kn': (
        "⚠️ ವೈದ್ಯಕೀಯ ಹಕ್ಕುತ್ಯಾಗ: ಮೆಡಿಕೇರ್ ಎಐ ಕೇವಲ ಮಾಹಿತಿಯುಕ್ತ ಮಾರ್ಗದರ್ಶನವನ್ನು ನೀಡುತ್ತದೆ ಮತ್ತು ಇದು ವೃತ್ತಿಪರ "
        "ವೈದ್ಯಕೀಯ ಸಲಹೆ, ಕ್ಲಿನಿಕಲ್ ರೋಗನಿರ್ಣಯ ಅಥವಾ ಚಿಕಿತ್ಸೆಗೆ ಪರ್ಯಾಯವಲ್ಲ. ವೈಯಕ್ತಿಕ ಆರೋಗ್ಯ ಕಾಳಜಿಗಳಿಗಾಗಿ ಯಾವಾಗಲೂ "
        "ಅರ್ಹ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ. ತುರ್ತು ಪರಿಸ್ಥಿತಿಯಲ್ಲಿ ತಕ್ಷಣವೇ 108 ಅಥವಾ 112 ಗೆ ಕರೆ ಮಾಡಿ."
    )
}

LANGUAGE_NAMES = {
    'en': 'English',
    'hi': 'Hindi (हिंदी)',
    'kn': 'Kannada (ಕನ್ನಡ)'
}

# Red flag emergency keywords for safety gate
EMERGENCY_KEYWORDS = [
    'chest pain', 'heart attack', 'cannot breathe', 'difficulty breathing',
    'severe bleeding', 'stroke', 'unconscious', 'fainting', 'paralysis',
    'slurred speech', 'choking', 'poison', 'overdose', 'suicidal',
    'सीने में दर्द', 'सांस लेने में तकलीफ', 'बेहोश', 'लकवा',
    'ಎದೆ ನೋವು', 'ಉಸಿರಾಟದ ತೊಂದರೆ', 'ಪ್ರಜ್ಞಾಹೀನ', 'ಪಾರ್ಶ್ವವಾಯು'
]

def check_emergency_flags(text: str) -> bool:
    """Check if the patient input contains acute emergency keywords."""
    lower_text = text.lower()
    return any(keyword in lower_text for keyword in EMERGENCY_KEYWORDS)

def get_gemini_client():
    """Initialize and return Gemini client if api key is provided."""
    api_key = Config.GEMINI_API_KEY
    if not api_key or api_key == 'your_gemini_api_key_here':
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Warning: Could not initialize Gemini client: {e}")
        return None

def chat_with_health_assistant(user_message: str, history: List[Dict[str, str]] = None, language: str = 'en') -> Dict[str, Any]:
    """
    Empathetic, clinically guardrailed AI Health Chatbot.
    Enforces strict patient privacy and non-diagnostic framing.
    """
    history = history or []
    lang = language if language in ['en', 'hi', 'kn'] else 'en'
    target_lang = LANGUAGE_NAMES.get(lang, 'English')
    disclaimer = DISCLAIMERS.get(lang, DISCLAIMERS['en'])

    # Emergency tripwire
    is_emergency = check_emergency_flags(user_message)
    emergency_warning = ""
    if is_emergency:
        if lang == 'hi':
            emergency_warning = "🚨 **तत्काल आपातकालीन चेतावनी**: आपके द्वारा बताए गए लक्षण किसी गंभीर चिकित्सा आपातकाल का संकेत हो सकते हैं। कृपया तुरंत **108 (एम्बुलेंस)** या **112 (राष्ट्रीय आपातकाल)** पर कॉल करें या निकटतम आपातकालीन कक्ष में जाएं!\n\n"
        elif lang == 'kn':
            emergency_warning = "🚨 **ತುರ್ತು ಎಚ್ಚರಿಕೆ**: ನೀವು ತಿಳಿಸಿದ ಲಕ್ಷಣಗಳು ಗಂಭೀರ ವೈದ್ಯಕೀಯ ತುರ್ತು ಪರಿಸ್ಥಿತಿಯನ್ನು ಸೂಚಿಸಬಹುದು. ದಯವಿಟ್ಟು ತಕ್ಷಣವೇ **108 (ಆಂಬ್ಯುಲೆನ್ಸ್)** ಅಥವಾ **112 (ರಾಷ್ಟ್ರೀಯ ತುರ್ತು ಸಂಖ್ಯೆ)** ಗೆ ಕರೆ ಮಾಡಿ ಅಥವಾ ಹತ್ತಿರದ ಆಸ್ಪತ್ರೆಗೆ ಭೇಟಿ ನೀಡಿ!\n\n"
        else:
            emergency_warning = "🚨 **IMMEDIATE EMERGENCY ALERT**: The symptoms described may indicate an acute medical emergency. Please call **108 (Ambulance)** or **112 (National Emergency)** immediately or visit the nearest emergency room!\n\n"

    client = get_gemini_client()

    system_instruction = f"""
You are "MediCare AI", a warm, empathetic, and professional healthcare informational assistant.
You strictly adhere to modern medical ethics and patient safety protocols:

1. ABSOLUTE MEDICAL NON-DIAGNOSIS RULE:
   - Never state or suggest a definitive diagnosis.
   - Do not say "You have X". Instead say "These symptoms can sometimes be associated with X..." or "Possible general causes for such symptoms include...".
   - Never prescribe prescription-only pharmaceuticals, antibiotics, or dosages.

2. COMMUNICATION & LANGUAGE:
   - You MUST communicate entirely in {target_lang}.
   - Maintain a caring, respectful, reassuring, and clear tone suitable for all age groups.

3. RESPONSE STRUCTURE:
   - **General Understanding**: Acknowledge the user's concern empathetically.
   - **Informational Causes**: Mention 2-3 potential non-definitive possibilities for educational context.
   - **Safe Self-Care / Comfort Measures**: Non-invasive suggestions (hydration, rest, gentle comfort measures).
   - **When to Consult a Physician**: Specific warning signs requiring clinical attention.

4. DISCLAIMER REQUIREMENT:
   - Always conclude with the standard medical disclaimer.
"""

    if client:
        try:
            # Build conversation context
            conversation_text = ""
            for msg in history[-6:]:
                role = "User" if msg.get('sender') == 'user' else 'Assistant'
                conversation_text += f"{role}: {msg.get('message', '')}\n"
            conversation_text += f"User: {user_message}\nAssistant:"

            prompt = f"{system_instruction}\n\nRecent Conversation:\n{conversation_text}"
            
            response = client.models.generate_content(
                model=Config.GEMINI_MODEL,
                contents=prompt
            )
            ai_reply = response.text.strip()

            # Ensure disclaimer is attached
            if disclaimer not in ai_reply:
                ai_reply = f"{emergency_warning}{ai_reply}\n\n---\n{disclaimer}"
            else:
                ai_reply = f"{emergency_warning}{ai_reply}"

            return {
                "message": ai_reply,
                "language": lang,
                "is_emergency": is_emergency,
                "disclaimer": disclaimer,
                "model": Config.GEMINI_MODEL
            }

        except Exception as e:
            print(f"Gemini API Error in Chat: {e}")
            # Fallback to intelligent local response engine

    # Fallback response if Gemini API key is not configured or network issue
    fallback_text = generate_fallback_chat_reply(user_message, lang, is_emergency)
    return {
        "message": f"{emergency_warning}{fallback_text}\n\n---\n{disclaimer}",
        "language": lang,
        "is_emergency": is_emergency,
        "disclaimer": disclaimer,
        "model": "MediCare Clinical Knowledge Engine (Local Fallback)"
    }

def analyze_symptoms(symptoms_text: str, duration: str = "1-2 days", severity: str = "Mild", age_group: str = "Adult", language: str = 'en') -> Dict[str, Any]:
    """
    Comprehensive Symptom Information Checker.
    Evaluates urgency, recommends specialist, suggests comfort measures and questions for doctor.
    """
    lang = language if language in ['en', 'hi', 'kn'] else 'en'
    target_lang = LANGUAGE_NAMES.get(lang, 'English')
    disclaimer = DISCLAIMERS.get(lang, DISCLAIMERS['en'])

    is_emergency = check_emergency_flags(symptoms_text) or severity.lower() == 'severe'
    default_urgency = "Emergency" if is_emergency else ("Moderate" if severity.lower() == 'moderate' else "Low")

    client = get_gemini_client()

    prompt = f"""
You are an expert Clinical Triage Informational AI assisting a patient.
Patient Information:
- Symptoms: "{symptoms_text}"
- Duration: "{duration}"
- Stated Severity: "{severity}"
- Age Group: "{age_group}"
- Target Language: {target_lang}

TASK:
Analyze these symptoms strictly for informational guidance. NEVER PROVIDE A MEDICAL DIAGNOSIS.
You must respond with a valid JSON object matching the following structure in {target_lang}:

{{
    "urgency_level": "Low" | "Moderate" | "High" | "Emergency",
    "recommended_specialty": "e.g. General Medicine, Cardiology, Dermatologist, ENT, Orthopedics, etc.",
    "potential_considerations": ["Consideration 1 (framed non-diagnostically)", "Consideration 2", "Consideration 3"],
    "home_care_measures": ["Safe self-care tip 1", "Tip 2", "Tip 3"],
    "questions_for_doctor": ["Question 1 to ask physician", "Question 2 to ask physician", "Question 3"],
    "red_flags": ["Critical signs that require immediate hospital visit 1", "Sign 2"],
    "summary_explanation": "A gentle, 2-3 sentence overview explaining what these symptoms might indicate and the recommended course of action."
}}

JSON OUTPUT ONLY (no markdown fences, no extra text outside the JSON):
"""

    if client:
        try:
            response = client.models.generate_content(
                model=Config.GEMINI_MODEL,
                contents=prompt
            )
            raw_text = response.text.strip()
            
            # Clean markdown code blocks if returned
            clean_json = re.sub(r'^```json\s*', '', raw_text)
            clean_json = re.sub(r'^```\s*', '', clean_json)
            clean_json = re.sub(r'```$', '', clean_json).strip()

            parsed = json.loads(clean_json)
            parsed["disclaimer"] = disclaimer
            parsed["is_emergency"] = is_emergency or parsed.get("urgency_level") in ["High", "Emergency"]
            return parsed

        except Exception as e:
            print(f"Gemini API Error in Symptom Analysis: {e}")

    # Fallback structured assessment
    return generate_fallback_symptom_assessment(symptoms_text, duration, severity, age_group, lang, is_emergency)

def generate_fallback_chat_reply(message: str, lang: str, is_emergency: bool) -> str:
    """Pre-curated clinically verified responses for demo or fallback mode."""
    lower = message.lower()

    if lang == 'hi':
        if 'बुखार' in lower or 'fever' in lower:
            return (
                "**सामान्य बुखार के संबंध में जानकारी:**\n\n"
                "• **संभावित कारण**: मौसमी वायरल संक्रमण, थकान या प्रतिरक्षा प्रतिक्रिया।\n"
                "• **देखभाल के उपाय**: पर्याप्त आराम करें, खूब पानी और ओआरएस पिएं, माथे पर ठंडे पानी की पट्टी रखें।\n"
                "• **डॉक्टर से परामर्श कब लें**: यदि तापमान 102°F से अधिक हो, 3 दिनों से अधिक रहे, या तेज सिरदर्द व उल्टी हो।"
            )
        elif 'सिरदर्द' in lower or 'headache' in lower:
            return (
                "**सिरदर्द के संबंध में जानकारी:**\n\n"
                "• **संभावित कारण**: तनाव, नींद की कमी, निर्जलीकरण (पानी की कमी) या माइग्रेन।\n"
                "• **देखभाल के उपाय**: शांत और अंधेरे कमरे में आराम करें, पर्याप्त पानी पिएं, स्क्रीन से दूरी बनाएं।\n"
                "• **चेतावनी**: यदि सिरदर्द अचानक और बहुत तीव्र हो, या दृष्टि धुंधली हो, तो तुरंत चिकित्सा सहायता लें।"
            )
        else:
            return (
                "नमस्ते! मैं मेडीकेयर एआई हूँ। आपके द्वारा साझा की गई जानकारी के आधार पर, यह महत्वपूर्ण है कि आप अपने शरीर के संकेतों को ध्यान से समझें।\n\n"
                "• पर्याप्त तरल पदार्थों का सेवन करें और भरपूर नींद लें।\n"
                "• यदि लक्षण लगातार बने रहते हैं या बढ़ते हैं, तो कृपया हमारे 'डॉक्टर अपॉइंटमेंट' सेक्शन से किसी विशेषज्ञ से परामर्श लें।"
            )
    elif lang == 'kn':
        if 'ಜ್ವರ' in lower or 'fever' in lower:
            return (
                "**ಸಾಮಾನ್ಯ ಜ್ವರದ ಕುರಿತು ಮಾಹಿತಿ:**\n\n"
                "• **ಸಂಭಾವ್ಯ ಕಾರಣಗಳು**: ಕಾಲೋಚಿತ ವೈರಲ್ ಸೋಂಕು ಅಥವಾ ದೇಹದ ಆಯಾಸ.\n"
                "• **ಆರೈಕೆ ಕ್ರಮಗಳು**: ಸಾಕಷ್ಟು ವಿಶ್ರಾಂತಿ ಪಡೆಯಿರಿ, ಹೆಚ್ಚು ನೀರು ಮತ್ತು ಎಳನೀರು ಕುಡಿಯಿರಿ.\n"
                "• **ವೈದ್ಯರನ್ನು ಯಾವಾಗ ಸಂಪರ್ಕಿಸಬೇಕು**: ಜ್ವರ 3 ದಿನಗಳಿಗಿಂತ ಹೆಚ್ಚು ಕಾಲ ಮುಂದುವರಿದರೆ ಅಥವಾ ತೀವ್ರ ತಲೆನೋವು ಇದ್ದರೆ."
            )
        elif 'ತಲೆನೋವು' in lower or 'headache' in lower:
            return (
                "**ತಲೆನೋವಿನ ಕುರಿತು ಮಾಹಿತಿ:**\n\n"
                "• **ಸಂಭಾವ್ಯ ಕಾರಣಗಳು**: ಒತ್ತಡ, ನಿದ್ರೆಯ ಕೊರತೆ, ಡಿಹೈಡ್ರೇಶನ್ ಅಥವಾ ಮೈಗ್ರೇನ್.\n"
                "• **ಆರೈಕೆ ಕ್ರಮಗಳು**: ಕತ್ತಲೆಯಾದ ಶಾಂತ ಕೋಣೆಯಲ್ಲಿ ವಿಶ್ರಾಂತಿ ತೆಗೆದುಕೊಳ್ಳಿ, ಸಾಕಷ್ಟು ನೀರು ಕುಡಿಯಿರಿ.\n"
                "• **ಎಚ್ಚರಿಕೆ**: ತಲೆನೋವು ಹಠಾತ್ತನೆ ತೀವ್ರವಾದರೆ ತಕ್ಷಣ ವೈದ್ಯರನ್ನು ಭೇಟಿ ಮಾಡಿ."
            )
        else:
            return (
                "ನಮಸ್ಕಾರ! ನಾನು ಮೆಡಿಕೇರ್ ಎಐ. ನಿಮ್ಮ ಆರೋಗ್ಯ ಕಾಳಜಿಯನ್ನು ನಾನು ಅರ್ಥಮಾಡಿಕೊಂಡಿದ್ದೇನೆ.\n\n"
                "• ಸಾಕಷ್ಟು ವಿಶ್ರಾಂತಿ ಮತ್ತು ಆರೋಗ್ಯಕರ ಆಹಾರವನ್ನು ಸೇವಿಸಿ.\n"
                "• ಲಕ್ಷಣಗಳು ಮುಂದುವರಿದರೆ ನಮ್ಮ ಪ್ಲಾಟ್‌ಫಾರ್ಮ್ ಮೂಲಕ ನುರಿತ ವೈದ್ಯರೊಂದಿಗೆ ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್ ಕಾಯ್ದಿರಿಸಿ."
            )
    else:
        if 'fever' in lower or 'temperature' in lower:
            return (
                "**General Insights on Fever & Elevated Temperature:**\n\n"
                "• **Potential Considerations**: Acute viral response, mild seasonal infection, or immune activation.\n"
                "• **Comfort & Home Care**: Maintain diligent hydration (electrolytes, warm broths), get restorative bed rest, and dress in light, breathable cotton.\n"
                "• **When to Consult a Doctor**: If your temperature surpasses 102°F (38.9°C), persists past 72 hours, or is accompanied by a stiff neck or rash."
            )
        elif 'headache' in lower or 'migraine' in lower:
            return (
                "**General Insights on Headaches:**\n\n"
                "• **Potential Considerations**: Tension headache from screen fatigue, mild dehydration, lack of sleep, or postural neck strain.\n"
                "• **Comfort & Home Care**: Rest in a dimly lit, quiet room, apply a cool or warm compress to forehead, and hydrate with water.\n"
                "• **When to Consult a Doctor**: Seek urgent evaluation if the pain is sudden and explosive ('thunderclap'), accompanied by speech difficulty, or visual aura."
            )
        elif 'cough' in lower or 'cold' in lower:
            return (
                "**General Insights on Cough & Respiratory Discomfort:**\n\n"
                "• **Potential Considerations**: Upper respiratory tract viral infection, post-nasal drip, or environmental allergen irritation.\n"
                "• **Comfort & Home Care**: Steam inhalation twice daily, warm honey and ginger tea, and elevate your head while sleeping.\n"
                "• **When to Consult a Doctor**: If breathing feels labored, wheezing occurs, or phlegm contains streaks of blood."
            )
        else:
            return (
                "Hello! I am your MediCare AI healthcare assistant.\n\n"
                "I have registered your health query. While I can offer general health education and comfort guidance, "
                "a formal physical assessment by a licensed physician is always recommended for persistent symptoms.\n\n"
                "• Ensure optimal daily hydration and adequate sleep.\n"
                "• You can also browse our verified health articles or book a consultation with our listed specialists on the platform."
            )

def generate_fallback_symptom_assessment(symptoms: str, duration: str, severity: str, age_group: str, lang: str, is_emergency: bool) -> Dict[str, Any]:
    """Fallback structured assessment matching the required schema."""
    urgency = "Emergency" if is_emergency else ("Moderate" if severity.lower() == 'moderate' else "Low")
    specialty = "General Medicine"

    lower = symptoms.lower()
    if any(k in lower for k in ['skin', 'rash', 'itching', 'acne']):
        specialty = "Dermatology"
    elif any(k in lower for k in ['heart', 'chest', 'palpitation', 'pulse', 'bp']):
        specialty = "Cardiology"
    elif any(k in lower for k in ['bone', 'joint', 'knee', 'back', 'fracture', 'sprain']):
        specialty = "Orthopedics"
    elif any(k in lower for k in ['child', 'baby', 'infant']):
        specialty = "Pediatrics"
    elif any(k in lower for k in ['anxiety', 'depress', 'sleep', 'stress', 'mind']):
        specialty = "Psychiatry"

    if lang == 'hi':
        return {
            "urgency_level": urgency,
            "recommended_specialty": specialty,
            "potential_considerations": [
                f"{symptoms} से जुड़े सामान्य मौसमी अथवा जीवनशैली कारक",
                "शरीर की सामान्य रोग प्रतिरोधक प्रतिक्रिया",
                "पर्याप्त पोषण या जलयोजन की कमी"
            ],
            "home_care_measures": [
                "पर्याप्त मात्रा में पानी, नारियल पानी अथवा ओआरएस का सेवन करें।",
                "दिन में कम से कम 7-8 घंटे का पूर्ण विश्राम लें।",
                "तली-भुनी चीजों से परहेज करें और हल्का सुपाच्य भोजन लें।"
            ],
            "questions_for_doctor": [
                "क्या इन लक्षणों के लिए कोई विशिष्ट रक्त परीक्षण आवश्यक है?",
                "क्या कोई आहार या दैनिक गतिविधि संबंधी सावधानी बरतनी चाहिए?",
                "लक्षण कितने दिनों में पूरी तरह ठीक होने की संभावना है?"
            ],
            "red_flags": [
                "सांस लेने में अत्यधिक कठिनाई या सीने में भारीपन।",
                "तापमान 103°F से अधिक होना या लगातार उल्टी होना।",
                "अचानक अत्यधिक कमजोरी या दृष्टि में धुंधलापन।"
            ],
            "summary_explanation": f"आपके द्वारा बताए गए लक्षणों ({symptoms}) की गंभीरता {severity} स्तर की है। इस स्थिति में प्राथमिक स्व-देखभाल के साथ {specialty} के विशेषज्ञ से सलाह लेना उचित रहेगा।",
            "disclaimer": DISCLAIMERS['hi'],
            "is_emergency": is_emergency
        }
    elif lang == 'kn':
        return {
            "urgency_level": urgency,
            "recommended_specialty": specialty,
            "potential_considerations": [
                f"{symptoms} ಗೆ ಸಂಬಂಧಿಸಿದ ಸಾಮಾನ್ಯ ಕಾಲೋಚಿತ ಲಕ್ಷಣಗಳು",
                "ದೇಹದ ನೈಸರ್ಗಿಕ ರೋಗನಿರೋಧಕ ಪ್ರತಿಕ್ರಿಯೆ",
                "ದಣಿವು ಅಥವಾ ದ್ರವಾಂಶದ ಕೊರತೆ"
            ],
            "home_care_measures": [
                "ಸಾಕಷ್ಟು ನೀರು, ಎಳನೀರು ಅಥವಾ ORS ಕುಡಿಯಿರಿ.",
                "ದಿನಕ್ಕೆ 7-8 ಗಂಟೆಗಳ ಕಾಲ ಸಂಪೂರ್ಣ ವಿಶ್ರಾಂತಿ ತೆಗೆದುಕೊಳ್ಳಿ.",
                "ಹಗುರವಾದ ಮತ್ತು ಸುಲಭವಾಗಿ ಜೀರ್ಣವಾಗುವ ಆಹಾರವನ್ನು ಸೇವಿಸಿ."
            ],
            "questions_for_doctor": [
                "ಈ ಲಕ್ಷಣಗಳಿಗೆ ಯಾವುದೇ ನಿರ್ದಿಷ್ಟ ರಕ್ತ ಪರೀಕ್ಷೆ ಅಗತ್ಯವಿದೆಯೇ?",
                "ಯಾವ ರೀತಿಯ ಆಹಾರ ಪಥ್ಯವನ್ನು ಅನುಸರಿಸಬೇಕು?",
                "ಎಷ್ಟು ದಿನಗಳಲ್ಲಿ ಇವು ಗುಣಮುಖವಾಗಬಹುದು?"
            ],
            "red_flags": [
                "ಉಸಿರಾಟದಲ್ಲಿ ತೀವ್ರ ತೊಂದರೆ ಅಥವಾ ಎದೆ ನೋವು.",
                "ಜ್ವರ 103°F ಗಿಂತ ಹೆಚ್ಚಾಗುವುದು ಅಥವಾ ನಿರಂತರ ವಾಂತಿ.",
                "ಹಠಾತ್ ದೌರ್ಬಲ್ಯ ಅಥವಾ ದೃಷ್ಟಿ ಮಂದವಾಗುವುದು."
            ],
            "summary_explanation": f"ನೀವು ನಮೂದಿಸಿದ ಲಕ್ಷಣಗಳು ({symptoms}) {severity} ಹಂತದಲ್ಲಿದೆ. ಸೂಕ್ತ ಆರೈಕೆಯೊಂದಿಗೆ {specialty} ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸುವುದು ಸೂಕ್ತವಾಗಿದೆ.",
            "disclaimer": DISCLAIMERS['kn'],
            "is_emergency": is_emergency
        }
    else:
        return {
            "urgency_level": urgency,
            "recommended_specialty": specialty,
            "potential_considerations": [
                f"Informational association with standard physiological stress or seasonal factors",
                "Mild transient inflammatory or immune system response",
                "Dehydration, physical fatigue, or environmental triggers"
            ],
            "home_care_measures": [
                "Maintain optimal hydration with water, electrolyte drinks, or clear broths.",
                "Ensure 7 to 8 hours of quiet, restorative rest without physical strain.",
                "Eat light, easily digestible meals and avoid high-sodium or fried items."
            ],
            "questions_for_doctor": [
                "Are there specific diagnostic blood tests or imaging recommended for these symptoms?",
                "Could any lifestyle or dietary adjustments accelerate recovery?",
                "What timeline should I expect before these symptoms resolve completely?"
            ],
            "red_flags": [
                "Severe shortness of breath, chest constriction, or blue lips.",
                "Spiking fever exceeding 103°F or persistent inability to keep fluids down.",
                "Sudden weakness on one side of the body or changes in mental alertness."
            ],
            "summary_explanation": f"Based on your report of '{symptoms}' with {severity} intensity over {duration}, this assessment indicates a {urgency} urgency profile. We recommend scheduling a consultation with a {specialty} specialist.",
            "disclaimer": DISCLAIMERS['en'],
            "is_emergency": is_emergency
        }
