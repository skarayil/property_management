<div align="center">

# 🏢 Emlak Yönetim Sistemi

<img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=22&pause=1000&color=10B981&center=true&vCenter=true&width=600&lines=Yapay+Zeka+Destekli+CRM+%26+Portföy+Yönetimi;Python+%26+Tkinter+ile+Geliştirildi;Ek+Kurulum+Gerektirmez!" alt="Typing SVG" />

<br/>

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![SQLite](https://img.shields.io/badge/SQLite-Auto%20Created-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Tkinter](https://img.shields.io/badge/Tkinter-Built--in-FFD43B?style=for-the-badge&logo=python&logoColor=black)](https://docs.python.org/3/library/tkinter.html)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey?style=for-the-badge&logo=linux&logoColor=white)](https://github.com/skarayil)
[![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)](https://github.com/skarayil)

<br/>

> **Emlakçılar için yapay zeka destekli, tam özellikli CRM ve portföy yönetim uygulaması.**  
> Sıfır bağımlılık — Python 3 ve Tkinter ile çalışır, hiçbir ek kurulum gerektirmez.

<br/>

[🚀 Hızlı Başlangıç](#-kurulum-ve-çalıştırma) • [✨ Özellikler](#-özellikler) • [📁 Proje Yapısı](#-proje-yapısı) • [👩‍💻 Geliştirici](#-geliştirici)

</div>

---

## ✨ Özellikler

<table>
  <tr>
    <td align="center">🎯</td>
    <td><strong>Lead Skorlama</strong></td>
    <td>Her müşteriyi 0–100 arası puanlar, otomatik etiket atar (🔥 Sıcak Alıcı, 💼 Yatırımcı Adayı, ❄️ Soğuk Lead…)</td>
  </tr>
  <tr>
    <td align="center">🔍</td>
    <td><strong>Portföy Eşleştirme</strong></td>
    <td>Yeni ilan eklenince uyumlu müşterileri otomatik bulur ve WhatsApp bildirimi önerir</td>
  </tr>
  <tr>
    <td align="center">📅</td>
    <td><strong>Randevu Yönetimi</strong></td>
    <td>Çakışma önleme, mülk sahibi müsaitlik takvimi kontrolü</td>
  </tr>
  <tr>
    <td align="center">🔔</td>
    <td><strong>Takip Merkezi</strong></td>
    <td>30+ gün sessiz müşterileri listeler, gösterim sonrası WhatsApp anketi gönderir</td>
  </tr>
  <tr>
    <td align="center">📁</td>
    <td><strong>Evrak Yönetimi</strong></td>
    <td>Kimlik, tapu, vekaletname vb. dosyaları müşteri profiline bağlar</td>
  </tr>
  <tr>
    <td align="center">📊</td>
    <td><strong>Dashboard & Analiz</strong></td>
    <td>Dönüşüm oranı, kaynak dağılımı, popüler ilanlar <em>(matplotlib gerektirir)</em></td>
  </tr>
  <tr>
    <td align="center">💰</td>
    <td><strong>Komisyon Takibi</strong></td>
    <td>Satış ve kiralama komisyonlarını hesaplar ve kaydeder</td>
  </tr>
  <tr>
    <td align="center">📄</td>
    <td><strong>Sözleşme Taslağı</strong></td>
    <td>Kira ve satış sözleşmelerini otomatik oluşturur</td>
  </tr>
  <tr>
    <td align="center">📧</td>
    <td><strong>E-posta Sistemi</strong></td>
    <td>Gmail SMTP entegrasyonu ile doğrudan müşteri iletişimi</td>
  </tr>
  <tr>
    <td align="center">📑</td>
    <td><strong>PDF & CSV Raporlama</strong></td>
    <td>Emlak, müşteri ve komisyon raporları <em>(fpdf gerektirir)</em></td>
  </tr>
</table>

---

## 🚀 Kurulum ve Çalıştırma

### 1 — Repoyu Klonla

```bash
git clone https://github.com/skarayil/property_management.git
cd property_management
```

### 2 — Uygulamayı Başlat *(Ek kurulum yok!)*

```bash
python3 run.py
```

> **Not:** Python 3.8+ gereklidir. Tkinter Python ile birlikte gelir.

### 3 — İsteğe Bağlı Özellikler

```bash
pip install -r requirements.txt
```

| Paket | Sağladığı Özellik |
|-------|------------------|
| `matplotlib` | Dashboard grafikleri |
| `Pillow` | Emlak fotoğrafı önizleme |
| `fpdf` | PDF rapor üretimi |

---

## 📁 Proje Yapısı

```
emlak_app/
├── run.py                     ← Başlangıç noktası — bunu çalıştırın
├── requirements.txt           ← İsteğe bağlı bağımlılıklar
├── README.md
│
├── main.py                    ← Uygulama giriş noktası & ana menü
├── db.py                      ← Veritabanı bağlantısı (SQLite, otomatik oluşturulur)
├── ui_utils.py                ← Paylaşılan UI bileşenleri
├── dashboard.py               ← Performans analitiği
├── reports.py                 ← PDF rapor üretimi
├── settings_ui.py             ← Uygulama ayarları
│
├── property_ops.py            ← Emlak yönetimi UI koordinatörü
├── customer_ops.py            ← Müşteri yönetimi UI koordinatörü
├── appointment_ops.py         ← Randevu yönetimi
├── commission_ops.py          ← Komisyon takibi
├── contract_ops.py            ← Sözleşme taslakları
│
└── modules/                   ← İş mantığı alt modülleri
    ├── customer_scoring.py    ← Lead skorlama algoritması (0–100)
    ├── customer_crud.py       ← Müşteri DB işlemleri
    ├── customer_followup.py   ← Takip merkezi & WhatsApp
    ├── customer_documents.py  ← Evrak yönetimi
    ├── property_crud.py       ← Emlak DB işlemleri & fotoğraf
    └── property_matching.py   ← Ters portföy eşleştirme
```

---

## 🗄️ Veritabanı

Uygulama ilk çalıştırmada `emlak_v3.db` (SQLite) dosyasını otomatik oluşturur. Herhangi bir yapılandırma gerekmez. Aşağıdaki tablolar otomatik kurulur:

| Tablo | Açıklama |
|-------|----------|
| `emlak` | Mülk kayıtları (tür, konum, fiyat, müsaitlik…) |
| `musteri` | Müşteri profilleri (lead skoru, etiket, kaynak…) |
| `randevu` | Randevu ve gösterim kayıtları |
| `komisyon` | İşlem komisyonu kayıtları |
| `evraklar` | Müşteriye bağlı belgeler |
| `ayarlar` | Firma ve e-posta ayarları |

---

## 🎯 Lead Skorlama Algoritması

Her müşteri 4 kritere göre **0–100** arası otomatik olarak puanlanır:

```
Bütçe Tanımlı      → +20 puan
Kredi Uygunluğu    → Evet: +30 | Belirsiz: +10 | Hayır: 0
Taşınma Aciliyeti  → Yüksek: +30 | Orta: +15 | Düşük: +5
Müşteri Tipi       → Alıcı: +20 | Kiralayan: +15 | Kiracı: +10 | Satıcı: +5
```

| Skor Aralığı | Etiket |
|-------------|--------|
| 75 – 100 | 🔥 Sıcak Alıcı |
| 55 – 74  | 💼 Yatırımcı Adayı |
| 35 – 54  | 📅 Hafta Sonu Alıcısı |
| 20 – 34  | 💬 Sadece Fiyat Soran |
| 0 – 19   | ❄️ Soğuk Lead |

---

## 💬 WhatsApp Entegrasyonu

Uygulama **WhatsApp Web** (`wa.me` linkleri) kullanır — Business API gerekmez. Mesaj gönder butonlarına tıklandığında tarayıcıda WhatsApp Web açılır ve mesaj taslağı hazır gelir.

**Otomatik mesaj senaryoları:**
- 🔔 Yeni ilanla eşleşen müşterilere portföy bildirimi
- ❄️ 30+ gün iletişimsiz soğuk müşterilere yeniden aktivasyon
- 📋 Gösterim tamamlandıktan sonra geri bildirim anketi

---

## 🖥️ Gereksinimler

| Gereksinim | Detay |
|-----------|-------|
| **Python** | 3.8 veya üzeri |
| **İşletim Sistemi** | macOS, Windows, Linux |
| **Tkinter** | Python ile birlikte gelir (ayrıca kurulum gerekmez) |
| **SQLite** | Python ile birlikte gelir (ayrıca kurulum gerekmez) |

---

## 📝 Lisans

Bu yazılım **[Sude Naz Karayıldırım](https://github.com/skarayil)** tarafından geliştirilmiştir.  
Tüm fikri ve hukuki hakları saklıdır. © 2026

Kişisel veya ticari kullanım serbesttir; ancak kaynak göstermek koşuluyla izin verilir.

---

<div align="center">

## 👩‍💻 Created by Sude Naz Karayıldırım

[![42 Profile](https://img.shields.io/badge/42%20Profile-skarayil-black?style=flat-square&logo=42&logoColor=white)](https://profile.intra.42.fr/users/skarayil)
[![GitHub](https://img.shields.io/badge/GitHub-skarayil-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/skarayil)

**⭐ Eğer bu proje işinize yaradıysa, repo'ya star vermeyi unutmayın!**

<sub>© 2026 Sude Naz Karayıldırım • Professional Edition • github.com/skarayil</sub>

</div>
