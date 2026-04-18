"""
musteri_scoring.py
──────────────────
Lead skorlama algoritması ve otomatik etiketleme.
"""


def hesapla_skor_ve_etiket(butce, kredi, aciliyet, tip):
    """
    Müşteri verilerine göre 0-100 arası bir skor ve etiket döndürür.

    Parametreler:
        butce       : float veya None
        kredi       : 'Evet' | 'Hayır' | 'Belirsiz' | None
        aciliyet    : 'Yüksek' | 'Orta' | 'Düşük' | None
        tip         : 'Alıcı' | 'Satıcı' | 'Kiralayan' | 'Kiracı' | None

    Döndürür:
        (skor: int, etiket: str)
    """
    skor = 0

    # Bütçe puanı
    if butce and butce > 0:
        skor += 20

    # Kredi uygunluğu puanı
    skor += {"Evet": 30, "Belirsiz": 10, "Hayır": 0}.get(kredi, 0)

    # Aciliyet puanı
    skor += {"Yüksek": 30, "Orta": 15, "Düşük": 5}.get(aciliyet, 0)

    # Müşteri tipi puanı
    skor += {"Alıcı": 20, "Kiralayan": 15, "Kiracı": 10, "Satıcı": 5}.get(tip, 0)

    # Etiket belirleme
    if skor >= 75:
        etiket = "🔥 Sıcak Alıcı"
    elif skor >= 55:
        etiket = "💼 Yatırımcı Adayı"
    elif skor >= 35:
        etiket = "📅 Hafta Sonu Alıcısı"
    elif skor >= 20:
        etiket = "💬 Sadece Fiyat Soran"
    else:
        etiket = "❄️ Soğuk Lead"

    return skor, etiket
