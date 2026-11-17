"""Komut çözümleyici testleri:  python test_komutlar.py"""
from komutlar import coz, uyandirma_ayikla

ORNEKLER = [
    ("Not defterini aç", {"tur": "ac", "uygulama": "notepad"}),
    ("not defteri aç", {"tur": "ac", "uygulama": "notepad"}),
    ("Hesap makinesini açar mısın", {"tur": "ac", "uygulama": "hesap"}),
    ("Chrome'u kapat", {"tur": "kapat", "uygulama": "chrome"}),
    ("WhatsApp'ı aç", {"tur": "ac", "uygulama": "whatsapp"}),
    ("whatsappı kapat lütfen", {"tur": "kapat", "uygulama": "whatsapp"}),
    ("Not defterine merhaba dünya yaz", {"tur": "uygulamaya_yaz", "uygulama": "notepad", "metin": "Merhaba dünya"}),
    ("not defterine yaz bugün hava çok güzel nokta", {"tur": "uygulamaya_yaz", "uygulama": "notepad", "metin": "Bugün hava çok güzel."}),
    ("Word'e yaz sayın müdürüm virgül", {"tur": "uygulamaya_yaz", "uygulama": "word", "metin": "Sayın müdürüm,"}),
    ("WhatsApp'ta Ahmet'e merhaba nasılsın soru işareti gönder",
     {"tur": "whatsapp", "kisi": "Ahmet", "metin": "Merhaba nasılsın?", "gonder": True}),
    ("WhatsApp'tan Ayşe Yılmaz'a akşam geliyorum yaz",
     {"tur": "whatsapp", "kisi": "Ayşe Yılmaz", "metin": "Akşam geliyorum", "gonder": False}),
    ("whatsapp annem'e mesaj gönder eve geldim",
     {"tur": "whatsapp", "kisi": "annem", "metin": "Eve geldim", "gonder": True}),
    ("WhatsApp'ta Mehmet'in sohbetini aç", {"tur": "whatsapp", "kisi": "Mehmet", "metin": "", "gonder": False}),
    ("WhatsApp'a yaz tamam", {"tur": "uygulamaya_yaz", "uygulama": "whatsapp", "metin": "Tamam"}),
    ("yaz iyi akşamlar", {"tur": "yaz", "metin": "İyi akşamlar"}),
    ("şunu yaz toplantı yarın saat üçte", {"tur": "yaz", "metin": "Toplantı yarın saat üçte"}),
    ("Google'da hava durumu ara", {"tur": "ara", "sorgu": "hava durumu"}),
    ("istanbul nüfusu ara", {"tur": "ara", "sorgu": "istanbul nüfusu"}),
    ("YouTube'da Barış Manço şarkıları aç", {"tur": "youtube", "sorgu": "Barış Manço şarkıları"}),
    ("YouTube'u aç", {"tur": "site", "ad": "youtube"}),
    ("Spotify'ı aç", {"tur": "ac", "uygulama": "spotify"}),
    ("Zoom'u aç", {"tur": "ac_ara", "ad": "Zoom"}),
    ("Steam'i kapat", {"tur": "kapat", "uygulama": "steam"}),
    ("steami aç", {"tur": "ac", "uygulama": "steam"}),
    ("Steam'i aç", {"tur": "ac", "uygulama": "steam"}),
    ("stim aç", {"tur": "ac", "uygulama": "steam"}),
    ("İstimi aç", {"tur": "ac", "uygulama": "steam"}),
    ("Steam açık", {"tur": "ac", "uygulama": "steam"}),
    ("aç Steam'i", {"tur": "ac", "uygulama": "steam"}),
    ("steam uygulamasını aç", {"tur": "ac", "uygulama": "steam"}),
    ("Steam'i açar mısın lütfen", {"tur": "ac", "uygulama": "steam"}),
    ("discordu kapat", {"tur": "kapat", "uygulama": "discord"}),
    ("zoomu aç", {"tur": "ac_ara", "ad": "zoom"}),
    ("Epic Games'i aç", {"tur": "ac_ara", "ad": "Epic Games"}),
    ("Jarvis'i kapat", {"tur": "cikis"}),
    ("kapan", {"tur": "cikis"}),
    ("sesi kıs", {"tur": "tus"}),
    ("Kaydet", {"tur": "tus"}),
    ("pencereyi kapat", {"tur": "tus"}),
    ("saat kaç", {"tur": "saat"}),
    ("ekran görüntüsü al", {"tur": "ekran_goruntusu"}),
    ("asistanı kapat", {"tur": "cikis"}),
    ("bugün hava güzel", {"tur": "bilinmiyor"}),
    # sorular ve sohbet -> yapay zekâya gider (bilinmiyor)
    ("Türkiye'nin başkenti neresi", {"tur": "bilinmiyor"}),
    ("Ay Dünya'ya ne kadar uzak", {"tur": "bilinmiyor"}),
    ("bana bir şiir yaz", {"tur": "bilinmiyor"}),
    ("bana bir fıkra anlat", {"tur": "bilinmiyor"}),
    ("nasılsın", {"tur": "bilinmiyor"}),
    ("konuşmayı unut", {"tur": "unut"}),
    # "bana" ile başlasa da gerçek komutlar bozulmasın
    ("not defterine bana göre güzel yaz", {"tur": "uygulamaya_yaz", "uygulama": "notepad"}),
]


def test():
    hata = 0
    for cumle, beklenen in ORNEKLER:
        sonuc = coz(cumle)
        uyuyor = all(sonuc.get(k) == v for k, v in beklenen.items())
        if not uyuyor:
            hata += 1
        print(("OK  " if uyuyor else "HATA"), repr(cumle), "->", sonuc)

    kelimeler = ["jarvis", "carvis", "cervis", "jervis", "çarvis", "jarviz"]
    uyandirmalar = [
        ("Jarvis, not defterini aç", (True, "not defterini aç")),
        ("Jarvis Steam'i aç", (True, "Steam'i aç")),
        ("hey Jarvis saat kaç", (True, "saat kaç")),
        ("Carvis steami aç", (True, "steami aç")),
        ("Jarvıs sesi kıs", (True, "sesi kıs")),
        ("Javis kaydet", (True, "kaydet")),
        ("Jarvis", (True, "")),
        ("Jarvis'i kapat", (True, "Jarvis'i kapat")),
        ("not defterini aç", (False, "not defterini aç")),
        ("Asistan not defterini aç", (False, "Asistan not defterini aç")),
        ("bugün çarşıya gittim", (False, "bugün çarşıya gittim")),
    ]
    for cumle, beklenen in uyandirmalar:
        s = uyandirma_ayikla(cumle, kelimeler)
        if s != beklenen:
            hata += 1
        print(("OK  " if s == beklenen else "HATA"), "uyandırma", repr(cumle), "->", s)

    # Google'ın birden çok tahmini: anlaşılabilen ilk tahmin seçilmeli
    from asistan import tahmin_sec
    secim = tahmin_sec(["Jarvis teyzemi gördüm", "Jarvis Steam'i aç", "Jarvis steam açık"], kelimeler, False, {})
    beklenen = ("Jarvis Steam'i aç", True, "Steam'i aç")
    if secim != beklenen:
        hata += 1
    print(("OK  " if secim == beklenen else "HATA"), "tahmin seçimi ->", secim)

    toplam = len(ORNEKLER) + len(uyandirmalar) + 1
    print(f"\n{toplam - hata} başarılı, {hata} hatalı")
    return hata


if __name__ == "__main__":
    raise SystemExit(1 if test() else 0)
