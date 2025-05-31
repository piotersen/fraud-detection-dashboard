import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load the historical transactions dataset
data = pd.read_csv('transactions.csv')

# Drop identifier columns that are not useful for prediction
if 'Transaction_ID' in data.columns:
    data = data.drop(['Transaction_ID', 'User_ID'], axis=1)

# Separate features (X) and target label (y)
X = data.drop('Fraud_Label', axis=1)
y = data['Fraud_Label']

# Encode categorical features as numeric codes
mappings = {}  # to store category-to-code mappings for each categorical column
for col in X.select_dtypes(include=['object', 'category']).columns:
    # Convert to categorical and then to codes
    X[col] = X[col].astype('category')
    # Create a mapping from category value to numeric code
    cat_mapping = {category: code for code, category in enumerate(X[col].cat.categories)}
    mappings[col] = cat_mapping
    # Replace values in X with the numeric codes
    X[col] = X[col].map(cat_mapping)

# (Optional) Convert boolean columns to integers (True/False -> 1/0) for safety
for col in X.select_dtypes(include=['bool']).columns:
    X[col] = X[col].astype(int)

# Train a Random Forest classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save the model and mappings to a pickle file
with open('fraud_model.pkl', 'wb') as f:
    pickle.dump((model, mappings, list(X.columns)), f)

print("Model trained and saved to fraud_model.pkl")
print("Model trained on columns:")
print(X.columns.tolist())

