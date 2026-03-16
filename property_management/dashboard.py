import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from property_management.db import get_connection

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def show_dashboard(root):
    if not MATPLOTLIB_AVAILABLE:
        messagebox.showerror("Hata", "Dashboard için matplotlib gerekli!\npip install matplotlib")
        return

    dash_window = tk.Toplevel(root)
    dash_window.title("📊 Dashboard & Performans Analitiği")
    dash_window.geometry("1100x700")
    dash_window.configure(bg='#0f172a')

    tk.Label(dash_window, text="📊 PERFORMANS ANALİTİĞİ DASHBOARD",
             font=("Arial", 18, "bold"), bg='#0f172a', fg='white').pack(pady=10)

    # ── KPI Kartları ──
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM emlak")
    toplam_emlak = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM emlak WHERE durum = 'Satılık'")
    satilik = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM emlak WHERE durum = 'Kiralık'")
    kiralik = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM emlak WHERE durum IN ('Satıldı', 'Kiralandı')")
    satildi = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM musteri")
    toplam_musteri = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM randevu WHERE durum = 'Tamamlandı'")
    tamamlanan_randevu = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM randevu")
    toplam_randevu = c.fetchone()[0]
    c.execute("SELECT SUM(komisyon_tutari) FROM komisyon")
    toplam_komisyon = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(DISTINCT musteri_id) FROM randevu")
    randevuya_donen_musteri = c.fetchone()[0]

    donusum_orani = (randevuya_donen_musteri / toplam_musteri * 100) if toplam_musteri > 0 else 0
    randevu_tamamlanma = (tamamlanan_randevu / toplam_randevu * 100) if toplam_randevu > 0 else 0

    # Stat cards row
    stats_frame = tk.Frame(dash_window, bg='#0f172a')
    stats_frame.pack(fill=tk.X, padx=20, pady=5)

    def kpi_card(parent, title, value, color, row, col):
        card = tk.Frame(parent, bg=color, width=145, height=85)
        card.grid(row=row, column=col, padx=8, pady=5)
        card.grid_propagate(False)
        tk.Label(card, text=title, font=("Arial", 9, "bold"), bg=color, fg="white",
                 wraplength=130).pack(pady=(8, 2))
        tk.Label(card, text=str(value), font=("Arial", 15, "bold"), bg=color, fg="white").pack()

    kpi_card(stats_frame, "🏠 Toplam Emlak", toplam_emlak, "#3b82f6", 0, 0)
    kpi_card(stats_frame, "💚 Satılık", satilik, "#10b981", 0, 1)
    kpi_card(stats_frame, "🟡 Kiralık", kiralik, "#f59e0b", 0, 2)
    kpi_card(stats_frame, "✅ Satıldı/Kiralandı", satildi, "#22c55e", 0, 3)
    kpi_card(stats_frame, "👥 Müşteri", toplam_musteri, "#8b5cf6", 0, 4)
    kpi_card(stats_frame, "📅 Randevu Tamamlanma", f"%{randevu_tamamlanma:.0f}", "#0ea5e9", 0, 5)
    kpi_card(stats_frame, "🎯 Dönüşüm Oranı", f"%{donusum_orani:.0f}", "#f43f5e", 0, 6)
    kpi_card(stats_frame, "💰 Toplam Komisyon", f"{toplam_komisyon:,.0f}₺", "#d946ef", 1, 0)

    # ── Notebook ile birden fazla grafik ──
    notebook = ttk.Notebook(dash_window)
    notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    # ── Tab 1: Genel Grafiler ──
    tab1 = tk.Frame(notebook, bg='#1e293b')
    notebook.add(tab1, text="🏠 Emlak Analizi")

    try:
        fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        fig1.patch.set_facecolor('#1e293b')
        ax1.set_facecolor('#1e293b')
        ax2.set_facecolor('#1e293b')

        c.execute("SELECT durum, COUNT(*) FROM emlak GROUP BY durum")
        durum_data = c.fetchall()
        if durum_data:
            labels = [row[0] for row in durum_data]
            sizes = [row[1] for row in durum_data]
            colors_pie = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                    colors=colors_pie[:len(sizes)], textprops={'color': 'white'})
            ax1.set_title('Emlak Durum Dağılımı', color='white')

        c.execute("SELECT tur, COUNT(*) FROM emlak GROUP BY tur")
        tur_data = c.fetchall()
        if tur_data:
            turler = [row[0] for row in tur_data]
            sayilar = [row[1] for row in tur_data]
            bar_colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444']
            ax2.bar(turler, sayilar, color=[bar_colors[i % len(bar_colors)] for i in range(len(turler))])
            ax2.set_title('Emlak Türü Dağılımı', color='white')
            ax2.tick_params(axis='x', rotation=30, colors='white')
            ax2.tick_params(axis='y', colors='white')

        plt.tight_layout()
        canvas1 = FigureCanvasTkAgg(fig1, tab1)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    except Exception as e:
        tk.Label(tab1, text=f"Grafik yüklenemedi: {str(e)}", bg='#1e293b', fg='red').pack(pady=50)

    # ── Tab 2: Kaynak Dağılımı (Lead Analizi) ──
    tab2 = tk.Frame(notebook, bg='#1e293b')
    notebook.add(tab2, text="📡 Kaynak & Lead Analizi")

    try:
        fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(10, 4))
        fig2.patch.set_facecolor('#1e293b')
        ax3.set_facecolor('#1e293b')
        ax4.set_facecolor('#1e293b')

        # Kaynak dağılımı
        c.execute("""SELECT COALESCE(kaynak, 'Belirtilmemiş'), COUNT(*)
                     FROM musteri GROUP BY kaynak ORDER BY COUNT(*) DESC""")
        kaynak_data = c.fetchall()
        if kaynak_data:
            k_labels = [row[0] for row in kaynak_data]
            k_sizes = [row[1] for row in kaynak_data]
            kaynak_colors = ['#25D366', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#64748b']
            ax3.pie(k_sizes, labels=k_labels, autopct='%1.1f%%',
                    colors=kaynak_colors[:len(k_sizes)], textprops={'color': 'white'})
            ax3.set_title('Müşteri Kaynak Dağılımı', color='white')
        else:
            ax3.text(0.5, 0.5, 'Henüz kaynak verisi yok', ha='center', va='center',
                     transform=ax3.transAxes, color='white')
            ax3.set_title('Müşteri Kaynak Dağılımı', color='white')

        # Etiket (lead kategori) dağılımı
        c.execute("""SELECT COALESCE(etiket, '❄️ Soğuk Lead'), COUNT(*)
                     FROM musteri GROUP BY etiket ORDER BY COUNT(*) DESC""")
        etiket_data = c.fetchall()
        if etiket_data:
            e_labels = [row[0] for row in etiket_data]
            e_sizes = [row[1] for row in etiket_data]
            etiket_colors = ['#ef4444', '#f59e0b', '#3b82f6', '#22c55e', '#64748b']
            bars = ax4.barh(e_labels, e_sizes,
                            color=[etiket_colors[i % len(etiket_colors)] for i in range(len(e_labels))])
            ax4.set_title('Lead Etiket Dağılımı', color='white')
            ax4.tick_params(axis='x', colors='white')
            ax4.tick_params(axis='y', colors='white')
            for bar, val in zip(bars, e_sizes):
                ax4.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                         str(val), va='center', color='white')
        else:
            ax4.text(0.5, 0.5, 'Henüz etiket verisi yok', ha='center', va='center',
                     transform=ax4.transAxes, color='white')
            ax4.set_title('Lead Etiket Dağılımı', color='white')

        plt.tight_layout()
        canvas2 = FigureCanvasTkAgg(fig2, tab2)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    except Exception as e:
        tk.Label(tab2, text=f"Grafik yüklenemedi: {str(e)}", bg='#1e293b', fg='red').pack(pady=50)

    # ── Tab 3: Popüler İlanlar & Dönüşüm ──
    tab3 = tk.Frame(notebook, bg='#1e293b')
    notebook.add(tab3, text="🔥 Popüler İlanlar")

    tk.Label(tab3, text="Favorilere eklenen ama henüz satılmayan/kiralanmayan ilanlar (Fiyat revizyonu önerilir):",
             bg='#1e293b', fg='#94a3b8', font=("Arial", 10)).pack(pady=8)

    tree_frame = tk.Frame(tab3, bg='#1e293b')
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

    cols = ('ID', 'Tür', 'Konum', 'Fiyat', 'Durum', '❤️ Favori', 'Eklenme Tarihi')
    pop_tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=12)
    for col in cols:
        pop_tree.heading(col, text=col)
        pop_tree.column(col, width=120 if col not in ('ID', '❤️ Favori') else 60)
    pop_tree.pack(fill=tk.BOTH, expand=True)

    c.execute("""SELECT id, tur, konum, fiyat, durum,
                        COALESCE(favori_sayisi, 0), eklenme_tarihi
                 FROM emlak WHERE durum IN ('Satılık', 'Kiralık')
                 ORDER BY COALESCE(favori_sayisi, 0) DESC LIMIT 20""")
    for row in c.fetchall():
        pop_tree.insert('', 'end',
                        values=(row[0], row[1], row[2], f"{row[3]:,.0f}₺", row[4], row[5], row[6][:10]))

    # ── Tab 4: Dönüşüm Detayı ──
    tab4 = tk.Frame(notebook, bg='#1e293b')
    notebook.add(tab4, text="📈 Dönüşüm Analizi")

    info_frame = tk.Frame(tab4, bg='#1e293b')
    info_frame.pack(fill=tk.X, padx=20, pady=10)

    def big_stat(label, val, color):
        f = tk.Frame(info_frame, bg='#334155', padx=20, pady=15)
        f.pack(side=tk.LEFT, padx=10, pady=10)
        tk.Label(f, text=label, bg='#334155', fg='#94a3b8', font=("Arial", 11)).pack()
        tk.Label(f, text=val, bg='#334155', fg=color, font=("Arial", 22, "bold")).pack()

    big_stat("Toplam Müşteri", str(toplam_musteri), "#3b82f6")
    big_stat("Randevuya Dönen", str(randevuya_donen_musteri), "#10b981")
    big_stat("Dönüşüm Oranı", f"%{donusum_orani:.1f}", "#f59e0b")
    big_stat("Tamamlanan Gösterim", str(tamamlanan_randevu), "#22c55e")
    big_stat("Gösterim Tamamlanma %", f"%{randevu_tamamlanma:.1f}", "#8b5cf6")

    # Kaynak bazlı başarı tablosu
    tk.Label(tab4, text="Kaynak Bazlı Müşteri Dağılımı:",
             bg='#1e293b', fg='white', font=("Arial", 12, "bold")).pack(pady=(10, 5))

    tree2_f = tk.Frame(tab4, bg='#1e293b')
    tree2_f.pack(fill=tk.BOTH, expand=True, padx=15)

    cols2 = ('Kaynak', 'Müşteri Sayısı', 'Ort. Skor', 'Yüksek Skor (≥60)')
    src_tree = ttk.Treeview(tree2_f, columns=cols2, show='headings', height=8)
    for col in cols2:
        src_tree.heading(col, text=col)
        src_tree.column(col, width=200)
    src_tree.pack(fill=tk.BOTH, expand=True)

    c.execute("""SELECT COALESCE(kaynak, 'Belirtilmemiş'),
                        COUNT(*),
                        ROUND(AVG(COALESCE(skor, 0)), 1),
                        SUM(CASE WHEN COALESCE(skor, 0) >= 60 THEN 1 ELSE 0 END)
                 FROM musteri GROUP BY kaynak ORDER BY COUNT(*) DESC""")
    for row in c.fetchall():
        src_tree.insert('', 'end', values=row)

    conn.close()
