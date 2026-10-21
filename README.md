# Real-Time Plant Digital Twin & ECG Anomaly Detection

This project implements a real-time **Plant Digital Twin** using an **Arduino Uno** (simulated in **Wokwi**) and a **Random Forest** classifier in Python. It reads environmental sensor data (temperature, humidity, light) and physical shock triggers at **50 Hz**, extracts sliding-window time-series features, and displays live stress predictions on a **Matplotlib** dashboard.

The repository also includes an **ECG Anomaly Detection** script (`ekg.py`) that applies the same time-series feature extraction logic (`Lag` and `Rolling Mean/Std`) to detect anomalies on 1D ECG waveform data (`ecg_dataset.csv`).

## How It Works

1. **Arduino & Wokwi Simulation (`sketch.ino`, `diagram.json`, `wokwi.toml`)**
   - Uses a **DHT22** sensor (Pin `2`), a **Photoresistor / LDR** (Pin `A0`), and a **Pushbutton** (Pin `4`).
   - Generates a 50 Hz bio-signal stream with natural baseline drift and sends `signal,stateLabel` over serial (`115200` baud) through Wokwi's RFC2217 bridge (`rfc2217://localhost:4000`).
   - Simulates three plant states:
     - **0 — Normal (Calm):** Normal temperature, humidity, and light levels.
     - **1 — Environmental Stress:** Triggered when `Temperature > 30°C`, `Humidity < 40%`, or `Light > 800`.
     - **2 — Physical Trauma:** Triggered when the pushbutton is pressed.

2. **Time-Series Feature Engineering & Model Training (`plant.py`, `synthetic_data.py`)**
   - Raw single-point sensor values are noisy, so the pipeline computes 5 features at each time step:
     - Current signal (`Signal`)
     - Previous two steps (`Signal_Lag1`, `Signal_Lag2`)
     - 5-step rolling average (`Rolling_Mean_5`)
     - 5-step rolling standard deviation (`Rolling_Std_5`)
   - Data is split chronologically (`shuffle=False`, 80% train / 20% test) to avoid time-series data leakage.
   - Trains a pruned **Random Forest** classifier (`n_estimators=100`, `max_depth=5`, `min_samples_split=10`, `class_weight='balanced'`) and saves it as `plant_digital_twin_model_1.pkl`.

3. **Live AI Dashboard (`live_dashboard.py`)**
   - Connects to the Wokwi serial stream (`rfc2217://localhost:4000`), keeps the last 5 readings in a `deque` buffer, runs real-time inference with the trained `.pkl` model, and updates the live plot color and alert title (`CALM (NORMAL)`, `ENVIRONMENTAL STRESS`, or `PHYSICAL TRAUMA!`).

## Results

### Plant Digital Twin Classification (`plant.py`)


### ECG Anomaly Detection (`ekg.py`)


## Project Files

```text
├── sketch.ino                         # Arduino Uno firmware (DHT22, LDR, button & 50 Hz signal loop)
├── diagram.json                       # Wokwi circuit connections
├── wokwi.toml                         # Wokwi serial port forwarding config (port 4000)
├── synthetic_data.py                  # Generates chronological training/test signal data
├── plant.py                           # Trains and evaluates the Random Forest model
├── live_dashboard.py                  # Real-time Matplotlib dashboard connected to Wokwi
├── ekg.py                             # Random Forest anomaly detection on ECG data
├── plant_dataset.csv                  # Raw logged Wokwi sensor data
├── plant_dataset_1.csv                # Balanced chronological plant dataset
├── ecg_dataset.csv                    # ECG signal dataset
├── plant_digital_twin_model.pkl       # Saved Random Forest model (v1)
├── plant_digital_twin_model_1.pkl     # Saved Random Forest model (pruned)
├── Figure_1_plant.png                 # Plant Digital Twin output plot
├── Figure_1.png                       # ECG anomaly detection output plot
└── README.md
```

## Setup & Running the Project

Install the required Python libraries:

```bash
pip install pandas numpy scikit-learn matplotlib joblib pyserial
```

### 1. Train the Model
```bash
python synthetic_data.py
python plant.py
```

### 2. Run the Live Wokwi Dashboard
1. Open the project in **VS Code** and start the **Wokwi Simulator** (`diagram.json` / `wokwi.toml`).
2. While the simulation is running, start the dashboard in a terminal:
```bash
python live_dashboard.py
```

### 3. Run the ECG Anomaly Detection Script
```bash
python ekg.py
```