"""
emlak_ops.py
────────────
Emlak Yönetimi – UI koordinatörü.

Bu dosya yalnızca Tkinter form ve panel oluşturmayı içerir.
İş mantığı alt modüllere ayrılmıştır:

  modules/emlak_crud.py      → Veritabanı CRUD + fotoğraf + favori
  modules/emlak_matching.py  → Portföy eşleştirme (Reverse Matching)
"""

import tkinter as tk
from tkinter import ttk

from property_management.db import get_connection
from property_management.ui_utils import create_modern_button
import property_management.modules.property_crud as crud
from property_management.modules.property_matching import reverse_matching_check


def show_emlak_menu(root, show_main_menu_cb):
    """Emlak Yönetimi ana ekranını oluşturur ve gösterir."""
    for widget in root.winfo_children():
        widget.destroy()

    main_frame = tk.Frame(root, bg="#0f172a")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    tk.Label(
        main_frame,
        text="🏠 EMLAK YÖNETİMİ & PORTFÖY EŞLEŞTİRME",
        font=("Arial", 16, "bold"), bg="#0f172a", fg="white",
    ).pack(pady=15)

    content_frame = tk.Frame(main_frame, bg="#0f172a")
    content_frame.pack(fill=tk.BOTH, expand=True)

    # ── Sol Panel – Scrollable Form ─────────────────────────────────────────
    left_panel = tk.Frame(content_frame, bg="#1e293b", width=370)
    left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
    left_panel.pack_propagate(False)

    canvas = tk.Canvas(left_panel, bg="#334155", highlightthickness=0)
    scrollbar = tk.Scrollbar(left_panel, orient="vertical", command=canvas.yview)
    form_frame = tk.Frame(canvas, bg="#334155")
    form_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=form_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    tk.Label(
        form_frame, text="EMLAK BİLGİLERİ",
        font=("Arial", 13, "bold"), bg="#334155", fg="white"
    ).pack(pady=12)

    def lbl(text):
        tk.Label(form_frame, text=text, bg="#334155", fg="#e2e8f0").pack(anchor="w", padx=15)

    def entry_widget():
        e = tk.Entry(form_frame, width=34, bg="#1e293b", fg="white", insertbackground="white")
        e.pack(pady=(2, 8), padx=15)
        return e

    def combo_widget(values):
        cb = ttk.Combobox(form_frame, width=31, values=values)
        cb.pack(pady=(2, 8), padx=15)
        return cb

    lbl("Emlak Türü *");     crud.entry_tur      = entry_widget()
    lbl("Konum *");          crud.entry_konum    = entry_widget()
    lbl("Fiyat (₺) *");     crud.entry_fiyat    = entry_widget()

    lbl("Sahip Seç")
    crud.combo_sahip = ttk.Combobox(form_frame, width=31)
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, isim, tip FROM musteri")
    musteriler = c.fetchall()
    conn.close()
    crud.combo_sahip["values"] = [
        f"{m[0]} - {m[1]} ({m[2] or 'Belirtilmemiş'})" for m in musteriler
    ]
    crud.combo_sahip.pack(pady=(2, 8), padx=15)

    lbl("Isıtma");           crud.combo_isitma   = combo_widget(["Yok", "Doğalgaz", "Merkezi", "Klima", "Soba"])
    lbl("Bina Yaşı");        crud.entry_bina_yasi = entry_widget()
    lbl("Oda Sayısı *");     crud.entry_oda      = entry_widget()
    lbl("Metrekare *");      crud.entry_metrekare = entry_widget()
    lbl("Durum *");          crud.combo_durum    = combo_widget(["Satılık", "Kiralık", "Satıldı", "Kiralandı"])

    # ── Müsaitlik Takvimi ────────────────────────────────────────────────────
    tk.Label(
        form_frame, text="━━ MÜSAİTLİK TAKVİMİ ━━",
        font=("Arial", 10, "bold"), bg="#334155", fg="#f59e0b"
    ).pack(pady=(8, 4))

    lbl("Müsait Günler (örn: Pazartesi-Cuma)")
    crud.entry_musait_gunler = entry_widget()
    lbl("Müsait Saatler (örn: 10:00-18:00)")
    crud.entry_musait_saatler = entry_widget()

    lbl("Açıklama")
    crud.text_aciklama = tk.Text(
        form_frame, width=34, height=3, bg="#1e293b", fg="white", insertbackground="white"
    )
    crud.text_aciklama.pack(pady=(2, 8), padx=15)

    # Fotoğraf
    lbl("Fotoğraf")
    pf = tk.Frame(form_frame, bg="#334155")
    pf.pack(fill=tk.X, padx=15, pady=2)
    tk.Button(pf, text="📷 Seç", command=crud.select_photo, bg="#3b82f6", fg="white", width=10).pack(side=tk.LEFT)
    tk.Button(
        pf, text="👁 Görüntüle",
        command=lambda: crud.view_emlak_photo(root),
        bg="#8b5cf6", fg="white", width=10
    ).pack(side=tk.RIGHT)
    crud.photo_label = tk.Label(form_frame, text="Fotoğraf Seçilmedi", bg="#334155", fg="#BDC3C7")
    crud.photo_label.pack(pady=2)

    # ── Kaydet / Temizle ─────────────────────────────────────────────────────
    btn_frame = tk.Frame(left_panel, bg="#334155")
    btn_frame.pack(pady=15)

    def _add_and_match():
        """Kaydet + portföy eşleştirme tetikle."""
        crud.add_emlak(
            on_added_callback=lambda nid, tur, fiyat, oda, durum:
                reverse_matching_check(root, nid, tur, fiyat, oda, durum)
        )

    crud.btn_save_emlak = create_modern_button(btn_frame, "💾 Kaydet", _add_and_match, "#10b981", width=13)
    crud.btn_save_emlak.pack(side=tk.LEFT, padx=5)
    create_modern_button(btn_frame, "🗑 Temizle", crud.clear_emlak_entries, "#f59e0b", width=12).pack(side=tk.LEFT, padx=5)

    # ── Sağ Panel – Liste ─────────────────────────────────────────────────────
    right_panel = tk.Frame(content_frame, bg="#1e293b")
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    tk.Label(
        right_panel, text="EMLAK LİSTESİ",
        font=("Arial", 13, "bold"), bg="#334155", fg="white"
    ).pack(pady=12)

    search_frame = tk.Frame(right_panel, bg="#334155")
    search_frame.pack(fill=tk.X, padx=15, pady=8)
    tk.Label(search_frame, text="🔍 Arama:", bg="#334155", fg="white").pack(side=tk.LEFT)
    crud.entry_search_emlak = tk.Entry(
        search_frame, bg="#1e293b", fg="white", insertbackground="white"
    )
    crud.entry_search_emlak.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 5))
    create_modern_button(
        search_frame, "Ara", crud.search_emlak, "#2196F3", width=8
    ).pack(side=tk.RIGHT)

    list_frame = tk.Frame(right_panel, bg="#334155")
    list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

    sb = tk.Scrollbar(list_frame)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    crud.listbox_emlak = tk.Listbox(
        list_frame, font=("Consolas", 8), bg="#1e293b", fg="#F0F6FC",
        height=15, yscrollcommand=sb.set, selectbackground="#3b82f6"
    )
    crud.listbox_emlak.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb.config(command=crud.listbox_emlak.yview)

    # ── Alt Butonlar ─────────────────────────────────────────────────────────
    bottom_frame = tk.Frame(right_panel, bg="#334155")
    bottom_frame.pack(fill=tk.X, padx=15, pady=12)

    row1 = tk.Frame(bottom_frame, bg="#334155")
    row1.pack()
    create_modern_button(row1, "✏️ Düzenle",  crud.edit_emlak,   "#f59e0b").pack(side=tk.LEFT, padx=4)
    create_modern_button(row1, "🗑️ Sil",      crud.delete_emlak, "#ef4444").pack(side=tk.LEFT, padx=4)
    create_modern_button(row1, "🔄 Yenile",   crud.list_emlak,   "#334155").pack(side=tk.LEFT, padx=4)
    create_modern_button(row1, "❤️ Favori+1", crud.favori_ekle,  "#e11d48", width=12).pack(side=tk.LEFT, padx=4)

    create_modern_button(
        root, "🏠 Ana Menü", lambda: show_main_menu_cb(root), "#d946ef", width=20, height=2
    ).pack(pady=12)

    crud.list_emlak()
