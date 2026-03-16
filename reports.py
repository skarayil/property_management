import csv
import datetime
from tkinter import messagebox
from property_management.db import get_connection, load_settings

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


def create_pdf_report(report_type):
    try:
        if not FPDF_AVAILABLE:
            messagebox.showerror("Eksik Kütüphane", "FPDF kütüphanesi bulunamadı!\nLütfen terminalden 'pip install fpdf' komutunu çalıştırın 😊")
            return

        filename = f"raporlar/{report_type}_raporu_{datetime.date.today().strftime('%d_%m_%Y')}.pdf"
        settings = load_settings()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        pdf.set_fill_color(30, 41, 59) 
        pdf.set_text_color(255, 255, 255)
        
        def tr2en(text):
            return str(text).replace('ı','i').replace('ş','s').replace('ç','c').replace('ğ','g').replace('ö','o').replace('ü','u') \
                            .replace('İ','I').replace('Ş','S').replace('Ç','C').replace('Ğ','G').replace('Ö','O').replace('Ü','U')
                            
        title_text = f"{settings[1]} - {report_type.upper()} RAPORU"
        pdf.cell(0, 15, tr2en(title_text), 0, 1, 'C', fill=True)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, f"Tarih: {datetime.date.today().strftime('%d.%m.%Y')}", 0, 1, 'R')
        pdf.ln(5)

        pdf.set_font('Arial', 'B', 10)
        pdf.set_fill_color(241, 245, 249)

        conn = get_connection()
        c = conn.cursor()

        if report_type == "emlak":
            c.execute("SELECT id, tur, konum, fiyat, durum FROM emlak ORDER BY id")
            headers = ['ID', 'TUR', 'KONUM', 'FIYAT', 'DURUM']
            widths = [15, 30, 60, 40, 30]
            
            for i, h in enumerate(headers):
                pdf.cell(widths[i], 10, h, 1, 0, 'C', fill=True)
            pdf.ln()
            
            pdf.set_font('Arial', '', 9)
            for row in c.fetchall():
                pdf.cell(widths[0], 10, str(row[0]), 1, 0, 'C')
                pdf.cell(widths[1], 10, tr2en(row[1]), 1, 0, 'C')
                pdf.cell(widths[2], 10, tr2en(row[2])[:30], 1, 0, 'C')
                pdf.cell(widths[3], 10, f"{row[3]:,.0f} TL", 1, 0, 'C')
                pdf.cell(widths[4], 10, tr2en(row[4]), 1, 1, 'C')

        elif report_type == "musteri":
            c.execute("SELECT id, isim, tip, telefon FROM musteri ORDER BY id")
            headers = ['ID', 'ISIM', 'TIP', 'TELEFON']
            widths = [15, 60, 40, 50]
            
            for i, h in enumerate(headers):
                pdf.cell(widths[i], 10, h, 1, 0, 'C', fill=True)
            pdf.ln()
            
            pdf.set_font('Arial', '', 9)
            for row in c.fetchall():
                pdf.cell(widths[0], 10, str(row[0]), 1, 0, 'C')
                tip = str(row[2]) if row[2] else 'Belirtilmemis'
                pdf.cell(widths[1], 10, tr2en(row[1])[:30], 1, 0, 'C')
                pdf.cell(widths[2], 10, tr2en(tip), 1, 0, 'C')
                pdf.cell(widths[3], 10, str(row[3]), 1, 1, 'C')

        conn.close()
        pdf.output(filename)
        messagebox.showinfo("Başarılı", f"Rapor oluşturuldu:\n\n📁 {filename} ✨")

    except Exception as e:
        messagebox.showerror("Hata", f"Rapor oluşturulamadı: {str(e)}")
