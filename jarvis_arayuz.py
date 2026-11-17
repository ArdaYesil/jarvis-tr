"""Jarvis - HUD arayüzlü sürüm.

    python jarvis_arayuz.py      (ya da jarvis.bat)

Mimari:
  * Dinleyici thread'i : mikrofonu dinler, Google'a gönderir, komutu kuyruğa koyar
  * Yürütücü thread'i  : kuyruktan komut alır, uygular, sesli yanıt verir
  * Arayüz             : arayuz/index.html (pywebview penceresi), Api sınıfı üzerinden konuşur
"""
import json
import os
import queue
import threading
import time
import traceback
import warnings

import psutil
import webview

from asistan import KLASOR, VARSAYILAN_AYAR, Ses, ayar_yukle, gunluge_yaz, tahmin_sec
from komutlar import coz
from uygulamalar import UYGULAMALAR

with warnings.catch_warnings():
    warnings.simplefilter("ignore", DeprecationWarning)
    try:
        import audioop
    except ImportError:  # Python 3.13+
        audioop = None

EK_VARSAYILAN = {
    "uyandirma_gerekli": True,
    "ses_hizi": 0,         # -10 .. 10
    "ses_seviyesi": 100,   # 0 .. 100
}
AYAR_YOLU = os.path.join(KLASOR, "ayarlar.json")
HATA_GUNLUGU = os.path.join(KLASOR, "jarvis_hata.txt")


def hata_yaz(e):
    try:
        with open(HATA_GUNLUGU, "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + repr(e) + "\n" + traceback.format_exc() + "\n")
    except Exception:
        pass


def _rms(veri):
    if audioop:
        return audioop.rms(veri, 2)
    import array
    a = array.array("h", veri)
    if not a:
        return 0
    return int((sum(x * x for x in a[::4]) / max(1, len(a) // 4)) ** 0.5)


class Jarvis:
    def __init__(self):
        self.ayar = {**VARSAYILAN_AYAR, **EK_VARSAYILAN, **ayar_yukle()}
        self.pencere = None
        self.kuyruk = queue.Queue()
        self.mesgul = threading.Event()        # yürütücü çalışırken mikrofonu dinleme
        self.dinleme_acik = threading.Event()  # arayüzden duraklat / devam
        self.dinleme_acik.set()
        self.durdur = threading.Event()
        self.mikrofon_degisti = threading.Event()
        self.baslatildi = False
        self.ses = None
        self._son_seviye = 0.0
        self.istatistik = {"komut": 0, "basarili": 0, "baslangic": time.time()}
        self.cpu = 0.0
        # psutil.cpu_percent ölçümü thread başına tutulur; tek bir thread'de sürekli ölç
        threading.Thread(target=self._cpu_olc, daemon=True).start()

    def _cpu_olc(self):
        while not self.durdur.is_set():
            try:
                self.cpu = psutil.cpu_percent(interval=1.0)
            except Exception:
                time.sleep(1)

    # ---------- arayüze olay gönder ----------
    def olay(self, tur, **veri):
        if not self.pencere:
            return
        try:
            js = json.dumps({"t": tur, **veri}, ensure_ascii=False, default=str)
            self.pencere.evaluate_js(f"window.jarvis && window.jarvis.olay({js})")
        except Exception:
            pass

    def durum(self, v, metin=""):
        self.olay("durum", v=v, metin=metin)

    # ---------- başlat ----------
    def baslat(self):
        if self.baslatildi:
            return
        self.baslatildi = True
        threading.Thread(target=self._yurutucu, daemon=True).start()
        threading.Thread(target=self._dinleyici, daemon=True).start()

    # ---------- yürütücü ----------
    def _ses_ayarla(self):
        if self.ses and self.ses.motor:
            try:
                self.ses.motor.Rate = int(self.ayar.get("ses_hizi", 0))
                self.ses.motor.Volume = int(self.ayar.get("ses_seviyesi", 100))
            except Exception:
                pass

    def soyle(self, metin):
        if not metin:
            return
        self.olay("yanit", metin=metin)
        if self.ayar.get("sesli_yanit", True) and self.ses:
            self.durum("konusuyor")
            self.ses.soyle(metin)

    def _yurutucu(self):
        import pythoncom
        pythoncom.CoInitialize()  # SAPI ses motoru bu thread'e ait olmalı
        from eylemler import Eylemci
        self.ses = Ses(True)
        self._ses_ayarla()
        eylemci = Eylemci(self.ayar)
        while not self.durdur.is_set():
            try:
                kaynak, metin = self.kuyruk.get(timeout=0.5)
            except queue.Empty:
                continue
            if kaynak == "ayar_ses":  # ses hızı/seviyesi değişti
                self._ses_ayarla()
                continue
            self.mesgul.set()
            try:
                if kaynak == "soyle":
                    self.soyle(metin)
                    continue
                komut = coz(metin, self.ayar)
                self.olay("komut", komut=komut, kaynak=kaynak)
                if komut["tur"] == "bos":
                    continue
                self.istatistik["komut"] += 1
                if komut["tur"] == "cikis":
                    self.soyle("Görüşürüz")
                    time.sleep(0.3)
                    self.kapat()
                    return
                # tanınmayan cümle = soru: yapay zekâ düşünürken farklı durum göster
                self.durum("dusunuyor" if komut["tur"] == "bilinmiyor" else "isleniyor", metin)
                eylemci.ayar = self.ayar
                yanit = eylemci.calistir(komut)
                if not (yanit or "").startswith("Anlayamadım"):
                    self.istatistik["basarili"] += 1
                self.soyle(yanit)
                if not yanit:
                    self.olay("yanit", metin="✓ Tamamlandı", sessiz=True)
            except Exception as e:
                hata_yaz(e)
                self.olay("hata", metin=f"Hata: {e}")
                try:
                    self.soyle("Bir hata oluştu")
                except Exception:
                    pass
            finally:
                self.mesgul.clear()
                self.durum("bekleme" if self.dinleme_acik.is_set() else "duraklatildi")

    # ---------- dinleyici ----------
    def _dinleyici(self):
        try:
            import speech_recognition as sr
        except Exception as e:
            self.olay("hata", metin=f"Ses tanıma yüklenemedi: {e}")
            return
        r = sr.Recognizer()
        r.dynamic_energy_threshold = True
        r.pause_threshold = 0.8
        mic = None
        uyanik_bitis = 0.0

        while not self.durdur.is_set():
            try:
                if mic is None or self.mikrofon_degisti.is_set():
                    self.mikrofon_degisti.clear()
                    self.durum("kalibre", "Ortam gürültüsü ölçülüyor...")
                    mic = sr.Microphone(device_index=self.ayar.get("mikrofon_index"))
                    with mic as k:
                        r.adjust_for_ambient_noise(k, duration=1.5)
                    self.durum("bekleme")
                    if not getattr(self, "_merhaba_dendi", False):
                        self._merhaba_dendi = True
                        self.kuyruk.put(("soyle", "Jarvis hazır"))

                if not self.dinleme_acik.is_set() or self.mesgul.is_set():
                    self.olay("seviye", v=0)
                    time.sleep(0.2)
                    continue

                with mic as kaynak:
                    self._seviye_izle(kaynak)
                    try:
                        kayit = r.listen(kaynak, timeout=1.5, phrase_time_limit=15)
                    except sr.WaitTimeoutError:
                        continue
                if not self.dinleme_acik.is_set():
                    continue
                self.olay("seviye", v=0)
                self.durum("analiz")
                try:
                    sonuc = r.recognize_google(kayit, language=self.ayar.get("dil", "tr-TR"), show_all=True)
                except sr.UnknownValueError:  # anlaşılır konuşma yok (gürültü, öksürük...)
                    continue
                except sr.RequestError as e:
                    self.olay("hata", metin="Ses tanıma servisine ulaşılamadı (internet bağlantını kontrol et)")
                    time.sleep(3)
                    continue
                finally:
                    if not self.mesgul.is_set():
                        self.durum("bekleme" if self.dinleme_acik.is_set() else "duraklatildi")
                if not sonuc or not sonuc.get("alternative"):
                    continue
                tahminler = [a["transcript"] for a in sonuc["alternative"] if a.get("transcript")]
                if not tahminler:
                    continue

                if self.ayar.get("uyandirma_gerekli", True):
                    kelimeler = self.ayar.get("uyandirma_kelimeleri") or []
                else:
                    kelimeler = []
                uyanik = time.time() < uyanik_bitis
                metin, uyandi, komut = tahmin_sec(tahminler, kelimeler, uyanik, self.ayar)
                gunluge_yaz(tahminler, metin, komut if uyandi else None, self.ayar)
                self.olay("duydum", metin=metin, tahminler=tahminler[1:4], uyandi=uyandi)
                if not uyandi:
                    continue
                if not komut.strip():
                    uyanik_bitis = time.time() + self.ayar.get("uyandiktan_sonra_bekleme", 8)
                    self.durum("uyanik")
                    try:
                        import winsound
                        winsound.Beep(1000, 120)
                    except Exception:
                        pass
                    self.kuyruk.put(("soyle", "Efendim"))
                    continue
                uyanik_bitis = 0.0
                self.kuyruk.put(("ses", komut))
            except Exception as e:
                hata_yaz(e)
                self.olay("hata", metin=f"Mikrofon hatası: {e}")
                mic = None
                time.sleep(2)

    def _seviye_izle(self, kaynak):
        """Mikrofon akışını sarmalayıp ses seviyesini arayüze yollar (halkalar sese tepki versin)."""
        akis = kaynak.stream
        orijinal = akis.read
        son = [0.0]

        def oku(boyut):
            veri = orijinal(boyut)
            simdi = time.time()
            if simdi - son[0] > 0.05:
                son[0] = simdi
                try:
                    seviye = min(1.0, _rms(veri) / 2500.0)
                    self.olay("seviye", v=round(seviye, 3))
                except Exception:
                    pass
            return veri

        akis.read = oku

    # ---------- ayarlar ----------
    def ayar_kaydet(self, yeni):
        eski_mic = self.ayar.get("mikrofon_index")
        for k, v in yeni.items():
            if k in VARSAYILAN_AYAR or k in EK_VARSAYILAN:
                self.ayar[k] = v
        with open(AYAR_YOLU, "w", encoding="utf-8") as f:
            json.dump(self.ayar, f, ensure_ascii=False, indent=2)
        if self.ayar.get("mikrofon_index") != eski_mic:
            self.mikrofon_degisti.set()
        # ses motoru yürütücü thread'ine ait: hız/ses ayarını orada uygulat
        self.kuyruk.put(("ayar_ses", ""))

    def kapat(self):
        self.durdur.set()
        try:
            self.pencere.destroy()
        except Exception:
            pass


class Api:
    """Arayüzdeki JavaScript'in çağırabildiği fonksiyonlar (window.pywebview.api.*)."""

    def __init__(self, j: Jarvis):
        self._j = j

    def _arayuz_ayari(self):
        """API anahtarı arayüze hiç gönderilmez; sadece kayıtlı olup olmadığı bildirilir."""
        a = dict(self._j.ayar)
        a["claude_api_kayitli"] = bool((a.pop("claude_api_anahtari", "") or "").strip()) or bool(os.environ.get("ANTHROPIC_API_KEY"))
        a["claude_api_anahtari"] = ""
        return a

    def hazir(self):
        self._j.baslat()
        return {"ayar": self._arayuz_ayari(), "uygulamalar": self.uygulamalar()}

    def ayarlari_al(self):
        return self._arayuz_ayari()

    def ayarlari_kaydet(self, yeni):
        yeni = dict(yeni)
        yeni.pop("claude_api_kayitli", None)
        if not (yeni.get("claude_api_anahtari") or "").strip():
            yeni.pop("claude_api_anahtari", None)  # boş kutu = mevcut anahtarı koru
        self._j.ayar_kaydet(yeni)
        return self._arayuz_ayari()

    def anahtar_sil(self):
        self._j.ayar_kaydet({"claude_api_anahtari": ""})
        return self._arayuz_ayari()

    def yapay_zeka_dene(self):
        """Ayarlardaki 'Bağlantıyı dene' düğmesi: kısa bir soru sorup sonucu döner."""
        from beyin import Beyin
        b = Beyin(self._j.ayar)
        if not b.hazir_mi():
            return {"ok": False, "metin": "Kayıtlı bir API anahtarı yok."}
        cevap = b.sor("Bağlantı testi: sadece 'Bağlantı başarılı' de.")
        ok = "başarılı" in cevap.lower()
        return {"ok": ok, "metin": cevap}

    def mikrofonlar(self):
        # PortAudio aynı anda iki thread'den başlatılırsa çöker; liste açılışta bir kez alınır
        return MIKROFONLAR

    def komut_gonder(self, metin):
        metin = (metin or "").strip()
        if metin:
            self._j.kuyruk.put(("yazi", metin))
        return True

    def dinleme(self, acik):
        if acik:
            self._j.dinleme_acik.set()
            self._j.durum("bekleme")
        else:
            self._j.dinleme_acik.clear()
            self._j.durum("duraklatildi")
        return acik

    def uygulamalar(self):
        return [{"anahtar": k, "ad": u["goster"]} for k, u in UYGULAMALAR.items()]

    def sistem(self):
        try:
            disk = psutil.disk_usage(os.environ.get("SystemDrive", "C:") + "\\")
            pil = psutil.sensors_battery()
            ag = psutil.net_io_counters()
            return {
                "cpu": self._j.cpu,
                "ram": psutil.virtual_memory().percent,
                "ram_gb": round(psutil.virtual_memory().used / 1024 ** 3, 1),
                "ram_toplam": round(psutil.virtual_memory().total / 1024 ** 3, 1),
                "disk": disk.percent,
                "disk_bos": round(disk.free / 1024 ** 3),
                "pil": pil.percent if pil else None,
                "sarj": bool(pil.power_plugged) if pil else None,
                "gonderilen": ag.bytes_sent,
                "alinan": ag.bytes_recv,
                "surec": len(psutil.pids()),
                "acilis": psutil.boot_time(),
                "komut": self._j.istatistik["komut"],
                "basarili": self._j.istatistik["basarili"],
                "oturum": self._j.istatistik["baslangic"],
            }
        except Exception as e:
            hata_yaz(e)
            return {}

    def gunluk_ac(self):
        yol = os.path.join(KLASOR, "jarvis_gunluk.txt")
        if not os.path.exists(yol):
            open(yol, "a", encoding="utf-8").close()
        os.startfile(yol)

    def kucult(self):
        self._j.pencere.minimize()

    def buyut(self):
        pencere_yerlestir(not pencere_buyuk_mu())

    def kapat(self):
        self._j.kapat()


MIKROFONLAR = []


def _hwnd():
    import win32gui
    return win32gui.FindWindow(None, "JARVIS")


def _calisma_alani():
    """Pencerenin bulunduğu monitörün görev çubuğu hariç alanı (fiziksel piksel)."""
    import win32api
    h = _hwnd()
    mon = win32api.MonitorFromWindow(h, 2) if h else win32api.MonitorFromPoint((0, 0), 2)
    return win32api.GetMonitorInfo(mon)["Work"]


def pencere_buyuk_mu():
    import win32gui
    h = _hwnd()
    return bool(h) and tuple(win32gui.GetWindowRect(h)) == tuple(_calisma_alani())


def pencere_yerlestir(buyuk=True):
    """Çerçevesiz pencereyi ekrana sığdırır (büyük) ya da ortalanmış %80 boyuta getirir."""
    import win32con
    import win32gui
    h = _hwnd()
    if not h:
        return
    l, t, r, b = _calisma_alani()
    w, hh = r - l, b - t
    if not buyuk:
        nw, nh = int(w * 0.8), int(hh * 0.85)
        l, t, w, hh = l + (w - nw) // 2, t + (hh - nh) // 2, nw, nh
    win32gui.SetWindowPos(h, 0, l, t, w, hh, win32con.SWP_NOZORDER | win32con.SWP_SHOWWINDOW)


def mikrofonlari_oku():
    """Giriş aygıtlarını listeler (sadece ana thread'de, dinleyici başlamadan önce çağır)."""
    try:
        import pyaudio
        pa = pyaudio.PyAudio()
        liste, gorulen = [], set()
        for i in range(pa.get_device_count()):
            d = pa.get_device_info_by_index(i)
            # sadece giriş aygıtları; MME (hostApi 0) kopyalarını tekilleştir
            if d.get("maxInputChannels", 0) > 0 and d.get("hostApi") == 0:
                ad = d["name"]
                # PortAudio UTF-8 adı Windows-1252 gibi çözüyor: "EÅŸleÅŸtirici" -> "Eşleştirici"
                for kodlama in ("cp1252", "latin-1"):
                    try:
                        ad = ad.encode(kodlama).decode("utf-8")
                        break
                    except (UnicodeEncodeError, UnicodeDecodeError):
                        pass
                if ad not in gorulen and "eşleştirici" not in ad.lower() and "mapper" not in ad.lower():
                    gorulen.add(ad)
                    liste.append({"index": i, "ad": ad})
        pa.terminate()
        return liste
    except Exception as e:
        hata_yaz(e)
        return []


def main():
    MIKROFONLAR.extend(mikrofonlari_oku())
    j = Jarvis()
    html = os.path.join(KLASOR, "arayuz", "index.html")
    j.pencere = webview.create_window(
        "JARVIS", html, js_api=Api(j),
        width=1480, height=900, min_size=(1150, 720),
        frameless=True, easy_drag=False, background_color="#02070d",
    )
    # ekran ölçeklendirmesi ne olursa olsun görev çubuğu hariç ekranı kaplasın
    j.pencere.events.shown += lambda: pencere_yerlestir(True)
    webview.start(debug=False)
    j.durdur.set()


if __name__ == "__main__":
    import sys
    # pythonw (jarvis.bat) ile konsol yokken print/log çağrıları çökmesin
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")
    try:
        main()
    except Exception as e:
        hata_yaz(e)
        raise
