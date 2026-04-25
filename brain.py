import requests
import time

print("Membangunkan Otak Digital Twin (Versi REST API)...")

# URL Database-mu (jangan lupa .json di akhir saat memanggil data)
BASE_URL = "https://digital-twin-fb5b1-default-rtdb.firebaseio.com/smart_room"

# Array untuk menyimpan ingatan suhu 5 detik terakhir
ingatan_suhu = []

print("🧠 AI Aktif! Memantau anomali data secara real-time...\n")

while True:
    try:
        # 1. BACA SENSOR: Mengambil data dari Firebase
        respon_sensor = requests.get(f"{BASE_URL}/sensor.json")
        data_sensor = respon_sensor.json()
        
        if data_sensor and 'suhu' in data_sensor:
            suhu_sekarang = data_sensor['suhu']
            ingatan_suhu.append(suhu_sekarang)

            # Batasi ingatan hanya 5 detik terakhir
            if len(ingatan_suhu) > 5:
                ingatan_suhu.pop(0)

            print(f"[{time.strftime('%H:%M:%S')}] Riwayat 5 dtk: {ingatan_suhu}")

            # 2. BACA KONTROL: Mengecek status Mode Manual & AC
            respon_kontrol = requests.get(f"{BASE_URL}/kontrol.json")
            status_kontrol = respon_kontrol.json()
            
            is_manual = status_kontrol.get('mode_manual', False) if status_kontrol else False

            # ==========================================
            # ALGORITMA PREDIKTIF (ANOMALY DETECTION)
            # ==========================================
            if len(ingatan_suhu) == 5 and not is_manual:
                
                # Hitung selisih suhu terbaru dengan 5 detik lalu
                lonjakan = ingatan_suhu[-1] - ingatan_suhu[0]

                # SKENARIO BAHAYA (Suhu melonjak drastis)
                if lonjakan >= 3:
                    print("⚠️ ANOMALI TERDETEKSI: Suhu naik terlalu cepat!")
                    print("   Tindakan AI: Menyalakan AC secara preventif SEBELUM panas!\n")
                    
                    # Mengirim perintah UPDATE ke Firebase (menggunakan PATCH)
                    requests.patch(f"{BASE_URL}/kontrol.json", json={"ac_pendingin": True})
                
                # SKENARIO AMAN (Suhu kembali dingin)
                elif suhu_sekarang <= 20:
                    if status_kontrol.get('ac_pendingin', False):
                        print("✅ Kondisi Stabil. Mematikan AC untuk efisiensi energi.\n")
                        requests.patch(f"{BASE_URL}/kontrol.json", json={"ac_pendingin": False})

    except Exception as e:
        print(f"Terjadi kesalahan koneksi: {e}")

    # Tunggu 1 detik sebelum siklus selanjutnya
    time.sleep(1)