import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import joblib
import numpy as np

try:
    model = joblib.load('plant_digital_twin_model_1.pkl')
    print("AI Model loaded successfully! The system is now autonomous.")
except Exception as e:
    print("Model not found! Please run the training code first and save the model.")
    exit()

URL = 'rfc2217://localhost:4000'
try:
    s = serial.serial_for_url(URL, baudrate=115200)
except Exception as e:
    print(f"Connection error: {e}")
    exit()

# Queue to hold the last 100 data points for the graph
max_points = 100
data_signal = deque([500] * max_points, maxlen=max_points)

# FEATURE MEMORY FOR THE AI (Holds the last 5 data points)
feature_buffer = deque([500] * 5, maxlen=5)

fig, ax = plt.subplots(figsize=(10, 5))
fig.canvas.manager.set_window_title('Plant Digital Twin - AI Inference')
line, = ax.plot(data_signal, color='blue', linewidth=2)
ax.set_ylim(100, 900)

def update(frame):
    while s.in_waiting: 
        try:
            line_str = s.readline().decode('utf-8').strip()
            
            # Get the signal from Arduino 
            signal_val = float(line_str.split(',')[0]) 
            
            # Add the signal to both graph and AI memory buffers
            data_signal.append(signal_val)
            feature_buffer.append(signal_val)
            
            # Calculate features dynamically using the last 5 points
            sig = feature_buffer[-1]         # Current signal
            lag1 = feature_buffer[-2]        # 1 step lag
            lag2 = feature_buffer[-3]        # 2 steps lag
            mean_5 = np.mean(feature_buffer) # Rolling mean of the last 5
            std_5 = np.std(feature_buffer)   # Rolling standard deviation of the last 5
            
            ai_prediction = model.predict([[sig, lag1, lag2, mean_5, std_5]])[0]
            
            line.set_ydata(data_signal)
            
            if ai_prediction == 2:
                ax.set_title("PHYSICAL TRAUMA!", color='red', fontsize=16, fontweight='bold')
                line.set_color('red')
                fig.patch.set_facecolor('#ffe6e6') 
            elif ai_prediction == 1:
                ax.set_title("ENVIRONMENTAL STRESS", color='orange', fontsize=14, fontweight='bold')
                line.set_color('orange')
                fig.patch.set_facecolor('#fff5e6')
            else:
                ax.set_title("CALM (NORMAL)", color='blue', fontsize=14)
                line.set_color('blue')
                fig.patch.set_facecolor('white')

        except Exception as e:
            pass

    return line,

ani = animation.FuncAnimation(fig, update, interval=50, cache_frame_data=False)
plt.tight_layout()
plt.show()