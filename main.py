import os
import tkinter as tk
from tkinter import messagebox

from property_management.db import load_settings
from property_management.ui_utils import create_modern_button
from property_management.property_ops import show_emlak_menu
from property_management.customer_ops import show_musteri_menu
from property_management.appointment_ops import show_randevu_menu
from property_management.commission_ops import show_komisyon_menu
from property_management.dashboard import show_dashboard, MATPLOTLIB_AVAILABLE
from property_management.settings_ui import show_settings, show_email_menu
from property_management.contract_ops import show_sozlesme_menu
from property_management.customer_ops import show_takip_paneli


# Update reports module directly or wrap it here
from property_management.reports import create_pdf_report
import datetime
import csv
from property_management.db import get_connection

def rapor_emlak():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM emlak ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    if not rows:
        messagebox.showinfo("Uyarı", "Emlak kaydı yok!")
        return

    filename = f"raporlar/emlak_raporu_{datetime.date.today().strftime('%d_%m_%Y')}.csv"
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Tür", "Konum", "Fiyat", "Oda", "M²", "Durum", "Açıklama", "Fotoğraf", "Tarih"])
        writer.writerows(rows)
    messagebox.showinfo("Başarılı", f"Emlak raporu oluşturuldu: {filename}")


def rapor_musteri():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM musteri ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    if not rows:
        messagebox.showinfo("Uyarı", "Müşteri kaydı yok!")
        return

    filename = f"raporlar/musteri_raporu_{datetime.date.today().strftime('%d_%m_%Y')}.csv"
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "İsim", "Telefon", "Email", "Adres", "Tarih"])
        writer.writerows(rows)
    messagebox.showinfo("Başarılı", f"Müşteri raporu oluşturuldu: {filename}")


def komisyon_raporu():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""SELECT k.id, e.tur, e.konum, m.isim, k.islem_turu, k.tutar, k.komisyon_orani, k.komisyon_tutari, k.tarih
                 FROM komisyon k
                          JOIN emlak e ON k.emlak_id = e.id
                          JOIN musteri m ON k.musteri_id = m.id
                 ORDER BY k.tarih DESC""")
    rows = c.fetchall()
    conn.close()

    if not rows:
        messagebox.showinfo("Uyarı", "Komisyon kaydı yok!")
        return

    filename = f"raporlar/komisyon_raporu_{datetime.date.today().strftime('%d_%m_%Y')}.csv"
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Emlak Tür", "Konum", "Müşteri", "İşlem", "Tutar", "Oran%", "Komisyon", "Tarih"])
        writer.writerows(rows)
    messagebox.showinfo("Başarılı", f"Komisyon raporu oluşturuldu: {filename}")


def ozet_rapor():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM emlak")
    toplam_emlak = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM emlak WHERE durum = 'Satılık'")
    satilik = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM emlak WHERE durum = 'Kiralık'")
    kiralik = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM musteri")
    toplam_musteri = c.fetchone()[0]

    c.execute("SELECT SUM(komisyon_tutari) FROM komisyon")
    toplam_komisyon = c.fetchone()[0] or 0
    conn.close()

    ozet_text = f"""
EMLAK YÖNETİM SİSTEMİ ÖZET RAPORU
═══════════════════════════════════════════════
Tarih: {datetime.date.today().strftime('%d.%m.%Y')}
Saat: {datetime.datetime.now().strftime('%H:%M:%S')}

EMLAK İSTATİSTİKLERİ:
• Toplam Emlak: {toplam_emlak}
• Satılık: {satilik}
• Kiralık: {kiralik}

MÜŞTERİ İSTATİSTİKLERİ:
• Toplam Müşteri: {toplam_musteri}

FİNANSAL BİLGİLER:
• Toplam Komisyon: {toplam_komisyon:,.2f} ₺

═══════════════════════════════════════════════
© 2026 Emlak Yönetim Sistemi | Geliştirici: github.com/skarayil
Professional Edition
═══════════════════════════════════════════════
    """

    filename = f"raporlar/ozet_raporu_{datetime.date.today().strftime('%d_%m_%Y')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(ozet_text)
    messagebox.showinfo("Başarılı", f"Özet rapor oluşturuldu: {filename}")


def show_rapor_menu(root, show_main_menu_cb):
    for widget in root.winfo_children():
        widget.destroy()

    main_frame = tk.Frame(root, bg='#0f172a')
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    tk.Label(main_frame, text="📊 RAPORLAMA MERKEZİ", font=("Arial", 20, "bold"),
             bg='#0f172a', fg='white').pack(pady=30)

    btn_container = tk.Frame(main_frame, bg='#0f172a')
    btn_container.pack(expand=True)

    csv_frame = tk.Frame(btn_container, bg='#0f172a')
    csv_frame.pack(pady=20)

    tk.Label(csv_frame, text="📄 CSV RAPORLARI", font=("Arial", 16, "bold"),
             bg='#0f172a', fg='white').pack(pady=10)

    csv_buttons = tk.Frame(csv_frame, bg='#0f172a')
    csv_buttons.pack()

    create_modern_button(csv_buttons, "🏠 Emlak CSV", rapor_emlak, "#10b981", width=18, height=3).pack(side=tk.LEFT, padx=15)
    create_modern_button(csv_buttons, "👥 Müşteri CSV", rapor_musteri, "#3b82f6", width=18, height=3).pack(side=tk.LEFT, padx=15)
    create_modern_button(csv_buttons, "💰 Komisyon CSV", komisyon_raporu, "#f59e0b", width=18, height=3).pack(side=tk.LEFT, padx=15)

    other_frame = tk.Frame(btn_container, bg='#0f172a')
    other_frame.pack(pady=20)

    tk.Label(other_frame, text="📋 DİĞER RAPORLAR", font=("Arial", 16, "bold"), bg='#0f172a', fg='white').pack(pady=10)

    other_buttons = tk.Frame(other_frame, bg='#0f172a')
    other_buttons.pack()

    create_modern_button(other_buttons, "📈 Özet TXT", ozet_rapor, "#f59e0b", width=18, height=3).pack(side=tk.LEFT, padx=15)
    create_modern_button(other_buttons, "📄 Emlak PDF", lambda: create_pdf_report("emlak"), "#a855f7", width=18, height=3).pack(side=tk.LEFT, padx=15)
    create_modern_button(other_buttons, "📄 Müşteri PDF", lambda: create_pdf_report("musteri"), "#ef4444", width=18, height=3).pack(side=tk.LEFT, padx=15)

    create_modern_button(root, "🏠 Ana Menü", lambda: show_main_menu_cb(root), "#d946ef", width=20, height=3).pack(pady=30)



def show_main_menu(root):
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg='#0f172a')

    header_frame = tk.Frame(root, bg='#1e293b', height=120)
    header_frame.pack(fill=tk.X, pady=(0, 25))
    header_frame.pack_propagate(False)

    settings = load_settings()

    tk.Label(header_frame, text="🏢", font=("Arial", 30), bg='#1e293b', fg='white').pack(pady=(15, 5))
    tk.Label(header_frame, text=settings[1],
             font=("Arial", 20, "bold"), bg='#1e293b', fg='white').pack()
    tk.Label(header_frame, text="Professional Edition",
             font=("Arial", 12), bg='#1e293b', fg='#BDC3C7').pack(pady=(5, 15))

    menu_container = tk.Frame(root, bg='#0f172a')
    menu_container.pack(expand=True)

    tk.Label(menu_container, text="ANA MENÜ", font=("Arial", 18, "bold"),
             bg='#0f172a', fg='white').pack(pady=(0, 30))

    row1 = tk.Frame(menu_container, bg='#0f172a')
    row1.pack(pady=15)

    create_modern_button(row1, "🏠 Emlak\nYönetimi", lambda: show_emlak_menu(root, show_main_menu), "#10b981", width=18, height=5).pack(side=tk.LEFT, padx=20)
    create_modern_button(row1, "👥 Müşteri\nYönetimi", lambda: show_musteri_menu(root, show_main_menu), "#3b82f6", width=18, height=5).pack(side=tk.LEFT, padx=20)
    create_modern_button(row1, "📅 Randevu\nSistemi", lambda: show_randevu_menu(root, show_main_menu), "#f59e0b", width=18, height=5).pack(side=tk.LEFT, padx=20)

    row2 = tk.Frame(menu_container, bg='#0f172a')
    row2.pack(pady=15)

    create_modern_button(row2, "💰 Komisyon\nHesaplama", lambda: show_komisyon_menu(root, show_main_menu), "#8b5cf6", width=18, height=5).pack(side=tk.LEFT, padx=20)
    create_modern_button(row2, "📊 Dashboard\n& Analiz", lambda: show_dashboard(root), "#f59e0b", width=18, height=5).pack(side=tk.LEFT, padx=20)
    create_modern_button(row2, "📋 Raporlama\nMerkezi", lambda: show_rapor_menu(root, show_main_menu), "#0ea5e9", width=18, height=5).pack(side=tk.LEFT, padx=20)

    row3 = tk.Frame(menu_container, bg='#0f172a')
    row3.pack(pady=15)

    create_modern_button(row3, "📧 Email\nSistemi", lambda: show_email_menu(root), "#3b82f6", width=18, height=5).pack(side=tk.LEFT, padx=20)
    create_modern_button(row3, "📄 Sözleşme\nOluştur", lambda: show_sozlesme_menu(root, show_main_menu), "#a855f7", width=18, height=5).pack(side=tk.LEFT, padx=20)
    create_modern_button(row3, "⚙️ Sistem\nAyarları", lambda: show_settings(root), "#64748b", width=18, height=5).pack(side=tk.LEFT, padx=20)

    row4 = tk.Frame(menu_container, bg='#0f172a')
    row4.pack(pady=15)

    create_modern_button(row4, "🔔 Takip\nMerkezi", lambda: show_takip_paneli(root), "#f59e0b", width=18, height=5).pack(side=tk.LEFT, padx=20)

    footer_frame = tk.Frame(root, bg='#0f172a')
    footer_frame.pack(side=tk.BOTTOM, pady=20)

    tk.Label(footer_frame, text="═══════════════════════════════════════════════════════════",
             font=("Arial", 10), bg='#0f172a', fg='#64748b').pack()
    tk.Label(footer_frame, text="🚀 Professional Edition - Emlakçılar için tasarlandı",
             font=("Arial", 11, "bold"), bg='#0f172a', fg='#3498DB').pack()
    tk.Label(footer_frame, text=f"© 2026 {settings[1]} • Geliştirici: github.com/skarayil",
             font=("Arial", 9), bg='#0f172a', fg='#64748b').pack()

def check_dependencies():
    missing_libs = []
    try:
        from PIL import Image, ImageTk
    except ImportError:
        missing_libs.append("Pillow (pip install Pillow)")

    if not MATPLOTLIB_AVAILABLE:
        missing_libs.append("matplotlib (pip install matplotlib)")

    if missing_libs:
        warning_text = "⚠️ EKSİK KÜTÜPHANELER\n\n"
        warning_text += "Aşağıdaki kütüphaneleri yükleyiniz:\n\n"
        warning_text += "\n".join(f"• {lib}" for lib in missing_libs)
        warning_text += "\n\n💡 Terminal/CMD'de yukarıdaki komutları çalıştırın."

        messagebox.showwarning("Eksik Kütüphaneler", warning_text)
        return False
    return True

def startup_message():
    settings = load_settings()

    startup_text = f"""
🎉 HOŞ GELDİNİZ! 🎉

{settings[1]}
Professional Edition

Geliştirici: github.com/skarayil

🚀 Özellikler:
✅ Emlak ve müşteri yönetimi
✅ Email sistemi ve bildirimler
✅ Randevu takip sistemi
✅ Komisyon hesaplama
✅ Dashboard ve analiz
✅ Kapsamlı raporlama
✅ Sözleşme oluşturma
✅ Fotoğraf yönetimi

💡 İpucu: Ayarlar menüsünden firma bilgilerinizi 
   ve email ayarlarınızı yapılandırın!

Başarılı işlemler dileriz! 🏆
    """

    messagebox.showinfo("🎯 Emlak Yönetim Sistemi", startup_text)

def run_app():
    root = tk.Tk()
    root.title("Emlak Yönetim Sistemi - Professional Edition")
    root.geometry("1200x800")
    root.configure(bg='#0f172a')

    for folder in ['emlak_fotograflari', 'raporlar']:
        if not os.path.exists(folder):
            os.makedirs(folder)

    try:
        check_dependencies()
        startup_message()
        show_main_menu(root)
        root.mainloop()

    except Exception as e:
        messagebox.showerror("❌ Kritik Hata", f"Program başlatılamadı:\n\n{str(e)}")

if __name__ == "__main__":
    run_app()
