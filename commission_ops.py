import tkinter as tk
from tkinter import messagebox, ttk
import datetime

from property_management.db import get_connection
from property_management.ui_utils import create_modern_button

def show_komisyon_menu(root, show_main_menu_cb):
    for widget in root.winfo_children():
        widget.destroy()

    kom_window = tk.Frame(root, bg='#334155')
    kom_window.pack(fill=tk.BOTH, expand=True, padx=200, pady=50)

    tk.Label(kom_window, text="💰 KOMİSYON HESAPLAMA", font=("Arial", 16, "bold"),
             bg='#334155', fg='white').pack(pady=20)

    tk.Label(kom_window, text="Emlak:", bg='#334155', fg='white').pack()
    emlak_var = tk.StringVar()
    emlak_combo = ttk.Combobox(kom_window, textvariable=emlak_var, width=60)
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, tur, konum, fiyat FROM emlak WHERE durum IN ('Satılık', 'Kiralık')")
    emlaklar = c.fetchall()
    
    emlak_combo['values'] = [f"{e[0]} - {e[1]} - {e[2]} - {e[3]:,.0f}₺" for e in emlaklar]
    emlak_combo.pack(pady=5)

    tk.Label(kom_window, text="Müşteri:", bg='#334155', fg='white').pack(pady=(10, 0))
    musteri_var = tk.StringVar()
    musteri_combo = ttk.Combobox(kom_window, textvariable=musteri_var, width=60)
    
    c.execute("SELECT id, isim, telefon FROM musteri")
    musteriler = c.fetchall()
    conn.close()
    
    musteri_combo['values'] = [f"{m[0]} - {m[1]} - {m[2]}" for m in musteriler]
    musteri_combo.pack(pady=5)

    tk.Label(kom_window, text="İşlem Türü:", bg='#334155', fg='white').pack(pady=(10, 0))
    islem_var = tk.StringVar(value="Satış")
    islem_combo = ttk.Combobox(kom_window, textvariable=islem_var, width=59, values=["Satış", "Kira"])
    islem_combo.pack(pady=5)

    tk.Label(kom_window, text="İşlem Tutarı (₺):", bg='#334155', fg='white').pack(pady=(10, 0))
    tutar_entry = tk.Entry(kom_window, width=62)
    tutar_entry.pack(pady=5)

    tk.Label(kom_window, text="Komisyon Oranı (%):", bg='#334155', fg='white').pack(pady=(10, 0))
    oran_entry = tk.Entry(kom_window, width=62)
    oran_entry.insert(0, "3")
    oran_entry.pack(pady=5)

    komisyon_label = tk.Label(kom_window, text="Komisyon: 0 ₺", font=("Arial", 14, "bold"),
                              bg='#334155', fg='#F1C40F')
    komisyon_label.pack(pady=15)

    def hesapla():
        try:
            tutar = float(tutar_entry.get().replace(',', ''))
            oran = float(oran_entry.get())
            komisyon = (tutar * oran) / 100
            komisyon_label.config(text=f"Komisyon: {komisyon:,.2f} ₺")
        except ValueError:
            messagebox.showerror("Hata", "Geçerli sayı girin!")

    def kaydet():
        try:
            if not emlak_var.get() or not musteri_var.get():
                messagebox.showerror("Hata", "Emlak ve müşteri seçin!")
                return

            emlak_id = int(emlak_var.get().split(' - ')[0])
            musteri_id = int(musteri_var.get().split(' - ')[0])
            tutar = float(tutar_entry.get().replace(',', ''))
            oran = float(oran_entry.get())
            komisyon = (tutar * oran) / 100

            conn = get_connection()
            c = conn.cursor()
            c.execute("""INSERT INTO komisyon (emlak_id, musteri_id, islem_turu, tutar,
                                               komisyon_orani, komisyon_tutari, tarih)
                         VALUES (?, ?, ?, ?, ?, ?, ?)""",
                      (emlak_id, musteri_id, islem_var.get(), tutar, oran, komisyon,
                       datetime.date.today().isoformat()))
            
            yeni_durum = "Satıldı" if islem_var.get() == "Satış" else "Kiralandı"
            c.execute("UPDATE emlak SET durum = ? WHERE id = ?", (yeni_durum, emlak_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", f"Komisyon kaydedildi: {komisyon:,.2f} ₺")
            show_main_menu_cb(root)

        except ValueError:
            messagebox.showerror("Hata", "Geçerli değerler girin!")

    btn_frame = tk.Frame(kom_window, bg='#334155')
    btn_frame.pack(pady=20)

    tk.Button(btn_frame, text="🧮 Hesapla", command=hesapla, bg="#3b82f6", fg="white", width=12).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="💾 Kaydet", command=kaydet, bg="#10b981", fg="white", width=12).pack(side=tk.LEFT, padx=10)
    
    create_modern_button(root, "🏠 Ana Menü", lambda: show_main_menu_cb(root), "#d946ef", width=20, height=2).pack(pady=15)
