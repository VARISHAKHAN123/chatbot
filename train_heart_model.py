import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# ✅ 1. Create models folder if not exist
os.makedirs('models', exist_ok=True)

# ✅ 2. Load heart disease dataset
df = pd.read_csv('heart.csv')

# ✅ 3. One-hot encode categorical variables
df_encoded = pd.get_dummies(df, drop_first=True)

# ✅ 4. Split features and labels
X = df_encoded.drop('HeartDisease', axis=1)
y = df_encoded['HeartDisease']

# ✅ 5. Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ✅ 6. Train model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# ✅ 7. Save model and feature columns in a compatible format (no compression)
joblib.dump(model, 'models/heart_model.pkl', compress=0)
joblib.dump(X.columns.tolist(), 'models/heart_columns.pkl', compress=0)

print("✅ Heart model and columns saved successfully in 'models/' folder.")
