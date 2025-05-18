import joblib
from sklearn.preprocessing import LabelEncoder

# Step 1: Define all possible intents (same as your response.json keys)
intents = ["symptoms", "book_appointment", "greetings"]

# Step 2: Initialize and fit the label encoder
label_encoder = LabelEncoder()
label_encoder.fit(intents)

# Step 3: Save the encoder as a pickle file
joblib.dump(label_encoder, "label_encoder.pkl")

print("✅ Label encoder saved successfully as 'label_encoder.pkl'")
