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
    return render_template('banks.html')

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
    return render_template('cash-journal.html')

@app.route('/bank-journal')
def bank_journal():
    return render_template('bank-journal.html')

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
    return render_template('account-statements.html')

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
            'transitions': 'true'
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
