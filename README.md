# SnapLoop — Cross-Platform Ekran Kaydedici

Windows, macOS ve Linux üzerinde çalışan, masaüstü ekran kaydı uygulaması.

---

## Kurulum

### 1. Python Gereksinimi
Python 3.9 veya üstü gereklidir.
https://python.org/downloads

### 2. Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

### 3. Uygulamayı Başlat
```bash
python snaploop.py
```

---

## Linux'ta Pencere Listesi için
Pencere bazlı kayıt için `wmctrl` gereklidir:
```bash
sudo apt install wmctrl       # Ubuntu/Debian
sudo dnf install wmctrl       # Fedora
sudo pacman -S wmctrl         # Arch
```

---

## Özellikler

- **Çoklu Ekran Desteği:** Tüm ekranları, seçili ekranları veya tek bir pencereyi kaydet
- **Esnek Zamanlama:** "X saniyede bir" kare yakalama, süre limiti
- **Kalite Kontrolü:** %10–%100 kalite kaydırıcısı, PNG / JPEG / WEBP format seçimi
- **Boyut Limiti:** MB cinsinden limit, aşılınca otomatik durdurma
- **Otomatik ZIP:** Kayıt bitince tüm kareler ZIP'lenir
- **Kayıt Yöneticisi:** Tüm oturumları listele, indir, sil
- **Mail Gönderimi:** ZIP dosyasını SMTP ile doğrudan mail olarak gönder

---

## Mail Ayarları (Gmail için)
1. Google Hesabı → Güvenlik → 2 Adımlı Doğrulama'yı etkinleştir
2. "Uygulama Şifreleri" oluştur
3. SnapLoop'ta Mail sekmesine gir, şifreyi uygulama şifresiyle doldur

---

## Kayıtların Konumu
`~/SnapLoop_Recordings/`  klasörüne kaydedilir.
