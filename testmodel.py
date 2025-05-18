import pickle

# Load the saved model and vectorizer
with open("chat_model.pkl", "rb") as f:
    vectorizer, model = pickle.load(f)

# Test inputs (Intent)
test = ["cold", "fever", "sore throat", "cough"]

# Vectorize the test input
X_test = vectorizer.transform(test)

# Get predictions
predictions = model.predict(X_test)

# Print predictions
for query, response in zip(test, predictions):
    print(f"Query: {query} -> Response: {response}")
