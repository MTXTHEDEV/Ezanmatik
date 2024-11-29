import time
from datetime import datetime, timedelta
import requests
import pyautogui

def get_azan_time(city="Şehir"):
    url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=Turkey&method=2"
    response = requests.get(url)
    data = response.json()

    if data['code'] == 200:
        timings = data['data']['timings']
        return {
            "fajr": timings["Fajr"],  
            "dhuhr": timings["Dhuhr"], 
            "asr": timings["Asr"], 
            "maghrib": timings["Maghrib"], 
            "isha": timings["Isha"], 
        }
    else:
        print("Ezan vakitleri alınırken bir hata oluştu.")
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

def check_and_control_music():
    azan_times = get_azan_time()

    if azan_times is None:
        return

    already_stopped_for = None 
    while True:
        current_time = datetime.now()
        for azan, azan_time in azan_times.items():
            azan_datetime = datetime.strptime(azan_time, "%H:%M").replace(
                year=current_time.year, month=current_time.month, day=current_time.day
            )

            if current_time >= azan_datetime and already_stopped_for != azan:
                print(f"Ezan vakti geldi ({azan_names[azan]} Ezanı: {azan_time}). Müzik durduruluyor.")
                stop_music()
                already_stopped_for = azan

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
            print("Günün tüm ezanları geçti, ezan vakitleri yenileniyor...")
            azan_times = get_azan_time()
            already_stopped_for = None  


check_and_control_music()
