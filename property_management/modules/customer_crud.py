"""
musteri_crud.py
───────────────
Müşteri veritabanı işlemleri: ekleme, güncelleme, silme, listeleme.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import datetime

from property_management.db import get_connection
from property_management.modules.customer_scoring import hesapla_skor_ve_etiket

# ── Modül-düzeyi widget referansları ──────────────────────────────────────────
entry_isim = None
entry_telefon = None
entry_email = None
combo_tip = None
text_adres = None
listbox_musteri = None
entry_search_musteri = None
btn_save_musteri = None
editing_musteri_id = None

entry_butce = None
combo_kredi = None
combo_aciliyet = None
combo_kaynak = None


# ── DB Yardımcıları ───────────────────────────────────────────────────────────
def _build_musteri_from_form():
    """Form alanlarından sözlük döndürür."""
    butce_str = entry_butce.get().replace(",", "").replace(".", "") if entry_butce else ""
    try:
        butce = float(butce_str) if butce_str else None
    except ValueError:
        butce = None
    return {
        "isim": entry_isim.get(),
        "telefon": entry_telefon.get(),
        "email": entry_email.get(),
        "tip": combo_tip.get(),
        "adres": text_adres.get("1.0", tk.END).strip(),
        "butce": butce,
        "kredi": combo_kredi.get() if combo_kredi else "",
        "aciliyet": combo_aciliyet.get() if combo_aciliyet else "",
        "kaynak": combo_kaynak.get() if combo_kaynak else "",
    }


# ── CRUD İşlemleri ────────────────────────────────────────────────────────────
def add_musteri():
    d = _build_musteri_from_form()
    if not (d["isim"] and d["telefon"]):
        messagebox.showerror("Eksik Bilgi", "Lütfen isim ve telefon bilgilerini eksiksiz doldurun 😊")
        return

    skor, etiket = hesapla_skor_ve_etiket(d["butce"], d["kredi"], d["aciliyet"], d["tip"])
    now = datetime.datetime.now().isoformat()

    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """INSERT INTO musteri (isim, telefon, email, adres, eklenme_tarihi, tip,
                                butce, kredi_uygunluk, aciliyet, skor, etiket,
                                son_iletisim_tarihi, kaynak)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (d["isim"], d["telefon"], d["email"], d["adres"], now, d["tip"],
         d["butce"], d["kredi"], d["aciliyet"], skor, etiket, now, d["kaynak"]),
    )
    conn.commit()
    conn.close()

    messagebox.showinfo(
        "Başarılı",
        f"Müşteri eklendi! ✨\n\n🏷️ Etiket: {etiket}\n⭐ Müşteri Skoru: {skor}/100",
    )
    clear_musteri_entries()
    list_musteri()


def update_musteri():
    d = _build_musteri_from_form()
    if not (d["isim"] and d["telefon"]):
        messagebox.showerror("Eksik Bilgi", "Lütfen isim ve telefon bilgilerini eksiksiz doldurun 😊")
        return

    skor, etiket = hesapla_skor_ve_etiket(d["butce"], d["kredi"], d["aciliyet"], d["tip"])

    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """UPDATE musteri
           SET isim=?, telefon=?, email=?, tip=?, adres=?,
               butce=?, kredi_uygunluk=?, aciliyet=?, skor=?, etiket=?,
               son_iletisim_tarihi=?, kaynak=?
           WHERE id=?""",
        (d["isim"], d["telefon"], d["email"], d["tip"], d["adres"],
         d["butce"], d["kredi"], d["aciliyet"], skor, etiket,
         datetime.datetime.now().isoformat(), d["kaynak"], editing_musteri_id),
    )
    conn.commit()
    conn.close()

    messagebox.showinfo("Başarılı", f"Müşteri güncellendi! ✨\n🏷️ Yeni Etiket: {etiket}\n⭐ Skor: {skor}/100")
    clear_musteri_entries()
    list_musteri()
    if btn_save_musteri:
        btn_save_musteri.config(text="💾 Kaydet", command=add_musteri)


def delete_musteri():
    selected = listbox_musteri.curselection()
    if not selected:
        messagebox.showerror("Uyarı", "Lütfen silmek için bir müşteri seçin 😊")
        return
    if not messagebox.askyesno("Onay", "Müşteri kaydını silmek istediğinizden emin misiniz?"):
        return

    musteri_id = _selected_musteri_id()
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM musteri WHERE id = ?", (musteri_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Başarılı", "Müşteri başarıyla silindi! 🗑️")
    list_musteri()


def edit_musteri():
    global editing_musteri_id
    selected = listbox_musteri.curselection()
    if not selected:
        messagebox.showerror("Uyarı", "Lütfen düzenlemek için bir müşteri seçin 😊")
        return

    musteri_id = _selected_musteri_id()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM musteri WHERE id = ?", (musteri_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return

    entry_isim.delete(0, tk.END); entry_isim.insert(0, row[1])
    entry_telefon.delete(0, tk.END); entry_telefon.insert(0, row[2])
    entry_email.delete(0, tk.END); entry_email.insert(0, row[3] or "")
    combo_tip.set(row[6] if len(row) > 6 and row[6] else "")
    text_adres.delete("1.0", tk.END); text_adres.insert("1.0", row[4] or "")

    if entry_butce and len(row) > 7 and row[7]:
        entry_butce.delete(0, tk.END); entry_butce.insert(0, str(int(row[7])))
    if combo_kredi and len(row) > 8 and row[8]:
        combo_kredi.set(row[8])
    if combo_aciliyet and len(row) > 9 and row[9]:
        combo_aciliyet.set(row[9])
    if combo_kaynak and len(row) > 13 and row[13]:
        combo_kaynak.set(row[13])

    editing_musteri_id = musteri_id
    if btn_save_musteri:
        btn_save_musteri.config(text="✏️ Güncelle", command=update_musteri)


def list_musteri(search_term=None):
    conn = get_connection()
    c = conn.cursor()
    if search_term:
        c.execute(
            """SELECT * FROM musteri
               WHERE LOWER(isim) LIKE ? OR LOWER(telefon) LIKE ?
                  OR LOWER(email) LIKE ? OR LOWER(tip) LIKE ? OR LOWER(etiket) LIKE ?
               ORDER BY skor DESC""",
            tuple([f"%{search_term}%"] * 5),
        )
    else:
        c.execute("SELECT * FROM musteri ORDER BY skor DESC")
    rows = c.fetchall()
    conn.close()

    if not listbox_musteri:
        return
    listbox_musteri.delete(0, tk.END)
    for row in rows:
        etiket = row[11] if len(row) > 11 and row[11] else ""
        tip = row[6] if len(row) > 6 and row[6] else "Belirtilmemiş"
        skor = row[10] if len(row) > 10 and row[10] is not None else 0
        butce = f"{row[7]:,.0f}₺" if len(row) > 7 and row[7] else "-"
        listbox_musteri.insert(
            tk.END,
            f"ID:{row[0]} | {etiket} | {row[1]} | {tip} | {row[2]} | Bütçe:{butce} | Skor:{skor}",
        )


def search_musteri():
    term = entry_search_musteri.get().lower()
    list_musteri(term if term else None)


def clear_musteri_entries():
    if not entry_isim:
        return
    entry_isim.delete(0, tk.END)
    entry_telefon.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    combo_tip.set("")
    text_adres.delete("1.0", tk.END)
    for widget in [entry_butce]:
        if widget:
            widget.delete(0, tk.END)
    for widget in [combo_kredi, combo_aciliyet, combo_kaynak]:
        if widget:
            widget.set("")


# ── Yardımcılar ───────────────────────────────────────────────────────────────
def _selected_musteri_id():
    item = listbox_musteri.get(listbox_musteri.curselection()[0])
    return int(item.split(" | ")[0].split(":")[1])
