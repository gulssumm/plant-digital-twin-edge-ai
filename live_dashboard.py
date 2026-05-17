import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# 1. Sanal Port Bağlantısı (Python, Arduino'nun yazdığı portun diğer ucunu dinler)

# COM port yerine doğrudan Wokwi'nin ağ yayınını dinliyoruz
URL = 'rfc2217://localhost:4000'

try:
    # serial_for_url komutu ağ üzerinden gelen seri veriyi yakalar
    s = serial.serial_for_url(URL, baudrate=115200)
    print("Wokwi simülasyonuna başarıyla bağlanıldı. Canlı yayın başlıyor...")
except Exception as e:
    print(f"Bağlantı hatası: {e}")
    exit()

# 2. Grafik Hafızası (Sahnede aynı anda son 100 veri noktasını göstereceğiz)
max_points = 100
data_signal = deque([500] * max_points, maxlen=max_points)

# 3. Grafik Çerçevesinin Kurulumu
fig, ax = plt.subplots(figsize=(10, 5))
fig.canvas.manager.set_window_title('Bitki Dijital İkizi - Canlı Monitör')
line, = ax.plot(data_signal, color='blue', linewidth=2)
ax.set_ylim(100, 900) # Sinyalin genlik sınırları
ax.set_xlabel("Son 100 Zaman Adımı")
ax.set_ylabel("Sinyal Genliği")

# 4. Her Milisaniyede Çalışacak Canlı Güncelleme Fonksiyonu
def update(frame):
    while s.in_waiting: # Portta okunmayı bekleyen veri varsa
        try:
            # Arduino'dan gelen "Sinyal,Durum" formatındaki satırı oku
            line_str = s.readline().decode('utf-8').strip()
            signal_val, label_val = line_str.split(',')
            
            # Yeni sinyali grafiğin sonuna ekle (en eski veri otomatik silinir)
            data_signal.append(float(signal_val))
            label = int(label_val)
            
            # Ekranda akan çizgiyi güncelle
            line.set_ydata(data_signal)
            
            # Gelen Durum Etiketine (Label) göre arayüzün rengini ve alarmını değiştir
            if label == 2:
                ax.set_title("DURUM: FİZİKSEL TRAVMA!", color='red', fontsize=18, fontweight='bold')
                line.set_color('red')
                fig.patch.set_facecolor('#ffe6e6') # Arka planı hafif kırmızı yap
            elif label == 1:
                ax.set_title("DURUM: ÇEVRESEL STRES", color='orange', fontsize=16, fontweight='bold')
                line.set_color('orange')
                fig.patch.set_facecolor('#fff5e6')
            else:
                ax.set_title("DURUM: HUZURLU (NORMAL)", color='blue', fontsize=16)
                line.set_color('blue')
                fig.patch.set_facecolor('white')
                
        except Exception as e:
            # Sinyal anlık koparsa veya hatalı gelirse görmezden gel
            pass
            
    return line,

# 5. Animasyonu Başlat (Her 50 milisaniyede bir ekranı yenile)
ani = animation.FuncAnimation(fig, update, interval=50, cache_frame_data=False)

plt.tight_layout()
plt.show()