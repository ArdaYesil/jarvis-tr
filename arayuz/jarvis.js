/* ============ JARVIS HUD - arayüz mantığı ============ */
(() => {
  "use strict";
  const $ = (s) => document.querySelector(s);
  const el = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; };

  const DURUMLAR = {
    baslatiliyor: ["BAŞLATILIYOR", "sistem yükleniyor"],
    kalibre: ["KALİBRASYON", "ortam gürültüsü ölçülüyor"],
    bekleme: ["DİNLEMEDE", "“Jarvis” de"],
    uyanik: ["SİZİ DİNLİYORUM", "komutunuzu söyleyin"],
    analiz: ["ANALİZ", "ses çözümleniyor"],
    isleniyor: ["İŞLENİYOR", "komut uygulanıyor"],
    dusunuyor: ["DÜŞÜNÜYOR", "cevaplıyor"],
    konusuyor: ["YANITLIYOR", "sesli yanıt"],
    duraklatildi: ["DURAKLATILDI", "mikrofon kapalı"],
    hata: ["HATA", "ayrıntı kayıtta"],
  };

  const AYAR_SEMASI = [
    { sekme: "SES", alanlar: [
      { k: "uyandirma_gerekli", t: "anahtar", ad: "Uyandırma kelimesi gerekli", acik: "Kapalıysa her cümle komut sayılır (yanlışlıkla tetiklenebilir)." },
      { k: "uyandirma_kelimeleri", t: "liste", ad: "Uyandırma kelimeleri", acik: "Virgülle ayır. İlk kelime ana isimdir." },
      { k: "mikrofon_index", t: "mikrofon", ad: "Mikrofon" },
      { k: "dil", t: "secim", ad: "Tanıma dili", secenekler: [["tr-TR", "Türkçe"], ["en-US", "English (US)"], ["de-DE", "Deutsch"]] },
      { k: "uyandiktan_sonra_bekleme", t: "aralik", ad: "Uyandıktan sonra bekleme", min: 3, max: 20, adim: 1, birim: " sn", acik: "Sadece “Jarvis” dedikten sonra komutu bekleme süresi." },
    ]},
    { sekme: "YANIT", alanlar: [
      { k: "sesli_yanit", t: "anahtar", ad: "Sesli yanıt", acik: "Jarvis cevaplarını Türkçe sesle okur." },
      { k: "ses_hizi", t: "aralik", ad: "Konuşma hızı", min: -10, max: 10, adim: 1, birim: "" },
      { k: "ses_seviyesi", t: "aralik", ad: "Ses seviyesi", min: 0, max: 100, adim: 5, birim: "%" },
      { k: "yazinca_soyle", t: "anahtar", ad: "Yazınca “yazdım” desin" },
    ]},
    { sekme: "YAZMA", alanlar: [
      { k: "noktalama_sozcukleri", t: "anahtar", ad: "Noktalama sözcükleri", acik: "“virgül”, “nokta”, “soru işareti” dediğinde işarete çevirir." },
      { k: "ilk_harf_buyuk", t: "anahtar", ad: "İlk harf büyük", acik: "Yazdırılan metnin ilk harfini büyük yapar." },
      { k: "whatsapp_arama_bekleme", t: "aralik", ad: "WhatsApp kişi arama süresi", min: 0.5, max: 5, adim: 0.1, birim: " sn", acik: "Kişi geç bulunuyorsa artır." },
      { k: "whatsapp_aramada_asagi_ok", t: "anahtar", ad: "WhatsApp: aramada ↓ tuşu", acik: "İlk sonuç yanlış sohbeti açıyorsa dene." },
    ]},
    { sekme: "YAPAY ZEKÂ", alanlar: [
      { k: "yapay_zeka", t: "anahtar", ad: "Sorulara cevap ver", acik: "Komut olmayan her cümle Claude yapay zekâsına sorulur." },
      { k: "claude_api_anahtari", t: "api", ad: "Claude API anahtarı", acik: "console.anthropic.com → API Keys bölümünden alınır. Bu bilgisayardaki ayarlar.json dosyasına kaydedilir, arayüze geri gösterilmez." },
      { k: "web_arama", t: "anahtar", ad: "İnternette araştırabilsin", acik: "Hava durumu, haberler, fiyatlar gibi güncel sorular için web araması yapar." },
      { k: "yapay_zeka_dusunme", t: "secim", ad: "Düşünme seviyesi", secenekler: [["low", "Hızlı (önerilen)"], ["medium", "Dengeli"], ["high", "Derin — yavaş ama daha titiz"]] },
    ]},
    { sekme: "GELİŞMİŞ", alanlar: [
      { k: "acilis_bekleme", t: "aralik", ad: "Uygulama açılış bekleme", min: 4, max: 30, adim: 1, birim: " sn" },
      { k: "yeni_acilan_bekleme", t: "aralik", ad: "Yeni açılan pencere bekleme", min: 0.5, max: 8, adim: 0.5, birim: " sn" },
      { k: "gunluk", t: "anahtar", ad: "Duyulanları günlüğe yaz", acik: "jarvis_gunluk.txt — yanlış anlamaları düzeltmek için." },
    ]},
  ];

  const VARSAYILAN = {
    uyandirma_gerekli: true, uyandirma_kelimeleri: ["jarvis", "carvis", "cervis", "jervis", "çarvis", "jarviz"],
    mikrofon_index: null, dil: "tr-TR", uyandiktan_sonra_bekleme: 8, sesli_yanit: true, ses_hizi: 0,
    ses_seviyesi: 100, yazinca_soyle: false, noktalama_sozcukleri: true, ilk_harf_buyuk: true,
    whatsapp_arama_bekleme: 1.8, whatsapp_aramada_asagi_ok: false, acilis_bekleme: 12,
    yeni_acilan_bekleme: 2.5, gunluk: true,
    yapay_zeka: true, web_arama: true, yapay_zeka_dusunme: "low", claude_api_anahtari: "", claude_api_kayitli: false,
  };

  const REHBER = [
    "Steam'i aç", "not defterine merhaba yaz", "WhatsApp'ta Ahmet'e selam yaz", "Chrome'u kapat",
    "Google'da hava durumu ara", "YouTube'da lofi müzik aç", "sesi kıs", "kaydet", "saat kaç",
    "ekran görüntüsü al", "masaüstünü göster", "bugünün tarihi",
    "Ay Dünya'ya ne kadar uzak?", "bana bir fıkra anlat", "yarın İstanbul'da hava nasıl olacak?", "konuşmayı unut",
  ];

  let api = null;           // window.pywebview.api
  let ayar = { ...VARSAYILAN };
  let taslak = { ...VARSAYILAN };
  let mikrofonlar = [];
  let seciliSekme = 0;
  let dinlemeAcik = true;
  let hedefSeviye = 0, seviye = 0;
  let durum = "baslatiliyor";
  let oncekiAg = null;
  let oturumBas = Date.now() / 1000;

  /* ================= olaylar (Python -> arayüz) ================= */
  const jarvis = {
    olay(e) {
      switch (e.t) {
        case "durum": durumAyarla(e.v); break;
        case "seviye": hedefSeviye = e.v; break;
        case "duydum": {
          const s = kayitEkle(e.uyandi ? "siz" : "siz soluk", e.uyandi ? "SİZ" : "DUYULDU", e.metin);
          if (e.tahminler && e.tahminler.length) s.querySelector(".metin").appendChild(el("span", "alternatif", "diğer tahminler: " + e.tahminler.join(" · ")));
          if (e.uyandi) altyazi(e.metin, "siz");
          break;
        }
        case "komut": {
          const son = $("#kayit").lastElementChild;
          if (son && e.komut && e.komut.tur && !["bos"].includes(e.komut.tur) && son.classList.contains("siz")) {
            son.querySelector(".metin").appendChild(el("span", "etiket", komutEtiketi(e.komut)));
          }
          break;
        }
        case "yanit":
          kayitEkle(e.sessiz ? "sistem" : "jarvis", e.sessiz ? "SİSTEM" : "JARVIS", e.metin);
          if (!e.sessiz) altyazi(e.metin, "jarvis");
          break;
        case "hata":
          kayitEkle("hata", "HATA", e.metin);
          bildirim(e.metin, true);
          break;
      }
    },
  };
  window.jarvis = jarvis;

  function komutEtiketi(k) {
    const ad = { ac: "AÇ", kapat: "KAPAT", ac_ara: "AÇ", kapat_ara: "KAPAT", yaz: "YAZ", uygulamaya_yaz: "YAZ",
      whatsapp: "WHATSAPP", ara: "ARA", youtube: "YOUTUBE", site: "SİTE", tus: "KISAYOL", saat: "SAAT",
      tarih: "TARİH", ekran_goruntusu: "EKRAN", kilitle: "KİLİT", yardim: "YARDIM", bilinmiyor: "SORU", unut: "UNUT", cikis: "ÇIKIŞ" }[k.tur] || k.tur.toUpperCase();
    const hedef = k.uygulama || k.ad || k.kisi || "";
    return hedef ? `${ad} · ${String(hedef).toUpperCase()}` : ad;
  }

  function durumAyarla(v) {
    durum = v;
    document.body.dataset.durum = v;
    const [baslik, alt] = DURUMLAR[v] || [v.toUpperCase(), ""];
    $("#ry-durum").textContent = baslik;
    $("#ry-alt").textContent = v === "bekleme" ? `“${ilkKelime()}” de` : alt;
    $("#hap-durum-yazi").textContent = baslik;
    $("#alt-durum").textContent = `ÇEKİRDEK · ${baslik}`;
    const hapMic = $("#hap-mic");
    hapMic.className = "hap " + (v === "duraklatildi" ? "kapali" : v === "kalibre" || v === "baslatiliyor" ? "uyari" : "aktif");
    $("#hap-durum").className = "hap " + (v === "hata" ? "kapali" : "aktif");
  }

  const ilkKelime = () => {
    const w = (ayar.uyandirma_kelimeleri || [])[0] || "jarvis";
    return w.charAt(0).toLocaleUpperCase("tr") + w.slice(1);
  };

  /* ================= kayıt ================= */
  function saatYazi(d = new Date()) { return d.toLocaleTimeString("tr-TR", { hour12: false }); }

  function kayitBos() {
    const k = $("#kayit");
    if (k.querySelector(".satir")) return;
    k.innerHTML = `<div class="kayit-bos"><span>Henüz konuşma yok</span>
      <span>“<b>${ilkKelime()}</b>” diyerek seslen ya da aşağıya komut yaz</span>
      <small>ipucu: komut kutusuna gitmek için <kbd>/</kbd> · ayarları kaydetmek için <kbd>Ctrl</kbd>+<kbd>S</kbd></small></div>`;
    $("#kayit-sayi").textContent = 0;
  }

  function kayitEkle(tur, kim, metin) {
    const k = $("#kayit");
    const bos = k.querySelector(".kayit-bos"); if (bos) bos.remove();
    const s = el("div", "satir " + tur);
    s.append(el("time", null, saatYazi()), el("span", "kim", kim), el("span", "metin", metin));
    k.appendChild(s);
    while (k.children.length > 250) k.firstChild.remove();
    k.scrollTop = k.scrollHeight;
    $("#kayit-sayi").textContent = k.querySelectorAll(".satir").length;
    return s;
  }

  let altyaziZaman = null;
  function altyazi(metin, tur) {
    const a = $("#altyazi");
    a.innerHTML = "";
    const kisa = metin.length > 170 ? metin.slice(0, 167).replace(/\s+\S*$/, "") + "…" : metin;
    const s = el("span", "yeni", tur === "siz" ? `“${kisa}”` : kisa);
    if (tur === "jarvis") s.style.color = "var(--cyan)";
    a.appendChild(s);
    clearTimeout(altyaziZaman);
    altyaziZaman = setTimeout(() => {
      a.innerHTML = `<span class="ipucu yeni">“<b>${ilkKelime()}</b>” diyerek seslen · örn. “${ilkKelime()}, Steam'i aç”</span>`;
    }, 9000);
  }

  let bildirimZaman = null;
  function bildirim(metin, hata = false) {
    const b = $("#bildirim");
    b.textContent = metin;
    b.className = "bildirim goster" + (hata ? " hata" : "");
    clearTimeout(bildirimZaman);
    bildirimZaman = setTimeout(() => (b.className = "bildirim" + (hata ? " hata" : "")), 2600);
  }

  /* ================= reaktör ================= */
  function tikleriCiz() {
    const g = $("#tikler");
    const ns = "http://www.w3.org/2000/svg";
    for (let i = 0; i < 120; i++) {
      const a = (i / 120) * Math.PI * 2;
      const uzun = i % 10 === 0;
      const r1 = 188, r2 = uzun ? 198 : 193;
      const l = document.createElementNS(ns, "line");
      l.setAttribute("x1", 200 + Math.cos(a) * r1); l.setAttribute("y1", 200 + Math.sin(a) * r1);
      l.setAttribute("x2", 200 + Math.cos(a) * r2); l.setAttribute("y2", 200 + Math.sin(a) * r2);
      if (uzun) l.setAttribute("class", "uzun");
      g.appendChild(l);
    }
  }

  const tuval = $("#dalga");
  const ctx = tuval.getContext("2d");
  const CUBUK = 96;
  const cubuklar = new Float32Array(CUBUK);

  function tuvalBoyut() {
    const r = tuval.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    tuval.width = r.width * dpr; tuval.height = r.height * dpr;
  }

  function renk() { return getComputedStyle(document.body).getPropertyValue("--vurgu").trim() || "#3fe0ff"; }
  let vurguRenk = "#3fe0ff";
  setInterval(() => (vurguRenk = renk()), 300);

  function ciz(t) {
    // seviyeyi yumuşat
    let hedef = hedefSeviye;
    if (durum === "konusuyor") hedef = 0.35 + 0.3 * Math.abs(Math.sin(t / 140)) * Math.abs(Math.sin(t / 370));
    if (durum === "analiz" || durum === "isleniyor") hedef = 0.15 + 0.08 * Math.sin(t / 90);
    seviye += (hedef - seviye) * (hedef > seviye ? 0.45 : 0.12);

    const w = tuval.width, h = tuval.height, cx = w / 2, cy = h / 2;
    const olcek = w / 400;
    ctx.clearRect(0, 0, w, h);
    const ic = 95 * olcek;
    for (let i = 0; i < CUBUK; i++) {
      const a = (i / CUBUK) * Math.PI * 2 - Math.PI / 2;
      const gurultu = (Math.sin(i * 0.9 + t / 230) + Math.sin(i * 2.3 - t / 170)) * 0.25 + 0.5;
      const nefes = durum === "duraklatildi" ? 0.02 : 0.05 + 0.03 * Math.sin(t / 900 + i / 6);
      const hedefUzunluk = (nefes + seviye * (0.4 + 0.6 * gurultu)) * 24 * olcek;
      cubuklar[i] += (hedefUzunluk - cubuklar[i]) * 0.3;
      const u = Math.max(1.5 * olcek, cubuklar[i]);
      ctx.strokeStyle = vurguRenk;
      ctx.globalAlpha = 0.35 + Math.min(0.6, seviye * 1.2);
      ctx.lineWidth = 2.2 * olcek;
      ctx.beginPath();
      ctx.moveTo(cx + Math.cos(a) * ic, cy + Math.sin(a) * ic);
      ctx.lineTo(cx + Math.cos(a) * (ic + u), cy + Math.sin(a) * (ic + u));
      ctx.stroke();
    }
    ctx.globalAlpha = 1;

    // çekirdek ölçeği
    const c = $("#cekirdek");
    c.style.transform = `scale(${1 + seviye * 0.18 + 0.02 * Math.sin(t / 600)})`;

    requestAnimationFrame(ciz);
  }

  /* ================= sistem ================= */
  function halkaGosterge(id, yuzde) {
    const g = $(id);
    const v = Math.max(0, Math.min(100, yuzde || 0));
    g.querySelector(".hg-dolu").style.strokeDashoffset = 263.9 * (1 - v / 100);
    g.querySelector(".hg-deger b").textContent = Math.round(v);
    g.classList.toggle("yuksek", v >= 70 && v < 90);
    g.classList.toggle("kritik", v >= 90);
  }

  function hiz(bayt) {
    if (bayt < 1024) return `${bayt.toFixed(0)} B/s`;
    if (bayt < 1024 ** 2) return `${(bayt / 1024).toFixed(1)} KB/s`;
    return `${(bayt / 1024 ** 2).toFixed(2)} MB/s`;
  }
  function sure(sn) {
    sn = Math.max(0, Math.floor(sn));
    const g = Math.floor(sn / 86400), s = Math.floor((sn % 86400) / 3600), d = Math.floor((sn % 3600) / 60);
    return g ? `${g}g ${s}s ${d}d` : `${String(s).padStart(2, "0")}:${String(d).padStart(2, "0")}:${String(sn % 60).padStart(2, "0")}`;
  }

  function sistemGuncelle(s) {
    if (!s || s.cpu == null) { $("#hap-ag").className = "hap kapali"; return; }
    halkaGosterge("#g-cpu", s.cpu);
    halkaGosterge("#g-ram", s.ram);
    $("#disk-yazi").textContent = `%${Math.round(s.disk)} · ${s.disk_bos} GB boş`;
    const dc = $("#disk-cubuk"); dc.style.width = s.disk + "%"; dc.classList.toggle("uyari", s.disk > 85);
    if (s.pil == null) { $("#pil-yazi").textContent = "pil yok"; $("#pil-cubuk").style.width = "0"; }
    else {
      $("#pil-yazi").textContent = `%${Math.round(s.pil)}${s.sarj ? " · şarjda" : ""}`;
      const pc = $("#pil-cubuk"); pc.style.width = s.pil + "%"; pc.classList.toggle("uyari", s.pil < 20);
    }
    const simdi = Date.now() / 1000;
    if (oncekiAg) {
      const dt = simdi - oncekiAg.t;
      $("#ag-in").textContent = hiz((s.alinan - oncekiAg.in) / dt);
      $("#ag-out").textContent = hiz((s.gonderilen - oncekiAg.out) / dt);
    }
    oncekiAg = { t: simdi, in: s.alinan, out: s.gonderilen };
    $("#hap-ag").className = "hap aktif";
    $("#yv-cpu").textContent = `%${Math.round(s.cpu)}`;
    $("#yv-ram").textContent = `%${Math.round(s.ram)}`;
    $("#yv-ag").textContent = $("#ag-in").textContent;
    $("#surec").textContent = s.surec;
    $("#acik-kalma").textContent = sure(simdi - s.acilis);
    $("#o-komut").textContent = s.komut;
    $("#o-basari").textContent = s.komut ? `%${Math.round((100 * s.basarili) / s.komut)}` : "—";
    if (s.oturum) oturumBas = s.oturum;
  }

  async function sistemDongu() {
    try { sistemGuncelle(api ? await api.sistem() : demoSistem()); } catch (e) { /* yoksay */ }
    setTimeout(sistemDongu, 1500);
  }

  function saatDongu() {
    const d = new Date();
    $("#saat").textContent = saatYazi(d);
    $("#tarih").textContent = d.toLocaleDateString("tr-TR", { weekday: "long", day: "numeric", month: "long", year: "numeric" }).toLocaleUpperCase("tr");
    const os = Math.floor(Date.now() / 1000 - oturumBas);
    $("#o-sure").textContent = `${String(Math.floor(os / 60)).padStart(2, "0")}:${String(os % 60).padStart(2, "0")}`;
  }

  /* ================= ayarlar ================= */
  function sekmeleriCiz() {
    const n = $("#sekmeler"); n.innerHTML = "";
    AYAR_SEMASI.forEach((s, i) => {
      const b = el("button", i === seciliSekme ? "secili" : "", s.sekme);
      b.onclick = () => { seciliSekme = i; sekmeleriCiz(); ayarlariCiz(); };
      n.appendChild(b);
    });
  }

  function aralikYuzde(inp) {
    const y = ((inp.value - inp.min) / (inp.max - inp.min)) * 100;
    inp.style.setProperty("--yuzde", y + "%");
  }

  function degisti() {
    const fark = JSON.stringify(taslak) !== JSON.stringify(ayar);
    $("#kaydedilmedi").classList.toggle("goster", fark);
    $("#ayar-noktasi").classList.toggle("goster", fark);
  }

  function ayarlariCiz() {
    const g = $("#ayar-govde"); g.innerHTML = "";
    for (const a of AYAR_SEMASI[seciliSekme].alanlar) {
      const kutu = el("div", "ayar");
      const bas = el("div", "ayar-bas");
      const lbl = el("label", null, a.ad);
      bas.appendChild(lbl);
      kutu.appendChild(bas);

      if (a.t === "anahtar") {
        const sw = el("label", "anahtar");
        const inp = el("input"); inp.type = "checkbox"; inp.checked = !!taslak[a.k];
        inp.onchange = () => { taslak[a.k] = inp.checked; degisti(); };
        sw.append(inp, el("span"));
        bas.appendChild(sw);
      } else if (a.t === "aralik") {
        const out = el("output", null, `${taslak[a.k]}${a.birim}`);
        bas.appendChild(out);
        const inp = el("input"); inp.type = "range"; inp.min = a.min; inp.max = a.max; inp.step = a.adim; inp.value = taslak[a.k];
        aralikYuzde(inp);
        inp.oninput = () => { taslak[a.k] = Number(inp.value); out.textContent = `${inp.value}${a.birim}`; aralikYuzde(inp); degisti(); };
        kutu.appendChild(inp);
      } else if (a.t === "liste") {
        const inp = el("input"); inp.type = "text"; inp.value = (taslak[a.k] || []).join(", ");
        inp.oninput = () => { taslak[a.k] = inp.value.split(",").map((x) => x.trim().toLocaleLowerCase("tr")).filter(Boolean); degisti(); };
        kutu.appendChild(inp);
      } else if (a.t === "api") {
        const inp = el("input"); inp.type = "password"; inp.autocomplete = "off"; inp.spellcheck = false;
        inp.placeholder = ayar.claude_api_kayitli ? "kayıtlı ✓  (değiştirmek için yenisini yapıştır)" : "sk-ant-… anahtarını buraya yapıştır";
        inp.value = taslak[a.k] || "";
        inp.oninput = () => { taslak[a.k] = inp.value.trim(); degisti(); };
        const durumYazi = el("div", "durum-yazi " + (ayar.claude_api_kayitli ? "ok" : ""),
          ayar.claude_api_kayitli ? "● Anahtar kayıtlı" : "○ Anahtar yok — sorular cevaplanamaz");
        const dug = el("div", "ayar-dugmeler");
        const dene = el("button", "ikincil-btn", "BAĞLANTIYI DENE");
        dene.onclick = async () => {
          if (taslak[a.k]) { bildirim("Önce KAYDET'e bas, sonra dene", true); return; }
          if (!api) { durumYazi.textContent = "Demo modunda denenemez"; return; }
          durumYazi.className = "durum-yazi"; durumYazi.textContent = "Deneniyor…";
          const r = await api.yapay_zeka_dene();
          durumYazi.className = "durum-yazi " + (r.ok ? "ok" : "hata");
          durumYazi.textContent = (r.ok ? "✓ " : "✗ ") + r.metin;
        };
        const sil = el("button", "ikincil-btn", "ANAHTARI KALDIR");
        sil.disabled = !ayar.claude_api_kayitli;
        sil.onclick = async () => {
          if (api) ayar = { ...VARSAYILAN, ...(await api.anahtar_sil()) };
          taslak = { ...taslak, claude_api_anahtari: "", claude_api_kayitli: false };
          ayar.claude_api_kayitli = false;
          bildirim("API ANAHTARI KALDIRILDI"); ayarlariCiz(); degisti(); yanVeriGuncelle();
        };
        dug.append(dene, sil);
        kutu.append(inp, durumYazi, dug);
      } else if (a.t === "secim" || a.t === "mikrofon") {
        const sel = el("select");
        const secenekler = a.t === "secim" ? a.secenekler : [["", "Windows varsayılanı"], ...mikrofonlar.map((m) => [String(m.index), m.ad])];
        for (const [v, ad] of secenekler) { const o = el("option", null, ad); o.value = v; sel.appendChild(o); }
        sel.value = taslak[a.k] == null ? "" : String(taslak[a.k]);
        sel.onchange = () => { taslak[a.k] = a.t === "mikrofon" ? (sel.value === "" ? null : Number(sel.value)) : sel.value; degisti(); };
        kutu.appendChild(sel);
      }
      if (a.acik) kutu.appendChild(el("p", null, a.acik));
      g.appendChild(kutu);
    }
  }

  function yanVeriGuncelle() {
    // Orbitron yazı tipinde Türkçe "İ" yok: Latin büyük harf kullan (JARVIS)
    $("#yv-uyandirma").textContent = ayar.uyandirma_gerekli ? ilkKelime().toUpperCase() : "KAPALI";
    $("#yv-yz").textContent = !ayar.yapay_zeka ? "KAPALI" : ayar.claude_api_kayitli ? "AÇIK" : "ANAHTAR YOK";
    $("#yv-mod").textContent = dinlemeAcik ? "SESLİ" : "YAZI";
  }

  async function kaydet() {
    try {
      if (api) ayar = { ...VARSAYILAN, ...(await api.ayarlari_kaydet(taslak)) };
      else ayar = { ...taslak, claude_api_kayitli: ayar.claude_api_kayitli || !!taslak.claude_api_anahtari, claude_api_anahtari: "" };
      taslak = { ...ayar };
      ayarlariCiz();
      degisti(); yanVeriGuncelle();
      if (durum === "bekleme") durumAyarla("bekleme");
      bildirim("AYARLAR KAYDEDİLDİ");
      kayitEkle("sistem", "SİSTEM", "Ayarlar güncellendi.");
    } catch (e) { bildirim("Ayarlar kaydedilemedi: " + e, true); }
  }

  /* ================= komut gönderme ================= */
  async function komutGonder(metin) {
    metin = metin.trim();
    if (!metin) return;
    kayitEkle("siz", "SİZ", metin);
    altyazi(metin, "siz");
    if (api) await api.komut_gonder(metin);
    else demoKomut(metin);
  }

  function hizliErisimCiz(liste) {
    const h = $("#hizli"); h.innerHTML = "";
    const oncelik = ["notepad", "whatsapp", "chrome", "opera", "steam", "spotify", "discord", "word", "hesap", "dosya"];
    liste.sort((a, b) => (oncelik.indexOf(a.anahtar) + 1 || 99) - (oncelik.indexOf(b.anahtar) + 1 || 99));
    for (const u of liste.slice(0, 10)) {
      const b = el("button", null, u.ad);
      b.title = `${u.ad} aç`;
      b.onclick = () => { komutGonder(`${u.ad} aç`); cekmeceKapat(); };
      h.appendChild(b);
    }
  }

  function rehberCiz() {
    const r = $("#rehber");
    for (const ornek of REHBER) {
      const b = el("button", null, ornek);
      b.title = "Komut kutusuna yaz";
      b.onclick = () => { const i = $("#komut-girdi"); i.value = ornek; cekmeceKapat(); i.focus(); };
      r.appendChild(b);
    }
  }

  /* ================= çekmeceler ================= */
  let acikCekmece = null;
  function cekmeceAc(id) {
    if (acikCekmece === id) { cekmeceKapat(); return; }
    document.querySelectorAll(".cekmece.acik").forEach((c) => c.classList.remove("acik"));
    const c = document.getElementById(id);
    if (!c) return;
    c.classList.add("acik");
    $("#perde").classList.add("acik");
    acikCekmece = id;
    document.querySelectorAll(".arac-btn").forEach((b) => b.classList.toggle("secili", b.dataset.cekmece === id));
  }
  function cekmeceKapat() {
    document.querySelectorAll(".cekmece.acik").forEach((c) => c.classList.remove("acik"));
    $("#perde").classList.remove("acik");
    document.querySelectorAll(".arac-btn.secili").forEach((b) => b.classList.remove("secili"));
    acikCekmece = null;
  }

  /* ================= bağlantılar ================= */
  function baglantilar() {
    document.querySelectorAll(".arac-btn").forEach((b) => (b.onclick = () => cekmeceAc(b.dataset.cekmece)));
    document.querySelectorAll(".cekmece-kapat").forEach((b) => (b.onclick = cekmeceKapat));
    $("#perde").onclick = cekmeceKapat;
    $("#komut-form").onsubmit = (e) => { e.preventDefault(); const i = $("#komut-girdi"); komutGonder(i.value); i.value = ""; };
    $("#btn-mic").onclick = async () => {
      dinlemeAcik = !dinlemeAcik;
      $("#btn-mic").classList.toggle("kapali", !dinlemeAcik);
      if (api) await api.dinleme(dinlemeAcik); else durumAyarla(dinlemeAcik ? "bekleme" : "duraklatildi");
      kayitEkle("sistem", "SİSTEM", dinlemeAcik ? "Mikrofon açıldı." : "Mikrofon duraklatıldı. Komutları yazarak verebilirsin.");
      yanVeriGuncelle();
    };
    $("#btn-kaydet").onclick = kaydet;
    $("#btn-varsayilan").onclick = () => { taslak = { ...VARSAYILAN, mikrofon_index: taslak.mikrofon_index }; ayarlariCiz(); degisti(); };
    $("#btn-temizle").onclick = () => { $("#kayit").innerHTML = ""; kayitBos(); };
    $("#btn-gunluk").onclick = () => api && api.gunluk_ac();
    $("#btn-kucult").onclick = () => api && api.kucult();
    $("#btn-buyut").onclick = () => api && api.buyut();
    $("#btn-kapat").onclick = () => api && api.kapat();
    document.addEventListener("keydown", (e) => {
      if (e.ctrlKey && e.key.toLowerCase() === "s") { e.preventDefault(); kaydet(); }
      if (e.key === "Escape" && acikCekmece) { e.preventDefault(); cekmeceKapat(); }
      const kisayol = { "1": "c-sistem", "2": "c-uygulamalar", "3": "c-rehber", "4": "c-ayarlar" }[e.key];
      if (e.altKey && kisayol) { e.preventDefault(); cekmeceAc(kisayol); }
      if (e.key === "/" && document.activeElement.tagName !== "INPUT") { e.preventDefault(); $("#komut-girdi").focus(); }
    });
    window.addEventListener("resize", tuvalBoyut);
  }

  const bekle = (ms) => new Promise((r) => setTimeout(r, ms));
  const ACILIS_SATIRLARI = [
    ["ÇEKİRDEK MODÜLLERİ", "OK"], ["KOMUT ÇÖZÜMLEYİCİ · TÜRKÇE", "OK"], ["KONUŞMA MOTORU · WINDOWS SAPI", "OK"],
    ["SES TANIMA · GOOGLE", "OK"], ["MİKROFON KANALI", "AÇIK"], ["ARAYÜZ", "HAZIR"],
  ];
  async function acilisOynat(hizli) {
    const ul = $("#ae-satirlar"), bar = $("#ae-ilerleme");
    for (let i = 0; i < ACILIS_SATIRLARI.length; i++) {
      const [ad, sonuc] = ACILIS_SATIRLARI[i];
      const li = el("li"); li.append(el("span", null, ad), el("b", null, sonuc));
      ul.appendChild(li);
      bar.style.width = `${((i + 1) / ACILIS_SATIRLARI.length) * 100}%`;
      await bekle(hizli ? 0 : 260 + Math.random() * 160);
    }
    await bekle(hizli ? 0 : 350);
  }
  function acilisKapat() {
    const a = $("#acilis");
    if (!a || a.classList.contains("bitti")) return;
    a.classList.add("bitti");
    document.body.classList.add("acildi");
    setTimeout(() => { a.remove(); tuvalBoyut(); }, 800);
  }

  async function baslat() {
    const onizleme = !api && (location.hash.match(/onizleme=(\w+)/) || [])[1];
    if (onizleme) document.body.classList.add("onizleme");
    const acilis = acilisOynat(!!onizleme);
    // güvenlik: bir şey ters giderse açılış ekranı arayüzü sonsuza kadar gizlemesin
    const emniyet = setTimeout(acilisKapat, 6000);
    try { await baslatIc(onizleme); }
    catch (e) { kayitEkle("hata", "HATA", "Arayüz başlatılamadı: " + e); }
    await acilis;
    clearTimeout(emniyet);
    acilisKapat();
  }

  async function baslatIc(onizleme) {
    tikleriCiz();
    tuvalBoyut();
    baglantilar();
    rehberCiz();
    sekmeleriCiz();
    requestAnimationFrame(ciz);
    setInterval(saatDongu, 1000); saatDongu();

    if (api) {
      const r = await api.hazir();
      ayar = { ...VARSAYILAN, ...r.ayar };
      hizliErisimCiz(r.uygulamalar);
      mikrofonlar = await api.mikrofonlar();
    } else if (onizleme) {
      onizlemeKur(onizleme);
    } else {
      demoBaslat();
    }
    taslak = { ...ayar };
    ayarlariCiz(); yanVeriGuncelle();
    kayitBos();
    sistemDongu();
  }

  /* tasarımı farklı durumlarda incelemek için: index.html#onizleme=isleniyor */
  function onizlemeKur(d) {
    demoBaslat(true);
    const ornek = [
      ["sistem", "SİSTEM", "Önizleme modu."],
      ["siz", "SİZ", "Jarvis Steam'i aç"], ["jarvis", "JARVIS", "Steam açılıyor"],
      ["siz soluk", "DUYULDU", "bugün hava çok güzel"],
      ["siz", "SİZ", "not defterine toplantı yarın saat üçte yaz"], ["sistem", "SİSTEM", "✓ Tamamlandı"],
      ["siz", "SİZ", "saat kaç"], ["jarvis", "JARVIS", "Saat 14:32"],
      ["siz", "SİZ", "Ay Dünya'ya ne kadar uzak?"], ["jarvis", "JARVIS", "Ay, Dünya'ya ortalama 384 bin kilometre uzaklıkta. Işık bu yolu yaklaşık 1,3 saniyede alıyor."],
    ];
    if (d !== "bos") for (const [t, k, m] of ornek) kayitEkle(t, k, m);
    const c = (location.hash.match(/cekmece=([\w-]+)/) || [])[1];
    const sekme = (location.hash.match(/sekme=(\d)/) || [])[1];
    if (sekme) seciliSekme = Number(sekme);
    if (c) setTimeout(() => { sekmeleriCiz(); ayarlariCiz(); cekmeceAc(c); }, 60);
    setTimeout(() => { durumAyarla(d === "bos" ? "bekleme" : d); hedefSeviye = 0.55; altyazi(d === "konusuyor" ? "Steam açılıyor" : "Jarvis Steam'i aç", d === "konusuyor" ? "jarvis" : "siz"); }, 50);
  }

  /* ================= demo modu (Python olmadan tarayıcıda) ================= */
  function demoSistem() {
    const t = Date.now() / 1000;
    demoSistem.ag = (demoSistem.ag || 1e9) + 150000 + Math.random() * 900000;
    return {
      cpu: 18 + 14 * Math.abs(Math.sin(t / 7)) + Math.random() * 6, ram: 61 + Math.random() * 2,
      disk: 72, disk_bos: 128, pil: 84, sarj: true, alinan: demoSistem.ag, gonderilen: demoSistem.ag / 9,
      surec: 287, acilis: t - 3 * 3600 - 1240, komut: demoKomut.n || 0, basarili: demoKomut.n || 0, oturum: oturumBas,
    };
  }
  function demoKomut(metin) {
    demoKomut.n = (demoKomut.n || 0) + 1;
    durumAyarla("isleniyor");
    setTimeout(() => {
      durumAyarla("konusuyor");
      jarvis.olay({ t: "yanit", metin: `${metin.replace(/'.*$/, "")} — demo modunda çalıştırılmadı` });
      setTimeout(() => durumAyarla("bekleme"), 1800);
    }, 700);
  }
  function demoBaslat(senaryosuz) {
    mikrofonlar = [{ index: 1, ad: "Microphone Array (AMD Audio)" }, { index: 3, ad: "Microphone Array (OMEN Cam)" }];
    hizliErisimCiz([
      { anahtar: "notepad", ad: "Not Defteri" }, { anahtar: "whatsapp", ad: "WhatsApp" }, { anahtar: "chrome", ad: "Chrome" },
      { anahtar: "opera", ad: "Opera" }, { anahtar: "steam", ad: "Steam" }, { anahtar: "spotify", ad: "Spotify" },
      { anahtar: "discord", ad: "Discord" }, { anahtar: "word", ad: "Word" }, { anahtar: "hesap", ad: "Hesap Makinesi" },
      { anahtar: "dosya", ad: "Dosya Gezgini" },
    ]);
    if (senaryosuz) return;
    setTimeout(() => bildirim("DEMO MODU · PYTHON BAĞLANTISI YOK"), 2600);
    durumAyarla("kalibre");
    setTimeout(() => durumAyarla("bekleme"), 1200);
    // ortam sesi
    setInterval(() => { if (durum === "bekleme" || durum === "uyanik") hedefSeviye = Math.random() < 0.15 ? Math.random() * 0.5 : Math.random() * 0.06; }, 120);
    const senaryo = [
      ["Jarvis Steam'i aç", { tur: "ac", uygulama: "steam" }, "Steam açılıyor"],
      ["Jarvis not defterine toplantı yarın saat üçte yaz", { tur: "uygulamaya_yaz", uygulama: "notepad" }, ""],
      ["Jarvis saat kaç", { tur: "saat" }, "Saat " + new Date().toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" })],
    ];
    let i = 0;
    const oynat = () => {
      const [duyulan, komut, yanit] = senaryo[i++ % senaryo.length];
      hedefSeviye = 0.7;
      setTimeout(() => {
        hedefSeviye = 0; durumAyarla("analiz");
        setTimeout(() => {
          jarvis.olay({ t: "duydum", metin: duyulan, tahminler: [], uyandi: true });
          jarvis.olay({ t: "komut", komut });
          durumAyarla("isleniyor");
          setTimeout(() => {
            if (yanit) { durumAyarla("konusuyor"); jarvis.olay({ t: "yanit", metin: yanit }); }
            else jarvis.olay({ t: "yanit", metin: "✓ Tamamlandı", sessiz: true });
            setTimeout(() => durumAyarla("bekleme"), 1600);
          }, 600);
        }, 700);
      }, 1300);
    };
    setTimeout(oynat, 2500);
    setInterval(oynat, 9000);
  }

  /* ================= giriş ================= */
  let basladi = false;
  function pywebviewHazir() {
    if (basladi) return; basladi = true;
    api = window.pywebview.api;
    baslat();
  }
  window.addEventListener("pywebviewready", pywebviewHazir);
  window.addEventListener("DOMContentLoaded", () => {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.hazir) pywebviewHazir();
    // pywebview penceresinde değilsek (normal tarayıcı) demo modunda başla
    setTimeout(() => { if (!basladi && !window.pywebview) { basladi = true; baslat(); } }, 1500);
  });
})();
