import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

URL = 'rfc2217://localhost:4000'

try:
    # The serial_for_url command captures serial data coming over the network
    s = serial.serial_for_url(URL, baudrate=115200)
    print("Successfully connected to the Wokwi simulation. Live stream is starting...")
except Exception as e:
    print(f"Connection error: {e}")
    exit()

# Graph Memory (It will display the last 100 data points on the screen at the same time)
max_points = 100
data_signal = deque([500] * max_points, maxlen=max_points)

# Graph Window
fig, ax = plt.subplots(figsize=(10, 5))
fig.canvas.manager.set_window_title('Plant Digital Twin - Live Monitor')
line, = ax.plot(data_signal, color='blue', linewidth=2)

ax.set_ylim(100, 900)  # Signal amplitude limits
ax.set_xlabel("Last 100 Time Steps")
ax.set_ylabel("Signal Amplitude")

# Live Update Function That Runs Every Millisecond
def update(frame):
    while s.in_waiting:  # If there is unread data waiting in the port
        try:
            # Read the line coming from Arduino in "Signal,Status" format
            line_str = s.readline().decode('utf-8').strip()
            signal_val, label_val = line_str.split(',')

            # Add the new signal to the end of the graph (oldest data is automatically removed)
            data_signal.append(float(signal_val))
            label = int(label_val)

            # Update the moving line on the screen
            line.set_ydata(data_signal)

            # Change the interface color and alarm according to the incoming Status Label
            if label == 2:
                ax.set_title(
                    "STATUS: PHYSICAL TRAUMA!",
                    color='red',
                    fontsize=18,
                    fontweight='bold'
                )
                line.set_color('red')
                fig.patch.set_facecolor('#ffe6e6')  

            elif label == 1:
                ax.set_title(
                    "STATUS: ENVIRONMENTAL STRESS",
                    color='orange',
                    fontsize=16,
                    fontweight='bold'
                )
                line.set_color('orange')
                fig.patch.set_facecolor('#fff5e6')

            else:
                ax.set_title(
                    "STATUS: CALM (NORMAL)",
                    color='blue',
                    fontsize=16
                )
                line.set_color('blue')
                fig.patch.set_facecolor('white')

        except Exception as e:
            # Ignore temporary signal interruptions or malformed data
            pass

    return line,

# Start the Animation (Refresh the screen every 50 milliseconds)
ani = animation.FuncAnimation(
    fig,
    update,
    interval=50,
    cache_frame_data=False
)

plt.tight_layout()
plt.show()