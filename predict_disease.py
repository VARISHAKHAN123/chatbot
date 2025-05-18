import numpy as np
import pandas as pd
import joblib

# Load models
diabetes_model = joblib.load('diabetes_model.pkl')
heart_model = joblib.load('models/heart_model.pkl')
heart_columns = joblib.load('models/heart_columns.pkl')  # list of columns used in training

# ================================
# Diabetes Prediction Function
# ================================
def predict_diabetes(data_dict):
    """
    data_dict = {
        'Pregnancies': 2,
        'Glucose': 130,
        'BloodPressure': 80,
        'SkinThickness': 25,
        'Insulin': 85,
        'BMI': 28.0,
        'DiabetesPedigreeFunction': 0.45,
        'Age': 35
    }
    """
    input_data = np.array([
        data_dict['Pregnancies'],
        data_dict['Glucose'],
        data_dict['BloodPressure'],
        data_dict['SkinThickness'],
        data_dict['Insulin'],
        data_dict['BMI'],
        data_dict['DiabetesPedigreeFunction'],
        data_dict['Age']
    ]).reshape(1, -1)

    prediction = diabetes_model.predict(input_data)
    return "Positive for Diabetes" if prediction[0] == 1 else "Negative for Diabetes"

#heart disease 

# ✅ Load model and feature columns
model = joblib.load('models/heart_model.pkl')
columns = joblib.load('models/heart_columns.pkl')

# ================================
# Heart Disease Prediction Function (Final Working Version)
# ================================
def predict_heart_disease(input_data):
    """
    input_data example from HTML form:
    {
        'age': 45,
        'sex': 0,
        'cp': 0,
        'trestbps': 120,
        'chol': 180,
        'fbs': 0,
        'restecg': 0,
        'thalach': 160,
        'exang': 0,
        'oldpeak': 0.0,
        'slope': 0,
        'ca': 0,
        'thal': 0
    }
    """

    # Convert to DataFrame
    df = pd.DataFrame([input_data])

    # One-hot encode categorical variables
    df_encoded = pd.get_dummies(df)

    # Fill missing columns (that were present during training)
    for col in heart_columns:
        if col not in df_encoded:
            df_encoded[col] = 0

    # Reorder columns to match training order
    df_encoded = df_encoded[heart_columns]

    # Predict
    prediction = heart_model.predict(df_encoded)

    if prediction[0] == 1:
        return "⚠️ The person is likely to have heart disease."
    else:
        return "✅ The person is likely healthy."