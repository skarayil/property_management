import tkinter as tk
from tkinter import messagebox, ttk
from property_management.db import get_connection, load_settings
from property_management.ui_utils import create_modern_button
import threading

try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False


def show_settings(root):
    settings_window = tk.Toplevel(root)
    settings_window.title("Ayarlar")
    settings_window.geometry("400x300")
    settings_window.configure(bg='#1e293b')

    tk.Label(settings_window, text="⚙️ AYARLAR", font=("Arial", 16, "bold"),
             bg='#1e293b', fg='white').pack(pady=20)

    settings = load_settings()

    tk.Label(settings_window, text="Firma Adı:", bg='#1e293b', fg='white').pack(pady=5)
    firma_entry = tk.Entry(settings_window, width=40)
    firma_entry.insert(0, settings[1])
    firma_entry.pack(pady=5)

    tk.Label(settings_window, text="Email:", bg='#1e293b', fg='white').pack(pady=5)
    email_entry = tk.Entry(settings_window, width=40)
    email_entry.insert(0, settings[2] if settings[2] else "")
    email_entry.pack(pady=5)

    tk.Label(settings_window, text="Şifre:", bg='#1e293b', fg='white').pack(pady=5)
    password_entry = tk.Entry(settings_window, width=40, show="*")
    password_entry.insert(0, settings[3] if settings[3] else "")
    password_entry.pack(pady=5)

    def save_settings():
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE ayarlar SET firma_adi=?, email_username=?, email_password=? WHERE id=1",
                  (firma_entry.get(), email_entry.get(), password_entry.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Başarılı", "Ayarlar kaydedildi!")
        settings_window.destroy()

    tk.Button(settings_window, text="💾 Kaydet", command=save_settings,
              bg="#10b981", fg="white", width=15).pack(pady=20)


def send_email(to_email, subject, message):
    if not EMAIL_AVAILABLE:
        messagebox.showerror("Hata", "Email sistemi bu Python sürümünde çalışmıyor!")
        return False

    try:
        settings = load_settings()
        if not settings[2] or not settings[3]:
            messagebox.showerror("Hata", "Email ayarları eksik!")
            return False

        msg = MimeMultipart()
        msg['From'] = settings[2]
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MimeText(message, 'plain'))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(settings[2], settings[3])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        messagebox.showerror("Hata", f"Email gönderilemedi: {str(e)}")
        return False


def show_email_menu(root):
    email_window = tk.Toplevel(root)
    email_window.title("Email Gönder")
    email_window.geometry("500x400")
    email_window.configure(bg='#1e293b')

    tk.Label(email_window, text="📧 EMAIL GÖNDER", font=("Arial", 16, "bold"),
             bg='#1e293b', fg='white').pack(pady=15)

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, isim, email FROM musteri WHERE email IS NOT NULL AND email != ''")
    musteriler = c.fetchall()
    conn.close()

    if not musteriler:
        tk.Label(email_window, text="Email adresi olan müşteri yok!",
                 bg='#1e293b', fg='red').pack(pady=20)
        return

    tk.Label(email_window, text="Alıcı:", bg='#1e293b', fg='white').pack()
    alici_var = tk.StringVar()
    alici_combo = ttk.Combobox(email_window, textvariable=alici_var, width=50)
    alici_combo['values'] = [f"{m[1]} - {m[2]}" for m in musteriler]
    alici_combo.pack(pady=5)

    tk.Label(email_window, text="Konu:", bg='#1e293b', fg='white').pack(pady=(10, 0))
    konu_entry = tk.Entry(email_window, width=50)
    konu_entry.pack(pady=5)

    tk.Label(email_window, text="Mesaj:", bg='#334155', fg='white').pack(pady=(10, 0))
    mesaj_text = tk.Text(email_window, width=50, height=8)
    mesaj_text.pack(pady=5)

    def send_action():
        if not alici_var.get() or not konu_entry.get():
            messagebox.showerror("Hata", "Alıcı ve konu gerekli!")
            return

        email = alici_var.get().split(' - ')[1]

        def send_thread():
            if send_email(email, konu_entry.get(), mesaj_text.get("1.0", tk.END)):
                messagebox.showinfo("Başarılı", "Email gönderildi!")
                email_window.destroy()

        threading.Thread(target=send_thread).start()

    tk.Button(email_window, text="📧 Gönder", command=send_action,
              bg="#10b981", fg="white").pack(pady=10)
