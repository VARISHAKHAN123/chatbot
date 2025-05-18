from flask import Blueprint, redirect, request, jsonify, render_template, session, current_app, url_for
from services.symptom_service import handle_user_message, handle_age_input
from services.doctor_service import get_doctor_list
from services.predict_disease import predict_diabetes, predict_heart_disease
from langdetect import detect
from flask import request, jsonify



chat_bp = Blueprint('chat_bp', __name__)
chat_logs_bp = Blueprint('chat_logs_bp', __name__)
# ===============================
# Main Page
# ===============================
@chat_bp.route('/')
def index():
    return render_template('index.html')

# ===============================
# Chat Handler
# ===============================
@chat_bp.route('/get', methods=['POST'])
def get_response():
    return handle_user_message(request, session, current_app.conn)

# ===============================
# Age Handler
# ===============================
@chat_bp.route('/age', methods=['POST'])
def age_response():
    return handle_age_input(request, session, current_app.conn)

# ===============================
# Doctor Lookup
# ===============================
@chat_bp.route('/doctor', methods=['POST'])
def doctor_response():
    location = request.form.get('location')
    language = session.get('language', 'en')

    if not location:
        return jsonify({'message': 'Location not provided'}), 400

    doctor_info = get_doctor_list(location.lower(), language, session)
    return jsonify({'message': doctor_info})


# ===============================
# Diabetes Prediction (Step-by-step)
# ===============================
DIABETES_QUESTIONS = [
    ("Pregnancies", "Pregnancies"),
    ("Glucose level", "Glucose"),
    ("Blood Pressure", "BloodPressure"),
    ("Skin Thickness", "SkinThickness"),
    ("Insulin level", "Insulin"),
    ("BMI value", "BMI"),
    ("Diabetes Pedigree Function", "DiabetesPedigreeFunction"),
    ("Age", "Age")
]

@chat_bp.route('/chat/diabetes', methods=['POST'])
def diabetes_flow():
    if 'diabetes_step' not in session:
        session['diabetes_step'] = 0
        session['diabetes_data'] = {}

    step = session['diabetes_step']
    data = request.get_json()
    user_msg = data.get('message', '').strip()

    if step < len(DIABETES_QUESTIONS):
        if step > 0:
            key = DIABETES_QUESTIONS[step - 1][1]
            try:
                val = float(user_msg) if '.' in user_msg else int(user_msg)
                session['diabetes_data'][key] = val
            except ValueError:
                return jsonify({'message': f"Invalid input for {key}. Please enter a numeric value."})

        question_text = DIABETES_QUESTIONS[step][0]
        session['diabetes_step'] += 1
        return jsonify({'message': f"Please enter {question_text}:"})

    data = session.pop('diabetes_data', {})
    session.pop('diabetes_step', None)
    prediction = predict_diabetes(data)
    return jsonify({
    'message': f"Prediction result: {prediction}",
    'prediction': prediction
})



# ===============================
# Diabetes Prediction (Direct API)
# ===============================


@chat_bp.route('/predict/diabetes', methods=['POST'])
def predict_diabetes_form():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400  # Handle case where no data is sent
        prediction = predict_diabetes(data)
        return jsonify({'prediction': prediction})
    except Exception as e:
        print("Prediction Error:", e)
        return jsonify({'error': 'Prediction failed', 'message': str(e)}), 500  # Include the error message for debugging

@chat_bp.route('/chat/diabetes_form', methods=['POST'])
def diabetes_form_predict():
    data = request.get_json()
    prediction = predict_diabetes(data)
    return jsonify({
        'message': f"Prediction result: {prediction}",
        'prediction': prediction
    })


# ===============================
# Heart Disease Prediction
# ===============================



@chat_bp.route('/predict_heart', methods=['GET', 'POST'])
def predict_heart():
    if request.method == 'POST':
        try:
            input_data = {
                'age': int(request.form['age']),
                'sex': int(request.form['sex']),
                'cp': int(request.form['cp']),
                'trestbps': int(request.form['trestbps']),
                'chol': int(request.form['chol']),
                'fbs': int(request.form['fbs']),
                'restecg': int(request.form['restecg']),
                'thalach': int(request.form['thalach']),
                'exang': int(request.form['exang']),
                'oldpeak': float(request.form['oldpeak']),
                'slope': int(request.form['slope']),
                'ca': int(request.form['ca']),
                'thal': int(request.form['thal']),
            }
            result = predict_heart_disease(input_data)
            return render_template('heart_result.html', result=result)
        except Exception as e:
            return f"Error: {e}", 400
    return render_template('heart_form.html')


@chat_bp.route('/try_again')
def try_again():
    return redirect(url_for('index.html'))  


# ===============================
# Chat Logs Viewer
# ===============================
@chat_logs_bp.route('/chat_logs')
def chat_logs():
    cursor = current_app.conn.cursor()
    cursor.execute("SELECT user_message, bot_response, intent, language, timestamp FROM chat_logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    cursor.close()
    log_data = [
        {
            'user_message': row[0],
            'bot_response': row[1],
            'intent': row[2],
            'language': row[3],
            'timestamp': row[4]
        }
        for row in logs
    ]
    return render_template("chat_logs.html", logs=log_data)



# Mental Health Assessment
# ===============================
@chat_bp.route('/mental_assessment', methods=['POST'])
def handle_mental_assessment():
    data = request.json
    return jsonify({"message": '''Assessment submitted successfully. You're not alone 😟 — this can be managed, even without medication.

🌬️ **1. Deep Breathing (Box Breathing)**  
Inhale 4s → Hold 4s → Exhale 4s → Hold 4s

🚶 **2. 20-Minute Walk Outdoors**  
No phone. Look at nature. Boosts serotonin & lowers cortisol.

🎵 **3. Calming Instrumental Music**  
Activates alpha waves, reduces stress.

🌙 **4. Sleep Routine**  
- No screens before bed  
- Warm milk or chamomile tea  
- Write thoughts in a journal  
- Read a boring book to fall asleep  
- 4-7-8 breathing technique

🧠 **5. Paradoxical Intention**  
Try telling yourself: “I want to stay awake.” It often tricks your brain into sleeping.

🕯️ **6. Lavender Oil or Scent**  
Scientifically proven to lower anxiety.

❤️ **Support Options**  
- Talk to a friend or sibling — just 10 honest minutes help.  
- Record voice notes or journal.  
- Use anonymous support groups (7 Cups, Reddit r/KindVoice).

You’re never alone. I'm always here for you 🤗'''})





