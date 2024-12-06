import time
from datetime import datetime, timedelta
import requests
import pyautogui

# Yeni API'ye göre ezan vakitlerini çekmek için fonksiyon
def get_azan_time(city="Ankara", api_key="your_token"):
    url = f"https://api.collectapi.com/pray/all?data.city={city}"
    headers = {
        'content-type': "application/json",
        'authorization': f"apikey {api_key}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data['success']:
            result = data['result']
            return {
                "fajr": next((item['saat'] for item in result if item['vakit'] == "İmsak"), None),
                "dhuhr": next((item['saat'] for item in result if item['vakit'] == "Öğle"), None),
                "asr": next((item['saat'] for item in result if item['vakit'] == "İkindi"), None),
                "maghrib": next((item['saat'] for item in result if item['vakit'] == "Akşam"), None),
                "isha": next((item['saat'] for item in result if item['vakit'] == "Yatsı"), None)
            }
        else:
            print("API başarısız bir yanıt döndü.")
            return None
    else:
        print(f"Ezan vakitleri alınırken bir hata oluştu: {response.status_code}")
        return None


azan_names = {
    "fajr": "Sabah",
    "dhuhr": "Öğle",
    "asr": "İkindi",
    "maghrib": "Akşam",
    "isha": "Yatsı"
}

def stop_music():
    try:
        pyautogui.press('playpause')  
        print("Müzik durduruldu.")
    except Exception as e:
        print(f"Müzik durdurulurken bir hata oluştu: {e}")

def start_music():
    try:
        pyautogui.press('playpause')  
        print("Müzik başlatıldı.")
    except Exception as e:
        print(f"Müzik başlatılırken bir hata oluştu: {e}")


def check_and_control_music(api_key):
    # Sistemin çalıştırıldığı anda ezan vakitlerini bir kez çekiyoruz
    azan_times = get_azan_time(api_key=api_key)
    if azan_times is None:
        return

    already_stopped_for = None 

    while True:
        current_time = datetime.now()
        for azan, azan_time in azan_times.items():
            azan_datetime = datetime.strptime(azan_time, "%H:%M").replace(
                year=current_time.year, month=current_time.month, day=current_time.day
            )

            if current_time > azan_datetime + timedelta(minutes=10):
                continue
            if current_time >= azan_datetime and already_stopped_for != azan:
                print(f"Ezan vakti geldi ({azan_names[azan]} Ezanı: {azan_time}). Müzik durduruluyor.")
                stop_music()
                already_stopped_for = azan

                # 5 dakika bekleyip müziği tekrar başlat
                for i in range(5, 0, -1):
                    print(f"{i} dakika sonra müzik yeniden başlayacak.")
                    time.sleep(60) 

                start_music()
                break

            elif current_time < azan_datetime:
                time_diff = azan_datetime - current_time
                hours, remainder = divmod(time_diff.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                print(f"Sonraki Ezan: {azan_names[azan]}")
                print(f"Ezan Saati: {azan_time}")
                print(f"Kalan Süre: {hours} saat {minutes} dakika {seconds} saniye")

                if time_diff.total_seconds() < 60:
                    print("1 dakikadan az kaldı, saniyelik kontrol yapılıyor.")
                    time.sleep(1) 
                else:
                    time.sleep(60)  
                break

        if current_time > datetime.strptime(azan_times["isha"], "%H:%M").replace(
                year=current_time.year, month=current_time.month, day=current_time.day):
            print("Günün tüm ezanları geçti. Program sona eriyor.")
            break


# API anahtarınızı buraya girin
API_KEY = "APIKEY"
check_and_control_music(api_key=API_KEY)
