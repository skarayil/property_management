"""
run.py – Emlak Yönetim Sistemi başlatıcı
Projeyi klonladıktan sonra şu komutla çalıştırın:
    python3 run.py
"""
import sys
import os

# Repo kökünü Python path'ine ekle (python3 run.py ile de çalışsın)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from property_management.main import run_app

if __name__ == "__main__":
    run_app()
