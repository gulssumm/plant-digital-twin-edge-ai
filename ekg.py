import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

df = pd.read_csv('ecg_dataset.csv')

# Zaman serisi verilerinde bağlam yaratmak için "Lag" (Gecikme) özelliği ekliyoruz
# Modelin sadece anlık değere değil, bir önceki değere de bakmasını sağlar
df['Signal_Lag1'] = df['Signal'].shift(1)
df['Signal_Lag2'] = df['Signal'].shift(2)
df['Signal_Lag3'] = df['Signal'].shift(3)

# Son 5 adımın hareketli ortalaması (Sinyalin trendini gösterir, anlık parazitleri yumuşatır)
df['Rolling_Mean_5'] = df['Signal'].rolling(window=5).mean()

# Titreşim / Kararsızlık Dedektörü
df['Rolling_Std_5'] = df['Signal'].rolling(window=5).std()

df = df.dropna()

# Özellikler (X) ve Etiketler (y)
X = df[['Signal', 'Signal_Lag1', 'Signal_Lag2', 'Signal_Lag3', 'Rolling_Mean_5', 'Rolling_Std_5']]
y = df['Label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("\nModel Performansı")
print(classification_report(y_test, y_pred))

plt.figure(figsize=(12, 5))
test_results = X_test.copy()
test_results['Gercek'] = y_test
test_results['Tahmin'] = y_pred
test_results = test_results.sort_index()

plt.plot(test_results.index, test_results['Signal'], label='EKG Sinyali', color='blue', alpha=0.6)

# Anormallikleri kırmızı noktalarla işaretle
anomalies = test_results[test_results['Tahmin'] == 1]
plt.scatter(anomalies.index, anomalies['Signal'], color='red', label='Tespit Edilen Anormallik', zorder=5)

plt.title("Yapay Zeka Destekli EKG Anormallik Tespiti")
plt.xlabel("Zaman Adımı")
plt.ylabel("Sinyal Genliği")
plt.legend()
plt.tight_layout()
plt.show()