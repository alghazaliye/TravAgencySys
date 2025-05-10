from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Customer, TransportCompany, Country, City, BusRoute, BusType
from models import BusSchedule, BusTrip, BusBooking, BookingPayment, SystemSettings
from app import app, db
import logging

# الإعدادات الافتراضية للنظام
DEFAULT_SETTINGS = {
    # معلومات النظام الأساسية
    'system_name': {
        'value': 'نظام إدارة وكالة السفر والسياحة',
        'type': 'text',
        'description': 'اسم النظام الذي سيظهر في العنوان وجميع أنحاء التطبيق'
    },
    'system_slogan': {
        'value': 'حلول متكاملة لوكالات السفر والسياحة',
        'type': 'text',
        'description': 'شعار أو وصف قصير للنظام'
    },
    'company_name': {
        'value': 'وكالة السفر للسياحة والخدمات',
        'type': 'text',
        'description': 'اسم الشركة أو المؤسسة'
    },
    'dashboard_title': {
        'value': 'لوحة التحكم',
        'type': 'text',
        'description': 'العنوان الذي سيظهر في لوحة التحكم الرئيسية'
    },
    'primary_color': {
        'value': '#4e73df',
        'type': 'text',
        'description': 'اللون الرئيسي للنظام'
    },
    'secondary_color': {
        'value': '#1cc88a',
        'type': 'text',
        'description': 'اللون الثانوي للنظام'
    },
    'use_custom_logo': {
        'value': 'false',
        'type': 'boolean',
        'description': 'استخدام شعار مخصص بدلاً من أيقونة'
    },
    'logo_icon': {
        'value': 'fas fa-plane',
        'type': 'text',
        'description': 'أيقونة الشعار (تظهر عندما لا يتم استخدام شعار مخصص)'
    },
    'custom_logo_url': {
        'value': '',
        'type': 'text',
        'description': 'رابط الشعار المخصص'
    },
    'dark_mode': {
        'value': 'auto',
        'type': 'text',
        'description': 'وضع العرض (ليلي/نهاري)'
    },
    'rtl_mode': {
        'value': 'true',
        'type': 'boolean',
        'description': 'تمكين وضع RTL (من اليمين إلى اليسار)'
    },
    'enable_dark_mode': {
        'value': 'false',
        'type': 'boolean',
        'description': 'تمكين الوضع الداكن افتراضياً'
    },
    'default_currency': {
        'value': 'SAR',
        'type': 'text',
        'description': 'العملة الافتراضية للمعاملات المالية'
    }
}

# وظيفة لإنشاء الإعدادات الافتراضية
def create_default_settings():
    """إضافة الإعدادات الافتراضية للنظام إلى قاعدة البيانات"""
    created_count = 0
    for key, data in DEFAULT_SETTINGS.items():
        # البحث عما إذا كان الإعداد موجودًا بالفعل
        setting = SystemSettings.query.filter_by(setting_key=key).first()
        if not setting:
            # إنشاء إعداد جديد إذا لم يكن موجودًا
            setting = SystemSettings(
                setting_key=key,
                setting_value=data['value'],
                setting_type=data['type'],
                description=data['description']
            )
            db.session.add(setting)
            created_count += 1
    
    if created_count > 0:
        try:
            db.session.commit()
            logging.info(f"تم إنشاء {created_count} إعداد افتراضي")
        except Exception as e:
            db.session.rollback()
            logging.error(f"حدث خطأ أثناء إنشاء الإعدادات الافتراضية: {str(e)}")
    
    return created_count

# إنشاء متغير للإعدادات المستخدمة في جميع القوالب
def get_settings():
    """استرجاع إعدادات النظام"""
    all_settings = SystemSettings.query.all()
    settings_dict = {}
    
    # تحويل قائمة الإعدادات إلى قاموس
    for setting in all_settings:
        if setting.setting_type == 'boolean':
            settings_dict[setting.setting_key] = setting.setting_value.lower() in ('true', '1', 'yes')
        elif setting.setting_type == 'json':
            try:
                import json
                settings_dict[setting.setting_key] = json.loads(setting.setting_value)
            except:
                settings_dict[setting.setting_key] = None
        else:
            settings_dict[setting.setting_key] = setting.setting_value
    
    # إعدادات افتراضية في حالة عدم وجودها في قاعدة البيانات
    defaults = {
        'system_name': 'نظام إدارة وكالة السياحة والسفر',
        'dark_mode': 'auto',
        'primary_color': '#4e73df',
        'secondary_color': '#1cc88a',
        'sidebar_color': '#2c3e50',
        'navbar_color': '#ffffff',
        'navbar_text_color': '#333333',
        'text_primary_color': '#333333',
        'dark_primary_color': '#375bbb',
        'dark_sidebar_color': '#1a1a2e',
        'dark_text_color': '#e1e1e1',
        'navbar_dark_color': '#1e1e1e',
        'navbar_dark_text_color': '#e1e1e1',
        'rtl_layout': 'true',
        'enable_animations': 'true',
        'font_family': 'Tajawal',
        'border_radius': 'medium',
        'card_shadow': 'medium',
        'content_width': 'fluid',
        'sidebar_mini': 'false',
        'transitions': 'true',
        'layout_boxed': 'false',
        'navbar_fixed': 'true',
        'navbar_shadow': 'true',
        'navbar_transparent': 'false'
    }
    
    # دمج الإعدادات الافتراضية مع الإعدادات المخزنة
    for key, value in defaults.items():
        if key not in settings_dict:
            settings_dict[key] = value
    
    return settings_dict

# الصفحة الرئيسية وتسجيل الدخول
@app.route('/')
def index():
    """الصفحة الرئيسية"""
    settings = get_settings()
    return render_template('dashboard.html', settings=settings)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('يرجى إدخال اسم المستخدم وكلمة المرور', 'danger')
            settings = get_settings()
            return render_template('login.html', settings=settings)
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            # التحقق من وجود صفحة إعادة توجيه
            next_page = request.args.get('next')
            
            # التحقق من أن الرابط التالي ليس خارجياً (أمان)
            if next_page and not next_page.startswith('/'):
                next_page = None
                
            return redirect(next_page or url_for('index'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
    
    settings = get_settings()
    return render_template('login.html', settings=settings)

@app.route('/logout')
@login_required
def logout():
    """تسجيل الخروج"""
    logout_user()
    return redirect(url_for('login'))

# إدارة المستخدمين
@app.route('/users')
@login_required
def users():
    """صفحة إدارة المستخدمين"""
    user_list = User.query.all()
    settings = get_settings()
    return render_template('users.html', users=user_list, settings=settings)

@app.route('/api/users', methods=['POST'])
@login_required
def create_user():
    """إنشاء مستخدم جديد"""
    try:
        data = request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        is_admin = data.get('is_admin') == 'true'
        
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'اسم المستخدم موجود بالفعل'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'البريد الإلكتروني موجود بالفعل'}), 400
        
        # التحقق من وجود كلمة مرور
        if not password:
            return jsonify({'success': False, 'message': 'كلمة المرور مطلوبة'}), 400
            
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            is_admin=is_admin
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'تم إنشاء المستخدم بنجاح'})
    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء إنشاء المستخدم'}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """تحديث بيانات المستخدم"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.form
        
        user.full_name = data.get('full_name', user.full_name)
        user.email = data.get('email', user.email)
        user.is_admin = data.get('is_admin') == 'true'
        user.active = data.get('active') == 'true'
        
        # التحقق من وجود كلمة مرور جديدة
        new_password = data.get('password')
        if new_password:
            user.password_hash = generate_password_hash(new_password)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'تم تحديث المستخدم بنجاح'})
    except Exception as e:
        logging.error(f"Error updating user: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء تحديث المستخدم'}), 500

# إدارة العملاء
@app.route('/customers')
@login_required
def customers():
    """صفحة إدارة العملاء"""
    customer_list = Customer.query.all()
    settings = get_settings()
    return render_template('customers.html', customers=customer_list, settings=settings)

@app.route('/api/customers', methods=['POST'])
@login_required
def create_customer():
    """إنشاء عميل جديد"""
    try:
        data = request.form
        
        # التحقق من وجود الاسم الكامل
        full_name = data.get('full_name')
        if not full_name:
            return jsonify({'success': False, 'message': 'الاسم الكامل مطلوب'}), 400
            
        new_customer = Customer(
            full_name=full_name,
            mobile=data.get('mobile'),
            email=data.get('email'),
            id_type=data.get('id_type'),
            id_number=data.get('id_number'),
            nationality=data.get('nationality'),
            gender=data.get('gender'),
            address=data.get('address'),
            notes=data.get('notes')
        )
        
        db.session.add(new_customer)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'تم إنشاء العميل بنجاح'})
    except Exception as e:
        logging.error(f"Error creating customer: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء إنشاء العميل'}), 500

# إدارة الدول والمدن
@app.route('/countries')
@login_required
def countries():
    """صفحة إدارة الدول"""
    country_list = Country.query.all()
    settings = get_settings()
    return render_template('countries.html', countries=country_list, settings=settings)

@app.route('/cities')
@login_required
def cities():
    """صفحة إدارة المدن"""
    city_list = City.query.all()
    countries = Country.query.all()
    settings = get_settings()
    return render_template('cities.html', cities=city_list, countries=countries, settings=settings)

# حجز تذاكر الحافلات
@app.route('/bus-tickets')
@login_required
def bus_tickets():
    """صفحة حجز تذاكر الحافلات"""
    settings = get_settings()
    return render_template('bus-tickets.html', settings=settings)

@app.route('/bus-tickets-new')
@login_required
def bus_tickets_new():
    """الصفحة الجديدة لحجز تذاكر الحافلات"""
    companies = TransportCompany.query.filter_by(is_active=True).all()
    cities = City.query.filter_by(is_active=True).all()
    settings = get_settings()
    return render_template('bus-tickets-new.html', companies=companies, cities=cities, settings=settings)

@app.route('/new_bus_booking')
@login_required
def new_bus_booking():
    """صفحة حجز حافلة جديدة"""
    companies = TransportCompany.query.filter_by(is_active=True).all()
    cities = City.query.filter_by(is_active=True).all()
    settings = get_settings()
    return render_template('new_bus_booking.html', companies=companies, cities=cities, settings=settings)

# التأشيرات والخدمات الأخرى
@app.route('/work-visa')
@login_required
def work_visa():
    """صفحة تأشيرات العمل"""
    settings = get_settings()
    return render_template('work-visa.html', settings=settings)

@app.route('/family-visit')
@login_required
def family_visit():
    """صفحة تأشيرات الزيارة العائلية"""
    settings = get_settings()
    return render_template('family-visit.html', settings=settings)

@app.route('/umrah-visa')
@login_required
def umrah_visa():
    """صفحة تأشيرات العمرة"""
    settings = get_settings()
    return render_template('umrah-visa.html', settings=settings)

@app.route('/airline-tickets')
@login_required
def airline_tickets():
    """صفحة تذاكر الطيران"""
    settings = get_settings()
    return render_template('airline-tickets.html', settings=settings)

@app.route('/mail-tracking')
@login_required
def mail_tracking():
    """صفحة متابعة البريد"""
    settings = get_settings()
    return render_template('mail-tracking.html', settings=settings)

@app.route('/suppliers')
@login_required
def suppliers():
    """صفحة الموردين"""
    settings = get_settings()
    return render_template('suppliers.html', settings=settings)

# خدمات الإدارة المالية
@app.route('/banks')
@login_required
def banks():
    """صفحة البنوك"""
    settings = get_settings()
    return render_template('banks.html', settings=settings)

@app.route('/payment-vouchers')
@login_required
def payment_vouchers():
    """صفحة سندات الصرف"""
    settings = get_settings()
    return render_template('payment-vouchers.html', settings=settings)

@app.route('/receipts')
@login_required
def receipts():
    """صفحة سندات القبض"""
    settings = get_settings()
    return render_template('receipts.html', settings=settings)

@app.route('/currencies')
@login_required
def currencies():
    """صفحة العملات"""
    settings = get_settings()
    return render_template('currencies.html', settings=settings)

@app.route('/daily-journal')
@login_required
def daily_journal():
    """صفحة القيود اليومية"""
    settings = get_settings()
    return render_template('daily-journal.html', settings=settings)

@app.route('/financial-settings')
@login_required
def financial_settings():
    """صفحة الإعدادات المالية"""
    settings = get_settings()
    return render_template('financial-settings.html', settings=settings)

@app.route('/reports')
@login_required
def reports():
    """صفحة التقارير"""
    settings = get_settings()
    return render_template('reports.html', settings=settings)

@app.route('/id-types')
@login_required
def id_types():
    """صفحة أنواع الهوية"""
    settings = get_settings()
    return render_template('id-types.html', settings=settings)

# إعدادات النظام
@app.route('/system-settings')
@login_required
def system_settings():
    """صفحة إعدادات النظام"""
    settings_list = SystemSettings.query.all()
    settings = get_settings()
    
    # إعداد قاموس الأوصاف الافتراضي
    setting_descriptions = {
        # معلومات النظام
        'system_name': {
            'description': 'اسم النظام الذي سيظهر في العنوان وجميع أنحاء التطبيق'
        },
        'dark_text_color': {
            'description': 'لون النص في الوضع الليلي'
        },
        'navbar_color': {
            'description': 'لون خلفية شريط التنقل'
        },
        'system_slogan': {
            'description': 'شعار أو وصف قصير للنظام'
        },
        'navbar_text_color': {
            'description': 'لون النص في شريط التنقل'
        },
        'navbar_dark_text_color': {
            'description': 'لون النص في شريط التنقل (الوضع الليلي)'
        },
        'dashboard_title': {
            'description': 'العنوان الذي سيظهر في لوحة التحكم الرئيسية'
        },
        'primary_color': {
            'description': 'اللون الرئيسي للنظام'
        },
        'secondary_color': {
            'description': 'اللون الثانوي للنظام'
        },
        'dark_mode': {
            'description': 'وضع العرض (ليلي/نهاري)',
            'options': 'light,dark,auto'
        },
        'logo_icon': {
            'description': 'أيقونة الشعار (تظهر عندما لا يتم استخدام شعار مخصص)'
        },
        'custom_logo_url': {
            'description': 'رابط الشعار المخصص (إذا كنت تستخدم شعار مخصص)'
        },
        'use_custom_logo': {
            'description': 'استخدام شعار مخصص بدلاً من أيقونة'
        }
    }
    
    # جلب أوصاف الإعدادات من قاعدة البيانات إذا كانت موجودة
    for setting in settings_list:
        if setting.setting_key not in setting_descriptions:
            setting_descriptions[setting.setting_key] = {}
        
        setting_descriptions[setting.setting_key]['description'] = setting.description
        setting_descriptions[setting.setting_key]['type'] = setting.setting_type
        
        # إعدادات القوائم المنسدلة
        if setting.setting_key == 'dark_mode':
            setting_descriptions[setting.setting_key]['options'] = 'light,dark,auto'
        elif setting.setting_key == 'content_width':
            setting_descriptions[setting.setting_key]['options'] = 'fluid,fixed'
        elif setting.setting_key == 'border_radius':
            setting_descriptions[setting.setting_key]['options'] = 'none,small,medium,large'
        elif setting.setting_key == 'card_shadow':
            setting_descriptions[setting.setting_key]['options'] = 'none,small,medium,large'
    
    # إضافة قائمة الأيقونات للشعار
    icon_options = [
        'fas fa-plane',
        'fas fa-car',
        'fas fa-bus',
        'fas fa-ship',
        'fas fa-train',
        'fas fa-globe',
        'fas fa-map-marker-alt',
        'fas fa-suitcase',
        'fas fa-passport',
        'fas fa-ticket-alt',
        'fas fa-hotel',
        'fas fa-umbrella-beach',
        'fas fa-mountain',
        'fas fa-mosque',
        'fas fa-kaaba',
        'fas fa-route',
        'fas fa-compass',
        'fas fa-calendar-alt',
        'fas fa-user-friends',
        'fas fa-building'
    ]
    
    return render_template('system-settings.html', 
                          settings_list=settings_list, 
                          settings=settings, 
                          setting_descriptions=setting_descriptions,
                          icon_options=icon_options)

@app.route('/api/system-settings', methods=['POST'])
@login_required
def update_settings():
    """تحديث إعدادات النظام"""
    try:
        data = request.form
        for key, value in data.items():
            SystemSettings.set_value(key, value)
        
        return jsonify({'success': True, 'message': 'تم تحديث الإعدادات بنجاح'})
    except Exception as e:
        logging.error(f"Error updating settings: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء تحديث الإعدادات'}), 500
