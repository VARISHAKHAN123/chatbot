import joblib

# Load the model, vectorizer, and label encoder
model = joblib.load("intent_classifier.pkl")
vectorizer = joblib.load("vectorizer.pkl")
label_encoder = joblib.load("label_encoder.pkl")

# English Responses
responses_en = {
    "fever": "😷 You have a fever. Please rest and drink fluids!",
    "cold": "🥶 You seem to have a cold. Stay warm and hydrated!",
    "cough": "🤧 You're coughing a lot. Try warm water and rest!",
    "sore_throat": "😖 Sore throat detected. Gargle with warm salt water!",
    "symptoms": "📋 Common symptoms: fever, cold, cough, sore throat."
}

# Hindi Responses
responses_hi = {
    "fever": "😷 Aapko bukhar hai. Kripya aaram karein aur paani piyen!",
    "cold": "🥶 Aapko sardee ho gayi hai. Garam kapde pehnen aur aaram karein!",
    "cough": "🤧 Aapko khansi hai. Garam paani piyen aur rest karein!",
    "sore_throat": "😖 Gala dard hai. Garam paani se gargle karein!",
    "symptoms": "📋 Aam lakshan: bukhar, sardee, khansi, gala dard."
}

# Language Detection
def detect_language(text):
    hindi_words = ["bukhar", "sardi", "khansi", "gala", "dard", "hai", "ho raha", "ho rahi", "lag gayi"]
    for word in hindi_words:
        if word.lower() in text.lower():
            return "hi"
    return "en"

# Predict Intent and Give Response
def predict_intent(user_input):
    user_input_vectorized = vectorizer.transform([user_input])
    prediction = model.predict(user_input_vectorized)
    predicted_label = label_encoder.inverse_transform(prediction)[0]
    
    lang = detect_language(user_input)
    
    if lang == "hi":
        return responses_hi.get(predicted_label, "😕 Maaf kijiye, main samajh nahi paya.")
    else:
        return responses_en.get(predicted_label, "😕 Sorry, I couldn't understand.")

# Test loop
if __name__ == "__main__":
    while True:
        user_input = input("\n💬 Enter your message (or type 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        response = predict_intent(user_input)
        print("🤖:", response)
