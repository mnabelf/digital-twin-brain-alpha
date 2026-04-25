import requests
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# ==========================================
# 1. WEB SERVER PALSU (UNTUK MENGAKALI RENDER)
# ==========================================
class ServerPalsu(BaseHTTPRequestHandler):
    def do_GET(self):
        # Membalas ping dari Render agar server tidak dimatikan
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write(b"Status: OK. Otak AI Digital Twin Sedang Berjalan di Background!")

def jalankan_server():
    # Render otomatis memberikan port lewat environment variable
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), ServerPalsu)
    server.serve_forever()

# Menjalankan server web palsu di jalur terpisah (background thread)
threading.Thread(target=jalankan_server, daemon=True).start()

# ==========================================
# 2. LOGIKA UTAMA OTAK DIGITAL TWIN
# ==========================================
print("Membangunkan Otak Digital Twin (Versi Web Service Hack)...")

BASE_URL = "https://digital-twin-fb5b1-default-rtdb.firebaseio.com/smart_room"
ingatan_suhu = []

print("🧠 AI Aktif! Memantau anomali data secara real-time...\n")

while True:
    try:
        respon_sensor = requests.get(f"{BASE_URL}/sensor.json")
        data_sensor = respon_sensor.json()
        
        if data_sensor and 'suhu' in data_sensor:
            suhu_sekarang = data_sensor['suhu']
            ingatan_suhu.append(suhu_sekarang)

            if len(ingatan_suhu) > 5:
                ingatan_suhu.pop(0)

            print(f"[{time.strftime('%H:%M:%S')}] Riwayat 5 dtk: {ingatan_suhu}")

            respon_kontrol = requests.get(f"{BASE_URL}/kontrol.json")
            status_kontrol = respon_kontrol.json()
            is_manual = status_kontrol.get('mode_manual', False) if status_kontrol else False

            if len(ingatan_suhu) == 5 and not is_manual:
                lonjakan = ingatan_suhu[-1] - ingatan_suhu[0]

                if lonjakan >= 3 and suhu_sekarang < 25:
                    print("⚠️ ANOMALI TERDETEKSI: Suhu naik terlalu cepat!")
                    requests.patch(f"{BASE_URL}/kontrol.json", json={"ac_pendingin": True})
                
                elif suhu_sekarang <= 20:
                    if status_kontrol.get('ac_pendingin', False):
                        print("✅ Kondisi Stabil. Mematikan AC.")
                        requests.patch(f"{BASE_URL}/kontrol.json", json={"ac_pendingin": False})

    except Exception as e:
        print(f"Terjadi kesalahan koneksi: {e}")

    time.sleep(1)
