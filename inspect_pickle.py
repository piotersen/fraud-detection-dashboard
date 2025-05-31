import pickle

with open("fraud_model.pkl", "rb") as f:
    obj = pickle.load(f)

print("Type:", type(obj))
if isinstance(obj, tuple):
    print("Tuple length:", len(obj))
    for i, item in enumerate(obj):
        print(f"Item {i} type:", type(item))
else:
    print("Loaded object:", obj)
