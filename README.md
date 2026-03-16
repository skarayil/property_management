# 🏠 Emlak Yönetim Sistemi

> Emlakçılar için yapay zeka destekli, tam özellikli CRM ve portföy yönetim uygulaması.  
> Python 3 ve Tkinter ile geliştirilmiştir — **ek kurulum gerektirmez.**

**Geliştirici:** [skarayil](https://github.com/skarayil)  
**Tüm hakları saklıdır. Bu yazılım [skarayil](https://github.com/skarayil) tarafından oluşturulmuştur.**

---

## 📋 Özellikler

| Modül | Açıklama |
|-------|----------|
| 🎯 **Lead Skorlama** | Her müşteriyi 0–100 arası puanlar, otomatik etiket atar (Sıcak Alıcı, Soğuk Lead…) |
| 🔍 **Portföy Eşleştirme** | Yeni ilan eklenince uyumlu müşterileri bulur, WhatsApp bildirimi önerir |
| 📅 **Randevu Yönetimi** | Çakışma önleme, mülk sahibi müsaitlik kontrolü |
| 🔔 **Takip Merkezi** | 30+ gün sessiz müşterileri listeler, gösterim sonrası anket gönderir |
| 📁 **Evrak Yönetimi** | Kimlik, tapu vb. dosyaları müşteriye bağlar |
| 📊 **Dashboard** | Dönüşüm oranı, kaynak dağılımı, popüler ilanlar *(matplotlib gerektirir)* |
| 💰 **Komisyon Takibi** | Satış/kiralama komisyonlarını kaydeder |
| 📄 **Sözleşme Taslağı** | Otomatik kira/satış sözleşmesi üretir |
| 📧 **E-posta** | Müşterilere e-posta gönderimi |
| 📑 **PDF Rapor** | Emlak ve müşteri raporları *(fpdf gerektirir)* |

---

## 🚀 Kurulum ve Çalıştırma

### 1. Repoyu klonla
```bash
git clone https://github.com/skarayil/property_management.git
cd property_management
```

### 2. Uygulamayı başlat *(ek kurulum yok)*
```bash
python3 run.py
```

> **Not:** Python 3.8+ gereklidir. Tkinter Python ile birlikte gelir, ayrıca kurmanıza gerek yoktur.

### 3. İsteğe bağlı özellikler için (Dashboard, PDF, Fotoğraf önizleme)
```bash
pip install -r requirements.txt
```

| Paket | Sağladığı Özellik |
|-------|------------------|
| `matplotlib` | Dashboard grafikleri |
| `Pillow` | Emlak fotoğrafı önizleme |
| `fpdf` | PDF rapor üretimi |

---

## 📁 Project Structure

```
property_management/
├── run.py                     ← Entry point – run this to start the app
├── requirements.txt           ← Optional dependencies
├── README.md
│
├── main.py                    ← App entry point & main menu
├── db.py                      ← Database connection (SQLite, auto-created)
├── ui_utils.py                ← Shared UI components
├── dashboard.py               ← Performance analytics
├── reports.py                 ← PDF report generation
├── settings_ui.py             ← App settings
│
├── property_ops.py            ← Property management UI coordinator
├── customer_ops.py            ← Customer management UI coordinator
├── appointment_ops.py         ← Appointment management
├── commission_ops.py          ← Commission tracking
├── contract_ops.py            ← Contract templates
│
└── modules/                   ← Business logic sub-modules
    ├── customer_scoring.py    ← Lead scoring algorithm (0–100)
    ├── customer_crud.py       ← Customer DB operations
    ├── customer_followup.py   ← Follow-up center & WhatsApp
    ├── customer_documents.py  ← Document management
    ├── property_crud.py       ← Property DB operations & photo
    └── property_matching.py   ← Reverse portfolio matching
```

---

## 🗄️ Database

The app automatically creates `emlak_v3.db` (SQLite) on first run. No configuration needed.


---

## 💬 WhatsApp Entegrasyonu

Uygulama, WhatsApp Business API yerine **WhatsApp Web** (`wa.me` linkleri) kullanır. Mesaj gönder butonlarına tıklandığında tarayıcınızda WhatsApp Web açılır ve mesaj taslağı hazırlanmış olarak gelir.

---

## 🖥️ Gereksinimler

- **Python:** 3.8 veya üzeri
- **İşletim Sistemi:** macOS, Windows, Linux
- **Tkinter:** Python ile birlikte gelir (ayrıca kurulum gerekmez)

---

## 📸 Ekran Görüntüleri

> *(Ekran görüntüleri buraya eklenebilir)*

---

## 📝 Lisans

Bu yazılım **[skarayil](https://github.com/skarayil)** tarafından geliştirilmiştir.  
Tüm fikri ve hukuki hakları **skarayil**'e aittir. © 2026  

Kişisel / ticari kullanım serbesttir; ancak kaynak göstermek şartıyla izin verilir.
