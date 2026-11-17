"""Bilinen uygulamalar ve siteler.

Yeni uygulama eklemek için UYGULAMALAR'a bir kayıt ekle:
  "anahtar": {
      "adlar":   söylenebilecek isimler (küçük harf, ek almadan),
      "ac":      çalıştırılacak komut  (yoksa Başlat menüsünde "arama" ile aranır),
      "arama":   Başlat menüsünde aranacak isim,
      "surec":   işlem (process) adları  -> pencereyi bulmak / kapatmak için,
      "baslik":  pencere başlığında geçen kelimeler -> pencereyi bulmak için,
  }
"""

UYGULAMALAR = {
    "notepad": {
        "adlar": ["not defter", "notepad", "not defteri", "notdefter"],
        "ac": "notepad.exe",
        "surec": ["notepad.exe"],
        "baslik": ["not defteri", "notepad"],
        "goster": "Not Defteri",
        "yeni_belge": ["ctrl", "n"],
    },
    "whatsapp": {
        "adlar": ["whatsapp", "whats app", "watsap", "vatsap", "watsapp", "wp"],
        "arama": "WhatsApp",
        "surec": ["whatsapp.exe", "whatsapp.root.exe"],
        "baslik": ["whatsapp"],
        "goster": "WhatsApp",
    },
    "hesap": {
        "adlar": ["hesap makine", "hesap makinesi", "calculator"],
        "ac": "calc.exe",
        "surec": ["calculatorapp.exe", "calc.exe"],
        "baslik": ["hesap makinesi", "calculator"],
        "goster": "Hesap Makinesi",
    },
    "paint": {
        "adlar": ["paint", "boya"],
        "ac": "mspaint.exe",
        "surec": ["mspaint.exe"],
        "baslik": ["paint"],
        "goster": "Paint",
    },
    "chrome": {
        "adlar": ["chrome", "krom", "google chrome"],
        "ac": 'start "" chrome',
        "surec": ["chrome.exe"],
        "baslik": ["google chrome"],
        "goster": "Chrome",
    },
    "edge": {
        "adlar": ["edge", "microsoft edge"],
        "ac": 'start "" msedge',
        "surec": ["msedge.exe"],
        "baslik": ["microsoft edge", "edge"],
        "goster": "Edge",
    },
    "opera": {
        "adlar": ["opera", "tarayıcı"],
        "arama": "Opera",
        "surec": ["opera.exe"],
        "baslik": ["- opera"],
        "goster": "Opera",
    },
    "word": {
        "adlar": ["word", "vord", "kelime işlemci"],
        "arama": "Word",
        "surec": ["winword.exe"],
        "baslik": ["word"],
        "goster": "Word",
    },
    "excel": {
        "adlar": ["excel", "eksel"],
        "arama": "Excel",
        "surec": ["excel.exe"],
        "baslik": ["excel"],
        "goster": "Excel",
    },
    "powerpoint": {
        "adlar": ["powerpoint", "power point", "pavırpoint"],
        "arama": "PowerPoint",
        "surec": ["powerpnt.exe"],
        "baslik": ["powerpoint"],
        "goster": "PowerPoint",
    },
    "spotify": {
        "adlar": ["spotify", "spotifay", "spotfy"],
        "arama": "Spotify",
        "surec": ["spotify.exe"],
        "baslik": ["spotify"],
        "goster": "Spotify",
    },
    "dosya": {
        "adlar": ["dosya gezgin", "dosyalar", "klasörler", "explorer", "bilgisayarım"],
        "ac": "explorer.exe",
        "surec": [],  # explorer.exe'yi öldürmek masaüstünü kapatır, sadece pencere kapatılır
        "baslik": ["dosya gezgini", "file explorer"],
        "goster": "Dosya Gezgini",
    },
    "gorev": {
        "adlar": ["görev yönetici", "task manager"],
        "ac": "taskmgr.exe",
        "surec": ["taskmgr.exe"],
        "baslik": ["görev yöneticisi", "task manager"],
        "goster": "Görev Yöneticisi",
    },
    "ayarlar": {
        "adlar": ["ayarlar", "windows ayarlar"],
        "ac": 'start "" ms-settings:',
        "surec": ["systemsettings.exe"],
        "baslik": ["ayarlar", "settings"],
        "goster": "Ayarlar",
    },
    "cmd": {
        "adlar": ["komut istem", "cmd", "terminal"],
        "ac": 'start "" cmd.exe',
        "surec": ["cmd.exe"],
        "baslik": ["komut istemi", "command prompt"],
        "goster": "Komut İstemi",
    },
    "vscode": {
        "adlar": ["vs code", "visual studio code", "vscode", "vs kod"],
        "ac": 'start "" code',
        "surec": ["code.exe"],
        "baslik": ["visual studio code"],
        "goster": "VS Code",
    },
    "steam": {
        # Google "Steam"i çoğu zaman "stim", "istim", "sitim" diye yazıya döküyor
        "adlar": ["steam", "stim", "istim", "estim", "sitim", "stem", "ıstım"],
        "ac": 'start "" steam://open/main',
        "kapat_komut": 'start "" steam://exit',  # pencereyi kapatmak Steam'i sadece tepsiye gizler
        "surec": ["steam.exe", "steamwebhelper.exe"],
        "baslik": [],
        "goster": "Steam",
    },
    "discord": {
        "adlar": ["discord", "diskord"],
        "arama": "Discord",
        "surec": ["discord.exe"],
        "baslik": ["discord"],
        "goster": "Discord",
    },
    "telegram": {
        "adlar": ["telegram"],
        "arama": "Telegram",
        "surec": ["telegram.exe"],
        "baslik": ["telegram"],
        "goster": "Telegram",
    },
}

# "youtube'u aç" gibi denince tarayıcıda açılacak siteler
SITELER = {
    "youtube": "https://www.youtube.com",
    "yutup": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "instagram": "https://www.instagram.com",
    "twitter": "https://x.com",
    "netflix": "https://www.netflix.com",
    "haritalar": "https://maps.google.com",
    "chatgpt": "https://chatgpt.com",
    "claude": "https://claude.ai",
}
