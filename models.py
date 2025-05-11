from datetime import datetime, date
from flask_login import UserMixin
from app import db

# تعريف نموذج المستخدم
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

# نموذج العملاء
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

# نموذج شركات النقل
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
    
    # العلاقات
    bus_routes = db.relationship('BusRoute', backref='company', lazy=True)

# نموذج الدول
class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    cities = db.relationship('City', backref='country_rel', lazy=True)

# نموذج المدن
class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات - defined separately to avoid circular imports
    departures = db.relationship('BusRoute', foreign_keys='BusRoute.departure_city_id', backref='departure_city', lazy=True)
    destinations = db.relationship('BusRoute', foreign_keys='BusRoute.destination_city_id', backref='destination_city', lazy=True)

# نموذج مسارات الحافلات
class BusRoute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    departure_city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    destination_city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('transport_company.id'), nullable=False)
    route_code = db.Column(db.String(20))
    distance = db.Column(db.Float)  # بالكيلومتر
    duration = db.Column(db.Integer)  # بالدقائق
    base_price = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    schedules = db.relationship('BusSchedule', backref='route', lazy=True)

# نموذج أنواع الحافلات
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
    price_multiplier = db.Column(db.Float, default=1.0)  # معامل ضرب سعر المسار
    is_active = db.Column(db.Boolean, default=True)
    
    # العلاقات
    schedules = db.relationship('BusSchedule', backref='bus_type', lazy=True)

# نموذج جداول الحافلات
class BusSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('bus_route.id'), nullable=False)
    bus_type_id = db.Column(db.Integer, db.ForeignKey('bus_type.id'), nullable=False)
    departure_time = db.Column(db.Time, nullable=False)
    arrival_time = db.Column(db.Time)
    days_of_week = db.Column(db.String(20))  # مثال: "1,2,3,4,5" للأيام العادية
    price = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    trips = db.relationship('BusTrip', backref='schedule', lazy=True)

# نموذج رحلات الحافلات
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

# نموذج حجوزات الحافلات
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

# نموذج مدفوعات الحجز
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

# نموذج العملات
class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)  # رمز العملة (مثلا: SAR, USD)
    name = db.Column(db.String(100), nullable=False)  # اسم العملة (ريال سعودي، دولار أمريكي)
    symbol = db.Column(db.String(10))  # رمز العملة (﷼، $)
    exchange_rate = db.Column(db.Float, default=1.0)  # سعر الصرف مقابل العملة الأساسية
    is_default = db.Column(db.Boolean, default=False)  # هل هي العملة الافتراضية
    is_active = db.Column(db.Boolean, default=True)  # هل العملة مفعلة
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

# نموذج صناديق النقد
class CashRegister(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # اسم الصندوق
    code = db.Column(db.String(20), unique=True)  # كود الصندوق
    balance = db.Column(db.Float, default=0.0)  # رصيد الصندوق
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'))  # العملة
    is_active = db.Column(db.Boolean, default=True)  # هل الصندوق مفعل
    notes = db.Column(db.Text)  # ملاحظات
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    currency = db.relationship('Currency', foreign_keys=[currency_id])
    
    def __str__(self):
        return self.name

# نموذج الحسابات البنكية
class BankAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String(100), nullable=False)  # اسم البنك
    account_name = db.Column(db.String(100), nullable=False)  # اسم الحساب
    account_number = db.Column(db.String(50), unique=True)  # رقم الحساب
    iban = db.Column(db.String(50), unique=True)  # رقم الآيبان
    swift_code = db.Column(db.String(20))  # كود السويفت
    balance = db.Column(db.Float, default=0.0)  # رصيد الحساب
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'))  # العملة
    is_active = db.Column(db.Boolean, default=True)  # هل الحساب مفعل
    notes = db.Column(db.Text)  # ملاحظات
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    currency = db.relationship('Currency', foreign_keys=[currency_id])
    
    def __str__(self):
        return f"{self.bank_name} - {self.account_name}"

# نموذج دليل الحسابات المالي (Chart of Accounts)
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # اسم الحساب
    account_number = db.Column(db.String(20))  # رقم الحساب
    category_id = db.Column(db.Integer)  # رمز الفئة
    account_type = db.Column(db.String(50))  # نوع الحساب (أصول، خصوم، إيرادات، مصروفات)
    is_bank_account = db.Column(db.Boolean, default=False)  # هل هو حساب بنكي
    is_cash_account = db.Column(db.Boolean, default=False)  # هل هو حساب نقدي
    parent_id = db.Column(db.Integer, db.ForeignKey('account.id'))  # الحساب الأب (للتسلسل الهرمي)
    balance = db.Column(db.Float, default=0.0)  # الرصيد
    description = db.Column(db.Text)  # وصف الحساب
    is_active = db.Column(db.Boolean, default=True)  # حالة الحساب
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    children = db.relationship('Account', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def __str__(self):
        return f"{self.account_number} - {self.name}" if self.account_number else self.name
    
    def get_balance(self):
        """حساب الرصيد النهائي"""
        return self.balance

# نموذج فئات الحسابات
class AccountCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # اسم الفئة
    code = db.Column(db.String(20))  # رمز الفئة
    description = db.Column(db.Text)  # وصف الفئة
    is_active = db.Column(db.Boolean, default=True)  # حالة الفئة
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __str__(self):
        return self.name

# نموذج القيد المحاسبي
class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry_number = db.Column(db.String(20), unique=True)  # رقم القيد
    date = db.Column(db.Date, nullable=False)  # تاريخ القيد
    reference_type = db.Column(db.String(50))  # نوع المرجع
    reference_id = db.Column(db.String(50))  # رقم المرجع
    description = db.Column(db.Text)  # وصف القيد
    entry_type = db.Column(db.String(50))  # نوع القيد
    status = db.Column(db.String(20))  # حالة القيد
    is_posted = db.Column(db.Boolean, default=False)  # هل تم ترحيل القيد
    posted_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # من قام بترحيل القيد
    posted_at = db.Column(db.DateTime)  # تاريخ الترحيل
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # من أنشأ القيد
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    creator = db.relationship('User', foreign_keys=[created_by])
    poster = db.relationship('User', foreign_keys=[posted_by])
    lines = db.relationship('JournalLine', backref='entry', lazy=True, cascade="all, delete-orphan")
    
    def __str__(self):
        return f"قيد رقم {self.entry_number} بتاريخ {self.date}"

# نموذج سطور القيد المحاسبي
class JournalLine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    journal_id = db.Column(db.Integer, db.ForeignKey('journal_entry.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    debit = db.Column(db.Float, default=0.0)  # المبلغ المدين
    credit = db.Column(db.Float, default=0.0)  # المبلغ الدائن
    description = db.Column(db.Text)  # وصف السطر
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    account = db.relationship('Account', foreign_keys=[account_id])
    
    def __str__(self):
        return f"{self.account.name}: مدين {self.debit} - دائن {self.credit}"

# نموذج حركات الحسابات
class AccountTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    journal_id = db.Column(db.Integer, db.ForeignKey('journal_entry.id'))
    transaction_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # debit أو credit
    description = db.Column(db.Text)
    reference_type = db.Column(db.String(50))
    reference_id = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    account = db.relationship('Account', foreign_keys=[account_id])
    journal = db.relationship('JournalEntry', foreign_keys=[journal_id])
    
    def __str__(self):
        return f"حركة {self.transaction_type} بقيمة {self.amount} على حساب {self.account.name}"

# نموذج سند القبض
class ReceiptVoucher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voucher_number = db.Column(db.String(20), unique=True)  # رقم السند
    voucher_date = db.Column(db.Date, nullable=False)  # تاريخ السند
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))  # العميل
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))  # الحساب
    amount = db.Column(db.Float, nullable=False)  # المبلغ
    payment_method = db.Column(db.String(50))  # طريقة الدفع (نقدي، شيك، تحويل بنكي)
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'))  # العملة
    exchange_rate = db.Column(db.Float, default=1.0)  # سعر الصرف
    reference = db.Column(db.String(100))  # المرجع
    description = db.Column(db.Text)  # الوصف
    journal_id = db.Column(db.Integer, db.ForeignKey('journal_entry.id'))  # القيد المحاسبي المرتبط
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # من أنشأ السند
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    customer = db.relationship('Customer', foreign_keys=[customer_id])
    account = db.relationship('Account', foreign_keys=[account_id])
    currency = db.relationship('Currency', foreign_keys=[currency_id])
    journal = db.relationship('JournalEntry', foreign_keys=[journal_id])
    user = db.relationship('User', foreign_keys=[created_by])
    
    def __str__(self):
        return f"سند قبض رقم {self.voucher_number} بتاريخ {self.voucher_date}"

# نموذج سند الصرف
class PaymentVoucher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voucher_number = db.Column(db.String(20), unique=True)  # رقم السند
    voucher_date = db.Column(db.Date, nullable=False)  # تاريخ السند
    beneficiary = db.Column(db.String(200))  # المستفيد
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))  # الحساب
    amount = db.Column(db.Float, nullable=False)  # المبلغ
    payment_method = db.Column(db.String(50))  # طريقة الدفع (نقدي، شيك، تحويل بنكي)
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'))  # العملة
    exchange_rate = db.Column(db.Float, default=1.0)  # سعر الصرف
    reference = db.Column(db.String(100))  # المرجع
    description = db.Column(db.Text)  # الوصف
    journal_id = db.Column(db.Integer, db.ForeignKey('journal_entry.id'))  # القيد المحاسبي المرتبط
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # من أنشأ السند
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    account = db.relationship('Account', foreign_keys=[account_id])
    currency = db.relationship('Currency', foreign_keys=[currency_id])
    journal = db.relationship('JournalEntry', foreign_keys=[journal_id])
    user = db.relationship('User', foreign_keys=[created_by])
    
    def __str__(self):
        return f"سند صرف رقم {self.voucher_number} بتاريخ {self.voucher_date}"

# نموذج إعدادات النظام
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
