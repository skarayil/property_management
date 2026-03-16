import sqlite3
import os

_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'emlak_v3.db')

def get_connection():
    return sqlite3.connect(_DB_PATH)

def create_tables():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS emlak
                 (id INTEGER PRIMARY KEY, tur TEXT, konum TEXT, fiyat REAL, oda_sayisi TEXT, metrekare INTEGER, durum TEXT, aciklama TEXT, fotograf_yolu TEXT, eklenme_tarihi TEXT, sahip_id INTEGER, isitma TEXT, bina_yasi INTEGER, musait_gunler TEXT, musait_saatler TEXT, favori_sayisi INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS musteri
                 (id INTEGER PRIMARY KEY, isim TEXT, telefon TEXT, email TEXT, adres TEXT, eklenme_tarihi TEXT, tip TEXT, butce REAL, kredi_uygunluk TEXT, aciliyet TEXT, skor INTEGER DEFAULT 0, etiket TEXT, son_iletisim_tarihi TEXT, kaynak TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS komisyon
                 (id INTEGER PRIMARY KEY, emlak_id INTEGER, musteri_id INTEGER, islem_turu TEXT, tutar REAL, komisyon_orani REAL, komisyon_tutari REAL, tarih TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS randevu
                 (id INTEGER PRIMARY KEY, emlak_id INTEGER, musteri_id INTEGER, tarih TEXT, saat TEXT, durum TEXT, notlar TEXT, gosterim_geri_bildirim TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS ayarlar
                 (id INTEGER PRIMARY KEY, firma_adi TEXT, email_username TEXT, email_password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS evraklar
                 (id INTEGER PRIMARY KEY, musteri_id INTEGER, evrak_adi TEXT, dosya_yolu TEXT, yuklenme_tarihi TEXT)''')
    
    c.execute("INSERT OR IGNORE INTO ayarlar (id, firma_adi) VALUES (1, 'Emlak Yönetim Sistemi')")
    conn.commit()
    conn.close()

def update_database_schema():
    conn = get_connection()
    c = conn.cursor()
    # Emlak tablosu kontrolleri
    c.execute("PRAGMA table_info(emlak)")
    emlak_columns = [col[1] for col in c.fetchall()]
    
    if "sahip_id" not in emlak_columns:
        c.execute("ALTER TABLE emlak ADD COLUMN sahip_id INTEGER")
    if "isitma" not in emlak_columns:
        c.execute("ALTER TABLE emlak ADD COLUMN isitma TEXT")
    if "bina_yasi" not in emlak_columns:
        c.execute("ALTER TABLE emlak ADD COLUMN bina_yasi INTEGER")
        
    # Musteri tablosu kontrolleri
    c.execute("PRAGMA table_info(musteri)")
    musteri_columns = [col[1] for col in c.fetchall()]
    
    if "tip" not in musteri_columns:
        c.execute("ALTER TABLE musteri ADD COLUMN tip TEXT")
    if "butce" not in musteri_columns:
        c.execute("ALTER TABLE musteri ADD COLUMN butce REAL")
    if "kredi_uygunluk" not in musteri_columns:
        c.execute("ALTER TABLE musteri ADD COLUMN kredi_uygunluk TEXT")
    if "aciliyet" not in musteri_columns:
        c.execute("ALTER TABLE musteri ADD COLUMN aciliyet TEXT")
    if "skor" not in musteri_columns:
        c.execute("ALTER TABLE musteri ADD COLUMN skor INTEGER DEFAULT 0")
    if "etiket" not in musteri_columns:
        c.execute("ALTER TABLE musteri ADD COLUMN etiket TEXT")
    if "son_iletisim_tarihi" not in musteri_columns:
        c.execute("ALTER TABLE musteri ADD COLUMN son_iletisim_tarihi TEXT")
    if "kaynak" not in musteri_columns:
        c.execute("ALTER TABLE musteri ADD COLUMN kaynak TEXT")

    # Emlak tablosu kontrolleri
    c.execute("PRAGMA table_info(emlak)")
    emlak_columns2 = [col[1] for col in c.fetchall()]
    if "musait_gunler" not in emlak_columns2:
        c.execute("ALTER TABLE emlak ADD COLUMN musait_gunler TEXT")
    if "musait_saatler" not in emlak_columns2:
        c.execute("ALTER TABLE emlak ADD COLUMN musait_saatler TEXT")
    if "favori_sayisi" not in emlak_columns2:
        c.execute("ALTER TABLE emlak ADD COLUMN favori_sayisi INTEGER DEFAULT 0")

    # Randevu tablosu kontrolleri
    c.execute("PRAGMA table_info(randevu)")
    randevu_columns = [col[1] for col in c.fetchall()]
    if "gosterim_geri_bildirim" not in randevu_columns:
        c.execute("ALTER TABLE randevu ADD COLUMN gosterim_geri_bildirim TEXT")

    # Evraklar tablosu
    c.execute('''CREATE TABLE IF NOT EXISTS evraklar
                 (id INTEGER PRIMARY KEY, musteri_id INTEGER, evrak_adi TEXT, dosya_yolu TEXT, yuklenme_tarihi TEXT)''')

    conn.commit()
    conn.close()

def load_settings():
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM ayarlar WHERE id = 1")
        settings = c.fetchone()
        return settings if settings else (1, 'Emlak Yönetim Sistemi', None, None)
    finally:
        conn.close()

# Initialize DB when imported
create_tables()
update_database_schema()
