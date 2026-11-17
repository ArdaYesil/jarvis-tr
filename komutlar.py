"""Türkçe sesli komut çözümleyici.

Konuşmadan gelen metni bir eylem sözlüğüne çevirir. Windows'a dokunmaz,
bu yüzden mikrofonsuz test edilebilir (test_komutlar.py).
"""
import re

from uygulamalar import SITELER, UYGULAMALAR

KESME = "'’‘`´"

import difflib

# Google bazen "aç" kelimesini "açık", "aça", "hac" gibi duyabiliyor; hepsini kabul et
AC = {"aç", "açar", "açsana", "açın", "açabilir", "açık", "aça", "açıver", "açılsın",
      "açmanı", "açalım", "açıl", "başlat", "başlatır", "çalıştır", "çalıştırır"}
KAPAT = {"kapat", "kapatır", "kapatsana", "kapatın", "kapa", "kapatıver", "kapansın",
         "kapatmanı", "kapatalım", "kapatabilir", "sonlandır"}
# "steam uygulamasını aç" -> aradaki genel isimleri at
GENEL_ISIM = {"uygulamasını", "uygulaması", "uygulamayı", "programını", "programı",
              "oyununu", "oyunu", "uygulama", "program"}
YAZ = {"yaz", "yazar", "yazsana", "yazın", "yazabilir"}
GONDER = {"gönder", "yolla", "at", "gönderir", "yollar"}
ARA = {"ara", "arat", "aratır", "arar", "bul"}
YT_FIIL = {"aç", "ara", "oynat", "izle", "çal", "bul"}
DOLGU = {"lütfen", "mısın", "misin", "musun", "müsün", "bakalım", "hadi"}

CIKIS = {
    "çıkış", "çıkış yap", "asistanı kapat", "asistan kapat", "kendini kapat",
    "jarvis'i kapat", "jarvisi kapat", "jarvis kapat", "jarvis kapan", "kapan",
    "dinlemeyi bırak", "dinlemeyi durdur", "programı sonlandır", "güle güle",
}

# Sabit cümleler -> klavye kısayolu / özel eylem
def _tus(*kombolar, yanit="", tekrar=1):
    return {"tur": "tus", "tuslar": [list(k) for k in kombolar], "tekrar": tekrar, "yanit": yanit}

SABIT = {
    "kaydet": _tus(("ctrl", "s"), yanit="Kaydediyorum"),
    "dosyayı kaydet": _tus(("ctrl", "s"), yanit="Kaydediyorum"),
    "geri al": _tus(("ctrl", "z")),
    "ileri al": _tus(("ctrl", "y")),
    "tümünü seç": _tus(("ctrl", "a")),
    "hepsini seç": _tus(("ctrl", "a")),
    "kopyala": _tus(("ctrl", "c")),
    "yapıştır": _tus(("ctrl", "v")),
    "kes": _tus(("ctrl", "x")),
    "enter": _tus(("enter",)),
    "entera bas": _tus(("enter",)),
    "entere bas": _tus(("enter",)),
    "enter'a bas": _tus(("enter",)),
    "gönder": _tus(("enter",), yanit="Gönderildi"),
    "yeni satır": _tus(("shift", "enter")),
    "alt satır": _tus(("shift", "enter")),
    "sil": _tus(("backspace",)),
    "son harfi sil": _tus(("backspace",)),
    "son kelimeyi sil": _tus(("ctrl", "backspace")),
    "kelimeyi sil": _tus(("ctrl", "backspace")),
    "hepsini sil": _tus(("ctrl", "a"), ("delete",)),
    "tümünü sil": _tus(("ctrl", "a"), ("delete",)),
    "boşluk": _tus(("space",)),
    "tab": _tus(("tab",)),
    "escape": _tus(("esc",)),
    "iptal": _tus(("esc",)),
    "pencereyi kapat": _tus(("alt", "f4")),
    "bu pencereyi kapat": _tus(("alt", "f4")),
    "pencereyi küçült": _tus(("win", "down")),
    "pencereyi büyüt": _tus(("win", "up")),
    "masaüstünü göster": _tus(("win", "d")),
    "masaüstüne dön": _tus(("win", "d")),
    "pencere değiştir": _tus(("alt", "tab")),
    "diğer pencere": _tus(("alt", "tab")),
    "yeni sekme": _tus(("ctrl", "t")),
    "yeni sekme aç": _tus(("ctrl", "t")),
    "sekmeyi kapat": _tus(("ctrl", "w")),
    "sayfayı yenile": _tus(("f5",)),
    "yenile": _tus(("f5",)),
    "geri git": _tus(("alt", "left")),
    "ileri git": _tus(("alt", "right")),
    "aşağı kaydır": _tus(("pagedown",)),
    "yukarı kaydır": _tus(("pageup",)),
    "yeni dosya": _tus(("ctrl", "n")),
    "sesi aç": _tus(("volumeup",), tekrar=5, yanit="Ses açıldı"),
    "sesi artır": _tus(("volumeup",), tekrar=5, yanit="Ses artırıldı"),
    "sesi yükselt": _tus(("volumeup",), tekrar=5, yanit="Ses artırıldı"),
    "sesi kıs": _tus(("volumedown",), tekrar=5, yanit="Ses kısıldı"),
    "sesi azalt": _tus(("volumedown",), tekrar=5, yanit="Ses kısıldı"),
    "sesi kapat": _tus(("volumemute",)),
    "sessize al": _tus(("volumemute",)),
    "müziği durdur": _tus(("playpause",)),
    "müziği başlat": _tus(("playpause",)),
    "durdur": _tus(("playpause",)),
    "devam et": _tus(("playpause",)),
    "sonraki şarkı": _tus(("nexttrack",)),
    "önceki şarkı": _tus(("prevtrack",)),
    "ekran görüntüsü al": {"tur": "ekran_goruntusu"},
    "ekran resmi al": {"tur": "ekran_goruntusu"},
    "saat kaç": {"tur": "saat"},
    "saat": {"tur": "saat"},
    "bugün ayın kaçı": {"tur": "tarih"},
    "bugünün tarihi": {"tur": "tarih"},
    "tarih": {"tur": "tarih"},
    "bilgisayarı kilitle": {"tur": "kilitle"},
    "ekranı kilitle": {"tur": "kilitle"},
    "yardım": {"tur": "yardim"},
    "neler yapabilirsin": {"tur": "yardim"},
    "komutlar": {"tur": "yardim"},
    "konuşmayı unut": {"tur": "unut"},
    "sohbeti unut": {"tur": "unut"},
    "sohbeti sıfırla": {"tur": "unut"},
    "yeni konu": {"tur": "unut"},
}

# Yazdırılan metinde noktalama sözcükleri
NOKTALAMA = [
    (r"\s*\bsoru işareti\b", "?"),
    (r"\s*\bünlem işareti\b", "!"),
    (r"\s*\bünlem\b", "!"),
    (r"\s*\biki nokta\b", ":"),
    (r"\s*\bvirgül\b", ","),
    (r"\s*\bnokta\b", "."),
    (r"\s*\byeni satır\b\s*", "\n"),
]


def kucuk(s: str) -> str:
    """Türkçe kurallara uygun küçük harf."""
    return s.replace("I", "ı").replace("İ", "i").lower()


def buyuk_ilk(s: str) -> str:
    if not s:
        return s
    c = s[0]
    c = {"i": "İ", "ı": "I"}.get(c, c.upper())
    return c + s[1:]


def _norm(t: str) -> str:
    t = kucuk(t)
    for k in KESME[1:]:
        t = t.replace(k, "'")
    return re.sub(r"[^\w']", "", t).strip("'")


def _kok(t: str) -> str:
    """Ahmet'e -> Ahmet ,  Spotify'ı -> Spotify (orijinal yazımı korur)"""
    for k in KESME:
        if k in t:
            return t.split(k)[0]
    return re.sub(r"[^\w]", "", t)


def _ad_temizle(tokenler) -> str:
    """Bilinmeyen uygulama adını ekinden arındırır: "Steam'i" -> Steam, "zoomu" -> zoom."""
    tokenler = [t for t in tokenler if _norm(t) not in GENEL_ISIM]
    parcalar = []
    for i, t in enumerate(tokenler):
        if any(k in t for k in KESME):
            parcalar.append(_kok(t))
        elif i == len(tokenler) - 1 and len(t) > 4:
            # kesme işareti yoksa sondaki belirtme ekini (-ı -i -u -ü -yı -yi ...) at
            parcalar.append(re.sub(r"(y?[ıiuüIİ])$", "", re.sub(r"[^\w]", "", t)))
        else:
            parcalar.append(re.sub(r"[^\w]", "", t))
    return " ".join(p for p in parcalar if p)


def _parcala(metin: str):
    n, o = [], []
    for t in metin.split():
        nt = _norm(t)
        if nt:
            n.append(nt)
            o.append(t)
    # baştaki/sondaki dolgu sözcüklerini at
    while n and n[-1] in DOLGU:
        n.pop(); o.pop()
    while n and n[0] in DOLGU:
        n.pop(0); o.pop(0)
    # "açar mısın" -> "açar" ortadaki soru eklerini de at
    tut = [i for i, t in enumerate(n) if t not in {"mısın", "misin", "musun", "müsün"}]
    return [n[i] for i in tut], [o[i] for i in tut]


def metni_duzenle(tokenler, noktalama=True, ilk_buyuk=True) -> str:
    s = " ".join(tokenler).strip()
    # sondaki "diye" ("merhaba diye yaz")
    s = re.sub(r"\s+diye$", "", s, flags=re.IGNORECASE)
    if noktalama:
        for desen, yerine in NOKTALAMA:
            s = re.sub(desen, yerine, s, flags=re.IGNORECASE)
    s = s.strip(" ")
    return buyuk_ilk(s) if ilk_buyuk else s


# -------- uygulama adı eşleme --------
def _ad_listesi():
    liste = []
    for anahtar, u in UYGULAMALAR.items():
        for ad in u["adlar"]:
            liste.append((ad.split(), anahtar, "uygulama"))
    for ad in SITELER:
        liste.append(([ad], ad, "site"))
    # uzun isimler önce ("google chrome" "google"dan önce)
    liste.sort(key=lambda x: (-len(x[0]), -len(" ".join(x[0]))))
    return liste

_ADLAR = _ad_listesi()


def _ek_uygun(kalan: str) -> bool:
    """Ada eklenen kısım Türkçe bir hal eki gibi mi? (not defter+ine, chrome+'u)"""
    if kalan == "":
        return True
    if kalan.startswith("'"):
        return True
    return len(kalan) <= 4 and kalan.isalpha()


def uygulama_bul(n, bas=0):
    """n[bas:] bir uygulama/site adıyla başlıyorsa (anahtar, tur, kac_token) döner."""
    for parcalar, anahtar, tur in _ADLAR:
        k = len(parcalar)
        if bas + k > len(n):
            continue
        if n[bas:bas + k - 1] != parcalar[:-1]:
            continue
        son = n[bas + k - 1]
        if son.startswith(parcalar[-1]) and _ek_uygun(son[len(parcalar[-1]):]):
            return anahtar, tur, k
    return None


# -------- alt çözümleyiciler --------
def _arama_coz(n, o, ayar):
    if len(n) < 2:
        return None
    ilk = n[0]
    # youtube'da X aç / oynat / izle
    if ilk.startswith("youtube") or ilk.startswith("yutup"):
        if ilk not in ("youtube", "yutup") or n[1] in ("da", "de"):
            bas = 1 if ilk not in ("youtube", "yutup") else 2
            govde_n, govde_o = n[bas:], o[bas:]
            if govde_n and govde_n[-1] in YT_FIIL:
                govde_o = govde_o[:-1]
            sorgu = metni_duzenle(govde_o, noktalama=False, ilk_buyuk=False)
            if sorgu:
                return {"tur": "youtube", "sorgu": sorgu}
    # google'da / internette X ara
    if (ilk.startswith("google") and ilk != "google") or ilk in ("internette", "webde", "nette"):
        govde_n, govde_o = n[1:], o[1:]
        if govde_n and govde_n[-1] in ARA:
            govde_o = govde_o[:-1]
        sorgu = metni_duzenle(govde_o, noktalama=False, ilk_buyuk=False)
        if sorgu:
            return {"tur": "ara", "sorgu": sorgu}
    # X ara  (ama "whatsapp'ta ahmet'i ara" değil)
    if n[-1] in ARA and not uygulama_bul(n, 0):
        sorgu = metni_duzenle(o[:-1], noktalama=False, ilk_buyuk=False)
        return {"tur": "ara", "sorgu": sorgu}
    return None


def _whatsapp_coz(n, o, ayar):
    """n/o: 'whatsapp' kelimesinden SONRAKİ tokenler."""
    if not n:
        return None
    noktalama = ayar.get("noktalama_sozcukleri", True)
    ilk_buyuk = ayar.get("ilk_harf_buyuk", True)

    # whatsapp'a yaz merhaba  -> açık sohbete yaz
    if n[0] in YAZ:
        return {"tur": "uygulamaya_yaz", "uygulama": "whatsapp",
                "metin": metni_duzenle(o[1:], noktalama, ilk_buyuk)}

    # kişiyi bul: ilk 3 token içinde kesme işaretli olan, ya da "X kişisine"
    kisi_son = None
    for i in range(min(3, len(n))):
        if "'" in n[i] or n[i] in ("kişisine", "kişisinin", "kişisini"):
            kisi_son = i
            break
    if kisi_son is None:
        # kesme işareti yoksa: "ahmete mesaj gönder ..." kalıbı
        if len(n) >= 2 and n[1] in ("mesaj", "mesajı") and re.search(r"(y?[ae])$", n[0]):
            kisi = re.sub(r"(y?[ae])$", "", _kok(o[0]))
            kisi_son = 0
        else:
            return None
    else:
        if n[kisi_son].startswith("kişisi"):
            kisi = " ".join(_kok(t) for t in o[:kisi_son])
        else:
            kisi = " ".join([*(o[:kisi_son]), _kok(o[kisi_son])])
    kisi = re.sub(r"[^\w\s]", "", kisi).strip()
    if not kisi:
        return None

    mn, mo = n[kisi_son + 1:], o[kisi_son + 1:]
    # "sohbetini aç" / "aç"
    if not mn or mn[-1] in AC:
        return {"tur": "whatsapp", "kisi": kisi, "metin": "", "gonder": False}

    if mn[0] in ("mesaj", "mesajı"):
        mn, mo = mn[1:], mo[1:]
    fiil = None
    if mn and (mn[0] in GONDER or mn[0] in YAZ):
        fiil, mn, mo = mn[0], mn[1:], mo[1:]
    elif mn and (mn[-1] in GONDER or mn[-1] in YAZ):
        fiil, mn, mo = mn[-1], mn[:-1], mo[:-1]
        if mn and mn[-1] in ("mesaj", "mesajı", "diye"):
            mn, mo = mn[:-1], mo[:-1]
    if fiil is None:
        return None
    return {"tur": "whatsapp", "kisi": kisi,
            "metin": metni_duzenle(mo, noktalama, ilk_buyuk),
            "gonder": fiil in GONDER}


# -------- ana fonksiyonlar --------
def _uyandirma_kelimesi_mi(t: str, kelimeler) -> bool:
    t = _norm(_kok(t))
    if not t:
        return False
    for k in kelimeler:
        k = kucuk(k)
        if t == k:
            return True
        # "Jarvis" bazen "Carvis", "Jarvıs", "Javis" diye duyuluyor: benzerlik yeterliyse kabul et
        if len(k) >= 5 and difflib.SequenceMatcher(None, t, k).ratio() >= 0.8:
            return True
    return False


def uyandirma_ayikla(metin: str, kelimeler):
    """'Jarvis, not defterini aç' -> (True, 'not defterini aç').
    kelimeler boşsa her cümle komuttur."""
    if not kelimeler:
        return True, metin
    tok = metin.split()
    for i in range(min(2, len(tok))):  # "hey Jarvis" de olur
        if _uyandirma_kelimesi_mi(tok[i], kelimeler):
            # "Jarvis'i kapat": burada isim komutun nesnesi, cümleyi bütün bırak
            if any(k in tok[i] for k in KESME) and _norm(tok[i]).split("'")[-1] in ("i", "ı", "yi", "yı"):
                return True, " ".join(tok[i:])
            return True, " ".join(tok[i + 1:]).strip(" ,.")
    return False, metin


def coz(metin: str, ayar=None) -> dict:
    ayar = ayar or {}
    noktalama = ayar.get("noktalama_sozcukleri", True)
    ilk_buyuk = ayar.get("ilk_harf_buyuk", True)
    n, o = _parcala(metin)
    if not n:
        return {"tur": "bos"}
    cumle = " ".join(n)

    if cumle in CIKIS:
        return {"tur": "cikis"}
    if cumle in SABIT:
        return dict(SABIT[cumle])

    # "bana bir şiir yaz", "bana bir fıkra anlat": bilgisayar komutu değil, yapay zekâya gider
    if n[0] in ("bana", "benim", "bize") and not uygulama_bul(n, 1):
        return {"tur": "bilinmiyor", "metin": metin}

    # "yaz merhaba dünya" / "şunu yaz ..."  -> aktif pencereye yaz
    if n[0] in YAZ and len(n) > 1:
        return {"tur": "yaz", "metin": metni_duzenle(o[1:], noktalama, ilk_buyuk)}
    if n[0] == "şunu" and len(n) > 2 and n[1] in YAZ:
        return {"tur": "yaz", "metin": metni_duzenle(o[2:], noktalama, ilk_buyuk)}

    r = _arama_coz(n, o, ayar)
    if r:
        return r

    u = uygulama_bul(n, 0)
    if u:
        anahtar, tur, k = u
        rn, ro = n[k:], o[k:]
        while rn and rn[0] in GENEL_ISIM:
            rn, ro = rn[1:], ro[1:]
        if tur == "site":
            if not rn or rn[0] in AC:
                return {"tur": "site", "url": SITELER[anahtar], "ad": anahtar}
        else:
            if not rn or (rn[0] in AC):
                return {"tur": "ac", "uygulama": anahtar}
            if rn[0] in KAPAT:
                return {"tur": "kapat", "uygulama": anahtar}
            if anahtar == "whatsapp":
                w = _whatsapp_coz(rn, ro, ayar)
                if w:
                    return w
            if rn[0] in YAZ and len(rn) > 1:
                return {"tur": "uygulamaya_yaz", "uygulama": anahtar,
                        "metin": metni_duzenle(ro[1:], noktalama, ilk_buyuk)}
            if rn[-1] in YAZ and len(rn) > 1:
                return {"tur": "uygulamaya_yaz", "uygulama": anahtar,
                        "metin": metni_duzenle(ro[:-1], noktalama, ilk_buyuk)}

    # Fiil başta söylendiyse: "aç Steam'i", "kapat chrome"
    if len(n) >= 2 and (n[0] in AC or n[0] in KAPAT) and n[-1] not in AC | KAPAT:
        ters = coz(" ".join(o[1:] + o[:1]), ayar)
        if ters["tur"] != "bilinmiyor":
            return ters

    # Bilinmeyen uygulama: "zoom'u aç", "steam kapat"
    if len(n) >= 2 and n[-1] in AC:
        ad = _ad_temizle(o[:-1])
        if ad:
            return {"tur": "ac_ara", "ad": ad}
    if len(n) >= 2 and n[-1] in KAPAT:
        ad = _ad_temizle(o[:-1])
        if ad:
            return {"tur": "kapat_ara", "ad": ad}

    # "merhaba dünya yaz" -> aktif pencereye
    if n[-1] in YAZ and len(n) > 1:
        return {"tur": "yaz", "metin": metni_duzenle(o[:-1], noktalama, ilk_buyuk)}

    return {"tur": "bilinmiyor", "metin": metin}
