from app.services.ml_service import load_model, predict_single
import pandas as pd

load_model()

df = pd.read_csv('data/creditcard.csv')

def test_row(idx):
    row = df.iloc[idx]
    features = {'time': row['Time'], 'amount': row['Amount']}
    features.update({f'v{i}': row[f'V{i}'] for i in range(1, 29)})
    prob, action = predict_single(features)
    print(f"Row {idx} | Probability: {prob:.4f} | Action: {action} | Actual label: {row['Class']}")

test_row(0)  # already tested — non-fraud

# find a real fraud case to test against
fraud_indices = df[df['Class'] == 1].index
test_row(fraud_indices[0])