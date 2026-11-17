"""Jarvis - Türkçe sesli komutlarla bilgisayarı yönetir.

Kullanım:
    python asistan.py               -> mikrofonla dinler
    python asistan.py --yazi        -> komutları klavyeden yazarak dene (mikrofonsuz)
    python asistan.py --mikrofonlar -> mikrofon listesini göster
"""
import argparse
import json
import os
import sys
import time
import winsound

from komutlar import coz, uyandirma_ayikla

KLASOR = os.path.dirname(os.path.abspath(__file__))

VARSAYILAN_AYAR = {
    "uyandirma_kelimeleri": ["jarvis", "carvis", "cervis", "jervis", "çarvis", "jarviz"],
    "gunluk": True,
    "uyandiktan_sonra_bekleme": 8,
    "dil": "tr-TR",
    "sesli_yanit": True,
    "yazinca_soyle": False,
    "mikrofon_index": None,
    "noktalama_sozcukleri": True,
    "ilk_harf_buyuk": True,
    "acilis_bekleme": 12,
    "yeni_acilan_bekleme": 2.5,
    "whatsapp_arama_bekleme": 1.8,
    "whatsapp_aramada_asagi_ok": False,
    # yapay zekâ (soru-cevap) — beyin.py
    "yapay_zeka": True,
    "web_arama": True,
    "yapay_zeka_dusunme": "low",   # low | medium | high
    "claude_api_anahtari": "",     # boşsa ANTHROPIC_API_KEY ortam değişkeni kullanılır
}


def ayar_yukle():
    ayar = dict(VARSAYILAN_AYAR)
    yol = os.path.join(KLASOR, "ayarlar.json")
    if os.path.exists(yol):
        with open(yol, encoding="utf-8") as f:
            ayar.update(json.load(f))
    else:
        with open(yol, "w", encoding="utf-8") as f:
            json.dump(VARSAYILAN_AYAR, f, ensure_ascii=False, indent=2)
    return ayar


class Ses:
    """Windows'un yerleşik konuşma motoru (SAPI) ile Türkçe yanıt."""

    def __init__(self, acik=True):
        self.motor = None
        if not acik:
            return
        try:
            import win32com.client
            self.motor = win32com.client.Dispatch("SAPI.SpVoice")
            turkce = None
            # Klasik SAPI sesleri + Windows 10/11'in OneCore sesleri (Tolga burada olur)
            kaynaklar = [self.motor.GetVoices()]
            try:
                kat = win32com.client.Dispatch("SAPI.SpObjectTokenCategory")
                kat.SetId(r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices", False)
                kaynaklar.append(kat.EnumerateTokens())
            except Exception:
                pass
            for liste in kaynaklar:
                for v in liste:
                    d = v.GetDescription()
                    if any(x in d for x in ("Turkish", "Türkçe", "Tolga")):
                        turkce = v
                        break
                if turkce is not None:
                    break
            if turkce is not None:
                self.motor.Voice = turkce
            else:
                print("! Türkçe ses bulunamadı; sesli yanıt kapatıldı. "
                      "(Ayarlar > Zaman ve dil > Konuşma'dan Türkçe ses ekleyebilirsin)")
                self.motor = None
        except Exception as e:
            print("! Sesli yanıt başlatılamadı:", e)
            self.motor = None

    def soyle(self, metin):
        if not metin:
            return
        print("  >", metin)
        if self.motor:
            try:
                self.motor.Speak(metin)
            except Exception:
                pass


def tahmin_sec(tahminler, kelimeler, uyanik, ayar):
    """Google'ın tahminleri arasından uyandırma kelimesi içeren ve anlaşılabilen ilkini seçer.
    Döner: (seçilen metin, uyandı mı, komut metni)"""
    adaylar = []
    for t in tahminler:
        uyandi, komut = uyandirma_ayikla(t, kelimeler)
        if uyanik:
            uyandi = True
        if uyandi:
            adaylar.append((t, komut))
    if not adaylar:
        return tahminler[0], False, tahminler[0]
    for t, komut in adaylar:
        if not komut.strip() or coz(komut, ayar)["tur"] != "bilinmiyor":
            return t, True, komut
    return adaylar[0][0], True, adaylar[0][1]


def gunluge_yaz(tahminler, secilen, komut, ayar):
    """Jarvis'e verilen komutları jarvis_gunluk.txt'ye yazar: yanlış anlamaları düzeltmek için.
    komut None ise cümle Jarvis'e söylenmemiştir (ortamdaki konuşma): gizlilik için ASLA kaydedilmez."""
    if komut is None or not ayar.get("gunluk", True):
        return
    try:
        with open(os.path.join(KLASOR, "jarvis_gunluk.txt"), "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | seçilen: {secilen} | "
                    f"komut: {coz(komut, ayar) if komut else '-'} | tahminler: {tahminler}\n")
    except Exception:
        pass


def isle(metin, ayar, eylemci, ses):
    komut = coz(metin, ayar)
    print("   komut:", komut)
    if komut["tur"] == "cikis":
        ses.soyle("Görüşürüz")
        return False
    try:
        ses.soyle(eylemci.calistir(komut))
    except Exception as e:  # FailSafe dahil: döngü ölmesin
        print("! Hata:", e)
        ses.soyle("Bir hata oluştu")
    return True


def yazi_modu(ayar, eylemci, ses):
    print("Yazı modu: komut yaz, Enter'a bas. (çıkış: 'çıkış')\n"
          "Not: kısayol komutları (kaydet, sil...) bu konsol penceresine gider.\n")
    while True:
        try:
            metin = input("komut> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if metin and not isle(metin, ayar, eylemci, ses):
            break


def ses_modu(ayar, eylemci, ses):
    import speech_recognition as sr

    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.8
    mic = sr.Microphone(device_index=ayar.get("mikrofon_index"))

    print("Ortam gürültüsü ölçülüyor, 2 saniye sessiz ol...")
    with mic as kaynak:
        r.adjust_for_ambient_noise(kaynak, duration=2)

    kelimeler = ayar.get("uyandirma_kelimeleri") or []
    if kelimeler:
        print(f"Hazır! Komuttan önce '{kelimeler[0]}' de.  Örn: '{kelimeler[0]}, not defterini aç'")
    else:
        print("Hazır! Komutunu söyle.")
    ses.soyle("Jarvis hazır")

    uyanik_bitis = 0.0
    while True:
        try:
            # Her turda mikrofonu yeniden açıyoruz: Jarvis kendi sesini duymasın.
            with mic as kaynak:
                print("\n🎤 Dinliyorum...")
                ses_kaydi = r.listen(kaynak, timeout=None, phrase_time_limit=15)
            sonuc = r.recognize_google(ses_kaydi, language=ayar.get("dil", "tr-TR"), show_all=True)
        except sr.UnknownValueError:  # anlaşılır konuşma yok
            continue
        except sr.RequestError as e:
            print("! Ses tanıma servisine ulaşılamadı (internet?):", e)
            time.sleep(3)
            continue
        except KeyboardInterrupt:
            break
        if not sonuc or not sonuc.get("alternative"):
            continue
        tahminler = [a["transcript"] for a in sonuc["alternative"] if a.get("transcript")]
        if not tahminler:
            continue

        uyanik = time.time() < uyanik_bitis  # "Jarvis" dedikten hemen sonraki cümle
        metin, uyandi, komut = tahmin_sec(tahminler, kelimeler, uyanik, ayar)
        print("Duydum:", metin, ("   (diğer tahminler: " + " | ".join(tahminler[1:4]) + ")") if len(tahminler) > 1 else "")
        gunluge_yaz(tahminler, metin, komut if uyandi else None, ayar)
        if not uyandi:
            continue
        if not komut.strip():
            winsound.Beep(1000, 150)
            ses.soyle("Efendim")
            uyanik_bitis = time.time() + ayar.get("uyandiktan_sonra_bekleme", 8)
            continue
        uyanik_bitis = 0.0
        if not isle(komut, ayar, eylemci, ses):
            break


def main():
    p = argparse.ArgumentParser(description="Türkçe sesli asistan")
    p.add_argument("--yazi", action="store_true", help="mikrofon yerine klavyeden komut")
    p.add_argument("--mikrofonlar", action="store_true", help="mikrofonları listele")
    p.add_argument("--sessiz", action="store_true", help="sesli yanıtı kapat")
    a = p.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if a.mikrofonlar:
        import speech_recognition as sr
        for i, ad in enumerate(sr.Microphone.list_microphone_names()):
            print(i, ad)
        return

    from eylemler import Eylemci
    ayar = ayar_yukle()
    ses = Ses(ayar.get("sesli_yanit", True) and not a.sessiz)
    eylemci = Eylemci(ayar)

    if a.yazi:
        yazi_modu(ayar, eylemci, ses)
    else:
        ses_modu(ayar, eylemci, ses)


if __name__ == "__main__":
    main()
