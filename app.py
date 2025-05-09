import os
import logging
from datetime import datetime, date
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# إضافة فلتر مخصص لتنسيق التاريخ
@app.template_filter('date')
def date_filter(value, format='%d/%m/%Y'):
    """فلتر لتنسيق التاريخ في قوالب Jinja"""
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            return value
    return value.strftime(format)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///travelagency.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    full_name = db.Column(db.String(150))
    active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def is_active(self):
        return self.active

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    mobile = db.Column(db.String(20))
    email = db.Column(db.String(120))
    id_type = db.Column(db.String(20))
    id_number = db.Column(db.String(30))
    nationality = db.Column(db.String(50))
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(10))
    address = db.Column(db.String(200))
    id_issue_date = db.Column(db.Date)
    id_expiry_date = db.Column(db.Date)
    id_issue_place = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TransportCompany(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True)
    contact_person = db.Column(db.String(100))
    contact_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bus_routes = db.relationship('BusRoute', backref='company', lazy=True)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), default="المملكة العربية السعودية")
    code = db.Column(db.String(10))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    departures = db.relationship('BusRoute', foreign_keys='BusRoute.departure_city_id', backref='departure_city', lazy=True)
    destinations = db.relationship('BusRoute', foreign_keys='BusRoute.destination_city_id', backref='destination_city', lazy=True)

class BusRoute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    departure_city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    destination_city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('transport_company.id'), nullable=False)
    route_code = db.Column(db.String(20))
    distance = db.Column(db.Float)  # in kilometers
    duration = db.Column(db.Integer)  # in minutes
    base_price = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    schedules = db.relationship('BusSchedule', backref='route', lazy=True)

class BusType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(20))
    description = db.Column(db.Text)
    seat_capacity = db.Column(db.Integer)
    has_wifi = db.Column(db.Boolean, default=False)
    has_ac = db.Column(db.Boolean, default=True)
    has_toilet = db.Column(db.Boolean, default=False)
    is_vip = db.Column(db.Boolean, default=False)
    price_multiplier = db.Column(db.Float, default=1.0)  # Factor to multiply base route price
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    schedules = db.relationship('BusSchedule', backref='bus_type', lazy=True)

class BusSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('bus_route.id'), nullable=False)
    bus_type_id = db.Column(db.Integer, db.ForeignKey('bus_type.id'), nullable=False)
    departure_time = db.Column(db.Time, nullable=False)
    arrival_time = db.Column(db.Time)
    days_of_week = db.Column(db.String(20))  # e.g., "1,2,3,4,5" for weekdays
    price = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trips = db.relationship('BusTrip', backref='schedule', lazy=True)

class BusTrip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('bus_schedule.id'), nullable=False)
    trip_date = db.Column(db.Date, nullable=False)
    bus_number = db.Column(db.String(20))
    driver_name = db.Column(db.String(100))
    driver_contact = db.Column(db.String(20))
    available_seats = db.Column(db.Integer)
    status = db.Column(db.String(20), default="scheduled")  # scheduled, in-progress, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BusBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # بيانات المسافر - القسم الأول
    passenger_name = db.Column(db.String(150), nullable=False)  # اسم المسافر (إجباري)
    mobile_number = db.Column(db.String(20))  # رقم الهاتف (اختياري)
    id_number = db.Column(db.String(30))  # رقم الهوية
    birth_date = db.Column(db.Date)  # تاريخ الميلاد
    gender = db.Column(db.String(10))  # الجنس (ذكر/أنثى)
    
    # بيانات الحجز - القسم الثاني
    trip_type = db.Column(db.String(20))  # نوع الرحلة (عادي/سياحي)
    departure_city = db.Column(db.String(100))  # مدينة المغادرة
    destination_city = db.Column(db.String(100))  # مدينة الوصول
    service_provider = db.Column(db.String(100))  # مزود الخدمة
    journey_type = db.Column(db.String(20))  # نوع الرحلة (ذهاب/ذهاب وعودة)
    travel_date = db.Column(db.Date)  # تاريخ السفر
    return_date = db.Column(db.Date)  # تاريخ العودة (في حالة الذهاب والعودة)
    
    # البيانات المالية - القسم الثالث
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)  # تاريخ ووقت العملية
    currency = db.Column(db.String(10), default="SAR")  # العملة
    selling_price = db.Column(db.Float)  # سعر البيع الإجمالي
    cost_price = db.Column(db.Float)  # سعر التكلفة الإجمالي
    payment_type = db.Column(db.String(20))  # نوع التوصيل المالي (نقد/أجل/تحويل بنكي)
    account = db.Column(db.String(50))  # الحساب (صندوق/عميل/بنك)
    received_amount = db.Column(db.Float, default=0)  # المبلغ الواصل
    remaining_amount = db.Column(db.Float, default=0)  # المبلغ المتبقي
    statement = db.Column(db.Text)  # البيان
    
    # بيانات النظام
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BookingPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bus_booking.id'), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    reference_number = db.Column(db.String(50))
    account = db.Column(db.String(50))  # cash-register, bank-account, etc.
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    booking = db.relationship('BusBooking', backref='payments')
    user = db.relationship('User', foreign_keys=[created_by])

class SystemSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(50), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    setting_type = db.Column(db.String(20), default='text')  # text, image, boolean, json
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_value(cls, key, default=None):
        """Get a setting value by key"""
        setting = cls.query.filter_by(setting_key=key).first()
        if setting:
            if setting.setting_type == 'boolean':
                return setting.setting_value.lower() in ('true', '1', 'yes')
            elif setting.setting_type == 'json':
                try:
                    import json
                    return json.loads(setting.setting_value)
                except:
                    return default
            else:
                return setting.setting_value
        return default
        
    @classmethod
    def set_value(cls, key, value, setting_type='text', description=None):
        """Set a setting value by key"""
        setting = cls.query.filter_by(setting_key=key).first()
        if setting:
            setting.setting_value = str(value)
            setting.updated_at = datetime.utcnow()
            if setting_type:
                setting.setting_type = setting_type
            if description:
                setting.description = description
        else:
            setting = cls(
                setting_key=key,
                setting_value=str(value),
                setting_type=setting_type,
                description=description
            )
            db.session.add(setting)
        db.session.commit()
        return setting

# النماذج المالية والمحاسبية

class AccountCategory(db.Model):
    """فئات الحسابات المالية"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True) 
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    accounts = db.relationship('Account', backref='category', lazy=True)

class Account(db.Model):
    """الحسابات المالية"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('account_category.id'))
    account_type = db.Column(db.String(50))  # أصول، خصوم، إيرادات، مصروفات، حقوق ملكية
    is_bank_account = db.Column(db.Boolean, default=False)
    is_cash_account = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=True)
    balance = db.Column(db.Float, default=0)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    children = db.relationship('Account', backref=db.backref('parent', remote_side=[id]), lazy=True)
    journal_entries_debit = db.relationship('JournalEntryLine', foreign_keys='JournalEntryLine.debit_account_id',
                                   backref='debit_account', lazy=True)
    journal_entries_credit = db.relationship('JournalEntryLine', foreign_keys='JournalEntryLine.credit_account_id',
                                    backref='credit_account', lazy=True)

class JournalEntry(db.Model):
    """قيود اليومية الرئيسية"""
    id = db.Column(db.Integer, primary_key=True)
    entry_number = db.Column(db.String(20), unique=True, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    reference_type = db.Column(db.String(50))  # نوع المستند المرجعي (فاتورة، سند صرف، إلخ)
    reference_id = db.Column(db.String(50))  # رقم المستند المرجعي
    description = db.Column(db.Text)
    entry_type = db.Column(db.String(20), default='manual')  # manual, sales, purchase, expenses, etc
    status = db.Column(db.String(20), default='draft')  # مسودة، مرحل، ملغي
    is_posted = db.Column(db.Boolean, default=False)
    posted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    posted_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    entry_lines = db.relationship('JournalEntryLine', backref='journal_entry', lazy=True, cascade="all, delete-orphan")
    creator = db.relationship('User', foreign_keys=[created_by])
    poster = db.relationship('User', foreign_keys=[posted_by])

    @property
    def total_debit(self):
        """إجمالي مبلغ المدين"""
        return sum(line.debit_amount for line in self.entry_lines)

    @property
    def total_credit(self):
        """إجمالي مبلغ الدائن"""
        return sum(line.credit_amount for line in self.entry_lines)

    @property
    def is_balanced(self):
        """التحقق من توازن القيد (المدين = الدائن)"""
        return round(self.total_debit, 2) == round(self.total_credit, 2)

class JournalEntryLine(db.Model):
    """بنود قيود اليومية"""
    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entry.id'), nullable=False)
    debit_account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    credit_account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    description = db.Column(db.Text)
    debit_amount = db.Column(db.Float, default=0)
    credit_amount = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FinancialPeriod(db.Model):
    """الفترات المالية"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_closed = db.Column(db.Boolean, default=False)
    closed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    closed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    closer = db.relationship('User', foreign_keys=[closed_by])

class PaymentVoucher(db.Model):
    """سندات الصرف"""
    id = db.Column(db.Integer, primary_key=True)
    voucher_number = db.Column(db.String(20), unique=True, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    beneficiary_type = db.Column(db.String(20))  # موظف، مورد، عميل، أخرى
    beneficiary_id = db.Column(db.Integer)  # المعرف في الجدول المناسب
    beneficiary_name = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))  # حساب الصرف (البنك أو الصندوق)
    payment_method = db.Column(db.String(20), default='cash')  # cash, check, transfer, etc
    reference_number = db.Column(db.String(50))  # رقم الشيك أو التحويل
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='posted')  # مصدر، ملغي
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entry.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    account = db.relationship('Account', foreign_keys=[account_id])
    journal_entry = db.relationship('JournalEntry', foreign_keys=[journal_entry_id])
    creator = db.relationship('User', foreign_keys=[created_by])

class ReceiptVoucher(db.Model):
    """سندات القبض"""
    id = db.Column(db.Integer, primary_key=True)
    voucher_number = db.Column(db.String(20), unique=True, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    payer_type = db.Column(db.String(20))  # عميل، موظف، أخرى
    payer_id = db.Column(db.Integer)  # المعرف في الجدول المناسب
    payer_name = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))  # حساب الاستلام (البنك أو الصندوق)
    payment_method = db.Column(db.String(20), default='cash')  # cash, check, transfer, etc
    reference_number = db.Column(db.String(50))  # رقم الشيك أو التحويل
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='posted')  # مستلم، ملغي
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entry.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    account = db.relationship('Account', foreign_keys=[account_id])
    journal_entry = db.relationship('JournalEntry', foreign_keys=[journal_entry_id])
    creator = db.relationship('User', foreign_keys=[created_by])

class Currency(db.Model):
    """العملات"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(3), unique=True, nullable=False)  # SAR, USD, EUR
    symbol = db.Column(db.String(5))  # ر.س, $, €
    exchange_rate = db.Column(db.Float, default=1.0)  # سعر الصرف نسبة إلى العملة الأساسية
    is_base_currency = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TaxSettings(db.Model):
    """إعدادات الضرائب"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rate = db.Column(db.Float, nullable=False, default=0)  # نسبة الضريبة (0.15 = 15%)
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FinancialSettings(db.Model):
    """الإعدادات المالية للنظام"""
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150))
    fiscal_year_start = db.Column(db.Date)
    base_currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'))
    default_tax_id = db.Column(db.Integer, db.ForeignKey('tax_settings.id'))
    enable_cost_centers = db.Column(db.Boolean, default=False)
    enable_budgets = db.Column(db.Boolean, default=False)
    default_cash_account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    default_bank_account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    base_currency = db.relationship('Currency', foreign_keys=[base_currency_id])
    default_tax = db.relationship('TaxSettings', foreign_keys=[default_tax_id])
    default_cash_account = db.relationship('Account', foreign_keys=[default_cash_account_id])
    default_bank_account = db.relationship('Account', foreign_keys=[default_bank_account_id])

class BankAccount(db.Model):
    """الحسابات البنكية"""
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    bank_name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(30), nullable=False)
    iban = db.Column(db.String(50))
    swift_code = db.Column(db.String(20))
    branch_name = db.Column(db.String(100))
    branch_code = db.Column(db.String(20))
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'))
    opening_balance = db.Column(db.Float, default=0)
    current_balance = db.Column(db.Float, default=0)
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    account = db.relationship('Account', foreign_keys=[account_id])
    currency = db.relationship('Currency', foreign_keys=[currency_id])

class CashRegister(db.Model):
    """صناديق النقد"""
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    balance = db.Column(db.Float, default=0)  # رصيد الصندوق
    is_main_register = db.Column(db.Boolean, default=False)  # هل هذا هو الصندوق الرئيسي
    is_active = db.Column(db.Boolean, default=True)  # حالة الصندوق نشط/غير نشط
    responsible_person = db.Column(db.String(100))  # الشخص المسؤول
    responsible_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'))
    opening_balance = db.Column(db.Float, default=0)
    notes = db.Column(db.Text)  # ملاحظات
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    account = db.relationship('Account', foreign_keys=[account_id])
    responsible_user = db.relationship('User', foreign_keys=[responsible_user_id])
    currency = db.relationship('Currency', foreign_keys=[currency_id])
    
    @property
    def current_balance(self):
        """للتوافق مع الكود الحالي، نعيد قيمة balance كـ current_balance"""
        return self.balance

class AccountTransaction(db.Model):
    """حركات الحسابات والصناديق"""
    id = db.Column(db.Integer, primary_key=True)
    
    # نوع الحركة: إيداع، سحب، تحويل
    transaction_type = db.Column(db.String(20), nullable=False)
    
    # المبلغ (إذا كان سالباً فهو سحب)
    amount = db.Column(db.Float, nullable=False)
    
    # الرصيد بعد الحركة
    balance_after = db.Column(db.Float, nullable=False)
    
    # معلومات المصدر
    source_type = db.Column(db.String(20), nullable=False)  # 'bank' أو 'cash'
    source_id = db.Column(db.Integer, nullable=False)
    
    # معلومات الوجهة (في حالة التحويل)
    destination_type = db.Column(db.String(20))
    destination_id = db.Column(db.Integer)
    
    # وصف الحركة والمرجع
    description = db.Column(db.Text)
    reference = db.Column(db.String(100))
    
    # معلومات المستخدم
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # تواريخ
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = db.relationship('User', foreign_keys=[user_id])

# Create all tables
with app.app_context():
    db.create_all()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
@app.route('/login')
def login():
    # Redirect directly to dashboard for now
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/airline-tickets')
def airline_tickets():
    return render_template('airline-tickets.html')

@app.route('/bus-tickets')
def bus_tickets():
    # تحويل مباشر إلى صفحة حجز تذكرة باص جديدة
    return redirect(url_for('new_bus_booking'))

@app.route('/api/bus-routes', methods=['GET'])
def get_bus_routes():
    departure_city_id = request.args.get('departure_city_id')
    destination_city_id = request.args.get('destination_city_id')
    
    # Query routes based on cities
    query = BusRoute.query.filter_by(is_active=True)
    
    if departure_city_id:
        query = query.filter_by(departure_city_id=departure_city_id)
    if destination_city_id:
        query = query.filter_by(destination_city_id=destination_city_id)
    
    routes = query.all()
    
    # Format for JSON response
    routes_data = [{
        'id': route.id,
        'departure_city': route.departure_city.name,
        'destination_city': route.destination_city.name,
        'company': route.company.name,
        'duration': route.duration,
        'base_price': route.base_price
    } for route in routes]
    
    return jsonify(routes_data)

@app.route('/api/bus-schedules', methods=['GET'])
def get_bus_schedules():
    route_id = request.args.get('route_id')
    date = request.args.get('date')
    
    if not route_id:
        return jsonify({'error': 'Route ID is required'}), 400
    
    # Query schedules for the route
    schedules = BusSchedule.query.filter_by(route_id=route_id, is_active=True).all()
    
    # Format for JSON response
    schedules_data = [{
        'id': schedule.id,
        'departure_time': schedule.departure_time.strftime('%H:%M'),
        'arrival_time': schedule.arrival_time.strftime('%H:%M') if schedule.arrival_time else None,
        'bus_type': schedule.bus_type.name,
        'price': schedule.price,
        'available_seats': 'Available' if schedule.is_active else 'Full'
    } for schedule in schedules]
    
    return jsonify(schedules_data)

@app.route('/api/create-bus-booking', methods=['POST'])
def create_bus_booking():
    try:
        # Get form data
        data = request.form
        logging.debug(f"Received booking data: {data}")
        
        # Basic validation
        required_fields = ['passengerName', 'sellPrice']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False, 
                    'error': f'الحقل المطلوب {field} غير موجود'
                }), 400
        
        # Create a unique booking number
        booking_count = BusBooking.query.count()
        booking_number = f"BUS-{booking_count + 1:06d}"
        
        # Create booking record with all fields based on the form data
        booking = BusBooking()
        booking.booking_number = booking_number
        
        # بيانات المسافر - القسم الأول
        booking.passenger_name = data.get('passengerName', '')
        booking.mobile_number = data.get('mobileNumber', '')
        booking.id_number = data.get('idNumber', '')
        
        # معالجة التواريخ
        try:
            birth_date_str = data.get('birthDate', '')
            if birth_date_str and birth_date_str.strip():
                booking.birth_date = datetime.strptime(birth_date_str, '%d  %B , %Y').date()
        except ValueError:
            logging.warning(f"Invalid birth date format: {data.get('birthDate')}")
        
        booking.gender = data.get('gender', '')
        
        # بيانات الحجز - القسم الثاني
        booking.trip_type = data.get('tripType', '')
        booking.departure_city = data.get('departureCity', '')
        booking.destination_city = data.get('destinationCity', '')
        booking.service_provider = data.get('supplierId', '')
        booking.journey_type = 'round-trip' if data.get('journeyTypeRoundTrip') == 'on' else 'one-way'
        
        try:
            reservation_date_str = data.get('reservationDate', '')
            if reservation_date_str and reservation_date_str.strip():
                booking.travel_date = datetime.strptime(reservation_date_str, '%d  %B , %Y').date()
        except ValueError:
            logging.warning(f"Invalid reservation date format: {data.get('reservationDate')}")
            booking.travel_date = date.today()
        
        try:
            return_date_str = data.get('returnDate', '')
            if return_date_str and return_date_str.strip():
                booking.return_date = datetime.strptime(return_date_str, '%d  %B , %Y').date()
        except ValueError:
            logging.warning(f"Invalid return date format: {data.get('returnDate')}")
        
        # البيانات المالية - القسم الثالث
        try:
            transaction_date_str = data.get('transactionDate', '')
            if transaction_date_str and transaction_date_str.strip():
                booking.transaction_date = datetime.strptime(transaction_date_str, '%d  %B , %Y').date()
        except ValueError:
            logging.warning(f"Invalid transaction date format: {data.get('transactionDate')}")
            booking.transaction_date = datetime.utcnow()
            
        booking.currency = data.get('currency', 'SAR')
        
        try:
            booking.selling_price = float(data.get('sellPrice', 0))
        except ValueError:
            booking.selling_price = 0
            
        try:
            booking.cost_price = float(data.get('purchasePrice', 0))
        except ValueError:
            booking.cost_price = 0
        
        booking.payment_type = data.get('paymentType', '')
        booking.account = data.get('accountId', '')
        
        try:
            booking.received_amount = float(data.get('receivedAmount', 0))
        except ValueError:
            booking.received_amount = 0
            
        try:
            booking.remaining_amount = float(data.get('remainingAmount', 0))
        except ValueError:
            # حساب المبلغ المتبقي تلقائياً
            booking.remaining_amount = max(0, booking.selling_price - booking.received_amount)
        
        # إنشاء البيان التلقائي
        statement = data.get('statement', '')
        if not statement:
            departure_city = booking.departure_city
            destination_city = booking.destination_city
            passenger_name = booking.passenger_name
            statement = f"حجز تذكرة من {departure_city} إلى {destination_city} للمسافر {passenger_name}"
        
        booking.statement = statement
        
        # Add booking to the database
        db.session.add(booking)
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'booking_id': booking.id, 
            'booking_number': booking.booking_number
        })
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating booking: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/bus-tickets-new')
def bus_tickets_new():
    # إعادة توجيه إلى قائمة حجوزات الباص
    return redirect(url_for('bus_tickets'))

@app.route('/new-bus-booking')
def new_bus_booking():
    # قائمة العملات
    currencies = [
        {"id": "SAR", "name": "ريال سعودي (SAR)"},
        {"id": "USD", "name": "دولار أمريكي (USD)"},
        {"id": "EUR", "name": "يورو (EUR)"},
        {"id": "YER", "name": "ريال يمني (YER)"}
    ]
    
    # استرجاع قائمة الحجوزات للعرض في الصفحة نفسها
    bookings = BusBooking.query.order_by(BusBooking.created_at.desc()).limit(10).all()
    
    # عرض صفحة حجوزات الباص بدون تفعيل نموذج الحجز
    # (سيتم تفعيله عبر JavaScript عند النقر على زر "حجز جديد")
    return render_template('bus-tickets.html', currencies=currencies, bookings=bookings, show_booking_form=False)

@app.route('/work-visa')
def work_visa():
    return render_template('work-visa.html')

@app.route('/family-visit')
def family_visit():
    return render_template('family-visit.html')

@app.route('/umrah-visa')
def umrah_visa():
    return render_template('umrah-visa.html')

@app.route('/umrah-guarantee')
def umrah_guarantee():
    return render_template('umrah-guarantee.html')

@app.route('/mail-tracking')
def mail_tracking():
    return render_template('mail-tracking.html')

@app.route('/customers')
def customers():
    return render_template('customers.html')

@app.route('/suppliers')
def suppliers():
    return render_template('suppliers.html')

@app.route('/banks')
def banks():
    """عرض صفحة إدارة الصناديق والبنوك"""
    # الحصول على الصناديق النقدية
    cash_registers = CashRegister.query.all()
    
    # الحصول على الحسابات البنكية
    bank_accounts = BankAccount.query.all()
    
    # الحصول على العملات
    currencies = Currency.query.filter_by(is_active=True).all()
    
    # الحصول على أرصدة كل عملة
    currency_totals = {}
    base_currency = Currency.query.filter_by(is_base_currency=True).first()
    base_currency_code = base_currency.code if base_currency else 'SAR'
    
    # تهيئة القاموس بجميع العملات وقيمها صفر
    for currency in currencies:
        currency_totals[currency.code] = {
            'cash': 0,
            'bank': 0,
            'total': 0,
            'symbol': currency.symbol,
            'name': currency.name,
            'id': currency.id
        }
    
    # حساب إجمالي الصناديق لكل عملة
    for register in cash_registers:
        currency_code = register.currency.code if register.currency else base_currency_code
        if currency_code in currency_totals:
            currency_totals[currency_code]['cash'] += register.balance if register.balance else 0
            currency_totals[currency_code]['total'] += register.balance if register.balance else 0
    
    # حساب إجمالي البنوك لكل عملة
    for account in bank_accounts:
        currency_code = account.currency.code if account.currency else base_currency_code
        if currency_code in currency_totals:
            currency_totals[currency_code]['bank'] += account.current_balance if account.current_balance else 0
            currency_totals[currency_code]['total'] += account.current_balance if account.current_balance else 0
    
    # حساب الإجمالي الكلي بالعملة الأساسية
    total_in_base_currency = 0
    for code, data in currency_totals.items():
        currency = next((c for c in currencies if c.code == code), None)
        if currency and currency.exchange_rate:
            # تحويل المبلغ إلى العملة الأساسية
            total_in_base_currency += data['total'] / currency.exchange_rate
    
    # الحصول على حركات الحسابات الأخيرة (10 حركات)
    # في المستقبل سيتم استبدال هذا بحركات حقيقية من قاعدة البيانات
    recent_transactions = []
    
    return render_template('banks.html', 
                          cash_registers=cash_registers,
                          bank_accounts=bank_accounts,
                          currencies=currencies,
                          currency_totals=currency_totals,
                          base_currency=base_currency,
                          total_in_base_currency=total_in_base_currency,
                          recent_transactions=recent_transactions)

@app.route('/api/bank-accounts', methods=['GET', 'POST'])
def api_bank_accounts():
    """واجهة برمجية لإدارة الحسابات البنكية"""
    if request.method == 'POST':
        # إضافة حساب بنكي جديد
        try:
            data = request.json
            bank_account = BankAccount(
                name=data.get('name'),
                account_number=data.get('account_number'),
                iban=data.get('iban'),
                bank_name=data.get('bank_name'),
                branch_name=data.get('branch_name'),
                swift_code=data.get('swift_code'),
                contact_person=data.get('contact_person'),
                contact_phone=data.get('contact_phone'),
                is_active=data.get('is_active', True),
                balance=data.get('balance', 0),
                notes=data.get('notes', '')
            )
            db.session.add(bank_account)
            db.session.commit()
            return jsonify({'success': True, 'id': bank_account.id, 'message': 'تم إضافة الحساب البنكي بنجاح'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400
    
    # الحصول على قائمة الحسابات البنكية
    bank_accounts = BankAccount.query.all()
    accounts_list = [{
        'id': account.id,
        'name': account.name,
        'account_number': account.account_number,
        'iban': account.iban,
        'bank_name': account.bank_name,
        'balance': account.current_balance,
        'is_active': account.is_active
    } for account in bank_accounts]
    
    return jsonify({'success': True, 'accounts': accounts_list})

@app.route('/api/bank-accounts/<int:account_id>', methods=['GET', 'PUT', 'DELETE'])
def api_bank_account(account_id):
    """واجهة برمجية للعمليات على حساب بنكي محدد"""
    account = BankAccount.query.get_or_404(account_id)
    
    if request.method == 'GET':
        # إرجاع تفاصيل الحساب البنكي
        account_data = {
            'id': account.id,
            'name': account.name,
            'account_number': account.account_number,
            'iban': account.iban,
            'bank_name': account.bank_name,
            'branch_name': account.branch_name,
            'swift_code': account.swift_code,
            'contact_person': account.contact_person,
            'contact_phone': account.contact_phone,
            'is_active': account.is_active,
            'balance': account.balance,
            'notes': account.notes,
            'created_at': account.created_at.strftime('%Y-%m-%d %H:%M:%S') if account.created_at else None,
            'updated_at': account.updated_at.strftime('%Y-%m-%d %H:%M:%S') if account.updated_at else None
        }
        return jsonify({'success': True, 'account': account_data})
    
    elif request.method == 'PUT':
        # تحديث بيانات الحساب البنكي
        try:
            data = request.json
            account.name = data.get('name', account.name)
            account.account_number = data.get('account_number', account.account_number)
            account.iban = data.get('iban', account.iban)
            account.bank_name = data.get('bank_name', account.bank_name)
            account.branch_name = data.get('branch_name', account.branch_name)
            account.swift_code = data.get('swift_code', account.swift_code)
            account.contact_person = data.get('contact_person', account.contact_person)
            account.contact_phone = data.get('contact_phone', account.contact_phone)
            account.is_active = data.get('is_active', account.is_active)
            account.notes = data.get('notes', account.notes)
            
            if 'balance' in data:
                # إذا تم تحديث الرصيد، يمكن إضافة سجل حركة
                new_balance = float(data.get('balance'))
                if new_balance != account.balance:
                    # إنشاء سجل حركة (في المستقبل)
                    pass
                account.balance = new_balance
            
            account.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify({'success': True, 'message': 'تم تحديث الحساب البنكي بنجاح'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400
    
    elif request.method == 'DELETE':
        # حذف الحساب البنكي
        try:
            # قبل الحذف، نتحقق من عدم وجود حركات مرتبطة بالحساب
            # في المستقبل سيتم إضافة هذا التحقق
            
            db.session.delete(account)
            db.session.commit()
            return jsonify({'success': True, 'message': 'تم حذف الحساب البنكي بنجاح'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/cash-registers', methods=['GET', 'POST'])
def api_cash_registers():
    """واجهة برمجية لإدارة الصناديق النقدية"""
    if request.method == 'POST':
        # إضافة صندوق نقدي جديد
        try:
            data = request.json
            cash_register = CashRegister(
                name=data.get('name'),
                location=data.get('location'),
                responsible_person=data.get('responsible_person'),
                is_main_register=data.get('is_main_register', False),
                is_active=data.get('is_active', True),
                balance=data.get('balance', 0),
                notes=data.get('notes', '')
            )
            
            # إذا كان هذا هو الصندوق الرئيسي، نجعل الصناديق الأخرى ليست رئيسية
            if cash_register.is_main_register:
                for register in CashRegister.query.filter_by(is_main_register=True).all():
                    register.is_main_register = False
            
            db.session.add(cash_register)
            db.session.commit()
            return jsonify({'success': True, 'id': cash_register.id, 'message': 'تم إضافة الصندوق النقدي بنجاح'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400
    
    # الحصول على قائمة الصناديق النقدية
    cash_registers = CashRegister.query.all()
    registers_list = [{
        'id': register.id,
        'name': register.name,
        'location': register.location,
        'responsible_person': register.responsible_person,
        'is_main_register': register.is_main_register,
        'balance': register.balance,
        'is_active': register.is_active
    } for register in cash_registers]
    
    return jsonify({'success': True, 'registers': registers_list})

@app.route('/api/cash-registers/<int:register_id>', methods=['GET', 'PUT', 'DELETE'])
def api_cash_register(register_id):
    """واجهة برمجية للعمليات على صندوق نقدي محدد"""
    register = CashRegister.query.get_or_404(register_id)
    
    if request.method == 'GET':
        # إرجاع تفاصيل الصندوق النقدي
        register_data = {
            'id': register.id,
            'name': register.name,
            'location': register.location,
            'responsible_person': register.responsible_person,
            'is_main_register': register.is_main_register,
            'is_active': register.is_active,
            'balance': register.balance,
            'notes': register.notes,
            'created_at': register.created_at.strftime('%Y-%m-%d %H:%M:%S') if register.created_at else None,
            'updated_at': register.updated_at.strftime('%Y-%m-%d %H:%M:%S') if register.updated_at else None
        }
        return jsonify({'success': True, 'register': register_data})
    
    elif request.method == 'PUT':
        # تحديث بيانات الصندوق النقدي
        try:
            data = request.json
            register.name = data.get('name', register.name)
            register.location = data.get('location', register.location)
            register.responsible_person = data.get('responsible_person', register.responsible_person)
            
            # التحقق من حالة الصندوق الرئيسي
            new_is_main = data.get('is_main_register', register.is_main_register)
            if new_is_main and not register.is_main_register:
                # إذا تم تعيين هذا الصندوق كرئيسي، نقوم بإلغاء الصناديق الرئيسية الأخرى
                for other_register in CashRegister.query.filter_by(is_main_register=True).all():
                    if other_register.id != register.id:
                        other_register.is_main_register = False
            
            register.is_main_register = new_is_main
            register.is_active = data.get('is_active', register.is_active)
            register.notes = data.get('notes', register.notes)
            
            if 'balance' in data:
                # إذا تم تحديث الرصيد، يمكن إضافة سجل حركة
                new_balance = float(data.get('balance'))
                if new_balance != register.balance:
                    # إنشاء سجل حركة (في المستقبل)
                    pass
                register.balance = new_balance
            
            register.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify({'success': True, 'message': 'تم تحديث الصندوق النقدي بنجاح'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400
    
    elif request.method == 'DELETE':
        # حذف الصندوق النقدي
        try:
            # قبل الحذف، نتحقق من عدم وجود حركات مرتبطة بالصندوق
            # في المستقبل سيتم إضافة هذا التحقق
            
            db.session.delete(register)
            db.session.commit()
            return jsonify({'success': True, 'message': 'تم حذف الصندوق النقدي بنجاح'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/deposit-money', methods=['POST'])
def api_deposit_money():
    """واجهة برمجية لإيداع المال في الحسابات والصناديق"""
    try:
        data = request.json
        account_type = data.get('account_type')  # 'bank' or 'cash'
        account_id = data.get('account_id', type=int)
        amount = data.get('amount', type=float)
        description = data.get('description', '')
        reference = data.get('reference', '')
        
        # الحصول على معرف المستخدم (إذا كان متاحاً)
        user_id = None
        if current_user.is_authenticated:
            user_id = current_user.id
        
        # التحقق من صحة البيانات
        if not account_type or not account_id or not amount:
            return jsonify({'success': False, 'message': 'يرجى توفير جميع البيانات المطلوبة'}), 400
        
        if amount <= 0:
            return jsonify({'success': False, 'message': 'يجب أن يكون المبلغ أكبر من صفر'}), 400
        
        # الحصول على الحساب
        account = None
        if account_type == 'bank':
            account = BankAccount.query.get(account_id)
        elif account_type == 'cash':
            account = CashRegister.query.get(account_id)
        
        if not account:
            return jsonify({'success': False, 'message': 'الحساب غير موجود'}), 404
        
        # إجراء الإيداع
        previous_balance = account.balance
        account.balance += amount
        
        # تحديث تاريخ التحديث
        account.updated_at = datetime.utcnow()
        
        # إنشاء حركة إيداع
        transaction = AccountTransaction(
            transaction_type='deposit',
            amount=amount,
            balance_after=account.balance,
            source_type=account_type,
            source_id=account_id,
            description=description or 'إيداع نقدي',
            reference=reference,
            user_id=user_id,
            transaction_date=datetime.utcnow()
        )
        
        # إضافة الحركة إلى قاعدة البيانات
        db.session.add(transaction)
        
        # حفظ التغييرات
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'تم الإيداع بنجاح',
            'previous_balance': previous_balance,
            'new_balance': account.balance,
            'transaction_id': transaction.id
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/withdraw-money', methods=['POST'])
def api_withdraw_money():
    """واجهة برمجية لسحب المال من الحسابات والصناديق"""
    try:
        data = request.json
        account_type = data.get('account_type')  # 'bank' or 'cash'
        account_id = data.get('account_id', type=int)
        amount = data.get('amount', type=float)
        description = data.get('description', '')
        reference = data.get('reference', '')
        
        # الحصول على معرف المستخدم (إذا كان متاحاً)
        user_id = None
        if current_user.is_authenticated:
            user_id = current_user.id
        
        # التحقق من صحة البيانات
        if not account_type or not account_id or not amount:
            return jsonify({'success': False, 'message': 'يرجى توفير جميع البيانات المطلوبة'}), 400
        
        if amount <= 0:
            return jsonify({'success': False, 'message': 'يجب أن يكون المبلغ أكبر من صفر'}), 400
        
        # الحصول على الحساب
        account = None
        if account_type == 'bank':
            account = BankAccount.query.get(account_id)
        elif account_type == 'cash':
            account = CashRegister.query.get(account_id)
        
        if not account:
            return jsonify({'success': False, 'message': 'الحساب غير موجود'}), 404
        
        # التحقق من الرصيد الكافي
        if account.balance < amount:
            return jsonify({'success': False, 'message': 'الرصيد غير كافٍ للسحب'}), 400
        
        # إجراء السحب
        previous_balance = account.balance
        account.balance -= amount
        
        # تحديث تاريخ التحديث
        account.updated_at = datetime.utcnow()
        
        # إنشاء حركة سحب
        transaction = AccountTransaction(
            transaction_type='withdraw',
            amount=-amount,  # قيمة سالبة لأنها سحب
            balance_after=account.balance,
            source_type=account_type,
            source_id=account_id,
            description=description or 'سحب نقدي',
            reference=reference,
            user_id=user_id,
            transaction_date=datetime.utcnow()
        )
        
        # إضافة الحركة إلى قاعدة البيانات
        db.session.add(transaction)
        
        # حفظ التغييرات
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'تم السحب بنجاح',
            'previous_balance': previous_balance,
            'new_balance': account.balance,
            'transaction_id': transaction.id
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/transfer-money', methods=['POST'])
def api_transfer_money():
    """واجهة برمجية للتحويل بين الحسابات والصناديق"""
    try:
        data = request.json
        source_type = data.get('source_type') # 'bank' or 'cash'
        source_id = data.get('source_id', type=int)
        destination_type = data.get('destination_type') # 'bank' or 'cash'
        destination_id = data.get('destination_id', type=int)
        amount = data.get('amount', type=float)
        description = data.get('description', '')
        reference = data.get('reference', '')
        
        # الحصول على معرف المستخدم (إذا كان متاحاً)
        user_id = None
        if current_user.is_authenticated:
            user_id = current_user.id
        
        # التحقق من صحة البيانات
        if not source_type or not source_id or not destination_type or not destination_id or not amount:
            return jsonify({'success': False, 'message': 'يرجى توفير جميع البيانات المطلوبة'}), 400
        
        if source_type == destination_type and source_id == destination_id:
            return jsonify({'success': False, 'message': 'لا يمكن التحويل إلى نفس الحساب'}), 400
        
        if amount <= 0:
            return jsonify({'success': False, 'message': 'يجب أن يكون المبلغ أكبر من صفر'}), 400
        
        # الحصول على الحساب المصدر
        source = None
        if source_type == 'bank':
            source = BankAccount.query.get(source_id)
        elif source_type == 'cash':
            source = CashRegister.query.get(source_id)
        
        if not source:
            return jsonify({'success': False, 'message': 'الحساب المصدر غير موجود'}), 404
        
        # الحصول على الحساب الوجهة
        destination = None
        if destination_type == 'bank':
            destination = BankAccount.query.get(destination_id)
        elif destination_type == 'cash':
            destination = CashRegister.query.get(destination_id)
        
        if not destination:
            return jsonify({'success': False, 'message': 'الحساب الوجهة غير موجود'}), 404
        
        # التحقق من الرصيد الكافي
        if source.balance < amount:
            return jsonify({'success': False, 'message': 'الرصيد غير كافٍ للتحويل'}), 400
        
        # إجراء التحويل
        source.balance -= amount
        destination.balance += amount
        
        # تحديث تاريخ التحديث
        source.updated_at = datetime.utcnow()
        destination.updated_at = datetime.utcnow()
        
        # إنشاء حركة سحب من المصدر
        source_transaction = AccountTransaction(
            transaction_type='transfer_out',
            amount=-amount,  # قيمة سالبة لأنها سحب
            balance_after=source.balance,
            source_type=source_type,
            source_id=source_id,
            destination_type=destination_type,
            destination_id=destination_id,
            description=description or 'تحويل إلى حساب آخر',
            reference=reference,
            user_id=user_id,
            transaction_date=datetime.utcnow()
        )
        
        # إنشاء حركة إيداع للوجهة
        destination_transaction = AccountTransaction(
            transaction_type='transfer_in',
            amount=amount,  # قيمة موجبة لأنها إيداع
            balance_after=destination.balance,
            source_type=source_type,
            source_id=source_id,
            destination_type=destination_type,
            destination_id=destination_id,
            description=description or 'تحويل من حساب آخر',
            reference=reference,
            user_id=user_id,
            transaction_date=datetime.utcnow()
        )
        
        # إضافة الحركات إلى قاعدة البيانات
        db.session.add(source_transaction)
        db.session.add(destination_transaction)
        
        # حفظ التغييرات
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'تم التحويل بنجاح',
            'source_balance': source.balance,
            'destination_balance': destination.balance,
            'transaction_id': source_transaction.id
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/payment-vouchers')
def payment_vouchers():
    return render_template('payment-vouchers.html')

@app.route('/receipt-vouchers')
def receipt_vouchers():
    return render_template('receipt-vouchers.html')

@app.route('/receipts')
def receipts():
    return render_template('receipts.html')

@app.route('/users')
def users():
    return render_template('users.html')

@app.route('/currencies')
def currencies():
    return render_template('currencies.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/budget-profits')
def budget_profits():
    return render_template('budget-profits.html')

@app.route('/cash-journal')
def cash_journal():
    """صفحة عرض تقارير حركات الصناديق النقدية"""
    # الحصول على حركات الصناديق النقدية
    cash_transactions = AccountTransaction.query.filter_by(source_type='cash').order_by(AccountTransaction.transaction_date.desc()).limit(100).all()
    
    # البحث عن أسماء الصناديق النقدية
    cash_ids = set()
    for transaction in cash_transactions:
        cash_ids.add(transaction.source_id)
        if transaction.destination_type == 'cash':
            cash_ids.add(transaction.destination_id)
    
    cash_registers = CashRegister.query.filter(CashRegister.id.in_(cash_ids)).all() if cash_ids else []
    cash_map = {register.id: register.name for register in cash_registers}
    
    # البحث عن أسماء الحسابات البنكية
    bank_ids = set()
    for transaction in cash_transactions:
        if transaction.destination_type == 'bank':
            bank_ids.add(transaction.destination_id)
    
    bank_accounts = BankAccount.query.filter(BankAccount.id.in_(bank_ids)).all() if bank_ids else []
    bank_map = {account.id: account.name for account in bank_accounts}
    
    return render_template('cash-journal.html', 
                           transactions=cash_transactions,
                           cash_map=cash_map,
                           bank_map=bank_map)

@app.route('/bank-journal')
def bank_journal():
    """صفحة عرض تقارير حركات الحسابات البنكية"""
    # الحصول على حركات الحسابات البنكية
    bank_transactions = AccountTransaction.query.filter_by(source_type='bank').order_by(AccountTransaction.transaction_date.desc()).limit(100).all()
    
    # البحث عن أسماء الحسابات البنكية
    bank_ids = set()
    for transaction in bank_transactions:
        bank_ids.add(transaction.source_id)
        if transaction.destination_type == 'bank':
            bank_ids.add(transaction.destination_id)
    
    bank_accounts = BankAccount.query.filter(BankAccount.id.in_(bank_ids)).all() if bank_ids else []
    bank_map = {account.id: account.name for account in bank_accounts}
    
    # البحث عن أسماء الصناديق النقدية
    cash_ids = set()
    for transaction in bank_transactions:
        if transaction.destination_type == 'cash':
            cash_ids.add(transaction.destination_id)
    
    cash_registers = CashRegister.query.filter(CashRegister.id.in_(cash_ids)).all() if cash_ids else []
    cash_map = {register.id: register.name for register in cash_registers}
    
    return render_template('bank-journal.html', 
                           transactions=bank_transactions,
                           bank_map=bank_map,
                           cash_map=cash_map)

@app.route('/countries-cities')
def countries_cities():
    return render_template('countries-cities.html')

@app.route('/id-types')
def id_types():
    return render_template('id-types.html')

@app.route('/daily-journal')
def daily_journal():
    return render_template('daily-journal.html')

@app.route('/employees')
def employees():
    return render_template('employees.html')

@app.route('/account-statements')
def account_statements():
    """صفحة عرض كشوف الحسابات"""
    bank_accounts = BankAccount.query.all()
    cash_registers = CashRegister.query.all()
    
    # تجميع جميع الحسابات
    accounts = []
    
    for bank in bank_accounts:
        accounts.append({
            'id': bank.id,
            'name': bank.bank_name,
            'type': 'bank',
            'balance': bank.current_balance
        })
    
    for cash in cash_registers:
        accounts.append({
            'id': cash.id,
            'name': cash.name,
            'type': 'cash',
            'balance': cash.balance
        })
    
    return render_template('account-statements.html', accounts=accounts)

@app.route('/api/account-transactions')
def api_account_transactions():
    """واجهة برمجية لاسترجاع حركات حساب معين"""
    account_type = request.args.get('account_type')  # 'bank' or 'cash'
    account_id = request.args.get('account_id', type=int)
    
    if not account_type or not account_id:
        return jsonify({'success': False, 'message': 'يرجى توفير جميع البيانات المطلوبة'}), 400
    
    # التحقق من وجود الحساب
    account = None
    if account_type == 'bank':
        account = BankAccount.query.get(account_id)
    elif account_type == 'cash':
        account = CashRegister.query.get(account_id)
    
    if not account:
        return jsonify({'success': False, 'message': 'الحساب غير موجود'}), 404
    
    # البحث عن حركات الحساب
    transactions = AccountTransaction.query.filter(
        (
            (AccountTransaction.source_type == account_type) & 
            (AccountTransaction.source_id == account_id)
        ) | (
            (AccountTransaction.destination_type == account_type) & 
            (AccountTransaction.destination_id == account_id)
        )
    ).order_by(AccountTransaction.transaction_date.desc()).all()
    
    # تحويل الحركات إلى قاموس JSON
    result = []
    bank_map = {}
    cash_map = {}
    
    # جمع الجهات ذات الصلة
    related_banks = set()
    related_cash = set()
    
    for t in transactions:
        if t.source_type == 'bank' and t.source_id != account_id:
            related_banks.add(t.source_id)
        if t.destination_type == 'bank' and t.destination_id != account_id:
            related_banks.add(t.destination_id)
        if t.source_type == 'cash' and t.source_id != account_id:
            related_cash.add(t.source_id)
        if t.destination_type == 'cash' and t.destination_id != account_id:
            related_cash.add(t.destination_id)
    
    # الحصول على أسماء الحسابات ذات الصلة
    if related_banks:
        banks = BankAccount.query.filter(BankAccount.id.in_(related_banks)).all()
        bank_map = {b.id: b.name for b in banks}
    
    if related_cash:
        cash_regs = CashRegister.query.filter(CashRegister.id.in_(related_cash)).all()
        cash_map = {c.id: c.name for c in cash_regs}
    
    for t in transactions:
        # تحديد نوع الحركة من منظور هذا الحساب
        transaction_direction = ''
        other_party_name = ''
        
        if t.source_type == account_type and t.source_id == account_id:
            # حركة صادرة من هذا الحساب
            if t.destination_type == 'bank':
                other_party_name = bank_map.get(t.destination_id, 'حساب بنكي')
            elif t.destination_type == 'cash':
                other_party_name = cash_map.get(t.destination_id, 'صندوق نقدي')
            
            if t.transaction_type == 'withdraw':
                transaction_direction = 'سحب'
            elif t.transaction_type == 'transfer_out':
                transaction_direction = 'تحويل إلى ' + other_party_name
            else:
                transaction_direction = t.transaction_type
        
        elif t.destination_type == account_type and t.destination_id == account_id:
            # حركة واردة إلى هذا الحساب
            if t.source_type == 'bank':
                other_party_name = bank_map.get(t.source_id, 'حساب بنكي')
            elif t.source_type == 'cash':
                other_party_name = cash_map.get(t.source_id, 'صندوق نقدي')
            
            if t.transaction_type == 'deposit':
                transaction_direction = 'إيداع'
            elif t.transaction_type == 'transfer_in':
                transaction_direction = 'تحويل من ' + other_party_name
            else:
                transaction_direction = t.transaction_type
        
        # إضافة الحركة إلى النتائج
        result.append({
            'id': t.id,
            'date': t.transaction_date.strftime('%Y-%m-%d %H:%M'),
            'type': transaction_direction,
            'amount': abs(t.amount),  # القيمة المطلقة للمبلغ
            'is_debit': t.amount < 0,  # هل هي حركة سحب
            'balance_after': t.balance_after if t.source_type == account_type and t.source_id == account_id else None,
            'description': t.description,
            'reference': t.reference,
            'other_party': other_party_name
        })
    
    # اختيار الاسم والرصيد بناءً على نوع الحساب
    account_name = account.bank_name if account_type == 'bank' else account.name
    account_balance = account.current_balance if account_type == 'bank' else account.balance
    
    return jsonify({
        'success': True,
        'account': {
            'name': account_name,
            'type': account_type,
            'balance': account_balance
        },
        'transactions': result
    })

@app.route('/financial-settings', methods=['GET', 'POST'])
def financial_settings():
    """صفحة الإعدادات المالية والمحاسبية"""
    # جلب الإعدادات المالية
    settings = FinancialSettings.query.first()
    
    # جلب بيانات الحسابات والفئات والعملات والضرائب والفترات المالية
    currencies = Currency.query.all()
    tax_settings = TaxSettings.query.all()
    account_categories = AccountCategory.query.all()
    accounts = Account.query.all()
    cash_accounts = Account.query.filter_by(is_cash_account=True).all()
    bank_accounts = Account.query.filter_by(is_bank_account=True).all()
    financial_periods = FinancialPeriod.query.all()
    
    # معالجة طلب التحديث (POST)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_general_settings':
            # تحديث الإعدادات العامة
            if not settings:
                settings = FinancialSettings()
                db.session.add(settings)
            
            settings.company_name = request.form.get('company_name')
            # تحويل التاريخ من النص
            try:
                fiscal_year_start = datetime.strptime(request.form.get('fiscal_year_start'), '%d/%m/%Y').date()
                settings.fiscal_year_start = fiscal_year_start
            except:
                pass
            
            settings.base_currency_id = request.form.get('base_currency_id', type=int)
            settings.default_tax_id = request.form.get('default_tax_id', type=int)
            settings.enable_cost_centers = 'enable_cost_centers' in request.form
            settings.enable_budgets = 'enable_budgets' in request.form
            settings.default_cash_account_id = request.form.get('default_cash_account_id', type=int)
            settings.default_bank_account_id = request.form.get('default_bank_account_id', type=int)
            
            db.session.commit()
            flash('تم تحديث الإعدادات المالية بنجاح', 'success')
        
        elif action == 'add_account_category':
            # إضافة فئة حساب جديدة
            category = AccountCategory(
                name=request.form.get('name'),
                code=request.form.get('code'),
                description=request.form.get('description'),
                is_active='is_active' in request.form
            )
            db.session.add(category)
            db.session.commit()
            flash('تم إضافة فئة الحساب بنجاح', 'success')
        
        elif action == 'add_account':
            # إضافة حساب جديد
            account = Account(
                name=request.form.get('name'),
                account_number=request.form.get('account_number'),
                category_id=request.form.get('category_id', type=int),
                account_type=request.form.get('account_type'),
                is_bank_account='is_bank_account' in request.form,
                is_cash_account='is_cash_account' in request.form,
                parent_id=request.form.get('parent_id', type=int) or None,
                balance=request.form.get('balance', type=float, default=0),
                description=request.form.get('description'),
                is_active='is_active' in request.form
            )
            db.session.add(account)
            db.session.commit()
            flash('تم إضافة الحساب بنجاح', 'success')
        
        elif action == 'add_tax_setting':
            # إضافة ضريبة جديدة
            tax = TaxSettings(
                name=request.form.get('name'),
                rate=float(request.form.get('rate', 0)) / 100,  # تحويل النسبة المئوية إلى كسر عشري
                is_default='is_default' in request.form,
                is_active='is_active' in request.form
            )
            # إذا كانت هذه هي الضريبة الافتراضية، قم بإلغاء تفعيل الضرائب الافتراضية الأخرى
            if tax.is_default:
                for t in TaxSettings.query.filter_by(is_default=True).all():
                    t.is_default = False
            
            db.session.add(tax)
            db.session.commit()
            flash('تم إضافة الضريبة بنجاح', 'success')
        
        elif action == 'add_currency':
            # إضافة عملة جديدة
            currency = Currency(
                name=request.form.get('name'),
                code=request.form.get('code'),
                symbol=request.form.get('symbol'),
                exchange_rate=request.form.get('exchange_rate', type=float, default=1.0),
                is_base_currency='is_base_currency' in request.form,
                is_active='is_active' in request.form
            )
            # إذا كانت هذه هي العملة الرئيسية، قم بإلغاء تفعيل العملات الرئيسية الأخرى
            if currency.is_base_currency:
                for c in Currency.query.filter_by(is_base_currency=True).all():
                    c.is_base_currency = False
                # إعادة ضبط سعر الصرف للعملة الرئيسية ليكون 1.0
                currency.exchange_rate = 1.0
            
            db.session.add(currency)
            db.session.commit()
            flash('تم إضافة العملة بنجاح', 'success')
        
        elif action == 'add_fiscal_period':
            # إضافة فترة مالية جديدة
            try:
                start_date = datetime.strptime(request.form.get('start_date'), '%d/%m/%Y').date()
                end_date = datetime.strptime(request.form.get('end_date'), '%d/%m/%Y').date()
                
                period = FinancialPeriod(
                    name=request.form.get('name'),
                    start_date=start_date,
                    end_date=end_date,
                    notes=request.form.get('notes')
                )
                db.session.add(period)
                db.session.commit()
                flash('تم إضافة الفترة المالية بنجاح', 'success')
            except:
                flash('حدث خطأ في تنسيق التاريخ', 'error')
        
        # إعادة توجيه لتجنب إعادة تقديم النموذج
        return redirect(url_for('financial_settings'))
    
    return render_template(
        'financial-settings.html',
        financial_settings=settings,
        currencies=currencies,
        tax_settings=tax_settings,
        account_categories=account_categories,
        accounts=accounts,
        cash_accounts=cash_accounts,
        bank_accounts=bank_accounts,
        financial_periods=financial_periods
    )

# تعديل before_request لإضافة إعدادات النظام لجميع القوالب

@app.before_request
def before_request():
    # تجنب تنفيذ هذا الكود للطلبات الخاصة بالملفات الثابتة
    if not request.path.startswith('/static/'):
        # استرجاع جميع إعدادات النظام
        settings_keys = [
            # إعدادات عامة للنظام
            'system_name', 'system_slogan', 'dashboard_title', 
            'company_name', 'company_cr', 'company_vat', 'company_address',
            'company_phone', 'company_email', 'company_website',
            
            # إعدادات المظهر والألوان
            'primary_color', 'secondary_color', 'sidebar_color', 'text_primary_color',
            'logo_icon', 'rtl_layout', 'font_family', 'enable_animations',
            
            # إعدادات مالية
            'default_currency', 'vat_rate', 'show_vat_in_reports',
            'currency_display_format', 'enable_multi_currency',
            'decimal_places', 'show_amounts_in_words',
            
            # إعدادات التاريخ والوقت
            'date_format', 'time_format', 'use_hijri_dates', 
            'show_both_dates', 'week_start_day', 'timezone',
            
            # إعدادات الإشعارات والتنبيهات
            'show_notifications', 'enable_emails', 'enable_sms',
            'notification_refresh_interval', 'low_stock_threshold',
            'ticket_expiry_alert_days', 'visa_expiry_alert_days',
            
            # إعدادات الطباعة والمستندات
            'invoice_prefix', 'receipt_prefix', 'booking_prefix', 'payment_prefix',
            'invoice_footer_text', 'invoice_terms', 'print_logo_on_documents',
            
            # إعدادات النظام والأمان
            'auto_logout_minutes', 'password_expiry_days', 'password_min_length',
            'enable_audit_log', 'backup_frequency', 'maintenance_mode'
        ]
        
        # تعريف القيم الافتراضية للإعدادات الأساسية
        default_values = {
            'system_name': 'وكالة السفر المتميزة',
            'system_slogan': 'للسفر والسياحة والخدمات',
            'dashboard_title': 'نظام إدارة وكالة السياحة والسفر',
            'primary_color': '#4e73df',
            'secondary_color': '#1cc88a',
            'sidebar_color': '#2c3e50',
            'text_primary_color': '#333333',
            'logo_icon': 'fas fa-plane-departure',
            'use_custom_logo': 'false',
            'custom_logo_url': '',
            'default_currency': 'SAR',
            'rtl_layout': 'true',
            'font_family': 'Tajawal',
            'enable_animations': 'true',
            'dark_mode': 'auto',
            'dark_sidebar': 'true',
            'dark_primary_color': '#375bbb',
            'dark_sidebar_color': '#1a1a2e',
            'dark_text_color': '#e1e1e1',
            'navbar_color': '#ffffff',
            'navbar_text_color': '#333333',
            'navbar_dark_color': '#1e1e1e',
            'navbar_dark_text_color': '#e1e1e1',
            'navbar_fixed': 'true',
            'navbar_transparent': 'false',
            'navbar_shadow': 'true',
            'layout_boxed': 'false',
            'content_width': 'fluid',
            'sidebar_mini': 'false',
            'card_shadow': 'medium',
            'border_radius': 'medium',
            'transitions': 'true',
            'copyright_text': '© 2025 وكالة السفر المتميزة. جميع الحقوق محفوظة.',
            'company_full_name': 'وكالة السفر المتميزة للسياحة والسفر',
            'company_license_number': 'ت.س: 123456789',
            'field_style': 'default',
            'button_style': 'default',
            'input_shadow': 'true',
            'input_rounded': 'medium',
            'table_style': 'bordered',
            'table_hover': 'true',
            'table_striped': 'true',
            'icon_size': 'medium',
            'icon_style': 'regular',
            'icon_color_mode': 'auto'
        }
        
        # تهيئة قاموس الإعدادات
        g.settings = {}
        
        # استرجاع جميع الإعدادات من قاعدة البيانات
        for key in settings_keys:
            # الحصول على قيمة كل إعداد مع قيم افتراضية
            default_value = default_values.get(key, '')
            g.settings[key] = SystemSettings.get_value(key, default_value)

# استخدام context_processor لإتاحة الإعدادات في جميع القوالب
@app.context_processor
def inject_settings():
    if hasattr(g, 'settings'):
        return {'settings': g.settings}
    return {'settings': {}}

@app.route('/system-settings', methods=['GET', 'POST'])
def system_settings():
    # Define default system settings if not exist
    default_settings = {
        # إعدادات عامة للنظام
        'system_name': {
            'value': 'وكالة السفر المتميزة',
            'type': 'text',
            'description': 'اسم النظام الذي يظهر في العنوان والشعار'
        },
        'system_slogan': {
            'value': 'للسفر والسياحة والخدمات',
            'type': 'text',
            'description': 'شعار النظام النصي'
        },
        'dashboard_title': {
            'value': 'نظام إدارة وكالة السياحة والسفر',
            'type': 'text',
            'description': 'عنوان لوحة التحكم'
        },
        'company_name': {
            'value': 'شركة السفر والسياحة',
            'type': 'text',
            'description': 'اسم الشركة الرسمي للعرض في التقارير والمستندات'
        },
        'company_cr': {
            'value': '',
            'type': 'text',
            'description': 'رقم السجل التجاري للشركة'
        },
        'company_vat': {
            'value': '',
            'type': 'text',
            'description': 'الرقم الضريبي للشركة'
        },
        'company_address': {
            'value': 'المملكة العربية السعودية',
            'type': 'text',
            'description': 'عنوان الشركة'
        },
        'company_phone': {
            'value': '',
            'type': 'text',
            'description': 'رقم هاتف الشركة'
        },
        'company_email': {
            'value': '',
            'type': 'text',
            'description': 'البريد الإلكتروني للشركة'
        },
        'company_website': {
            'value': '',
            'type': 'text',
            'description': 'موقع الويب للشركة'
        },
        
        # إعدادات المظهر والألوان
        'primary_color': {
            'value': '#4e73df',
            'type': 'color',
            'description': 'اللون الرئيسي للنظام'
        },
        'secondary_color': {
            'value': '#1cc88a',
            'type': 'color',
            'description': 'اللون الثانوي للنظام'
        },
        'sidebar_color': {
            'value': '#2c3e50',
            'type': 'color',
            'description': 'لون القائمة الجانبية'
        },
        'text_primary_color': {
            'value': '#333333',
            'type': 'color',
            'description': 'لون النص الرئيسي'
        },
        'logo_icon': {
            'value': 'fas fa-plane-departure',
            'type': 'icon',
            'description': 'الأيقونة المستخدمة في الشعار (Font Awesome)'
        },
        'use_custom_logo': {
            'value': 'false',
            'type': 'boolean',
            'description': 'استخدام شعار مخصص بدلاً من الأيقونة'
        },
        'custom_logo_url': {
            'value': '',
            'type': 'text',
            'description': 'رابط الشعار المخصص (إذا كان use_custom_logo مفعل)'
        },
        'rtl_layout': {
            'value': 'true',
            'type': 'boolean',
            'description': 'استخدام تخطيط من اليمين إلى اليسار (RTL)'
        },
        'font_family': {
            'value': 'Tajawal',
            'type': 'select',
            'description': 'الخط المستخدم في النظام',
            'options': 'Tajawal,Cairo,Almarai,Amiri,Scheherazade'
        },
        'enable_animations': {
            'value': 'true',
            'type': 'boolean',
            'description': 'تفعيل التأثيرات الحركية في الواجهة'
        },
        'dark_mode': {
            'value': 'auto',
            'type': 'select',
            'description': 'وضع العرض (ليلي/نهاري)',
            'options': 'light,dark,auto'
        },
        'dark_sidebar': {
            'value': 'true',
            'type': 'boolean',
            'description': 'استخدام خلفية داكنة للقائمة الجانبية'
        },
        'dark_primary_color': {
            'value': '#375bbb',
            'type': 'color',
            'description': 'اللون الرئيسي في الوضع الليلي'
        },
        'dark_sidebar_color': {
            'value': '#1a1a2e',
            'type': 'color',
            'description': 'لون القائمة الجانبية في الوضع الليلي'
        },
        'dark_text_color': {
            'value': '#e1e1e1',
            'type': 'color',
            'description': 'لون النص في الوضع الليلي'
        },
        'navbar_color': {
            'value': '#ffffff',
            'type': 'color',
            'description': 'لون خلفية شريط التنقل العلوي'
        },
        'navbar_text_color': {
            'value': '#333333',
            'type': 'color',
            'description': 'لون النص في شريط التنقل العلوي'
        },
        'navbar_dark_color': {
            'value': '#1e1e1e',
            'type': 'color',
            'description': 'لون خلفية شريط التنقل في الوضع الليلي'
        },
        'navbar_dark_text_color': {
            'value': '#e1e1e1',
            'type': 'color',
            'description': 'لون النص في شريط التنقل (الوضع الليلي)'
        },
        'navbar_fixed': {
            'value': 'true',
            'type': 'boolean',
            'description': 'تثبيت شريط التنقل العلوي عند التمرير'
        },
        'navbar_transparent': {
            'value': 'false',
            'type': 'boolean',
            'description': 'شريط تنقل شفاف'
        },
        'navbar_shadow': {
            'value': 'true',
            'type': 'boolean',
            'description': 'إظهار ظل لشريط التنقل'
        },
        'layout_boxed': {
            'value': 'false',
            'type': 'boolean',
            'description': 'استخدام تخطيط مضغوط للشاشة'
        },
        'content_width': {
            'value': 'fluid',
            'type': 'select',
            'description': 'عرض محتوى الصفحة',
            'options': 'fluid,fixed'
        },
        'sidebar_mini': {
            'value': 'false',
            'type': 'boolean',
            'description': 'استخدام القائمة الجانبية المصغرة'
        },
        'card_shadow': {
            'value': 'medium',
            'type': 'select',
            'description': 'حجم ظل البطاقات',
            'options': 'none,small,medium,large'
        },
        'border_radius': {
            'value': 'medium',
            'type': 'select',
            'description': 'مقدار انحناء الحواف',
            'options': 'none,small,medium,large'
        },
        'transitions': {
            'value': 'true',
            'type': 'boolean',
            'description': 'تفعيل التأثيرات الحركية'
        },
        
        # إعدادات الحقول والأزرار والجداول
        'field_style': {
            'value': 'default',
            'type': 'select',
            'description': 'نمط الحقول والمدخلات',
            'options': 'default,flat,outline'
        },
        'button_style': {
            'value': 'default',
            'type': 'select',
            'description': 'نمط الأزرار',
            'options': 'default,flat,gradient,outline'
        },
        'input_shadow': {
            'value': 'true',
            'type': 'boolean',
            'description': 'إضافة ظلال للحقول عند التركيز'
        },
        'input_rounded': {
            'value': 'medium',
            'type': 'select',
            'description': 'مقدار انحناء حواف الحقول',
            'options': 'none,small,medium,large,pill'
        },
        'table_style': {
            'value': 'bordered',
            'type': 'select',
            'description': 'نمط الجداول',
            'options': 'default,bordered,borderless,condensed'
        },
        'table_hover': {
            'value': 'true',
            'type': 'boolean',
            'description': 'تأثير التلميح عند المرور على صفوف الجداول'
        },
        'table_striped': {
            'value': 'true',
            'type': 'boolean',
            'description': 'لون الصفوف المتناوب في الجداول'
        },
        'icon_size': {
            'value': 'medium',
            'type': 'select',
            'description': 'حجم الأيقونات',
            'options': 'small,medium,large'
        },
        'icon_style': {
            'value': 'regular',
            'type': 'select',
            'description': 'نمط الأيقونات',
            'options': 'regular,solid,light,duotone'
        },
        'icon_color_mode': {
            'value': 'auto',
            'type': 'select',
            'description': 'وضع لون الأيقونات',
            'options': 'auto,custom,inherit'
        },
        
        # إعدادات مالية
        'default_currency': {
            'value': 'SAR',
            'type': 'select',
            'description': 'العملة الافتراضية للنظام',
            'options': 'SAR,USD,EUR,YER,AED,QAR,BHD,KWD,OMR,JOD,EGP'
        },
        'vat_rate': {
            'value': '15',
            'type': 'text',
            'description': 'نسبة ضريبة القيمة المضافة (%)'
        },
        'show_vat_in_reports': {
            'value': 'true',
            'type': 'boolean',
            'description': 'إظهار ضريبة القيمة المضافة في التقارير'
        },
        'currency_display_format': {
            'value': 'symbol_after',
            'type': 'select',
            'description': 'طريقة عرض العملات',
            'options': 'symbol_after,symbol_before,code_after,code_before'
        },
        'enable_multi_currency': {
            'value': 'true',
            'type': 'boolean',
            'description': 'تفعيل دعم العملات المتعددة'
        },
        'decimal_places': {
            'value': '2',
            'type': 'select',
            'description': 'عدد الخانات العشرية في عرض المبالغ',
            'options': '0,1,2,3'
        },
        'show_amounts_in_words': {
            'value': 'true',
            'type': 'boolean',
            'description': 'عرض المبالغ كتابة بالحروف العربية'
        },
                
        # إعدادات التاريخ والوقت
        'date_format': {
            'value': 'DD/MM/YYYY',
            'type': 'select',
            'description': 'صيغة عرض التاريخ في النظام',
            'options': 'DD/MM/YYYY,YYYY/MM/DD,DD-MM-YYYY,YYYY-MM-DD,DD MMMM, YYYY'
        },
        'time_format': {
            'value': 'HH:mm',
            'type': 'select',
            'description': 'صيغة عرض الوقت في النظام',
            'options': 'HH:mm,HH:mm:ss,hh:mm A,hh:mm:ss A'
        },
        'use_hijri_dates': {
            'value': 'false',
            'type': 'boolean',
            'description': 'استخدام التاريخ الهجري بدلاً من الميلادي'
        },
        'show_both_dates': {
            'value': 'false',
            'type': 'boolean',
            'description': 'عرض التاريخ الهجري والميلادي معاً'
        },
        'week_start_day': {
            'value': 'saturday',
            'type': 'select',
            'description': 'اليوم الأول في الأسبوع',
            'options': 'saturday,sunday,monday'
        },
        'timezone': {
            'value': 'Asia/Riyadh',
            'type': 'select',
            'description': 'المنطقة الزمنية',
            'options': 'Asia/Riyadh,Asia/Jeddah,Asia/Dubai,Asia/Kuwait,Asia/Qatar,Asia/Bahrain,Asia/Aden,Asia/Damascus,Asia/Amman,Asia/Cairo'
        },
        
        # إعدادات الإشعارات والتنبيهات
        'show_notifications': {
            'value': 'true',
            'type': 'boolean',
            'description': 'إظهار الإشعارات في الشريط العلوي'
        },
        'enable_emails': {
            'value': 'false',
            'type': 'boolean',
            'description': 'تفعيل إرسال الإشعارات عبر البريد الإلكتروني'
        },
        'enable_sms': {
            'value': 'false',
            'type': 'boolean',
            'description': 'تفعيل إرسال الإشعارات عبر الرسائل القصيرة'
        },
        'notification_refresh_interval': {
            'value': '60',
            'type': 'select',
            'description': 'الفاصل الزمني لتحديث الإشعارات (بالثواني)',
            'options': '30,60,120,300,600'
        },
        'low_stock_threshold': {
            'value': '5',
            'type': 'text',
            'description': 'عتبة التنبيه للمخزون المنخفض'
        },
        'ticket_expiry_alert_days': {
            'value': '3',
            'type': 'text',
            'description': 'عدد أيام التنبيه قبل انتهاء التذاكر'
        },
        'visa_expiry_alert_days': {
            'value': '7',
            'type': 'text',
            'description': 'عدد أيام التنبيه قبل انتهاء التأشيرات'
        },
        
        # إعدادات الطباعة والمستندات
        'invoice_prefix': {
            'value': 'INV-',
            'type': 'text',
            'description': 'بادئة رقم الفاتورة'
        },
        'receipt_prefix': {
            'value': 'REC-',
            'type': 'text',
            'description': 'بادئة رقم الإيصال'
        },
        'booking_prefix': {
            'value': 'BK-',
            'type': 'text',
            'description': 'بادئة رقم الحجز'
        },
        'payment_prefix': {
            'value': 'PAY-',
            'type': 'text',
            'description': 'بادئة رقم سند الصرف'
        },
        'invoice_footer_text': {
            'value': 'شكراً لاختياركم وكالة السفر المتميزة',
            'type': 'text',
            'description': 'النص الظاهر في أسفل الفاتورة'
        },
        'invoice_terms': {
            'value': 'تطبق الشروط والأحكام',
            'type': 'textarea',
            'description': 'شروط وأحكام الفاتورة'
        },
        'print_logo_on_documents': {
            'value': 'true',
            'type': 'boolean',
            'description': 'طباعة شعار الشركة على المستندات'
        },
        
        # إعدادات النظام والأمان
        'auto_logout_minutes': {
            'value': '30',
            'type': 'select',
            'description': 'وقت الخروج التلقائي بعد عدم النشاط (بالدقائق)',
            'options': '15,30,60,120,240,0'
        },
        'password_expiry_days': {
            'value': '90',
            'type': 'text',
            'description': 'عدد أيام انتهاء صلاحية كلمة المرور (0 للتعطيل)'
        },
        'password_min_length': {
            'value': '8',
            'type': 'text',
            'description': 'الحد الأدنى لطول كلمة المرور'
        },
        'enable_audit_log': {
            'value': 'true',
            'type': 'boolean',
            'description': 'تفعيل سجل التدقيق لمراقبة النشاطات'
        },
        'backup_frequency': {
            'value': 'daily',
            'type': 'select',
            'description': 'تكرار النسخ الاحتياطي التلقائي',
            'options': 'daily,weekly,monthly,manual'
        },
        'maintenance_mode': {
            'value': 'false',
            'type': 'boolean',
            'description': 'تفعيل وضع الصيانة (يمنع دخول المستخدمين غير المدراء)'
        }
    }
    
    # Initialize settings if they don't exist
    for key, data in default_settings.items():
        setting = SystemSettings.query.filter_by(setting_key=key).first()
        if not setting:
            SystemSettings.set_value(
                key=key,
                value=data['value'],
                setting_type=data['type'],
                description=data['description']
            )
    
    # Handle form submission
    if request.method == 'POST':
        try:
            # Gather all form data
            for key in default_settings.keys():
                if key in request.form:
                    value = request.form.get(key, default_settings[key]['value'])
                    setting_type = default_settings[key]['type']
                    description = default_settings[key]['description']
                    
                    # Update the setting
                    SystemSettings.set_value(
                        key=key,
                        value=value,
                        setting_type=setting_type,
                        description=description
                    )
            
            # Handle file uploads if needed
            # if 'logo_file' in request.files:
            #     file = request.files['logo_file']
            #     if file and file.filename:
            #         # Save file logic here
            
            flash('تم حفظ الإعدادات بنجاح', 'success')
            return redirect(url_for('system_settings'))
        except Exception as e:
            flash(f'حدث خطأ أثناء حفظ الإعدادات: {str(e)}', 'danger')
    
    # Get current settings to display in the form
    settings = {}
    for key in default_settings.keys():
        settings[key] = SystemSettings.get_value(key, default_settings[key]['value'])
    
    # Available icon options for logo
    icon_options = [
        'fas fa-plane-departure',
        'fas fa-plane',
        'fas fa-globe-asia',
        'fas fa-map-marked-alt',
        'fas fa-building',
        'fas fa-hotel',
        'fas fa-passport',
        'fas fa-suitcase-rolling',
        'fas fa-bus',
        'fas fa-car',
        'fas fa-ship',
        'fas fa-umbrella-beach'
    ]
    
    return render_template('system-settings.html', 
                         settings=settings,
                         icon_options=icon_options,
                         setting_descriptions=default_settings)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
