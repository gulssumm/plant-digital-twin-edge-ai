"""
ECG Signal Anomaly Detection Baseline using Lagged & Rolling Window Features.

Trains a balanced Random Forest classifier on time-series statistical features
extracted from 1D physiological signal recordings (ecg_dataset.csv).
"""

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

DATASET_PATH = "ecg_dataset.csv"
OUTPUT_PLOT = "Figure_1.png"


def run_ecg_anomaly_detection():
    df = pd.read_csv(DATASET_PATH)

    # Autoregressive lag features to capture short-term temporal context
    df["Signal_Lag1"] = df["Signal"].shift(1)
    df["Signal_Lag2"] = df["Signal"].shift(2)
    df["Signal_Lag3"] = df["Signal"].shift(3)

    # 5-step rolling window statistics for trend and local volatility
    df["Rolling_Mean_5"] = df["Signal"].rolling(window=5).mean()
    df["Rolling_Std_5"] = df["Signal"].rolling(window=5).std()
    df = df.dropna()

    feature_cols = [
        "Signal",
        "Signal_Lag1",
        "Signal_Lag2",
        "Signal_Lag3",
        "Rolling_Mean_5",
        "Rolling_Std_5",
    ]
    X = df[feature_cols]
    y = df["Label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=100, random_state=42, class_weight="balanced"
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("\nECG Anomaly Detection — Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Normal (0)", "Anomaly (1)"]))

    plt.figure(figsize=(12, 5))
    test_results = X_test.copy()
    test_results["Actual"] = y_test
    test_results["Predicted"] = y_pred
    test_results = test_results.sort_index()

    plt.plot(
        test_results.index,
        test_results["Signal"],
        label="ECG Signal",
        color="steelblue",
        alpha=0.65,
    )

    anomalies = test_results[test_results["Predicted"] == 1]
    plt.scatter(
        anomalies.index,
        anomalies["Signal"],
        color="crimson",
        label="Detected Anomaly",
        zorder=5,
    )

    plt.title("ECG Time-Series Anomaly Detection (Random Forest)")
    plt.xlabel("Time Step")
    plt.ylabel("Signal Amplitude")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT, dpi=150)
    plt.show()


if __name__ == "__main__":
    run_ecg_anomaly_detection()