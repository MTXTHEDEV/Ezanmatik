import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import requests
import pyautogui
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
from plyer import notification


def get_azan_time(city, api_key):
    """API'den ezan vakitlerini alır."""
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
            return {item['vakit']: item['saat'] for item in result}
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

        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.create_widgets()
        self.fetch_azan_times()
        self.update_timer()

    def create_widgets(self):
        font_large = ("Arial", 14, "bold")
        font_small = ("Arial", 12)
        self.info_label = tk.Label(self, text="Bir sonraki ezan bilgisi:", font=font_large, bg="#1e1e1e", fg="#ffffff")
        self.info_label.pack(pady=10)
        self.azan_label = tk.Label(self, text="Ezan Adı: Bekleniyor", font=font_small, bg="#1e1e1e", fg="#ffffff")
        self.azan_label.pack()
        self.time_label = tk.Label(self, text="Ezan Saati: Bekleniyor", font=font_small, bg="#1e1e1e", fg="#ffffff")
        self.time_label.pack()
        self.countdown_label = tk.Label(self, text="Kalan Süre: Bekleniyor", font=font_small, bg="#1e1e1e", fg="#ffffff")
        self.countdown_label.pack()
        self.music_timer_label = tk.Label(self, text="", font=font_small, bg="#1e1e1e", fg="#ff5555")
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
            MenuItem("Çık", quit_app)
        )
        self.tray_icon = Icon("Ezan Vakti Takip", image, "Ezan Takip", menu)
        self.tray_icon.run_detached()

    def show_notification(self, message):
        try:
            notification.notify(
                title="Ezan Vakti Takip",
                message=message,
                app_name="Ezan Takip"
            )
        except Exception as e:
            print(f"Bildirim hatası: {e}")

    def fetch_azan_times(self):
        self.azan_times = get_azan_time(self.city, self.api_key)
        if self.azan_times:
            now = datetime.now()
            self.azan_times = {
                k: datetime.strptime(v, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
                for k, v in self.azan_times.items()
            }
            self.next_azan_name, self.next_azan_time = self.get_next_azan()
        else:
            messagebox.showerror("Hata", "Ezan vakitleri alınamadı. API anahtarınızı kontrol edin.")

    def get_next_azan(self):
        now = datetime.now()
        for azan, azan_time in sorted(self.azan_times.items(), key=lambda x: x[1]):
            if azan_time > now:
                return azan, azan_time
        tomorrow = now + timedelta(days=1)
        self.azan_times = {k: v + timedelta(days=1) for k, v in self.azan_times.items()}
        return self.get_next_azan()

    def update_timer(self):
        now = datetime.now()

        if self.next_azan_time:
            time_diff = self.next_azan_time - now
            if time_diff.total_seconds() > 20: 
                self.azan_label.config(text=f"Ezan Adı: {self.next_azan_name}")
                self.time_label.config(text=f"Ezan Saati: {self.next_azan_time.strftime('%H:%M')}")
                self.countdown_label.config(
                    text=f"Kalan Süre: {time_diff.seconds // 3600:02}:{(time_diff.seconds % 3600) // 60:02}:{time_diff.seconds % 60:02}"
                )
            else:
                self.handle_azan_time()

        if self.music_stop_time:
            music_diff = self.music_stop_time - now
            if music_diff.total_seconds() > 0:
                self.music_timer_label.config(
                    text=f"Müzik devam etmesine kalan süre: {music_diff.seconds // 60:02}:{music_diff.seconds % 60:02}"
                )
            else:
                self.start_music()

        self.after(1000, self.update_timer)

    def handle_azan_time(self):
        """Ezan vakti veya 20 saniye öncesinde müziği durdurur."""
        self.countdown_label.config(text=f"{self.next_azan_name} ezanı yaklaşıyor!")
        self.stop_music()
        self.music_stop_time = datetime.now() + timedelta(minutes=6)  
        self.next_azan_name, self.next_azan_time = self.get_next_azan()

    def stop_music(self):
        try:
            pyautogui.press('playpause')
            self.music_timer_label.config(text="Müzik durduruldu.")
        except Exception as e:
            self.music_timer_label.config(text=f"Müzik durdurulamadı: {e}")

    def start_music(self):
        try:
            pyautogui.press('playpause')
            self.music_timer_label.config(text="Müzik yeniden başlatıldı.")
            self.music_stop_time = None
        except Exception as e:
            self.music_timer_label.config(text=f"Müzik başlatılamadı: {e}")


if __name__ == "__main__":
    city = ""
    api_key = ""
    app = AzanApp(city, api_key)
    app.mainloop()
