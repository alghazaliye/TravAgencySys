"""
نص برمجي لتشغيل بذور البيانات المحاسبية
"""
from flask import Flask
from app import app
import seed_accounting

if __name__ == "__main__":
    with app.app_context():
        # تنفيذ بذور البيانات المحاسبية
        seed_accounting.seed_accounting_data()
        print("تم تنفيذ بذور البيانات المحاسبية بنجاح!")