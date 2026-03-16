"""
musteri_ops.py
──────────────
Müşteri Yönetimi – UI koordinatörü.

Bu dosya yalnızca:
  - Tkinter form / panel oluşturmayı
  - Modül-düzeyi widget referanslarını
içerir. İş mantığı alt modüllere ayrılmıştır:

  modules/musteri_scoring.py  → Lead skoru algoritması
  modules/musteri_crud.py     → Veritabanı CRUD işlemleri
  modules/musteri_takip.py    → Takip merkezi & WhatsApp entegrasyonu
  modules/musteri_evrak.py    → Evrak / doküman yönetimi
"""

import tkinter as tk
from tkinter import ttk

from property_management.ui_utils import create_modern_button
import property_management.modules.customer_crud as crud
from property_management.modules.customer_scoring import hesapla_skor_ve_etiket  # noqa: re-export
from property_management.modules.customer_followup import show_takip_paneli, whatsapp_mesaj_gonder
from property_management.modules.customer_documents import show_evrak_yonetim


def show_musteri_menu(root, show_main_menu_cb):
    """Müşteri Yönetimi ana ekranını oluşturur ve gösterir."""
    for widget in root.winfo_children():
        widget.destroy()

    main_frame = tk.Frame(root, bg="#0f172a")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    tk.Label(
        main_frame,
        text="👥 MÜŞTERİ YÖNETİMİ & LEAD SKORLAMA",
        font=("Arial", 16, "bold"), bg="#0f172a", fg="white",
    ).pack(pady=15)

    content_frame = tk.Frame(main_frame, bg="#0f172a")
    content_frame.pack(fill=tk.BOTH, expand=True)

    # ── Sol Panel – Form ────────────────────────────────────────────────────
    left_panel = tk.Frame(content_frame, bg="#334155", width=340)
    left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
    left_panel.pack_propagate(False)

    canvas = tk.Canvas(left_panel, bg="#334155", highlightthickness=0)
    scrollbar = tk.Scrollbar(left_panel, orient="vertical", command=canvas.yview)
    form_scroll = tk.Frame(canvas, bg="#334155")
    form_scroll.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=form_scroll, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    tk.Label(
        form_scroll, text="MÜŞTERİ BİLGİLERİ",
        font=("Arial", 13, "bold"), bg="#334155", fg="white"
    ).pack(pady=12)

    def lbl(text):
        tk.Label(form_scroll, text=text, bg="#334155", fg="#e2e8f0").pack(anchor="w", padx=15)

    def entry_widget():
        e = tk.Entry(form_scroll, width=32, bg="#1e293b", fg="white", insertbackground="white")
        e.pack(pady=(2, 8), padx=15)
        return e

    lbl("İsim *");         crud.entry_isim     = entry_widget()
    lbl("Telefon *");      crud.entry_telefon  = entry_widget()
    lbl("E-mail");         crud.entry_email    = entry_widget()

    lbl("Tipi")
    crud.combo_tip = ttk.Combobox(form_scroll, width=29,
                                   values=["Alıcı", "Satıcı", "Kiralayan", "Kiracı"])
    crud.combo_tip.pack(pady=(2, 8), padx=15)

    # ── Lead Skorlama ──────────────────────────────────────────────────────
    tk.Label(
        form_scroll, text="━━ LEAD SKORLAMA ━━",
        font=("Arial", 10, "bold"), bg="#334155", fg="#f59e0b"
    ).pack(pady=(8, 4))

    lbl("Bütçe (₺)");      crud.entry_butce    = entry_widget()

    lbl("Kredi Uygunluğu")
    crud.combo_kredi = ttk.Combobox(form_scroll, width=29, values=["Evet", "Hayır", "Belirsiz"])
    crud.combo_kredi.pack(pady=(2, 8), padx=15)

    lbl("Taşınma Aciliyeti")
    crud.combo_aciliyet = ttk.Combobox(form_scroll, width=29,
                                        values=["Yüksek", "Orta", "Düşük"])
    crud.combo_aciliyet.pack(pady=(2, 8), padx=15)

    lbl("Kaynak (Nereden geldi?)")
    crud.combo_kaynak = ttk.Combobox(
        form_scroll, width=29,
        values=["Instagram", "Sahibinden", "Web Sitesi", "Referans", "Diğer"]
    )
    crud.combo_kaynak.pack(pady=(2, 8), padx=15)

    lbl("Adres")
    crud.text_adres = tk.Text(
        form_scroll, width=32, height=3, bg="#1e293b", fg="white", insertbackground="white"
    )
    crud.text_adres.pack(pady=(2, 8), padx=15)

    # ── Kaydet / Temizle ────────────────────────────────────────────────────
    btn_frame = tk.Frame(left_panel, bg="#334155")
    btn_frame.pack(pady=15)

    crud.btn_save_musteri = create_modern_button(
        btn_frame, "💾 Kaydet", crud.add_musteri, "#2196F3", width=13
    )
    crud.btn_save_musteri.pack(side=tk.LEFT, padx=5)
    create_modern_button(
        btn_frame, "🗑 Temizle", crud.clear_musteri_entries, "#f59e0b", width=12
    ).pack(side=tk.LEFT, padx=5)

    # ── Sağ Panel – Liste ────────────────────────────────────────────────────
    right_panel = tk.Frame(content_frame, bg="#334155")
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    tk.Label(
        right_panel,
        text="MÜŞTERİ LİSTESİ (Skora göre sıralı)",
        font=("Arial", 13, "bold"), bg="#334155", fg="white"
    ).pack(pady=12)

    search_frame = tk.Frame(right_panel, bg="#334155")
    search_frame.pack(fill=tk.X, padx=15, pady=8)
    tk.Label(search_frame, text="🔍 Ara:", bg="#334155", fg="white").pack(side=tk.LEFT)
    crud.entry_search_musteri = tk.Entry(
        search_frame, bg="#1e293b", fg="white", insertbackground="white"
    )
    crud.entry_search_musteri.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 5))
    create_modern_button(
        search_frame, "Ara", crud.search_musteri, "#2196F3", width=8
    ).pack(side=tk.RIGHT)

    list_frame = tk.Frame(right_panel, bg="#334155")
    list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

    sb = tk.Scrollbar(list_frame)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    crud.listbox_musteri = tk.Listbox(
        list_frame, font=("Consolas", 8), bg="#1e293b", fg="#F0F6FC",
        height=15, yscrollcommand=sb.set, selectbackground="#3b82f6"
    )
    crud.listbox_musteri.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb.config(command=crud.listbox_musteri.yview)

    # ── Alt Butonlar ─────────────────────────────────────────────────────────
    bottom_frame = tk.Frame(right_panel, bg="#334155")
    bottom_frame.pack(fill=tk.X, padx=15, pady=12)

    row1 = tk.Frame(bottom_frame, bg="#334155")
    row1.pack()
    create_modern_button(row1, "✏️ Düzenle",  crud.edit_musteri,   "#f59e0b").pack(side=tk.LEFT, padx=4)
    create_modern_button(row1, "🗑️ Sil",      crud.delete_musteri, "#ef4444").pack(side=tk.LEFT, padx=4)
    create_modern_button(row1, "🔄 Yenile",   crud.list_musteri,   "#334155").pack(side=tk.LEFT, padx=4)
    create_modern_button(
        row1, "📁 Evraklar",
        lambda: show_evrak_yonetim(root, crud.listbox_musteri),
        "#8b5cf6", width=12
    ).pack(side=tk.LEFT, padx=4)

    row2 = tk.Frame(bottom_frame, bg="#334155")
    row2.pack(pady=6)
    create_modern_button(
        row2, "💬 WhatsApp",
        lambda: whatsapp_mesaj_gonder(crud.listbox_musteri),
        "#25D366", width=16
    ).pack(side=tk.LEFT, padx=4)
    create_modern_button(
        row2, "🔔 Takip Merkezi",
        lambda: show_takip_paneli(root),
        "#f59e0b", width=16
    ).pack(side=tk.LEFT, padx=4)

    create_modern_button(
        root, "🏠 Ana Menü",
        lambda: show_main_menu_cb(root),
        "#d946ef", width=20, height=2
    ).pack(pady=12)

    crud.list_musteri()
