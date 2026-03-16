"""
musteri_evrak.py
────────────────
Müşteri evrak (doküman) yönetimi:
  - Dosya yükleme (kimlik, tapu, vekaletname vb.)
  - Evrak listeleme ve silme
"""

import tkinter as tk
from tkinter import messagebox, ttk, filedialog, simpledialog
import datetime
import shutil
import os

from property_management.db import get_connection
from property_management.ui_utils import create_modern_button


def show_evrak_yonetim(root, listbox_musteri):
    """
    Seçili müşteri için evrak yükleme / görüntüleme / silme penceresi.

    Parametreler:
        root            : tkinter kök penceresi
        listbox_musteri : müşteri listesi widget'ı (seçimi okumak için)
    """
    if not listbox_musteri:
        return
    selected = listbox_musteri.curselection()
    if not selected:
        messagebox.showerror("Uyarı", "Lütfen bir müşteri seçin!")
        return

    item = listbox_musteri.get(selected[0])
    musteri_id = int(item.split(" | ")[0].split(":")[1])
    musteri_isim = item.split(" | ")[2]

    win = tk.Toplevel(root)
    win.title(f"📁 Evraklar – {musteri_isim}")
    win.geometry("620x460")
    win.configure(bg="#0f172a")

    tk.Label(
        win, text=f"📁 {musteri_isim} – Evrak Yönetimi",
        font=("Arial", 14, "bold"), bg="#0f172a", fg="white"
    ).pack(pady=14)

    columns = ("ID", "Evrak Adı", "Yüklenme Tarihi")
    tree = ttk.Treeview(win, columns=columns, show="headings", height=12)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=50 if col == "ID" else 200)
    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)

    # ── Yardımcı Fonksiyonlar ────────────────────────────────────────────────
    def refresh_evraklar():
        for item_e in tree.get_children():
            tree.delete(item_e)
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "SELECT id, evrak_adi, yuklenme_tarihi FROM evraklar WHERE musteri_id = ?",
            (musteri_id,),
        )
        for row in c.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    def yukle_evrak():
        evrak_adi = simpledialog.askstring(
            "Evrak Adı",
            "Evrak adını girin (örn: Kimlik, Tapu, Vekaletname):",
            parent=win,
        )
        if not evrak_adi:
            return
        file_path = filedialog.askopenfilename(
            title="Evrak / Fotoğraf Seçin",
            filetypes=[
                ("Desteklenen dosyalar", "*.jpg *.jpeg *.png *.pdf *.bmp"),
                ("PDF", "*.pdf"),
                ("Resim", "*.jpg *.jpeg *.png"),
            ],
            parent=win,
        )
        if not file_path:
            return

        os.makedirs("musteri_evraklari", exist_ok=True)
        ext = os.path.splitext(file_path)[1]
        filename = (
            f"musteri_{musteri_id}_{evrak_adi}_"
            f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        )
        dest = os.path.join("musteri_evraklari", filename)
        shutil.copy2(file_path, dest)

        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO evraklar (musteri_id, evrak_adi, dosya_yolu, yuklenme_tarihi) VALUES (?,?,?,?)",
            (musteri_id, evrak_adi, dest, datetime.datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Başarılı", f"'{evrak_adi}' evrakı yüklendi! 📎", parent=win)
        refresh_evraklar()

    def sil_evrak():
        sel = tree.selection()
        if not sel:
            messagebox.showerror("Uyarı", "Silinecek evrakı seçin!", parent=win)
            return
        evrak_id = tree.item(sel[0])["values"][0]
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM evraklar WHERE id = ?", (evrak_id,))
        conn.commit()
        conn.close()
        refresh_evraklar()

    # ── Butonlar ─────────────────────────────────────────────────────────────
    btn_f = tk.Frame(win, bg="#0f172a")
    btn_f.pack(pady=10)
    create_modern_button(btn_f, "📎 Evrak Yükle", yukle_evrak, "#10b981", width=16).pack(side=tk.LEFT, padx=8)
    create_modern_button(btn_f, "🗑️ Sil", sil_evrak, "#ef4444", width=10).pack(side=tk.LEFT, padx=8)
    create_modern_button(btn_f, "🔄 Yenile", refresh_evraklar, "#334155", width=10).pack(side=tk.LEFT, padx=8)

    refresh_evraklar()
