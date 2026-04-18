import tkinter as tk
from tkinter import messagebox, ttk
import datetime

from property_management.db import get_connection
from property_management.ui_utils import create_modern_button


# ─────────────────────────────────────────────────────────────────────────────
# ÇAKIŞMA KONTROLÜ
# ─────────────────────────────────────────────────────────────────────────────
def check_conflict(emlak_id, tarih, saat, exclude_id=None):
    """
    Aynı emlak için aynı tarih ve saatte başka randevu var mı kontrol eder.
    Returns True if conflict exists.
    """
    conn = get_connection()
    c = conn.cursor()
    if exclude_id:
        c.execute("""SELECT COUNT(*) FROM randevu
                     WHERE emlak_id = ? AND tarih = ? AND saat = ? AND durum != 'İptal' AND id != ?""",
                  (emlak_id, tarih, saat, exclude_id))
    else:
        c.execute("""SELECT COUNT(*) FROM randevu
                     WHERE emlak_id = ? AND tarih = ? AND saat = ? AND durum != 'İptal'""",
                  (emlak_id, tarih, saat))
    count = c.fetchone()[0]
    conn.close()
    return count > 0


def check_musait_uyum(emlak_id, tarih_str, saat_str):
    """
    Mülk sahibinin belirlediği müsaitlik saatleri ile randevu saatini karşılaştırır.
    Returns (uyumlu: bool, musait_gunler: str, musait_saatler: str)
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT musait_gunler, musait_saatler FROM emlak WHERE id = ?", (emlak_id,))
    row = c.fetchone()
    conn.close()

    if not row or (not row[0] and not row[1]):
        return True, None, None  # Müsaitlik tanımlı değil, serbest

    musait_gunler = row[0] or ""
    musait_saatler = row[1] or ""
    return True, musait_gunler, musait_saatler  # Uyarı veriyoruz, engel koymuyor


def show_randevu_menu(root, show_main_menu_cb):
    for widget in root.winfo_children():
        widget.destroy()

    main_frame = tk.Frame(root, bg='#0f172a')
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    tk.Label(main_frame, text="📅 RANDEVU YÖNETİMİ & TAKVİM",
             font=("Arial", 16, "bold"), bg='#0f172a', fg='white').pack(pady=15)

    content_frame = tk.Frame(main_frame, bg='#0f172a')
    content_frame.pack(fill=tk.BOTH, expand=True)

    # ── Sol Panel – Form ──
    left_panel = tk.Frame(content_frame, bg='#334155', width=320)
    left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
    left_panel.pack_propagate(False)

    tk.Label(left_panel, text="YENİ RANDEVU", font=("Arial", 13, "bold"),
             bg='#334155', fg='white').pack(pady=12)

    tk.Label(left_panel, text="Emlak:", bg='#334155', fg='#e2e8f0').pack(anchor='w', padx=15)
    emlak_var = tk.StringVar()
    emlak_combo = ttk.Combobox(left_panel, textvariable=emlak_var, width=36)

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, tur, konum, musait_gunler, musait_saatler FROM emlak WHERE durum IN ('Satılık', 'Kiralık')")
    emlaklar = c.fetchall()

    emlak_combo['values'] = [f"{e[0]} - {e[1]} - {e[2]}" for e in emlaklar]
    emlak_combo.pack(pady=(2, 5), padx=15)

    # Müsaitlik bilgi etiketi
    musaitlik_label = tk.Label(left_panel, text="", bg='#334155', fg='#34d399',
                                font=("Arial", 9), wraplength=280)
    musaitlik_label.pack(padx=15, pady=(0, 5))

    def update_musaitlik(*args):
        sel = emlak_var.get()
        if sel:
            emlak_id = int(sel.split(" - ")[0])
            for e in emlaklar:
                if e[0] == emlak_id:
                    gunler = e[3] or "Belirtilmemiş"
                    saatler = e[4] or "Belirtilmemiş"
                    musaitlik_label.config(
                        text=f"🗓 Müsait: {gunler} | ⏰ {saatler}"
                    )
                    break

    emlak_var.trace('w', update_musaitlik)

    tk.Label(left_panel, text="Müşteri:", bg='#334155', fg='#e2e8f0').pack(anchor='w', padx=15, pady=(8, 0))
    musteri_var = tk.StringVar()
    musteri_combo = ttk.Combobox(left_panel, textvariable=musteri_var, width=36)

    c.execute("SELECT id, isim, telefon FROM musteri")
    musteriler = c.fetchall()
    conn.close()

    musteri_combo['values'] = [f"{m[0]} - {m[1]} - {m[2]}" for m in musteriler]
    musteri_combo.pack(pady=(2, 8), padx=15)

    tk.Label(left_panel, text="Tarih (GG.AA.YYYY):", bg='#334155', fg='#e2e8f0').pack(anchor='w', padx=15)
    tarih_entry = tk.Entry(left_panel, width=38, bg='#1e293b', fg='white', insertbackground='white')
    tarih_entry.insert(0, datetime.date.today().strftime('%d.%m.%Y'))
    tarih_entry.pack(pady=(2, 8), padx=15)

    tk.Label(left_panel, text="Saat:", bg='#334155', fg='#e2e8f0').pack(anchor='w', padx=15)
    saat_var = tk.StringVar()
    saat_combo = ttk.Combobox(left_panel, textvariable=saat_var, width=36)
    saat_combo['values'] = [f"{h:02d}:{m:02d}" for h in range(9, 20) for m in [0, 30]]
    saat_combo.pack(pady=(2, 8), padx=15)

    tk.Label(left_panel, text="Notlar:", bg='#334155', fg='#e2e8f0').pack(anchor='w', padx=15)
    notlar_text = tk.Text(left_panel, width=38, height=4, bg='#1e293b', fg='white', insertbackground='white')
    notlar_text.pack(pady=(2, 8), padx=15)

    # ── Sağ Panel – Liste ──
    right_panel = tk.Frame(content_frame, bg='#334155')
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    tk.Label(right_panel, text="RANDEVU LİSTESİ", font=("Arial", 13, "bold"),
             bg='#334155', fg='white').pack(pady=12)

    tree_frame = tk.Frame(right_panel, bg='#334155')
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

    scrollbar_randevu = tk.Scrollbar(tree_frame)
    scrollbar_randevu.pack(side=tk.RIGHT, fill=tk.Y)

    columns = ('ID', 'Emlak', 'Müşteri', 'Tarih', 'Saat', 'Durum', 'Geri Bildirim')
    randevu_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=14,
                                  yscrollcommand=scrollbar_randevu.set)
    scrollbar_randevu.config(command=randevu_tree.yview)

    col_widths = {'ID': 45, 'Emlak': 160, 'Müşteri': 110, 'Tarih': 90,
                  'Saat': 60, 'Durum': 90, 'Geri Bildirim': 130}
    for col in columns:
        randevu_tree.heading(col, text=col)
        randevu_tree.column(col, width=col_widths.get(col, 100))

    randevu_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def list_randevular():
        for item in randevu_tree.get_children():
            randevu_tree.delete(item)

        conn2 = get_connection()
        c2 = conn2.cursor()
        c2.execute("""SELECT r.id, e.tur || ' - ' || e.konum, m.isim, r.tarih, r.saat, r.durum,
                             COALESCE(r.gosterim_geri_bildirim, '—')
                      FROM randevu r
                      JOIN emlak e ON r.emlak_id = e.id
                      JOIN musteri m ON r.musteri_id = m.id
                      ORDER BY r.tarih DESC, r.saat DESC""")

        for row in c2.fetchall():
            randevu_tree.insert('', 'end', values=row)
        conn2.close()

    # ─── Randevu Ekleme ───
    def add_randevu():
        if not all([emlak_var.get(), musteri_var.get(), tarih_entry.get(), saat_var.get()]):
            messagebox.showerror("Hata", "Tüm alanları doldurun!")
            return

        try:
            emlak_id = int(emlak_var.get().split(' - ')[0])
            musteri_id = int(musteri_var.get().split(' - ')[0])
            tarih = tarih_entry.get()
            saat = saat_var.get()

            # ── Çakışma Kontrolü ──
            if check_conflict(emlak_id, tarih, saat):
                messagebox.showerror(
                    "⚠️ Randevu Çakışması!",
                    f"Bu emlak için {tarih} tarihinde saat {saat}'de zaten bir randevu var!\n\n"
                    f"Lütfen farklı bir saat veya tarih seçin."
                )
                return

            # ── Müsaitlik Uyarısı ──
            _, musait_gunler, musait_saatler = check_musait_uyum(emlak_id, tarih, saat)
            if musait_gunler or musait_saatler:
                devam = messagebox.askyesno(
                    "📅 Müsaitlik Bilgisi",
                    f"Mülk sahibi müsaitliği:\n"
                    f"🗓 Günler: {musait_gunler}\n"
                    f"⏰ Saatler: {musait_saatler}\n\n"
                    f"Yine de bu saate randevu oluşturmak istiyor musunuz?"
                )
                if not devam:
                    return

            conn3 = get_connection()
            c3 = conn3.cursor()
            c3.execute("""INSERT INTO randevu (emlak_id, musteri_id, tarih, saat, durum, notlar)
                          VALUES (?, ?, ?, ?, 'Bekliyor', ?)""",
                       (emlak_id, musteri_id, tarih, saat,
                        notlar_text.get("1.0", tk.END).strip()))
            conn3.commit()
            conn3.close()

            # Müşteri iletişim tarihini güncelle
            conn4 = get_connection()
            c4 = conn4.cursor()
            c4.execute("UPDATE musteri SET son_iletisim_tarihi = ? WHERE id = ?",
                       (datetime.datetime.now().isoformat(), musteri_id))
            conn4.commit()
            conn4.close()

            messagebox.showinfo("Başarılı ✅", f"Randevu oluşturuldu!\n📅 {tarih} – ⏰ {saat}")
            list_randevular()

        except Exception as e:
            messagebox.showerror("Hata", f"Hata: {str(e)}")

    # ─── Durum Güncelleme ───
    def update_durum(yeni_durum):
        selected = randevu_tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Randevu seçin!")
            return

        randevu_id = randevu_tree.item(selected[0])['values'][0]

        conn5 = get_connection()
        c5 = conn5.cursor()
        c5.execute("UPDATE randevu SET durum = ? WHERE id = ?", (yeni_durum, randevu_id))
        conn5.commit()
        conn5.close()

        messagebox.showinfo("Başarılı", f"Durum '{yeni_durum}' olarak güncellendi!")
        list_randevular()

    def delete_randevu():
        selected = randevu_tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Randevu seçin!")
            return
        if messagebox.askyesno("Onay", "Randevuyu silmek istiyor musunuz?"):
            randevu_id = randevu_tree.item(selected[0])['values'][0]
            conn6 = get_connection()
            c6 = conn6.cursor()
            c6.execute("DELETE FROM randevu WHERE id = ?", (randevu_id,))
            conn6.commit()
            conn6.close()
            list_randevular()

    # Randevu oluştur butonu
    tk.Button(left_panel, text="📅 Randevu Oluştur", command=add_randevu,
              bg="#10b981", fg="white", font=("Arial", 11, "bold"), width=22, height=2).pack(pady=15)

    btn_frame = tk.Frame(right_panel, bg='#334155')
    btn_frame.pack(pady=10)

    row1 = tk.Frame(btn_frame, bg='#334155')
    row1.pack()
    create_modern_button(row1, "✅ Tamamlandı", lambda: update_durum("Tamamlandı"), "#10b981").pack(side=tk.LEFT, padx=4)
    create_modern_button(row1, "❌ İptal", lambda: update_durum("İptal"), "#ef4444").pack(side=tk.LEFT, padx=4)
    create_modern_button(row1, "🗑️ Sil", delete_randevu, "#7f1d1d", width=8).pack(side=tk.LEFT, padx=4)
    create_modern_button(row1, "🔄 Yenile", list_randevular, "#334155").pack(side=tk.LEFT, padx=4)

    create_modern_button(root, "🏠 Ana Menü", lambda: show_main_menu_cb(root), "#d946ef", width=20, height=2).pack(pady=12)

    list_randevular()
