"""
musteri_takip.py
────────────────
Müşteri takip modülü:
  - 30+ gün iletişimsiz (soğuk) müşteri listesi
  - Gösterim sonrası anket gönderimi
  - WhatsApp Web entegrasyonu
"""

import tkinter as tk
from tkinter import messagebox, ttk
import datetime
import webbrowser
import urllib.parse

from property_management.db import get_connection
from property_management.ui_utils import create_modern_button


def _wa_url(telefon: str, mesaj: str) -> str:
    """Verilen numara ve mesaj için WhatsApp Web URL'si döndürür."""
    t = telefon.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not t.startswith("+"):
        t = "+90" + t.lstrip("0")
    return f"https://wa.me/{t}?text={urllib.parse.quote(mesaj)}"


def _guncelle_iletisim(musteri_id: int):
    """Müşterinin son_iletisim_tarihi sütununu şu anki zamana günceller."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE musteri SET son_iletisim_tarihi = ? WHERE id = ?",
        (datetime.datetime.now().isoformat(), musteri_id),
    )
    conn.commit()
    conn.close()


# ── WhatsApp Hızlı Mesaj ─────────────────────────────────────────────────────
def whatsapp_mesaj_gonder(listbox_musteri, mesaj_tipi: str = "genel"):
    """Listbox'tan seçili müşteriye WhatsApp Web'de mesaj taslağı açar."""
    if not listbox_musteri:
        return
    selected = listbox_musteri.curselection()
    if not selected:
        messagebox.showerror("Uyarı", "Lütfen bir müşteri seçin!")
        return

    item = listbox_musteri.get(selected[0])
    musteri_id = int(item.split(" | ")[0].split(":")[1])

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT isim, telefon FROM musteri WHERE id = ?", (musteri_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return

    isim, telefon = row
    mesajlar = {
        "takip": (f"Merhaba {isim} Hanım/Bey, geçtiğimiz günlerde gezdiğiniz mülkle ilgili "
                  f"düşüncelerinizi merak ettik. Teklifiniz ya da sorunuz var mı? 🏠"),
        "soguk": (f"Merhaba {isim} Hanım/Bey, bir süredir iletişime geçemedik. "
                  f"Aradığınız kriterlerde yeni fırsatlarımız var, görüşmek ister misiniz? 🔑"),
        "genel": f"Merhaba {isim} Hanım/Bey, nasıl yardımcı olabilirim?",
    }
    webbrowser.open(_wa_url(telefon, mesajlar.get(mesaj_tipi, mesajlar["genel"])))
    _guncelle_iletisim(musteri_id)


# ── Takip Merkezi Penceresi ───────────────────────────────────────────────────
def show_takip_paneli(root):
    """
    30 günden eski müşterileri ve son gösterim sonrası bildirim
    gereken randevuları listeleyen Takip Merkezi penceresi.
    """
    win = tk.Toplevel(root)
    win.title("🔔 Takip Merkezi")
    win.geometry("780x540")
    win.configure(bg="#0f172a")

    tk.Label(
        win, text="🔔 TAKİP MERKEZİ",
        font=("Arial", 16, "bold"), bg="#0f172a", fg="white"
    ).pack(pady=12)

    notebook = ttk.Notebook(win)
    notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

    # ── Tab 1: Soğuk Müşteriler ──────────────────────────────────────────────
    tab_soguk = tk.Frame(notebook, bg="#0f172a")
    notebook.add(tab_soguk, text="❄️ Soğuk Müşteriler")

    tk.Label(
        tab_soguk, text="30 gündür iletişim kurulmayan müşteriler:",
        bg="#0f172a", fg="#94a3b8"
    ).pack(pady=5)

    cols_s = ("ID", "İsim", "Telefon", "Etiket", "Son İletişim")
    tree_s = ttk.Treeview(tab_soguk, columns=cols_s, show="headings", height=12)
    for col in cols_s:
        tree_s.heading(col, text=col)
        tree_s.column(col, width=50 if col == "ID" else 130)
    tree_s.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    otuz_gun_once = (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat()
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """SELECT id, isim, telefon, etiket, son_iletisim_tarihi FROM musteri
           WHERE son_iletisim_tarihi < ? OR son_iletisim_tarihi IS NULL
           ORDER BY son_iletisim_tarihi ASC""",
        (otuz_gun_once,),
    )
    for row in c.fetchall():
        son = row[4][:10] if row[4] else "Hiç"
        tree_s.insert("", "end", values=(row[0], row[1], row[2], row[3] or "-", son))
    conn.close()

    def wa_soguk():
        sel = tree_s.selection()
        if not sel:
            messagebox.showerror("Uyarı", "Müşteri seçin!", parent=win)
            return
        vals = tree_s.item(sel[0])["values"]
        musteri_id, isim, telefon = vals[0], vals[1], vals[2]
        mesaj = (f"Merhaba {isim} Hanım/Bey, bir süredir iletişime geçemedik. "
                 f"Aradığınız kriterlerde yeni fırsatlarımız var, görüşmek ister misiniz? 🔑")
        webbrowser.open(_wa_url(telefon, mesaj))
        _guncelle_iletisim(musteri_id)

    create_modern_button(
        tab_soguk, "💬 WhatsApp Mesajı Gönder", wa_soguk, "#25D366", width=25
    ).pack(pady=8)

    # ── Tab 2: Gösterim Sonrası Anket ────────────────────────────────────────
    tab_gb = tk.Frame(notebook, bg="#0f172a")
    notebook.add(tab_gb, text="📋 Gösterim Sonrası Anket")

    tk.Label(
        tab_gb, text="Tamamlanan gösterimler – anket gönderilmeyi bekleyenler:",
        bg="#0f172a", fg="#94a3b8"
    ).pack(pady=5)

    cols_g = ("Randevu ID", "Mülk", "Müşteri", "Tarih", "Saat", "Geri Bildirim")
    tree_g = ttk.Treeview(tab_gb, columns=cols_g, show="headings", height=12)
    for col in cols_g:
        tree_g.heading(col, text=col)
        tree_g.column(col, width=80 if col == "Randevu ID" else 115)
    tree_g.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    conn2 = get_connection()
    c2 = conn2.cursor()
    c2.execute(
        """SELECT r.id, e.tur || ' - ' || e.konum, m.isim, m.telefon,
                  r.tarih, r.saat, r.gosterim_geri_bildirim
           FROM randevu r
           JOIN emlak e ON r.emlak_id = e.id
           JOIN musteri m ON r.musteri_id = m.id
           WHERE r.durum = 'Tamamlandı'
           ORDER BY r.tarih DESC, r.saat DESC
           LIMIT 50"""
    )
    gosterim_rows = c2.fetchall()
    conn2.close()

    for row in gosterim_rows:
        gb = row[6] if row[6] else "⏳ Bekleniyor"
        tree_g.insert("", "end", values=(row[0], row[1], row[2], row[4], row[5], gb))

    def anket_gonder():
        sel = tree_g.selection()
        if not sel:
            messagebox.showerror("Uyarı", "Randevu seçin!", parent=win)
            return
        vals = tree_g.item(sel[0])["values"]
        randevu_id = vals[0]
        musteri_isim = vals[2]

        conn3 = get_connection()
        c3 = conn3.cursor()
        c3.execute(
            "SELECT m.telefon FROM randevu r JOIN musteri m ON r.musteri_id = m.id WHERE r.id = ?",
            (randevu_id,),
        )
        row = c3.fetchone()
        if row:
            mesaj = (f"Merhaba {musteri_isim} Hanım/Bey, gezdiğiniz mülk nasıldı? "
                     f"Beğendiniz mi, ya da teklifiniz var mı? 😊🏠")
            webbrowser.open(_wa_url(row[0], mesaj))
            c3.execute(
                "UPDATE randevu SET gosterim_geri_bildirim = ? WHERE id = ?",
                ("Anket Gönderildi – " + datetime.datetime.now().strftime("%d.%m.%Y %H:%M"), randevu_id),
            )
            conn3.commit()
            messagebox.showinfo("Başarılı", "WhatsApp anketi hazırlandı! ✅", parent=win)
        conn3.close()

    create_modern_button(
        tab_gb, "📩 Anket WhatsApp'tan Gönder", anket_gonder, "#f59e0b", width=28
    ).pack(pady=8)
