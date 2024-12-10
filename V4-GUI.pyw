import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import requests
import pyautogui
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
from plyer import notification

def get_azan_times_from_api(city, api_key):
    url = f"https://api.collectapi.com/pray/all?data.city={city}"
    headers = {
        "content-type": "application/json",
        "authorization": f"apikey {api_key}"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                result = data["result"]
                return {item["vakit"]: item["saat"] for item in result}
    except Exception:
        pass
    return None

class AzanApp(tk.Tk):
    def __init__(self, city, api_key):
        super().__init__()
        self.title("Ezan Vakti Takip")
        self.geometry("400x300")
        self.configure(bg="#1e1e1e")

        self.city = city
        self.api_key = api_key
        self.azan_times = None
        self.next_azan_name = None
        self.next_azan_time = None
        self.music_stop_time = None
        self.tray_icon = None
        self.azan_approaching = False

        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.create_widgets()

        self.fetch_azan_times()
        self.update_timer()

    def create_widgets(self):
        font_large = ("Arial", 14, "bold")
        font_small = ("Arial", 12)

        self.info_label = tk.Label(
            self,
            text="Bir sonraki ezan bilgisi:",
            font=font_large,
            bg="#1e1e1e",
            fg="#ffffff"
        )
        self.info_label.pack(pady=10)

        self.azan_label = tk.Label(
            self,
            text="Ezan Adı: Bekleniyor",
            font=font_small,
            bg="#1e1e1e",
            fg="#ffffff"
        )
        self.azan_label.pack()

        self.time_label = tk.Label(
            self,
            text="Ezan Saati: Bekleniyor",
            font=font_small,
            bg="#1e1e1e",
            fg="#ffffff"
        )
        self.time_label.pack()

        self.countdown_label = tk.Label(
            self,
            text="Kalan Süre: Bekleniyor",
            font=font_small,
            bg="#1e1e1e",
            fg="#ffffff"
        )
        self.countdown_label.pack()

        self.music_timer_label = tk.Label(
            self,
            text="",
            font=font_small,
            bg="#1e1e1e",
            fg="#ff5555"
        )
        self.music_timer_label.pack(pady=10)

    def minimize_to_tray(self):
        self.withdraw()
        if not self.tray_icon:
            self.create_tray_icon()
        self.show_notification("Uygulama sistem tepsisine küçültüldü.")

    def create_tray_icon(self):
        def show_app():
            self.deiconify()
            self.tray_icon.stop()
            self.tray_icon = None

        def quit_app():
            if self.tray_icon:
                self.tray_icon.stop()
            self.quit()

        image = Image.new("RGB", (64, 64), color="black")
        draw = ImageDraw.Draw(image)
        draw.ellipse((16, 16, 48, 48), fill="white")

        menu = Menu(
            MenuItem("Göster", show_app),
            MenuItem("Çık", quit_app),
        )
        self.tray_icon = Icon("Ezan Vakti Takip", image, "Ezan Takip", menu)
        self.tray_icon.run_detached()

    def show_notification(self, message):
        try:
            notification.notify(
                title="Ezan Vakti Takip",
                message=message,
                app_name="Ezan Takip",
                timeout=5
            )
        except Exception:
            pass

    def fetch_azan_times(self):
        raw_times = get_azan_times_from_api(self.city, self.api_key)
        if raw_times:
            now = datetime.now()
            self.azan_times = {
                k: datetime.strptime(v, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
                for k, v in raw_times.items()
            }
            self.next_azan_name, self.next_azan_time = self.get_next_azan()
        else:
            messagebox.showerror("Hata", "Ezan vakitleri alınamadı. API anahtarınızı kontrol edin.")

    def get_next_azan(self):
        now = datetime.now()
        for azan, azan_time in sorted(self.azan_times.items(), key=lambda x: x[1]):
            if azan_time > now:
                return azan, azan_time
        self.azan_times = {k: v + timedelta(days=1) for k, v in self.azan_times.items()}
        return self.get_next_azan()

    def update_timer(self):
        now = datetime.now()

        if self.next_azan_time:
            time_diff = self.next_azan_time - now

            if time_diff.total_seconds() < 0:
                self.next_azan_name, self.next_azan_time = self.get_next_azan()
                time_diff = self.next_azan_time - now

            if time_diff.total_seconds() > 20:
                self.azan_approaching = False
                self.azan_label.config(text=f"Ezan Adı: {self.next_azan_name}")
                self.time_label.config(text=f"Ezan Saati: {self.next_azan_time.strftime('%H:%M:%S')}")
                self.countdown_label.config(
                    text=f"Kalan Süre: {int(time_diff.total_seconds() // 3600):02}:{int((time_diff.total_seconds() % 3600) // 60):02}:{int(time_diff.total_seconds() % 60):02}"
                )
            else:
                if not self.azan_approaching:
                    self.azan_approaching = True
                    self.handle_azan_time()

        if self.music_stop_time:
            music_diff = self.music_stop_time - now
            if music_diff.total_seconds() > 0:
                self.music_timer_label.config(
                    text=f"Müzik devam etmesine kalan süre: {int(music_diff.total_seconds() // 60):02}:{int(music_diff.total_seconds() % 60):02}"
                )
            else:
                self.start_music()

        self.after(1000, self.update_timer)

    def handle_azan_time(self):
        self.countdown_label.config(text=f"{self.next_azan_name} ezanı yaklaşıyor!")
        self.stop_music()
        self.music_stop_time = datetime.now() + timedelta(minutes=6)
        self.show_notification(f"{self.next_azan_name} ezanı yaklaşıyor! Müzik durduruldu.")
        self.next_azan_name, self.next_azan_time = self.get_next_azan()
        self.update_timer()

    def stop_music(self):
        try:
            pyautogui.press("playpause")
            self.music_timer_label.config(text="Müzik durduruldu.")
        except Exception:
            pass

    def start_music(self):
        try:
            pyautogui.press("playpause")
            self.music_timer_label.config(text="Müzik yeniden başlatıldı.")
            self.show_notification("Müzik yeniden başlatıldı.")
            self.music_stop_time = None
            self.update_timer()
        except Exception:
            pass

if __name__ == "__main__":
    city = "İstanbul" # Şehir adınızı buraya girin
    api_key = "apikey 111111111111111111111111111111111111" # Api anahtarınızı buraya girin
    app = AzanApp(city, api_key)
    app.mainloop()
