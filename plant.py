import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

df = pd.read_csv('plant_dataset.csv')

df['Signal_Lag1'] = df['Signal'].shift(1)
df['Signal_Lag2'] = df['Signal'].shift(2)
df['Rolling_Mean_5'] = df['Signal'].rolling(window=5).mean() # Dalganın genel yönü
df['Rolling_Std_5'] = df['Signal'].rolling(window=5).std()   # Titreşim / Gürültü şiddeti

df = df.dropna()

X = df[['Signal', 'Signal_Lag1', 'Signal_Lag2', 'Rolling_Mean_5', 'Rolling_Std_5']]
y = df['Label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)
joblib.dump(model, 'plant_digital_twin_model.pkl')

y_pred = model.predict(X_test)
print("\n Performance Report")
print(classification_report(y_test, y_pred, target_names=['0: Normal', '1: Stress', '2: Physical Trauma']))

plt.figure(figsize=(14, 6))

test_results = X_test.copy()
test_results['Gercek'] = y_test
test_results['Tahmin'] = y_pred
test_results = test_results.sort_index()

plt.plot(test_results.index, test_results['Signal'], label='Ham Sinyal', color='lightgray', zorder=1)

normal_points = test_results[test_results['Tahmin'] == 0]
stress_points = test_results[test_results['Tahmin'] == 1]
trauma_points = test_results[test_results['Tahmin'] == 2]

plt.scatter(normal_points.index, normal_points['Signal'], color='blue', label='Normal', s=10, zorder=2)
plt.scatter(stress_points.index, stress_points['Signal'], color='orange', label='Stress', s=20, zorder=3)
plt.scatter(trauma_points.index, trauma_points['Signal'], color='red', label='Trauma', s=40, zorder=4)

plt.title("Plant Digital Twin")
plt.xlabel("Time Steps")
plt.ylabel("Signal")
plt.legend()
plt.tight_layout()
plt.show()