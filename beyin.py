"""Jarvis'in soru-cevap beyni (Claude API).

Komut çözümleyicinin tanımadığı her cümle buraya gelir: "Türkiye'nin başkenti neresi",
"bana bir fıkra anlat", "yarın İstanbul'da hava nasıl olacak" gibi.

Kimlik bilgisi sırası: ayarlar.json'daki "claude_api_anahtari" -> ANTHROPIC_API_KEY ortam değişkeni
-> `ant auth login` profili (SDK kendisi çözer).
"""
import datetime
import os
import re
import threading

AYLAR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz",
         "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

MODEL = "claude-opus-5-5"

SISTEM = """Sen Jarvis'sin: kullanıcının Windows bilgisayarında çalışan, Türkçe konuşan kişisel sesli asistan.
Cevapların Windows'un Türkçe sesiyle yüksek sesle okunuyor. Bu yüzden:
- Kısa ve doğal konuşma dilinde cevap ver: çoğu soruda bir ila üç cümle. Kullanıcı ayrıntı isterse daha uzun anlatabilirsin.
- Markdown, madde işareti, tablo, emoji, bağlantı ya da kod bloğu kullanma; düz cümleler kur.
- Sayıları ve birimleri okunduğunda anlaşılır biçimde yaz (örneğin "yüzde 20", "3 derece").
- Bilmediğin ya da emin olmadığın şeyi uydurma; güncel bilgi gerekiyorsa web aramasını kullan.
- Kibar, sıcak ve hafif esprili ol ama lafı uzatma.
Uygulama açma, kapatma, yazı yazma gibi bilgisayar işlerini Jarvis'in komut sistemi ayrıca yapıyor; bu tür bir istek
sana geldiyse komutu anlaşılmamış demektir: kullanıcıya bunu nasıl söyleyebileceğini kısaca öner
(örnek: "Steam'i aç", "not defterine merhaba yaz")."""

GECMIS_TUR = 8  # hatırlanacak soru-cevap çifti


def _sade(metin: str) -> str:
    """Sesli okumaya uygun hale getir: markdown işaretlerini temizle."""
    metin = re.sub(r"```.*?```", "", metin, flags=re.S)
    metin = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", metin)  # [yazı](link) -> yazı
    metin = re.sub(r"[*_#`>]+", "", metin)
    metin = re.sub(r"^\s*[-•]\s+", "", metin, flags=re.M)
    metin = re.sub(r"\n{2,}", "\n", metin)
    return metin.strip()


class Beyin:
    def __init__(self, ayar):
        self.ayar = ayar
        self.gecmis = []  # [{"role": "user"|"assistant", "content": str}, ...]
        self._kilit = threading.Lock()
        self._istemci = None
        self._istemci_anahtar = None

    # ---------- kurulum ----------
    def _anahtar(self):
        return (self.ayar.get("claude_api_anahtari") or "").strip() or None

    def hazir_mi(self) -> bool:
        """Bir kimlik bilgisi bulunabiliyor mu? (anahtar, ortam değişkeni ya da ant profili)"""
        if not self.ayar.get("yapay_zeka", True):
            return False
        if self._anahtar() or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
            return True
        return os.path.isdir(os.path.join(os.path.expanduser("~"), ".config", "anthropic"))

    def _client(self):
        import anthropic
        anahtar = self._anahtar()
        if self._istemci is None or anahtar != self._istemci_anahtar:
            self._istemci = anthropic.Anthropic(api_key=anahtar, timeout=60.0) if anahtar else anthropic.Anthropic(timeout=60.0)
            self._istemci_anahtar = anahtar
        return self._istemci

    def unut(self):
        with self._kilit:
            self.gecmis.clear()

    # ---------- soru sor ----------
    def sor(self, soru: str) -> str:
        if not self.ayar.get("yapay_zeka", True):
            return "Soru cevaplama kapalı. Ayarlardan açabilirsin."
        if not self.hazir_mi():
            return ("Sorulara cevap verebilmem için ayarların Yapay Zekâ bölümüne "
                    "Claude API anahtarını eklemen gerekiyor.")
        import anthropic

        simdi = datetime.datetime.now()
        zaman = f"{simdi.day} {AYLAR[simdi.month - 1]} {simdi.year} {GUNLER[simdi.weekday()]}, saat {simdi:%H:%M}"
        # zaman bilgisi soruyla birlikte gider; sistem istemi sabit kalsın ki önbelleğe alınabilsin
        yeni = {"role": "user", "content": f"[Şu an: {zaman}]\n{soru}"}

        with self._kilit:
            mesajlar = self.gecmis[-GECMIS_TUR * 2:] + [yeni]

        araclar = []
        if self.ayar.get("web_arama", True):
            araclar.append({
                "type": "web_search_20260209", "name": "web_search", "max_uses": 3,
                "user_location": {"type": "approximate", "country": "TR", "timezone": "Europe/Istanbul"},
            })

        try:
            cevap = self._iste(mesajlar, araclar)
        except anthropic.AuthenticationError:
            return "Claude API anahtarı geçersiz görünüyor. Ayarlardan kontrol eder misin?"
        except anthropic.PermissionDeniedError:
            return "Bu API anahtarının Claude'u kullanma izni yok."
        except anthropic.RateLimitError:
            return "Şu an çok fazla istek gönderildi, biraz sonra tekrar sorar mısın?"
        except anthropic.APIConnectionError:
            return "Yapay zekâ servisine bağlanamadım. İnternet bağlantını kontrol et."
        except anthropic.APIStatusError as e:
            if e.status_code >= 500:
                return "Yapay zekâ servisinde geçici bir sorun var, birazdan tekrar dene."
            if "credit" in str(e.message).lower() or "billing" in str(e.message).lower():
                return "Anthropic hesabında yeterli kredi yok. console.anthropic.com adresinden kredi yüklemelisin."
            return f"Yapay zekâ isteği başarısız oldu: {e.message}"

        if cevap is None:
            return "Bu soruya cevap veremiyorum."
        with self._kilit:
            self.gecmis += [{"role": "user", "content": yeni["content"]},
                            {"role": "assistant", "content": cevap}]
            self.gecmis = self.gecmis[-GECMIS_TUR * 2:]
        return cevap

    def _iste(self, mesajlar, araclar):
        """İsteği gönderir; web araması uzun sürerse (pause_turn) devam ettirir.
        Cevap metnini, reddedilirse None döner."""
        istemci = self._client()
        mesajlar = list(mesajlar)
        ek = {"tools": araclar} if araclar else {}
        for _ in range(4):
            yanit = istemci.beta.messages.create(
                model=MODEL,
                max_tokens=4000,
                system=SISTEM,
                messages=mesajlar,
                **ek,
                # sohbet ve kısa sorular için düşük düşünme seviyesi: hızlı cevap
                output_config={"effort": self.ayar.get("yapay_zeka_dusunme", "low")},
                # güvenlik filtresi bir isteği reddederse sunucu uygun modelle yeniden dener
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            )
            if yanit.stop_reason == "pause_turn":
                mesajlar.append({"role": "assistant", "content": yanit.content})
                continue
            if yanit.stop_reason == "refusal":
                return None
            # web aramalı cevaplar kaynak atıflarının olduğu yerlerden birkaç metin bloğuna bölünür
            metin = "".join(b.text for b in yanit.content if b.type == "text")
            return _sade(metin) or "Buna bir cevabım yok."
        return "Araştırma çok uzun sürdü, soruyu biraz daha net sorar mısın?"
