# Ezanmatik
Ezan vakti geldiğinde otomatik olarak müziği durdurur ve 5 dakika sonra yeniden başlatır.
Hangi müzik programını / sitesini kullandığınızın bir önemi yok, sistem multimedya tuşları ile çalışır.

Kodun 6.satırındaki "Şehir"'i yaşadığınız şehir ile değiştirin.

Aladhan api kullanarak ezan vakitleri sürekli güncellenir.

Ezan vaktinden 1 dakikadan az kaldığında her saniye döngüye girer ve zamanlayıcı sona erdiğinde müzik 5 dakika duraklatılır.

Örnek çıktı:   https://prnt.sc/4L80DNW3h3vg

Hiç bilmeyenler için nasıl çalıştırılır:  
  
1- Python indirin. https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe  
2- Kurarken akttaki 2 tiki işaretleyip install now'a tıklayın. https://prnt.sc/dY0yHcUvvV8U  
3- Disable lengh limit butonuna da tıklayıp kurulumu bitirin. https://prnt.sc/xDc7QY90oEFH  
4- Komut sistemini açıp "pip install requests pyautogui" yazıp işlem bitene kadar bekleyin.  
5- İşlem bittikten sonra Ezanmatik.py dosyasını çalıştırın.


  -------------------------------------------------------------------------------------------

  V2-  
    
 Aladhan Api yerine CollectAPI kullanır. Kullanmak için CollectAPI'ye üye olmanız gerekir.  
 https://collectapi.com/tr/auth

 Vakitleri sürekli çekmek yerine 1 kez çekip kaydeder ve buna göre kalan vakitleri hesaplar.
  
 Kullanabilmek için 7. satıra kendi şehrinizi 115. satıra kendi api keyinizi girmelisiniz.

 ---------------------------------------------------------------------------------------------
 V4 (GUI)
  
 Terminal üzerinden çalışmaz, V2 gibi CollectAPI kullanır.  
   
 Görünümü: https://prnt.sc/9Ngs4DwlY1Qw  
   
 Kullanabilmek için 170 ve 171. satırdaki city ve api_key değerlerini girmelisiniz.  
   
 Kullanılan kütüphaneleri indirmek için kod: pip install requests pyautogui pystray pillow plyer

 
 
 
