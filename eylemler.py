"""Windows üzerinde komutları uygulayan katman."""
import ctypes
import datetime
import os
import subprocess
import time
import urllib.parse
import webbrowser

import psutil
import pyautogui
import pyperclip
import win32api
import win32con
import win32gui
import win32process

from uygulamalar import UYGULAMALAR

pyautogui.FAILSAFE = True  # fareyi ekranın sol üst köşesine götürürsen işlem durur
pyautogui.PAUSE = 0.05

AYLAR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz",
         "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

YARDIM = (
    "Örnek komutlar: not defterini aç. not defterine merhaba dünya yaz. "
    "WhatsApp'ta Ahmet'e merhaba nasılsın gönder. Chrome'u kapat. "
    "Google'da hava durumu ara. YouTube'da müzik aç. Sesi kıs. Kaydet. Saat kaç."
)


def _kucuk(s):
    return s.replace("I", "ı").replace("İ", "i").lower()


# ---------------- pencere işlemleri ----------------
def pencereler():
    """Görünür pencereler: [(hwnd, baslik, surec_adi)]"""
    sonuc = []

    def cb(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return True
        baslik = win32gui.GetWindowText(hwnd)
        if not baslik or baslik == "PopupHost":
            return True
        # sahipli pencereler, araç pencereleri ve boyutsuz pencereler gerçek uygulama penceresi değil
        if win32gui.GetWindow(hwnd, win32con.GW_OWNER):
            return True
        if win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & win32con.WS_EX_TOOLWINDOW:
            return True
        l, t, r, b = win32gui.GetWindowRect(hwnd)
        if r - l < 50 or b - t < 50:
            return True
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            ad = psutil.Process(pid).name().lower()
        except Exception:
            ad = ""
        sonuc.append((hwnd, baslik, ad))
        return True

    win32gui.EnumWindows(cb, None)
    return sonuc


def pencere_bul(anahtar=None, kelime=None):
    """Uygulama anahtarına ya da başlıkta geçen kelimeye göre pencereleri bulur."""
    bulunan = []
    if anahtar:
        u = UYGULAMALAR[anahtar]
        surecler = set(u.get("surec", []))
        basliklar = [_kucuk(b) for b in u.get("baslik", [])]
    else:
        surecler, basliklar = set(), [_kucuk(kelime or "")]
    for hwnd, baslik, surec in pencereler():
        b = _kucuk(baslik)
        if surec in surecler or any(k and k in b for k in basliklar):
            if surec in ("python.exe", "pythonw.exe", "windowsterminal.exe", "conhost.exe") and anahtar != "cmd":
                continue  # asistanın kendi konsolunu kapatma
            bulunan.append(hwnd)
    return bulunan


def odakla(hwnd):
    try:
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        # Windows, arka plandaki programın pencere öne getirmesini engeller;
        # ALT tuşuna basıp bırakmak bu kısıtı aşmanın bilinen yolu.
        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.3)
        return True
    except Exception:
        return False


def pencere_bekle(anahtar, sure=12.0):
    bitis = time.time() + sure
    while time.time() < bitis:
        h = pencere_bul(anahtar)
        if h:
            return h
        time.sleep(0.4)
    return []


# ---------------- yardımcılar ----------------
def yapistir(metin):
    """Metni panoya koyup Ctrl+V ile yapıştırır (Türkçe karakterler bozulmaz)."""
    try:
        eski = pyperclip.paste()
    except Exception:
        eski = None
    pyperclip.copy(metin)
    time.sleep(0.1)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.3)
    if eski:
        try:
            pyperclip.copy(eski)
        except Exception:
            pass


def baslat_menusunden_ac(ad):
    pyautogui.press("win")
    time.sleep(0.8)
    yapistir(ad)
    time.sleep(1.2)
    pyautogui.press("enter")


def kabuk(komut):
    subprocess.Popen(komut, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)


# ---------------- asistan ----------------
class Eylemci:
    def __init__(self, ayar):
        self.ayar = ayar
        self._beyin = None

    @property
    def beyin(self):
        if self._beyin is None:
            from beyin import Beyin
            self._beyin = Beyin(self.ayar)
        self._beyin.ayar = self.ayar  # ayarlar arayüzden değişmiş olabilir
        return self._beyin

    def calistir(self, k: dict) -> str:
        """Komutu uygular, sesli söylenecek yanıtı döner."""
        f = getattr(self, "_" + k["tur"], None)
        if f is None:
            return "Bunu anlayamadım"
        return f(k) or ""

    # --- uygulamalar ---
    def _uygulama_ac(self, anahtar):
        u = UYGULAMALAR[anahtar]
        if u.get("ac"):
            kabuk(u["ac"])
        else:
            baslat_menusunden_ac(u.get("arama", u["goster"]))

    def _hazirla(self, anahtar):
        """Uygulama açıksa öne getirir, değilse açıp bekler. Pencere döner."""
        h = pencere_bul(anahtar)
        yeni = False
        if not h:
            self._uygulama_ac(anahtar)
            h = pencere_bekle(anahtar, self.ayar.get("acilis_bekleme", 12))
            yeni = True
        if not h:
            return None, yeni
        odakla(h[0])
        if yeni:
            time.sleep(self.ayar.get("yeni_acilan_bekleme", 2.5))
            # Not Defteri eski oturumu geri yükleyebilir: metni eski dosyaya değil yeni sekmeye yaz
            if UYGULAMALAR[anahtar].get("yeni_belge"):
                pyautogui.hotkey(*UYGULAMALAR[anahtar]["yeni_belge"])
                time.sleep(0.6)
        return h[0], yeni

    def _ac(self, k):
        a = k["uygulama"]
        h = pencere_bul(a)
        if h:
            odakla(h[0])
            return f"{UYGULAMALAR[a]['goster']} zaten açık, öne getirdim"
        self._uygulama_ac(a)
        return f"{UYGULAMALAR[a]['goster']} açılıyor"

    def _kapat(self, k):
        a = k["uygulama"]
        u = UYGULAMALAR[a]
        if u.get("kapat_komut"):  # Steam gibi kendi kapatma yolu olanlar
            kabuk(u["kapat_komut"])
            return f"{u['goster']} kapatılıyor"
        h = pencere_bul(a)
        for hwnd in h:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        if h:
            return f"{u['goster']} kapatılıyor"
        # penceresi yoksa (tepside çalışıyorsa) süreci sonlandır
        oldu = False
        for p in psutil.process_iter(["name"]):
            if (p.info["name"] or "").lower() in u.get("surec", []):
                try:
                    p.terminate(); oldu = True
                except Exception:
                    pass
        return f"{u['goster']} kapatıldı" if oldu else f"{u['goster']} zaten açık değil"

    def _ac_ara(self, k):
        baslat_menusunden_ac(k["ad"])
        return f"{k['ad']} açılıyor"

    def _kapat_ara(self, k):
        h = pencere_bul(kelime=k["ad"])
        for hwnd in h:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        return f"{k['ad']} kapatılıyor" if h else f"{k['ad']} adında açık pencere bulamadım"

    # --- yazma ---
    def _yaz(self, k):
        if not k["metin"]:
            return "Ne yazacağımı duyamadım"
        yapistir(k["metin"])
        return "Yazdım" if self.ayar.get("yazinca_soyle", False) else ""

    def _uygulamaya_yaz(self, k):
        a = k["uygulama"]
        hwnd, _ = self._hazirla(a)
        if not hwnd:
            return f"{UYGULAMALAR[a]['goster']} penceresini bulamadım"
        if not k["metin"]:
            return ""
        yapistir(k["metin"])
        return "Yazdım" if self.ayar.get("yazinca_soyle", False) else ""

    def _whatsapp(self, k):
        hwnd, yeni = self._hazirla("whatsapp")
        if not hwnd:
            return "WhatsApp'ı açamadım"
        if yeni:
            time.sleep(2)
        # sohbet ara
        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.6)
        pyautogui.hotkey("ctrl", "a")
        yapistir(k["kisi"])
        time.sleep(self.ayar.get("whatsapp_arama_bekleme", 1.8))
        if self.ayar.get("whatsapp_aramada_asagi_ok", False):
            pyautogui.press("down")
            time.sleep(0.2)
        pyautogui.press("enter")
        time.sleep(1.0)
        if not k["metin"]:
            return f"{k['kisi']} sohbeti açıldı"
        yapistir(k["metin"])
        if k["gonder"]:
            time.sleep(0.3)
            pyautogui.press("enter")
            return f"{k['kisi']} kişisine gönderildi"
        return f"{k['kisi']} kişisine yazdım, göndermek için gönder de"

    # --- web ---
    def _site(self, k):
        webbrowser.open(k["url"])
        return f"{k['ad']} açılıyor"

    def _ara(self, k):
        webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote(k["sorgu"]))
        return f"{k['sorgu']} aranıyor"

    def _youtube(self, k):
        webbrowser.open("https://www.youtube.com/results?search_query=" + urllib.parse.quote(k["sorgu"]))
        return f"YouTube'da {k['sorgu']} aranıyor"

    # --- tuşlar ve sistem ---
    def _tus(self, k):
        for _ in range(k.get("tekrar", 1)):
            for kombo in k["tuslar"]:
                pyautogui.hotkey(*kombo)
                time.sleep(0.05)
        return k.get("yanit", "")

    def _ekran_goruntusu(self, k):
        klasor = os.path.join(os.path.expanduser("~"), "Pictures", "Asistan")
        os.makedirs(klasor, exist_ok=True)
        yol = os.path.join(klasor, datetime.datetime.now().strftime("ekran_%Y%m%d_%H%M%S.png"))
        pyautogui.screenshot().save(yol)
        print("   Kaydedildi:", yol)
        return "Ekran görüntüsü Resimler, Asistan klasörüne kaydedildi"

    def _saat(self, k):
        s = datetime.datetime.now()
        return f"Saat {s.hour}:{s.minute:02d}"

    def _tarih(self, k):
        s = datetime.date.today()
        return f"Bugün {s.day} {AYLAR[s.month - 1]} {s.year}, {GUNLER[s.weekday()]}"

    def _kilitle(self, k):
        ctypes.windll.user32.LockWorkStation()
        return ""

    def _yardim(self, k):
        return YARDIM

    def _bilinmiyor(self, k):
        # Komut değilse bir soru ya da sohbettir: yapay zekâya sor
        metin = k.get("metin", "").strip()
        if self.ayar.get("yapay_zeka", True) and metin:
            return self.beyin.sor(metin)
        # yapay zekâ kapalıysa ne duyduğunu söyle ki kullanıcı yanlış anlamayı fark etsin
        return f"Anlayamadım. Şunu duydum: {metin}"

    def _unut(self, k):
        self.beyin.unut()
        return "Tamam, konuşmamızı unuttum"

    def _bos(self, k):
        return ""
