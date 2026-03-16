"""
emlak_matching.py
─────────────────
Portföy Eşleştirme (Reverse Matching) modülü.

Yeni bir ilan eklendiğinde veritabanındaki potansiyel alıcılar/kiracılar
taranan ve uyumlu müşterilere WhatsApp Web üzerinden toplu bildirim
gönderilmesini sağlayan fonksiyonlar.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import datetime
import webbrowser
import urllib.parse

from property_management.db import get_connection
from property_management.ui_utils import create_modern_button


def _wa_url(telefon: str, mesaj: str) -> str:
    t = telefon.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not t.startswith("+"):
        t = "+90" + t.lstrip("0")
    return f"https://wa.me/{t}?text={urllib.parse.quote(mesaj)}"


def reverse_matching_check(root, emlak_id, tur, fiyat_float, oda_sayisi, durum):
    """
    Yeni eklenen ilan ile veritabanındaki potansiyel alıcıları eşleştirir.

    Tam uyum : müşteri bütçesi >= ilan fiyatı
    Kısmi uyum: müşteri bütçesi >= ilan fiyatı * 0.80
    """
    if root is None:
        return

    tip_filtre = "Alıcı" if durum in ("Satılık", "Satıldı") else "Kiralayan"
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, isim, telefon, butce, etiket FROM musteri WHERE tip = ? AND butce IS NOT NULL",
        (tip_filtre,),
    )
    musteriler = c.fetchall()
    conn.close()

    tam_uyum    = [m for m in musteriler if m[3] >= fiyat_float]
    kismi_uyum  = [m for m in musteriler if fiyat_float * 0.80 <= m[3] < fiyat_float]

    if not tam_uyum and not kismi_uyum:
        return

    msg = (
        f"🔍 PORTFÖY EŞLEŞMESİ BULUNDU!\n\n"
        f"Yeni ilan: {tur} – {fiyat_float:,.0f}₺ ({durum})\n\n"
        f"✅ Tam uyumlu müşteri: {len(tam_uyum)}\n"
        f"🟡 Kısmi uyumlu müşteri: {len(kismi_uyum)}\n\n"
        f"Uyumlu müşterilere WhatsApp bildirimi yapılsın mı?"
    )
    if messagebox.askyesno("🎯 Otomatik Portföy Eşleştirme", msg):
        _show_eslesme_penceresi(root, tam_uyum + kismi_uyum, tur, fiyat_float, durum)


def _show_eslesme_penceresi(root, musteriler, tur, fiyat, durum):
    """Eşleşen müşterileri listeleyen pencere + tekli/toplu WhatsApp gönderimi."""
    win = tk.Toplevel(root)
    win.title("🎯 Eşleşen Müşteriler")
    win.geometry("660x430")
    win.configure(bg="#0f172a")

    tk.Label(
        win,
        text=f"🎯 {tur} – {fiyat:,.0f}₺ için eşleşen müşteriler",
        font=("Arial", 13, "bold"), bg="#0f172a", fg="white",
    ).pack(pady=12)

    cols = ("ID", "İsim", "Telefon", "Bütçe", "Etiket")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=12)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=50 if col == "ID" else 120)
    tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

    for m in musteriler:
        tree.insert("", "end", values=(m[0], m[1], m[2], f"{m[3]:,.0f}₺", m[4] or "-"))

    def _wa_seciliye():
        sel = tree.selection()
        if not sel:
            messagebox.showerror("Uyarı", "Müşteri seçin!", parent=win)
            return
        vals = tree.item(sel[0])["values"]
        isim, telefon, musteri_id = vals[1], vals[2], vals[0]
        mesaj = (f"Merhaba {isim} Hanım/Bey! 🏠 Aradığınız özelliklerde yeni bir "
                 f"{tur} ilanımız var. Fiyat: {fiyat:,.0f}₺ ({durum}). "
                 f"Detay için sizi aramam uygun mu?")
        webbrowser.open(_wa_url(str(telefon), mesaj))
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE musteri SET son_iletisim_tarihi = ? WHERE id = ?",
            (datetime.datetime.now().isoformat(), musteri_id),
        )
        conn.commit()
        conn.close()

    def _wa_hepsine():
        if not messagebox.askyesno(
            "Emin misiniz?",
            f"{len(musteriler)} müşteriye ayrı ayrı WhatsApp sekmesi açılacak. Devam?",
            parent=win,
        ):
            return
        conn = get_connection()
        c = conn.cursor()
        for m in musteriler:
            mesaj = (f"Merhaba {m[1]} Hanım/Bey! 🏠 Aradığınız özelliklerde yeni bir "
                     f"{tur} ilanımız var. Fiyat: {fiyat:,.0f}₺ ({durum}). "
                     f"Detay için sizi aramam uygun mu?")
            webbrowser.open(_wa_url(str(m[2]), mesaj))
            c.execute(
                "UPDATE musteri SET son_iletisim_tarihi = ? WHERE id = ?",
                (datetime.datetime.now().isoformat(), m[0]),
            )
        conn.commit()
        conn.close()

    btn_f = tk.Frame(win, bg="#0f172a")
    btn_f.pack(pady=8)
    create_modern_button(btn_f, "💬 Seçiliye WA",   _wa_seciliye, "#25D366", width=18).pack(side=tk.LEFT, padx=8)
    create_modern_button(btn_f, "📢 Hepsine Gönder", _wa_hepsine,  "#f59e0b", width=18).pack(side=tk.LEFT, padx=8)
