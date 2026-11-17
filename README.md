# Jarvis — Türkçe Sesli Asistan

> [!WARNING]
> **Bu proje geliştirme aşamasındadır.** Çalışır durumda ama hatalar olabilir, özellikler değişebilir.
> Bilinen sınırlamalar için [Bilinen sınırlamalar](#bilinen-sınırlamalar) bölümüne bak.
> Bir sorun bulursan ya da önerin varsa GitHub'da **Issues** bölümünden bildirebilirsin.

Jarvis, bilgisayarını Türkçe sesli komutlarla yönetmeni sağlar. "Jarvis" diye seslenip söylediğini yapar:

- 🗂️ Uygulama açar ve kapatır: Not Defteri, WhatsApp, Chrome, Steam, Spotify, Word…
- ⌨️ Not Defteri, Word, WhatsApp gibi yerlere **senin yerine yazı yazar**
- 💬 WhatsApp'ta istediğin kişiye mesaj yazar ya da gönderir
- 🔎 Google'da ve YouTube'da arama yapar
- 🔊 Sesi açar/kısar, müziği durdurur, pencereleri yönetir, ekran görüntüsü alır
- 🧠 Sorularına cevap verir: *"Ay Dünya'ya ne kadar uzak?"* — **isteğe bağlı; ücretli bir yapay zekâ API anahtarı gerektirir** ([nasıl alınır?](#yapay-zekâ-api-anahtarı-nasıl-alınır))

> [!NOTE]
> Soru-cevap dışındaki **tüm özellikler ücretsizdir** ve API anahtarı olmadan çalışır.

Filmlerdeki gibi bir **hologram arayüzü** vardır: ortadaki halkalar sesine tepki verir, cevaplarını Türkçe sesle okur.

---

## İçindekiler
1. [Kurulum](#kurulum)
2. [Nasıl kullanılır?](#nasıl-kullanılır)
3. [Komut listesi](#komut-listesi)
4. [Sorulara cevap verme (yapay zekâ)](#sorulara-cevap-verme-yapay-zekâ)
5. [Arayüz rehberi](#arayüz-rehberi)
6. [Sorun giderme](#sorun-giderme)
7. [Gizlilik](#gizlilik)
8. [Bilinen sınırlamalar](#bilinen-sınırlamalar)
9. [Geliştiriciler için](#geliştiriciler-için)

---

## Kurulum

### Gerekenler
| | |
|---|---|
| İşletim sistemi | **Windows 10 veya 11** (başka sistemlerde çalışmaz) |
| Python | **3.12 veya üstü** |
| Donanım | Mikrofon (dizüstü bilgisayarın dahili mikrofonu yeterli) |
| İnternet | Gerekli (konuşma tanıma Google üzerinden yapılır) |

### Adım 1: Python'u kur
1. [python.org/downloads](https://www.python.org/downloads/) adresinden Python'u indir.
2. Kurulumun **ilk ekranında** en alttaki **"Add Python to PATH"** kutusunu **mutlaka işaretle**, sonra *Install Now*'a tıkla.

### Adım 2: Jarvis'i indir
1. Bu sayfanın üstündeki yeşil **Code** düğmesine tıkla → **Download ZIP**.
2. İnen ZIP dosyasına sağ tıkla → **Tümünü ayıkla** → bir klasöre çıkar (örneğin Masaüstü).

### Adım 3: Gerekli paketleri kur
1. Çıkardığın **Jarvis klasörünü** aç.
2. Pencerenin üstündeki **adres çubuğuna** tıkla, `cmd` yaz ve **Enter**'a bas. Siyah bir komut penceresi açılır.
3. Şu komutu yapıştırıp **Enter**'a bas ve bitmesini bekle (1–2 dakika sürebilir):
   ```
   python -m pip install -r requirements.txt
   ```

### Adım 4: Jarvis'i başlat
Klasördeki **`jarvis.bat`** dosyasına çift tıkla. Açılış animasyonundan sonra Jarvis *"Jarvis hazır"* der. Hazırsın! 🎉

### İsteğe bağlı: Türkçe ses
Jarvis cevaplarını Windows'un Türkçe sesiyle okur. Bilgisayarında Türkçe ses yoksa Jarvis yine çalışır ama **sessiz** cevap verir (sadece ekranda yazar). Eklemek için:
**Windows Ayarları → Zaman ve dil → Konuşma → Ses ekle → Türkçe**

### İsteğe bağlı: Sorulara cevap için API anahtarı
Jarvis'in sorularına cevap verebilmesi (*"Türkiye'nin başkenti neresi?"*) için bir **yapay zekâ API anahtarı** gerekir.
Adım adım anlatımı aşağıda: [Yapay zekâ API anahtarı nasıl alınır?](#yapay-zekâ-api-anahtarı-nasıl-alınır)
Bu adımı atlarsan Jarvis'in bütün bilgisayar komutları yine çalışır; yalnızca sorulara cevap veremez.

---

## Nasıl kullanılır?

### Altın kural: önce "Jarvis" de
Jarvis sürekli dinler ama **sadece adı söylendiğinde** harekete geçer. Böylece odadaki konuşmaları yanlışlıkla komut sanmaz.

> 🗣️ *"Jarvis, not defterini aç"*
> 🗣️ *"Jarvis, Steam'i aç"*
> 🗣️ *"Jarvis, saat kaç?"*

İstersen önce sadece **"Jarvis"** de; bip sesi gelir ve *"Efendim"* der. Ardından **8 saniye içinde** komutunu söyle.

### Konuşmak istemiyorsan: yaz
Ekranın altındaki **komut kutusuna** yazıp **Enter**'a basabilirsin. Yazarken "Jarvis" demene gerek yok.
Klavyeden `/` tuşuna basmak seni doğrudan komut kutusuna götürür.

### Dinlemeyi durdurmak
Komut kutusunun solundaki **mikrofon düğmesine** tıkla. Jarvis dinlemeyi bırakır; tekrar tıklayınca devam eder.

### Kapatmak
Sağ üstteki **✕** düğmesine bas ya da *"Jarvis'i kapat"* de.

### Acil durdurma
Jarvis senin yerine fare/klavye kullanırken bir şey ters giderse, **fareyi ekranın sol üst köşesine** götür. Yaptığı işlem anında durur.

---

## Komut listesi

Bunlar örnek; Jarvis aynı şeyin farklı söyleniş biçimlerini de anlar (*"Steam'i aç"*, *"Steam'i açar mısın"*, *"aç Steam'i"*).
Aşağıdakilerin hepsinin başına **"Jarvis"** eklemeyi unutma.

| Ne yapar | Örnek |
|---|---|
| Uygulama aç | "not defterini aç", "hesap makinesini aç", "WhatsApp'ı aç", "Spotify'ı aç" |
| Uygulama kapat | "Chrome'u kapat", "not defterini kapat", "Steam'i kapat" |
| Listede olmayan uygulama | "Zoom'u aç" — Başlat menüsünde arayıp açar |
| Uygulamaya yaz | "not defterine merhaba dünya yaz", "Word'e yaz sayın müdürüm virgül" |
| Açık pencereye yaz | "yaz iyi akşamlar", "şunu yaz toplantı yarın" |
| WhatsApp'ta yaz (**göndermez**) | "WhatsApp'ta Ahmet'e akşam geliyorum yaz" |
| WhatsApp'ta gönder | "WhatsApp'ta Ahmet'e merhaba nasılsın soru işareti gönder" |
| WhatsApp sohbeti aç | "WhatsApp'ta Mehmet'in sohbetini aç" |
| İnternette ara | "Google'da hava durumu ara", "YouTube'da Barış Manço aç" |
| Site aç | "YouTube'u aç", "Gmail'i aç" |
| Düzenleme | "kaydet", "geri al", "tümünü seç", "kopyala", "yapıştır", "sil", "son kelimeyi sil", "hepsini sil", "yeni satır", "gönder" |
| Pencere | "pencereyi kapat", "pencereyi küçült", "masaüstünü göster", "yeni sekme", "sekmeyi kapat" |
| Ses ve müzik | "sesi aç", "sesi kıs", "sessize al", "sonraki şarkı", "müziği durdur" |
| Diğer | "saat kaç", "bugünün tarihi", "ekran görüntüsü al", "ekranı kilitle", "yardım" |
| Soru sor | "Türkiye'nin başkenti neresi?", "bana bir fıkra anlat" (bkz. [yapay zekâ](#sorulara-cevap-verme-yapay-zekâ)) |
| Sohbeti sıfırla | "konuşmayı unut" |
| Jarvis'i kapat | "Jarvis'i kapat" |

**Yazdırırken noktalama:** *virgül, nokta, soru işareti, ünlem, iki nokta, yeni satır* dediğinde işarete çevrilir.
> 🗣️ *"Jarvis, not defterine merhaba virgül nasılsın soru işareti yaz"* → `Merhaba, nasılsın?`

**WhatsApp ipucu:** "yaz" mesajı yalnızca kutuya yazar; kontrol edip *"Jarvis, gönder"* diyebilirsin. Doğrudan "gönder" dersen hemen yollar.
Kişiyi WhatsApp'ın arama kutusundaki **ilk sonuçtan** seçer, bu yüzden rehberindeki ismi tam söyle.

Ekran görüntüleri **Resimler → Asistan** klasörüne kaydedilir.

---

## Sorulara cevap verme (yapay zekâ)

Bilgisayar komutu olmayan her cümleyi Jarvis bir **soru** olarak kabul eder ve Claude yapay zekâsına sorar. Cevabı sesli okur.

- Güncel sorular için internette arama yapabilir: *"yarın İstanbul'da hava nasıl?"*
- Son birkaç konuşmayı hatırlar, devam soruları çalışır: *"Türkiye'nin başkenti neresi?"* → *"Nüfusu ne kadar?"*
- *"Konuşmayı unut"* dersen sohbeti sıfırlar.
- Yapay zekâ düşünürken ortadaki halka **mora** döner.

### Yapay zekâ API anahtarı nasıl alınır?
Bu özellik **isteğe bağlıdır** ve Anthropic'in Claude yapay zekâsını kullanır. Bunun için kendi **API anahtarın** gerekir.
API anahtarı, Jarvis'in senin hesabın adına yapay zekâya soru sormasını sağlayan gizli bir şifredir.

> [!IMPORTANT]
> API kullanımı **ücretlidir** ve önceden yüklenen krediden düşülür. Her soru genellikle çok küçük bir tutar tutar,
> ama ne kadar harcadığını Anthropic Console'dan takip edebilir, harcama sınırı koyabilirsin.
> *(Claude.ai sohbet aboneliği API'yi kapsamaz; ikisi ayrı ücretlendirilir.)*

**1. Hesap aç**
[console.anthropic.com](https://console.anthropic.com) adresine git ve e-postanla ya da Google hesabınla kaydol.

**2. Kredi yükle**
Console'da **Billing** (Faturalandırma) bölümüne gir, bir ödeme yöntemi ekle ve kredi yükle.
Kredi olmadan anahtar oluşturabilirsin ama **çalışmaz**: Jarvis'teki bağlantı testi başarısız olur.

**3. Anahtarı oluştur**
Console'da **API Keys** bölümüne gir → **Create Key** düğmesine tıkla → anahtara bir isim ver (örneğin `Jarvis`) → oluştur.
Anahtar `sk-ant-` ile başlayan uzun bir metindir.

> [!CAUTION]
> Anahtar **yalnızca bir kez gösterilir**. Hemen **kopyala**; pencereyi kapatırsan tekrar göremezsin, yeni bir anahtar oluşturman gerekir.
> Anahtarı kimseyle paylaşma ve hiçbir yere (GitHub, mesajlar vb.) yapıştırma: anahtarını bilen herkes senin kredini harcayabilir.

**4. Anahtarı Jarvis'e yaz**
1. Jarvis'i aç (`jarvis.bat`).
2. Üstteki **⚙ AYARLAR** düğmesine tıkla (ya da `Alt+4`).
3. Açılan panelde **YAPAY ZEKÂ** sekmesine geç.
4. **"Claude API anahtarı"** kutusuna anahtarı yapıştır (`Ctrl+V`).
5. Alttaki **KAYDET** düğmesine bas. Kutunun altında **"● Anahtar kayıtlı"** yazısı görünür.
6. **BAĞLANTIYI DENE** düğmesine bas. **"✓ Bağlantı başarılı"** görüyorsan hazırsın.
7. Dene: *"Jarvis, Ay Dünya'ya ne kadar uzak?"*

Anahtar yalnızca senin bilgisayarındaki `ayarlar.json` dosyasına kaydedilir ve ekranda bir daha gösterilmez.
Silmek istersen aynı yerdeki **ANAHTARI KALDIR** düğmesini kullan.

**Bağlantı testi başarısız olursa:**
| Mesaj | Ne yapmalı |
|---|---|
| "API anahtarı geçersiz görünüyor" | Anahtarı eksik ya da yanlış kopyalamış olabilirsin. Console'dan yeni bir anahtar oluşturup tekrar yapıştır. |
| "Anthropic hesabında yeterli kredi yok" | Console'da **Billing** bölümünden kredi yükle. |
| "Bu API anahtarının Claude'u kullanma izni yok" | Anahtarın doğru hesaba ait olduğunu ve silinmediğini Console'daki **API Keys** bölümünden kontrol et. |
| "Yapay zekâ servisine bağlanamadım" | İnternet bağlantını kontrol et. |

---

## Arayüz rehberi

Ana ekranda yalnızca gerekenler var. Geri kalanı üst çubuktaki düğmelerle **yandan açılan panellerde**:

| Düğme | Kısayol | İçinde |
|---|---|---|
| SİSTEM | `Alt+1` | İşlemci, bellek, disk, pil, ağ durumu |
| UYGULAMALAR | `Alt+2` | Tek tıkla uygulama açma |
| REHBER | `Alt+3` | Örnek komutlar — tıklayınca komut kutusuna yazılır |
| AYARLAR | `Alt+4` | Tüm ayarlar (değişiklikten sonra **KAYDET** ya da `Ctrl+S`) |

Paneli kapatmak için `Esc`'ye bas, ✕'e ya da boş bir yere tıkla.

**Ortadaki halkaların rengi ne anlatıyor?**

| Renk | Anlamı |
|---|---|
| 🔵 Mavi | Dinliyor, "Jarvis" demeni bekliyor |
| ⚪ Beyaz parıltı | "Jarvis" dedin, komutunu bekliyor |
| 🟠 Turuncu | Sesini çözümlüyor ya da komutu uyguluyor |
| 🟣 Mor | Yapay zekâ sorunun cevabını düşünüyor |
| ⚫ Gri | Dinleme duraklatıldı |
| 🔴 Kırmızı | Bir hata oluştu (ayrıntısı konuşma kaydında) |

**Konuşma kaydı:** Jarvis'e söylediklerin ve cevapları burada görünür. "Jarvis" demeden duyulan konuşmalar **soluk renkte** görünür ve uygulanmaz.

**Ayarlarda neler var?**
- **Ses:** mikrofon seçimi, uyandırma kelimesi, tanıma dili
- **Yanıt:** sesli cevap açık/kapalı, konuşma hızı, ses seviyesi
- **Yazma:** noktalama sözcükleri, ilk harfi büyük yazma, WhatsApp ayarları
- **Yapay Zekâ:** API anahtarı, internet araması, düşünme seviyesi
- **Gelişmiş:** bekleme süreleri, günlük kaydı

### Arayüzsüz kullanım
- **`baslat.bat`**: arayüz olmadan, yalnızca siyah bir konsol penceresiyle çalışır.
- **`yazi_ile_dene.bat`**: mikrofon olmadan, komutları klavyeden yazarak denemek için.

---

## Sorun giderme

| Sorun | Çözüm |
|---|---|
| `jarvis.bat`'a çift tıkladım, hiçbir şey olmadı | Klasörde adres çubuğuna `cmd` yazıp şunu çalıştır: `python jarvis_arayuz.py`. Ekranda çıkan hata mesajı sorunu gösterir. Ayrıca klasörde `jarvis_hata.txt` oluşmuşsa ona bak. |
| `python` tanınmıyor hatası | Python kurulurken **"Add Python to PATH"** işaretlenmemiş. Python'u yeniden kurup kutuyu işaretle. |
| Paket kurulumunda **PyAudio** hatası | `python -m pip install --upgrade pip` çalıştırıp kurulumu tekrarla. Python sürümünün 3.12 veya üstü olduğundan emin ol. |
| Söylediklerimi duymuyor | AYARLAR → SES → **Mikrofon** listesinden doğru mikrofonu seç ve kaydet. Windows'un mikrofon iznini kontrol et: *Ayarlar → Gizlilik ve güvenlik → Mikrofon*. |
| "Ses tanıma servisine ulaşılamadı" | İnternet bağlantını kontrol et. |
| Sesli cevap vermiyor | Bilgisayarında Türkçe ses yok: [Kurulum](#kurulum) bölümündeki "İsteğe bağlı: Türkçe ses" adımına bak. Ayrıca AYARLAR → YANIT → "Sesli yanıt" açık olmalı. |
| Komutu yanlış anlıyor | Biraz daha yavaş ve net konuş. Ekrandaki konuşma kaydında Jarvis'in ne duyduğunu görebilirsin. Bir uygulama adını sürekli yanlış anlıyorsa [Geliştiriciler için](#geliştiriciler-için) bölümüne bak. |
| Sorulara "API anahtarı eklemen gerekiyor" diyor | [Yapay zekâ kurulumunu](#yapay-zekâ-api-anahtarı-nasıl-alınır) yap. |
| WhatsApp'ta yanlış kişiye gidiyor | Rehberdeki ismi tam söyle. Olmazsa AYARLAR → YAZMA → "WhatsApp: aramada ↓ tuşu"nu açmayı dene. |

---

## Gizlilik

- **Google:** Jarvis'in "Jarvis" dediğini anlayabilmesi için mikrofonun duyduğu konuşmalar yazıya çevrilmek üzere Google'a gönderilir. İstemediğin anlarda mikrofon düğmesiyle dinlemeyi duraklat.
- **Kayıt:** "Jarvis" denmeden duyulan konuşmalar **hiçbir dosyaya kaydedilmez**. Yalnızca Jarvis'e verdiğin komutlar, hataları ayıklamak için `jarvis_gunluk.txt` dosyasına yazılır. Bunu da kapatabilirsin: *AYARLAR → GELİŞMİŞ → "Duyulanları günlüğe yaz"*.
- **Yapay zekâ:** Yalnızca "Jarvis" diyerek sorduğun sorular Anthropic'e (Claude) gönderilir.
- **API anahtarı:** Yalnızca senin bilgisayarındaki `ayarlar.json` dosyasında durur. Bu dosya `.gitignore`'da olduğu için git'e eklenmez. Klasörün OneDrive/Dropbox gibi bir bulut klasöründeyse dosya oraya da eşitlenir; bunu istemiyorsan anahtarı `ANTHROPIC_API_KEY` ortam değişkenine koy ve ayarlardaki kutuyu boş bırak.

---

## Bilinen sınırlamalar

Proje geliştirme aşamasında olduğu için:

- Yalnızca **Windows**'ta çalışır.
- Konuşma tanıma için **internet** gerekir; çevrimdışı çalışmaz.
- Gürültülü ortamlarda ya da yabancı kelimelerde (uygulama adları gibi) komutları yanlış anlayabilir.
- WhatsApp ile mesajlaşma, WhatsApp'ın Windows uygulamasının arayüzüne bağlıdır; WhatsApp güncellenirse çalışmayabilir.
- Uygulamalar sistem dilinize ve kurulu sürüme göre farklı açılabilir. Listede olmayan uygulamalar Başlat menüsü aramasıyla açılır.
- Sorulara cevap verme özelliği ücretli bir API anahtarı gerektirir.

---

## Geliştiriciler için

### Proje yapısı
| Dosya | Görevi |
|---|---|
| `jarvis_arayuz.py` | Arayüzlü sürüm: pencere, dinleme ve komut işleme |
| `arayuz/` | Arayüzün tasarımı (`index.html`, `stil.css`, `jarvis.js`) |
| `asistan.py` | Konsol sürümü ve ortak parçalar (ayarlar, sesli yanıt) |
| `komutlar.py` | Türkçe cümleyi komuta çeviren çözümleyici |
| `eylemler.py` | Komutları Windows'ta uygulayan kısım |
| `beyin.py` | Yapay zekâ ile soru-cevap (Claude API, `claude-opus-5-5`) |
| `uygulamalar.py` | Bilinen uygulamalar ve siteler |
| `test_komutlar.py` | Çözümleyici testleri |

### Testleri çalıştırma
```
python test_komutlar.py
```

### Yeni uygulama eklemek
`uygulamalar.py` dosyasına bir kayıt ekle (dosyanın başında açıklama var). Google'ın bir uygulama adını sürekli yanlış yazdığını görürsen (örneğin "Steam" yerine "stim"), o yanlış yazımı o uygulamanın `adlar` listesine eklemen yeterli. Jarvis'in ne duyduğunu `jarvis_gunluk.txt` dosyasında görebilirsin.

### Arayüzü Python olmadan görmek
`arayuz/index.html` dosyasını tarayıcıda açarsan arayüz **demo modunda** çalışır. Belirli bir durumu görmek için adresin sonuna şunları ekleyebilirsin:
- `#onizleme=dusunuyor` (diğerleri: `bekleme`, `uyanik`, `analiz`, `isleniyor`, `konusuyor`, `duraklatildi`, `hata`, `bos`)
- Bir paneli açık görmek için: `#onizleme=bekleme&cekmece=c-ayarlar&sekme=3`
