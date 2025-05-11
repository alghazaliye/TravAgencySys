"""
مسارات خاصة بربط الحجوزات بالنظام المالي
"""
import os
import json
import uuid
from datetime import datetime, date, time, timedelta
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import desc, and_, or_, func

from app import app, db
from models import Account, JournalEntry, JournalLine, AccountTransaction

import logging

# تكوين سجل الأحداث
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_bus_booking_journal(booking_id, amount, description, customer_name, user_id):
    """إنشاء قيد محاسبي عند إنشاء حجز باص جديد"""
    try:
        # البحث عن الحسابات المطلوبة
        cash_account = Account.query.filter_by(is_cash_account=True, is_default=True).first()
        service_revenue_account = Account.query.filter_by(account_type='revenue', account_number='4001').first()
        
        if not cash_account or not service_revenue_account:
            logger.error("لم يتم العثور على الحسابات المطلوبة لإنشاء قيد محاسبي لحجز الباص")
            return None
        
        # إنشاء قيد محاسبي جديد
        journal_entry = JournalEntry(
            entry_date=date.today(),
            description=f"إيراد حجز باص - {description} - {customer_name}",
            reference="BUS-" + str(booking_id),
            status="posted",
            created_by=user_id
        )
        
        db.session.add(journal_entry)
        db.session.flush()  # للحصول على رقم القيد
        
        # إنشاء سطور القيد المحاسبي
        
        # سطر مدين (Cash Account)
        debit_line = JournalLine(
            journal_id=journal_entry.id,
            account_id=cash_account.id,
            debit_amount=amount,
            credit_amount=0,
            description=f"إيراد حجز باص - {description}",
            line_number=1
        )
        
        # سطر دائن (Revenue Account)
        credit_line = JournalLine(
            journal_id=journal_entry.id,
            account_id=service_revenue_account.id,
            debit_amount=0,
            credit_amount=amount,
            description=f"إيراد حجز باص - {description}",
            line_number=2
        )
        
        db.session.add_all([debit_line, credit_line])
        db.session.flush()
        
        # إنشاء حركات الحسابات
        debit_transaction = AccountTransaction(
            account_id=cash_account.id,
            journal_line_id=debit_line.id,
            amount=amount,
            transaction_type="debit",
            description=f"إيراد حجز باص - {description}",
            transaction_date=date.today()
        )
        
        credit_transaction = AccountTransaction(
            account_id=service_revenue_account.id,
            journal_line_id=credit_line.id,
            amount=amount,
            transaction_type="credit",
            description=f"إيراد حجز باص - {description}",
            transaction_date=date.today()
        )
        
        db.session.add_all([debit_transaction, credit_transaction])
        
        # تحديث أرصدة الحسابات
        cash_account.balance += amount
        service_revenue_account.balance += amount
        
        # حفظ التغييرات
        db.session.commit()
        
        logger.info(f"تم إنشاء قيد محاسبي بنجاح لحجز الباص رقم {booking_id}")
        return journal_entry.id
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ أثناء إنشاء قيد محاسبي لحجز الباص: {str(e)}")
        return None


def create_visa_journal(visa_id, amount, visa_type, description, customer_name, user_id):
    """إنشاء قيد محاسبي عند إنشاء طلب تأشيرة جديد"""
    try:
        # البحث عن الحسابات المطلوبة
        cash_account = Account.query.filter_by(is_cash_account=True, is_default=True).first()
        
        # تحديد حساب الإيرادات حسب نوع التأشيرة
        if visa_type == 'umrah':
            revenue_account_number = '4002'  # رقم حساب إيرادات تأشيرات العمرة
        elif visa_type == 'work':
            revenue_account_number = '4003'  # رقم حساب إيرادات تأشيرات العمل
        elif visa_type == 'family':
            revenue_account_number = '4004'  # رقم حساب إيرادات تأشيرات الزيارة العائلية
        else:
            revenue_account_number = '4000'  # رقم حساب الإيرادات العامة
        
        revenue_account = Account.query.filter_by(account_type='revenue', account_number=revenue_account_number).first()
        
        if not cash_account or not revenue_account:
            logger.error("لم يتم العثور على الحسابات المطلوبة لإنشاء قيد محاسبي لطلب التأشيرة")
            return None
        
        # إنشاء قيد محاسبي جديد
        journal_entry = JournalEntry(
            entry_date=date.today(),
            description=f"إيراد تأشيرة {visa_type} - {description} - {customer_name}",
            reference=f"VISA-{visa_type.upper()}-{visa_id}",
            status="posted",
            created_by=user_id
        )
        
        db.session.add(journal_entry)
        db.session.flush()  # للحصول على رقم القيد
        
        # إنشاء سطور القيد المحاسبي
        
        # سطر مدين (Cash Account)
        debit_line = JournalLine(
            journal_id=journal_entry.id,
            account_id=cash_account.id,
            debit_amount=amount,
            credit_amount=0,
            description=f"إيراد تأشيرة {visa_type} - {description}",
            line_number=1
        )
        
        # سطر دائن (Revenue Account)
        credit_line = JournalLine(
            journal_id=journal_entry.id,
            account_id=revenue_account.id,
            debit_amount=0,
            credit_amount=amount,
            description=f"إيراد تأشيرة {visa_type} - {description}",
            line_number=2
        )
        
        db.session.add_all([debit_line, credit_line])
        db.session.flush()
        
        # إنشاء حركات الحسابات
        debit_transaction = AccountTransaction(
            account_id=cash_account.id,
            journal_line_id=debit_line.id,
            amount=amount,
            transaction_type="debit",
            description=f"إيراد تأشيرة {visa_type} - {description}",
            transaction_date=date.today()
        )
        
        credit_transaction = AccountTransaction(
            account_id=revenue_account.id,
            journal_line_id=credit_line.id,
            amount=amount,
            transaction_type="credit",
            description=f"إيراد تأشيرة {visa_type} - {description}",
            transaction_date=date.today()
        )
        
        db.session.add_all([debit_transaction, credit_transaction])
        
        # تحديث أرصدة الحسابات
        cash_account.balance += amount
        revenue_account.balance += amount
        
        # حفظ التغييرات
        db.session.commit()
        
        logger.info(f"تم إنشاء قيد محاسبي بنجاح لطلب التأشيرة رقم {visa_id}")
        return journal_entry.id
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ أثناء إنشاء قيد محاسبي لطلب التأشيرة: {str(e)}")
        return None


def create_airline_ticket_journal(ticket_id, amount, description, customer_name, user_id):
    """إنشاء قيد محاسبي عند إنشاء تذكرة طيران جديدة"""
    try:
        # البحث عن الحسابات المطلوبة
        cash_account = Account.query.filter_by(is_cash_account=True, is_default=True).first()
        airline_revenue_account = Account.query.filter_by(account_type='revenue', account_number='4005').first()
        
        if not cash_account or not airline_revenue_account:
            logger.error("لم يتم العثور على الحسابات المطلوبة لإنشاء قيد محاسبي لتذكرة الطيران")
            return None
        
        # إنشاء قيد محاسبي جديد
        journal_entry = JournalEntry(
            entry_date=date.today(),
            description=f"إيراد تذكرة طيران - {description} - {customer_name}",
            reference="AIRLINE-" + str(ticket_id),
            status="posted",
            created_by=user_id
        )
        
        db.session.add(journal_entry)
        db.session.flush()  # للحصول على رقم القيد
        
        # إنشاء سطور القيد المحاسبي
        
        # سطر مدين (Cash Account)
        debit_line = JournalLine(
            journal_id=journal_entry.id,
            account_id=cash_account.id,
            debit_amount=amount,
            credit_amount=0,
            description=f"إيراد تذكرة طيران - {description}",
            line_number=1
        )
        
        # سطر دائن (Revenue Account)
        credit_line = JournalLine(
            journal_id=journal_entry.id,
            account_id=airline_revenue_account.id,
            debit_amount=0,
            credit_amount=amount,
            description=f"إيراد تذكرة طيران - {description}",
            line_number=2
        )
        
        db.session.add_all([debit_line, credit_line])
        db.session.flush()
        
        # إنشاء حركات الحسابات
        debit_transaction = AccountTransaction(
            account_id=cash_account.id,
            journal_line_id=debit_line.id,
            amount=amount,
            transaction_type="debit",
            description=f"إيراد تذكرة طيران - {description}",
            transaction_date=date.today()
        )
        
        credit_transaction = AccountTransaction(
            account_id=airline_revenue_account.id,
            journal_line_id=credit_line.id,
            amount=amount,
            transaction_type="credit",
            description=f"إيراد تذكرة طيران - {description}",
            transaction_date=date.today()
        )
        
        db.session.add_all([debit_transaction, credit_transaction])
        
        # تحديث أرصدة الحسابات
        cash_account.balance += amount
        airline_revenue_account.balance += amount
        
        # حفظ التغييرات
        db.session.commit()
        
        logger.info(f"تم إنشاء قيد محاسبي بنجاح لتذكرة الطيران رقم {ticket_id}")
        return journal_entry.id
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ أثناء إنشاء قيد محاسبي لتذكرة الطيران: {str(e)}")
        return None