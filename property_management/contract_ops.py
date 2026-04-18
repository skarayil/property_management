import tkinter as tk
from tkinter import messagebox, ttk
import datetime

from property_management.db import get_connection, load_settings
from property_management.ui_utils import create_modern_button

def show_sozlesme_menu(root, show_main_menu_cb):
    for widget in root.winfo_children():
        widget.destroy()

    main_frame = tk.Frame(root, bg='#0f172a')
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    tk.Label(main_frame, text="📄 SÖZLEŞME OLUŞTUR", font=("Arial", 18, "bold"), bg='#0f172a', fg='white').pack(pady=20)

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, tur, konum, fiyat FROM emlak WHERE durum IN ('Satılık', 'Kiralık')")
    emlaklar = c.fetchall()

    c.execute("SELECT id, isim, telefon FROM musteri")
    musteriler = c.fetchall()
    conn.close()

    if not emlaklar or not musteriler:
        warning_text = "⚠️ UYARI ⚠️\n\n"
        if not emlaklar:
            warning_text += "• Önce satılık/kiralık emlak ekleyin!\n"
        if not musteriler:
            warning_text += "• Önce müşteri ekleyin!\n"

        tk.Label(main_frame, text=warning_text, font=("Arial", 14, "bold"),
                 bg='#0f172a', fg='red', justify=tk.CENTER).pack(pady=50)

        create_modern_button(root, "🏠 Ana Menü", lambda: show_main_menu_cb(root), "#d946ef", width=20, height=3).pack(pady=30)
        return

    form_frame = tk.Frame(main_frame, bg='#334155')
    form_frame.pack(expand=True, padx=100, pady=30)

    tk.Label(form_frame, text="SÖZLEŞME BİLGİLERİ", font=("Arial", 16, "bold"), bg='#334155', fg='white').pack(pady=20)

    tk.Label(form_frame, text="📍 Emlak Seçin:", font=("Arial", 12, "bold"), bg='#334155', fg='white').pack(pady=5)
    emlak_var = tk.StringVar()
    emlak_combo = ttk.Combobox(form_frame, textvariable=emlak_var, width=70)
    emlak_combo['values'] = [f"{e[0]} - {e[1]} - {e[2]} - {e[3]:,.0f}₺" for e in emlaklar]
    emlak_combo.pack(pady=5)

    tk.Label(form_frame, text="👤 Müşteri Seçin:", font=("Arial", 12, "bold"), bg='#334155', fg='white').pack(pady=(15, 5))
    musteri_var = tk.StringVar()
    musteri_combo = ttk.Combobox(form_frame, textvariable=musteri_var, width=70)
    musteri_combo['values'] = [f"{m[0]} - {m[1]} - {m[2]}" for m in musteriler]
    musteri_combo.pack(pady=5)

    tk.Label(form_frame, text="📋 Sözleşme Türü:", font=("Arial", 12, "bold"), bg='#334155', fg='white').pack(pady=(15, 5))
    sozlesme_turu = tk.StringVar(value="Kira")
    radio_frame = tk.Frame(form_frame, bg='#334155')
    radio_frame.pack(pady=10)

    tk.Radiobutton(radio_frame, text="🏠 Kira Sözleşmesi", variable=sozlesme_turu, value="Kira",
                   bg='#334155', fg='white', font=("Arial", 12), selectcolor='#0f172a').pack(side=tk.LEFT, padx=30)
    tk.Radiobutton(radio_frame, text="💰 Satış Sözleşmesi", variable=sozlesme_turu, value="Satış",
                   bg='#334155', fg='white', font=("Arial", 12), selectcolor='#0f172a').pack(side=tk.LEFT, padx=30)

    def olustur_sozlesme():
        emlak = emlak_var.get()
        musteri = musteri_var.get()
        tur = sozlesme_turu.get()

        if not emlak or not musteri:
            messagebox.showerror("Hata", "Emlak ve müşteri seçin!")
            return

        settings = load_settings()
        tarih = datetime.date.today().strftime('%d.%m.%Y')
        sozlesme_no = f"{tur[0].upper()}{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        sozlesme_metni = f"""
{tur.upper()} SÖZLEŞMESİ
═══════════════════════════════════════════════

FİRMA: {settings[1]}
SÖZLEŞME NO: {sozlesme_no}
TARİH: {tarih}
SAAT: {datetime.datetime.now().strftime('%H:%M:%S')}

EMLAK BİLGİLERİ:
{emlak}

MÜŞTERİ BİLGİLERİ:
{musteri}

SÖZLEŞME DETAYLARI:
• Sözleşme Türü: {tur}
• Düzenleme Tarihi: {tarih}

Bu sözleşme yukarıda belirtilen taraflar arasında 
karşılıklı rıza ile düzenlenmiştir.

SÖZLEŞME KOŞULLARI:
1. Bu sözleşme {tarih} tarihinde düzenlenmiştir.
2. Taraflar bu sözleşme şartlarını kabul ederler.
3. Yasal haklar saklıdır.

İMZALAR:

MÜŞTERİ:                    FİRMA:
Ad: ........................  Ad: ........................
İmza: ......................  İmza: ......................
Tarih: {tarih}              Tarih: {tarih}

═══════════════════════════════════════════════
{settings[1]}
{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
═══════════════════════════════════════════════
        """

        filename = f"raporlar/{tur}_Sozlesmesi_{sozlesme_no}.txt"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(sozlesme_metni)

            messagebox.showinfo("✅ BAŞARILI",
                                f"Sözleşme oluşturuldu!\n\n"
                                f"📁 Dosya: {filename}\n"
                                f"📋 No: {sozlesme_no}")

        except Exception as e:
            messagebox.showerror("❌ HATA", f"Sözleşme oluşturulamadı: {str(e)}")

    btn_frame = tk.Frame(main_frame, bg='#0f172a')
    btn_frame.pack(pady=30)

    create_modern_button(btn_frame, "📄 Sözleşme Oluştur", olustur_sozlesme, "#10b981", width=25, height=4).pack(side=tk.LEFT, padx=20)
    create_modern_button(btn_frame, "🏠 Ana Menü", lambda: show_main_menu_cb(root), "#d946ef", width=25, height=4).pack(side=tk.LEFT, padx=20)
