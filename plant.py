import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

df = pd.read_csv('plant_dataset_1.csv')

df['Signal_Lag1'] = df['Signal'].shift(1)
df['Signal_Lag2'] = df['Signal'].shift(2)
df['Rolling_Mean_5'] = df['Signal'].rolling(window=5).mean() # General direction of the wave
df['Rolling_Std_5'] = df['Signal'].rolling(window=5).std()   # Vibration / Noise intensity

df = df.dropna()

X = df[['Signal', 'Signal_Lag1', 'Signal_Lag2', 'Rolling_Mean_5', 'Rolling_Std_5']]
y = df['Label']

# Chronological Split 
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    shuffle=False 
)

# Pruning the Forest (Preventing Memorization)
model = RandomForestClassifier(
    n_estimators=100, 
    max_depth=5,              # Force the model to be simpler
    min_samples_split=10,     # Don't create rules for tiny data clusters
    random_state=42, 
    class_weight='balanced'
)
model.fit(X_train, y_train)
joblib.dump(model, 'plant_digital_twin_model_1.pkl')

y_pred = model.predict(X_test)

# Check which classes actually exist in this specific test split
unique_classes = np.unique(np.concatenate((y_test, y_pred)))
all_target_names = {
    0: '0: Normal', 
    1: '1: Environmental Stress', 
    2: '2: Physical Trauma'
}
# Only fetch the names for the classes that are present
actual_target_names = [all_target_names[c] for c in unique_classes]

print("\nPerformance Report")
print(classification_report(y_test, y_pred, labels=unique_classes, target_names=actual_target_names))

plt.figure(figsize=(14, 6))

test_results = X_test.copy()
test_results['Actual'] = y_test
test_results['Predicted'] = y_pred
test_results = test_results.sort_index()

plt.plot(test_results.index, test_results['Signal'], label='Raw Signal', color='lightgray', zorder=1)

normal_points = test_results[test_results['Predicted'] == 0]
stress_points = test_results[test_results['Predicted'] == 1]
trauma_points = test_results[test_results['Predicted'] == 2]

plt.scatter(normal_points.index, normal_points['Signal'], color='blue', label='Normal', s=10, zorder=2)
plt.scatter(stress_points.index, stress_points['Signal'], color='orange', label='Environmental Stress', s=20, zorder=3)
plt.scatter(trauma_points.index, trauma_points['Signal'], color='red', label='Physical Trauma', s=40, zorder=4)

plt.title("Plant Digital Twin")
plt.xlabel("Time Steps")
plt.ylabel("Signal Amplitude")
plt.legend()
plt.tight_layout()
plt.show()