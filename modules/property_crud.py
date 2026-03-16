"""
emlak_crud.py
─────────────
Emlak veritabanı CRUD işlemleri: ekleme, güncelleme, silme, listeleme.
Ayrıca fotoğraf seçimi ve favori sayacı da burada bulunur.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import os
import shutil
import datetime

from property_management.db import get_connection

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ── Modül-düzeyi widget referansları ─────────────────────────────────────────
entry_tur = None
entry_konum = None
entry_fiyat = None
entry_oda = None
entry_metrekare = None
combo_durum = None
text_aciklama = None
listbox_emlak = None
entry_search_emlak = None
btn_save_emlak = None
photo_label = None
combo_sahip = None
combo_isitma = None
entry_bina_yasi = None
entry_musait_gunler = None
entry_musait_saatler = None

selected_photo_path = None
editing_emlak_id = None


# ── Fotoğraf ─────────────────────────────────────────────────────────────────
def select_photo():
    global selected_photo_path
    file_path = filedialog.askopenfilename(
        title="Emlak Fotoğrafı Seçin",
        filetypes=[("Resim dosyaları", "*.jpg *.jpeg *.png *.gif *.bmp")],
    )
    if file_path:
        filename = f"emlak_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        new_path = os.path.join("emlak_fotograflari", filename)
        shutil.copy2(file_path, new_path)
        selected_photo_path = new_path
        if photo_label:
            photo_label.config(text=f"Seçili: {filename}")


def view_emlak_photo(root):
    selected = listbox_emlak.curselection()
    if not selected:
        messagebox.showwarning("Uyarı", "Bir emlak seçin!")
        return
    emlak_id = _selected_emlak_id()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT fotograf_yolu FROM emlak WHERE id = ?", (emlak_id,))
    result = c.fetchone()
    conn.close()
    if result and result[0] and os.path.exists(result[0]):
        if PIL_AVAILABLE:
            w = tk.Toplevel(root)
            w.title("Emlak Fotoğrafı")
            w.geometry("500x400")
            try:
                img = Image.open(result[0])
                img.thumbnail((450, 350))
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(w, image=photo)
                lbl.image = photo
                lbl.pack(pady=20)
            except Exception:
                tk.Label(w, text="Fotoğraf yüklenemedi").pack(pady=50)
        else:
            messagebox.showinfo("Bilgi", f"Fotoğraf yolu: {result[0]}")
    else:
        messagebox.showinfo("Bilgi", "Bu emlak için fotoğraf bulunamadı.")


# ── Favori ───────────────────────────────────────────────────────────────────
def favori_ekle():
    if not listbox_emlak or not listbox_emlak.curselection():
        messagebox.showerror("Uyarı", "Bir emlak seçin!")
        return
    emlak_id = _selected_emlak_id()
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE emlak SET favori_sayisi = COALESCE(favori_sayisi, 0) + 1 WHERE id = ?",
        (emlak_id,),
    )
    conn.commit()
    conn.close()
    messagebox.showinfo("✅", "Favori sayısı güncellendi!")
    list_emlak()


# ── Yardımcı ─────────────────────────────────────────────────────────────────
def _selected_emlak_id():
    item = listbox_emlak.get(listbox_emlak.curselection()[0])
    return int(item.split(" | ")[0].split(":")[1])


def _parse_form():
    sahip_val = combo_sahip.get()
    return {
        "tur": entry_tur.get(),
        "konum": entry_konum.get(),
        "fiyat": entry_fiyat.get(),
        "oda_sayisi": entry_oda.get(),
        "metrekare": entry_metrekare.get(),
        "durum": combo_durum.get(),
        "aciklama": text_aciklama.get("1.0", tk.END).strip(),
        "sahip_id": sahip_val.split(" - ")[0] if sahip_val else None,
        "isitma": combo_isitma.get(),
        "bina_yasi": entry_bina_yasi.get(),
        "musait_gunler": entry_musait_gunler.get() if entry_musait_gunler else "",
        "musait_saatler": entry_musait_saatler.get() if entry_musait_saatler else "",
    }


# ── CRUD ─────────────────────────────────────────────────────────────────────
def add_emlak(on_added_callback=None):
    global selected_photo_path
    d = _parse_form()
    if not all([d["tur"], d["konum"], d["fiyat"], d["oda_sayisi"], d["metrekare"], d["durum"]]):
        messagebox.showerror("Eksik Bilgi", "Lütfen eksik alanları doldurduğunuzdan emin olun 😊")
        return
    try:
        fiyat_float = float(d["fiyat"].replace(",", ""))
        metrekare_int = int(d["metrekare"])
        now = datetime.datetime.now().isoformat()
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            """INSERT INTO emlak (tur, konum, fiyat, oda_sayisi, metrekare, durum,
                                  aciklama, fotograf_yolu, eklenme_tarihi, sahip_id, isitma, bina_yasi,
                                  musait_gunler, musait_saatler, favori_sayisi)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
            (d["tur"], d["konum"], fiyat_float, d["oda_sayisi"], metrekare_int, d["durum"],
             d["aciklama"], selected_photo_path, now, d["sahip_id"], d["isitma"], d["bina_yasi"],
             d["musait_gunler"], d["musait_saatler"]),
        )
        new_id = c.lastrowid
        conn.commit()
        conn.close()
        messagebox.showinfo("Başarılı", "Emlak eklendi! ✨")
        clear_emlak_entries()
        list_emlak()
        # Portföy eşleştirme callback
        if on_added_callback:
            on_added_callback(new_id, d["tur"], fiyat_float, d["oda_sayisi"], d["durum"])
    except ValueError:
        messagebox.showerror("Hata", "Fiyat ve metrekare sayısal olmalı 😊")


def update_emlak():
    global selected_photo_path, editing_emlak_id
    d = _parse_form()
    if not all([d["tur"], d["konum"], d["fiyat"], d["oda_sayisi"], d["metrekare"], d["durum"]]):
        messagebox.showerror("Eksik Bilgi", "Lütfen eksik alanları doldurduğunuzdan emin olun 😊")
        return
    try:
        fiyat_float = float(d["fiyat"].replace(",", ""))
        metrekare_int = int(d["metrekare"])
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            """UPDATE emlak
               SET tur=?, konum=?, fiyat=?, oda_sayisi=?, metrekare=?, durum=?, aciklama=?,
                   fotograf_yolu=?, sahip_id=?, isitma=?, bina_yasi=?,
                   musait_gunler=?, musait_saatler=?
               WHERE id = ?""",
            (d["tur"], d["konum"], fiyat_float, d["oda_sayisi"], metrekare_int, d["durum"],
             d["aciklama"], selected_photo_path, d["sahip_id"], d["isitma"], d["bina_yasi"],
             d["musait_gunler"], d["musait_saatler"], editing_emlak_id),
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Başarılı", "Emlak başarıyla güncellendi! ✨")
        clear_emlak_entries()
        list_emlak()
        if btn_save_emlak:
            btn_save_emlak.config(text="💾 Kaydet", command=add_emlak)
    except ValueError:
        messagebox.showerror("Hata", "Fiyat ve metrekare sayısal olmalı 😊")


def edit_emlak():
    global editing_emlak_id, selected_photo_path
    if not listbox_emlak or not listbox_emlak.curselection():
        messagebox.showerror("Uyarı", "Lütfen düzenlemek için emlak seçin 😊")
        return
    emlak_id = _selected_emlak_id()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM emlak WHERE id = ?", (emlak_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return

    entry_tur.delete(0, tk.END);      entry_tur.insert(0, row[1])
    entry_konum.delete(0, tk.END);    entry_konum.insert(0, row[2])
    entry_fiyat.delete(0, tk.END);    entry_fiyat.insert(0, str(row[3]))
    entry_oda.delete(0, tk.END);      entry_oda.insert(0, row[4])
    entry_metrekare.delete(0, tk.END); entry_metrekare.insert(0, str(row[5]))
    combo_durum.set(row[6])
    text_aciklama.delete("1.0", tk.END); text_aciklama.insert("1.0", row[7] or "")

    if len(row) > 9 and row[9]:
        c.execute("SELECT id, isim, tip FROM musteri WHERE id = ?", (row[9],))
        m = c.fetchone()
        combo_sahip.set(f"{m[0]} - {m[1]} ({m[2] or 'Belirtilmemiş'})" if m else "")
    else:
        combo_sahip.set("")

    combo_isitma.set(row[10] if len(row) > 10 and row[10] else "")
    entry_bina_yasi.delete(0, tk.END)
    entry_bina_yasi.insert(0, str(row[11]) if len(row) > 11 and row[11] else "")
    if entry_musait_gunler:
        entry_musait_gunler.delete(0, tk.END)
        entry_musait_gunler.insert(0, row[13] if len(row) > 13 and row[13] else "")
    if entry_musait_saatler:
        entry_musait_saatler.delete(0, tk.END)
        entry_musait_saatler.insert(0, row[14] if len(row) > 14 and row[14] else "")

    editing_emlak_id = emlak_id
    selected_photo_path = row[8]
    if selected_photo_path and photo_label:
        photo_label.config(text=f"Mevcut: {os.path.basename(selected_photo_path)}")
    if btn_save_emlak:
        btn_save_emlak.config(text="✏️ Güncelle", command=update_emlak)
    conn.close()


def delete_emlak():
    if not listbox_emlak or not listbox_emlak.curselection():
        messagebox.showerror("Hata", "Silmek için emlak seçin!")
        return
    if not messagebox.askyesno("Onay", "Emlak kaydını silmek istediğinizden emin misiniz?"):
        return
    emlak_id = _selected_emlak_id()
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM emlak WHERE id = ?", (emlak_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Başarılı", "Emlak silindi!")
    list_emlak()


def list_emlak():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM emlak ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    if not listbox_emlak:
        return
    listbox_emlak.delete(0, tk.END)
    for row in rows:
        fav = row[15] if len(row) > 15 and row[15] else 0
        listbox_emlak.insert(
            tk.END,
            f"ID:{row[0]} | {row[1]} | {row[2]} | {row[3]:,.0f}₺ | {row[4]} oda | {row[5]}m² | {row[6]} | ❤️{fav}",
        )


def search_emlak():
    term = entry_search_emlak.get().lower()
    if not term:
        list_emlak()
        return
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM emlak WHERE LOWER(tur) LIKE ? OR LOWER(konum) LIKE ? OR LOWER(durum) LIKE ?",
        tuple([f"%{term}%"] * 3),
    )
    rows = c.fetchall()
    conn.close()
    if not listbox_emlak:
        return
    listbox_emlak.delete(0, tk.END)
    for row in rows:
        fav = row[15] if len(row) > 15 and row[15] else 0
        listbox_emlak.insert(
            tk.END,
            f"ID:{row[0]} | {row[1]} | {row[2]} | {row[3]:,.0f}₺ | {row[4]} oda | {row[5]}m² | {row[6]} | ❤️{fav}",
        )


def clear_emlak_entries():
    global selected_photo_path
    entry_tur.delete(0, tk.END)
    entry_konum.delete(0, tk.END)
    entry_fiyat.delete(0, tk.END)
    combo_sahip.set("")
    combo_isitma.set("")
    entry_bina_yasi.delete(0, tk.END)
    entry_oda.delete(0, tk.END)
    entry_metrekare.delete(0, tk.END)
    combo_durum.set("")
    text_aciklama.delete("1.0", tk.END)
    if entry_musait_gunler:
        entry_musait_gunler.delete(0, tk.END)
    if entry_musait_saatler:
        entry_musait_saatler.delete(0, tk.END)
    selected_photo_path = None
    if photo_label:
        photo_label.config(text="Fotoğraf Seçilmedi")
