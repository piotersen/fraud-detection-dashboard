import csv
from datetime import datetime
from kafka import KafkaConsumer
import json
import pandas as pd
import pickle

# Load model, encoder dictionary, and features list
with open("fraud_model.pkl", "rb") as f:
    model, encoder_dict, features = pickle.load(f)

# Function to encode categorical variables using the saved encoder
def encode_input(row, encoder_dict):
    for col, mapping in encoder_dict.items():
        if col in row and row[col] in mapping:
            row[col] = mapping[row[col]]
        else:
            row[col] = mapping.get(row[col], 0)  # fallback for unknown category
    return row

# Start Kafka consumer
consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Consumer started and listening for messages...")

# Output CSV
output_file = "alerts_log.csv"
with open(output_file, "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Transaction_ID", "User_ID", "Status"])

# Consume and process messages
for message in consumer:
    data_dict = message.value
    try:
        # Encode and prepare input data
        input_data = encode_input(data_dict.copy(), encoder_dict)

        # Usuwamy tylko ID, zostawiamy Timestamp (jest potrzebny!)
        for col in ['Transaction_ID', 'User_ID']:
            input_data.pop(col, None)

        # Ensure correct column order
        X = pd.DataFrame([input_data])[features]

        # Predict
        prediction = model.predict(X)[0]
        txn_id = data_dict.get("Transaction_ID", "UNKNOWN")
        user_id = data_dict.get("User_ID", "UNKNOWN")

        # Log results
        with open(output_file, "a", newline='') as f:
            writer = csv.writer(f)
            if prediction == 1:
                print(f"ALERT: Fraudulent transaction detected! Transaction ID {txn_id} (User ID {user_id})")
                writer.writerow([datetime.now(), txn_id, user_id, "FRAUD"])
            else:
                print(f"OK: Legitimate transaction. Transaction ID {txn_id}")
                writer.writerow([datetime.now(), txn_id, user_id, "LEGIT"])

    except Exception as e:
        print("Error during prediction:", e)
        print("Offending data:", data_dict)
