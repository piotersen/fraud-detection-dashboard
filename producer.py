from kafka import KafkaProducer
import pandas as pd
import json
import time

# Initialize Kafka producer
producer = KafkaProducer(bootstrap_servers='localhost:9092')

# Load the dataset
df = pd.read_csv('transactions.csv')

# Show class distribution
print("Class balance in original dataset:")
print(df["Fraud_Label"].value_counts(normalize=True))

# Define the features used by the model
features = [
    'Transaction_Amount', 'Transaction_Type', 'Timestamp', 'Account_Balance',
    'Device_Type', 'Location', 'Merchant_Category', 'IP_Address_Flag',
    'Previous_Fraudulent_Activity', 'Daily_Transaction_Count',
    'Avg_Transaction_Amount_7d', 'Failed_Transaction_Count_7d', 'Card_Type',
    'Card_Age', 'Transaction_Distance', 'Authentication_Method',
    'Risk_Score', 'Is_Weekend'
]

# Send each transaction to Kafka
for _, row in df.iterrows():
    record = row[features].to_dict()
    producer.send('transactions', json.dumps(record).encode('utf-8'))
    producer.flush()
    time.sleep(0.1)

print("All transactions have been sent to the 'transactions' topic.")
