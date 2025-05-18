import random
from flask import jsonify
import spacy
from spacy.matcher import PhraseMatcher
from utils.language_utils import (
    detect_language,
    match_keywords,
    responses,
    suggest_medicine,
    emergency_keywords
)

# Load English spaCy model
nlp = spacy.load("en_core_web_sm")

# Diabetes-specific symptoms (Hindi + English)
diabetes_symptom_keywords = [
    "थकान", "थकावट", "बार-बार पेशाब", "बहुत प्यास लगना", "वज़न घटना", "धुंधली दृष्टि", "थकान महसूस",
    "fatigue", "frequent urination", "excessive thirst", "blurred vision", "weight loss"
]

# Main symptom keyword list for NLP
symptom_keywords = [
    "fever", "cold", "headache", "cough", "vomiting", "sore throat", "diarrhea", "stomach pain", "body pain",
    "fatigue", "chills", "weight loss", "appetite loss", "night sweats", "dizziness", "weakness",
    "shortness of breath", "unusual thirst", "sudden vision changes", "confusion or memory loss",
    "muscle or joint pain", "chest pain", "abdominal pain", "back pain", "throat pain", "leg pain",
    "pelvic pain", "painful urination", "nausea", "constipation", "indigestion", "heartburn", "bloating",
    "blood in stool", "dark urine", "pale stool", "itching", "skin rash", "jaundice", "blisters",
    "dry cracked skin", "bruising", "sweating", "changes in skin color", "redness or inflammation",
    "tingling or numbness", "seizures", "tremors", "balance problems", "difficulty speaking", "slurred speech",
    "weak coordination", "memory loss", "numbness or paralysis", "wheezing", "sore throat", "blood in cough",
    "chest tightness", "frequent urination", "blood in urine", "hot flashes", "unexplained weight gain",
    "increased sweating", "hair loss", "change in skin or nail texture", "depression", "anxiety", "irritability",
    "sleep problems", "mood swings", "irregular periods", "heavy bleeding", "painful intercourse",
    "vaginal discharge", "difficulty in erection", "testicular pain", "changes in libido", "heart palpitations",
    "swollen legs or feet", "high blood pressure"
]

# Setup PhraseMatcher for NLP-based symptom extraction
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
matcher.add("SYMPTOM", [nlp.make_doc(text.lower()) for text in symptom_keywords])

def extract_symptoms_nlp(text):
    doc = nlp(text.lower())
    matches = matcher(doc)
    return list(set([doc[start:end].text for _, start, end in matches]))

def contains_diabetes_symptom(message):
    return any(symptom.lower() in message.lower() for symptom in diabetes_symptom_keywords)

def handle_user_message(request, session, conn):
    cursor = conn.cursor()
    user_message = request.form['message']
    language = detect_language(user_message)

    # 1. Diabetes symptom check
    if contains_diabetes_symptom(user_message):
        return jsonify({
            "message": "⚠️ आपकी थकावट diabetes का लक्षण हो सकती है, कृपया नीचे form भरकर test कीजिए।",
            "trigger_diabetes_form": True
        })
 
    # 2. Emergency check
    if any(keyword in user_message.lower() for keyword in emergency_keywords):
        emergency_msg = {
            'en': "🚑 Emergency detected! Please call 108 or visit the nearest hospital immediately.",
            'hi': "🚑 आपातकालीन स्थिति! कृपया तुरंत 108 पर कॉल करें या निकटतम अस्पताल जाएं।"
        }
        return jsonify({'message': emergency_msg[language]})

    # 3. NLP-based symptom extraction
    extracted_symptoms = extract_symptoms_nlp(user_message)
    intent = extracted_symptoms[0] if extracted_symptoms else match_keywords(user_message)

    # 4. Get bot message
    bot_message = random.choice(responses.get(intent, responses['default'])[language])

    # 5. Store in database
    cursor.execute(
        "INSERT INTO chat_logs (user_message, bot_response, intent, language) VALUES (%s, %s, %s, %s)",
        (user_message, bot_message, intent, language)
    )
    conn.commit()
    cursor.close()

    # 6. Save to session
    session['symptom'] = intent
    session['language'] = language

    # 7. Ask for age if relevant
    if intent in responses:
        bot_message += " कृपया अपनी उम्र बताइए ताकि दवा का सुझाव दिया जा सके।" if language == 'hi' else " Please tell your age so that I can suggest medicine."

    return jsonify({'message': bot_message, 'symptom': intent})

def handle_age_input(request, session, conn):
    age_input = request.form['age']
    try:
        age = int(age_input)
    except ValueError:
        return jsonify({'message': "Please enter a valid age."})

    symptom = session.get('symptom')
    language = session.get('language', 'en')

    if symptom:
        medicine = suggest_medicine(age, symptom, language)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_logs (user_message, bot_response, intent, language) VALUES (%s, %s, %s, %s)",
            (f"Age: {age}", medicine, "medicine_suggestion", language)
        )
        conn.commit()
        cursor.close()
        session['symptom'] = None
        return jsonify({'message': medicine})

    return jsonify({'message': "No symptoms detected yet."})


def generate_mental_health_response(stress_level, trouble_sleeping, need_support):
    stress_level = int(stress_level)
    trouble_sleeping = trouble_sleeping.lower() == 'yes'
    need_support = need_support.lower() == 'yes'

    # Stress response
    if stress_level >= 80:
        stress_msg = (
            "😟 You're going through a very stressful time. "
            "Please remember, it's okay to not be okay. Try deep breathing, meditation, or journaling to ease your mind."
        )
    elif 50 <= stress_level < 80:
        stress_msg = (
            "😐 It looks like you're experiencing moderate stress. "
            "Take breaks, talk to someone you trust, and don’t ignore how you feel."
        )
    elif 20 <= stress_level < 50:
        stress_msg = (
            "🙂 Your stress seems manageable, but don’t forget to take care of your mental peace. "
            "Keep up the good habits!"
        )
    else:
        stress_msg = (
            "😌 Great! Your stress level is low. Keep nurturing your mental well-being with positivity and balance."
        )

    # Sleep response
    if trouble_sleeping:
        sleep_msg = (
            "🌙 Trouble sleeping can worsen stress. Try creating a relaxing bedtime routine, "
            "limit screen time before bed, and maintain a regular sleep schedule."
        )
    else:
        sleep_msg = "🌟 It's great that you're sleeping well! Good sleep is essential for a healthy mind."

    # Support response
    if need_support:
        support_msg = (
            "🧠 You said you need support. Please know that you're not alone. "
            "Talking to a friend, loved one, or therapist can truly help. I'm here to listen whenever you need."
        )
    else:
        support_msg = (
            "🤝 Even if you feel you don’t need support right now, it’s always okay to reach out later. "
            "Support is always available — don’t hesitate."
        )

    # Final combined message
    final_msg = f"{stress_msg}\n\n{sleep_msg}\n\n{support_msg}"
    return final_msg
