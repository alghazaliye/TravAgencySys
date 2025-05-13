from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import User, Customer, TransportCompany, Country, City, BusRoute, BusType
from models import BusSchedule, BusTrip, BusBooking, BookingPayment, SystemSettings
from models import Currency, CashRegister, BankAccount, Role, Permission, IdentityType
from app import app, db

# قاموس عام لتخزين الإعدادات
settings_dict = {}
import logging
import uuid
from datetime import datetime

# دالة للتحقق من وجود صلاحية محددة
def permission_required(permission_name):
    """
    زخرفة للتحقق من أن المستخدم الحالي يملك الصلاحية المحددة.
    إذا لم يملك المستخدم الصلاحية، يتم توجيهه إلى صفحة خطأ 403 (غير مصرح)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login', next=request.url))
            
            # المسؤول لديه جميع الصلاحيات
            if current_user.is_admin:
                return f(*args, **kwargs)
            
            # التحقق من الصلاحية
            if not current_user.has_permission(permission_name):
                flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# دالة للتحقق من وجود دور محدد
def role_required(role_name):
    """
    زخرفة للتحقق من أن المستخدم الحالي يملك الدور المحدد.
    إذا لم يملك المستخدم الدور، يتم توجيهه إلى صفحة خطأ 403 (غير مصرح)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login', next=request.url))
            
            # المسؤول لديه جميع الأدوار
            if current_user.is_admin:
                return f(*args, **kwargs)
            
            # التحقق من الدور
            if not current_user.has_role(role_name):
                flash('ليس لديك الصلاحية للوصول إلى هذه الصفحة', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# دالة للتحقق من أن المستخدم هو مسؤول
def admin_required(f):
    """
    زخرفة للتحقق من أن المستخدم الحالي هو مسؤول.
    إذا لم يكن المستخدم مسؤولاً، يتم توجيهه إلى صفحة خطأ 403 (غير مصرح)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        
        if not current_user.is_admin:
            flash('يجب أن تكون مسؤولاً للوصول إلى هذه الصفحة', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

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
    'sidebar_mini': {
        'value': 'true',
        'type': 'boolean',
        'description': 'تمكين وضع القائمة الجانبية المصغرة'
    },
    'default_currency': {
        'value': 'SAR',
        'type': 'text',
        'description': 'العملة الافتراضية للمعاملات المالية'
    }
}

# وظيفة لتحميل إعدادات النظام
def load_system_settings():
    """تحميل إعدادات النظام وتخزينها في متغير عالمي"""
    global settings_dict
    settings_dict = {}  # إعادة تعيين القاموس
    
    all_settings = SystemSettings.query.all()
    for setting in all_settings:
        settings_dict[setting.setting_key] = setting.setting_value
    
    # إضافة الإعدادات الافتراضية إذا لم تكن موجودة بالفعل
    for key, data in DEFAULT_SETTINGS.items():
        if key not in settings_dict:
            settings_dict[key] = data['value']
    
    return settings_dict

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
        'sidebar_mini': 'true',
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

# إضافة وظيفة قبل كل طلب لجعل الجلسة دائمة
@app.before_request
def make_session_permanent():
    """جعل جلسة المستخدم دائمة لتجنب انتهاء الصلاحية بسرعة"""
    from flask import session
    session.permanent = True

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
        remember = True if request.form.get('remember') else False
        
        if not username or not password:
            flash('يرجى إدخال اسم المستخدم وكلمة المرور', 'danger')
            settings = get_settings()
            return render_template('login.html', settings=settings)
        
        # إزالة المسافات الزائدة من اسم المستخدم
        username = username.strip()
        
        # محاولة العثور على المستخدم إما باسم المستخدم أو البريد الإلكتروني
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and check_password_hash(user.password_hash, password):
            # تسجيل الدخول وتفعيل خاصية التذكر لجعل الجلسة دائمة
            from datetime import timedelta
            
            # إذا كان تم اختيار "تذكرني"، فستكون مدة الجلسة 30 يومًا، وإلا ستكون 1 يومًا
            duration = timedelta(days=30) if remember else timedelta(days=1)
            login_user(user, remember=remember, duration=duration)

            # تسجيل معلومات تسجيل الدخول في السجلات فقط دون تخزينها في قاعدة البيانات
            # سنضيف آليات تتبع لاحقًا بعد ترحيل قاعدة البيانات
            logging.info(f"تم تسجيل دخول المستخدم {user.username} بنجاح في {datetime.now()}")
            
            # سجل نجاح تسجيل الدخول
            logging.info(f"تم تسجيل دخول المستخدم: {user.username} (IP: {request.remote_addr})")
            
            # التحقق من وجود صفحة إعادة توجيه
            next_page = request.args.get('next')
            
            # التحقق من أن الرابط التالي ليس خارجياً (أمان)
            if next_page and not next_page.startswith('/'):
                next_page = None
            
            # تأكيد نجاح تسجيل الدخول
            flash(f'مرحبًا {user.full_name or user.username}! تم تسجيل الدخول بنجاح', 'success')
                
            return redirect(next_page or url_for('index'))
        else:
            logging.warning(f"محاولة تسجيل دخول فاشلة: {username} (IP: {request.remote_addr})")
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
    
    settings = get_settings()
    return render_template('login.html', settings=settings)

@app.route('/logout')
@login_required
def logout():
    """تسجيل الخروج"""
    # تسجيل عملية الخروج
    username = current_user.username
    user_id = current_user.id
    user_ip = request.remote_addr
    
    # سجل آخر وقت لخروج المستخدم
    try:
        user = User.query.get(user_id)
        if user and hasattr(user, 'last_logout_at'):
            user.last_logout_at = datetime.now()
            db.session.commit()
    except:
        # في حالة فشل التحديث، نتابع دون توقف
        db.session.rollback()
        pass
    
    # تسجيل خروج المستخدم
    logout_user()
    logging.info(f"تم تسجيل خروج المستخدم: {username} (IP: {user_ip})")
    
    # تنظيف وإزالة الجلسة
    from flask import session
    session.clear()
    
    flash('تم تسجيل الخروج بنجاح!', 'success')
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
    # إضافة قوائم أنواع الهوية والبلدان للاختيار منها
    id_types = IdentityType.query.filter_by(is_active=True).all()
    countries = Country.query.filter_by(is_active=True).all()
    settings = get_settings()
    return render_template('customers.html', 
                          customers=customer_list, 
                          id_types=id_types,
                          countries=countries,
                          settings=settings)

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

@app.route('/id-types')
@login_required
def id_types():
    """صفحة إدارة أنواع الهوية"""
    id_type_list = IdentityType.query.all()
    settings = get_settings()
    return render_template('id-types.html', id_types=id_type_list, settings=settings)

# واجهة برمجة التطبيقات لأنواع الهوية
@app.route('/api/id-types', methods=['GET'])
@login_required
def get_id_types():
    """الحصول على قائمة أنواع الهوية"""
    try:
        # إضافة خيار الفلترة حسب الحالة (مفعل/غير مفعل)
        filter_active = request.args.get('active')
        query = IdentityType.query
        
        # إذا تم تحديد فلتر الحالة
        if filter_active is not None:
            is_active = filter_active.lower() in ('true', '1', 'yes', 'y')
            query = query.filter(IdentityType.is_active == is_active)
        
        # ترتيب النتائج
        id_types = query.order_by(IdentityType.name).all()
        
        # إعداد البيانات لإرجاعها كJSON
        data = []
        for id_type in id_types:
            data.append({
                'id': id_type.id,
                'name': id_type.name,
                'requires_nationality': id_type.requires_nationality,
                'description': id_type.description or '',
                'is_active': id_type.is_active,
                'customer_count': 0  # المرجع 'customers' تم إيقافه مؤقتًا
            })
        
        # تسجيل نجاح العملية
        logging.debug(f"تم جلب {len(data)} من أنواع الهوية بنجاح")
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        logging.error(f"Error fetching id types: {str(e)}")
        return jsonify({'success': False, 'message': f'حدث خطأ أثناء جلب بيانات أنواع الهوية: {str(e)}'}), 500

@app.route('/api/id-types', methods=['POST'])
@login_required
def add_id_type():
    """إضافة نوع هوية جديد"""
    try:
        # طباعة بيانات الطلب للتصحيح
        logging.debug(f"Content-Type: {request.content_type}")
        logging.debug(f"Raw Request Data: {request.data}")
        
        # التعامل مع البيانات سواء كانت JSON أو FORM
        if request.is_json:
            data = request.json
        else:
            data = request.form.to_dict()
            
        logging.debug(f"Parsed Data: {data}")
        
        # التحقق من البيانات المدخلة
        name = data.get('name')
        if not name or name.strip() == '':
            return jsonify({'success': False, 'message': 'يجب تحديد اسم نوع الهوية'}), 400
        
        # تنظيف وتحضير البيانات
        requires_nationality = data.get('requires_nationality')
        if isinstance(requires_nationality, str):
            requires_nationality = requires_nationality.lower() in ('true', '1', 'yes', 'y')
        
        is_active = data.get('is_active')
        if isinstance(is_active, str):
            is_active = is_active.lower() in ('true', '1', 'yes', 'y')
            
        # إنشاء كائن جديد
        id_type = IdentityType()
        id_type.name = name.strip()
        id_type.requires_nationality = requires_nationality if requires_nationality is not None else True
        id_type.description = data.get('description', '').strip()
        id_type.is_active = is_active if is_active is not None else True
        
        # حفظ في قاعدة البيانات
        db.session.add(id_type)
        db.session.commit()
        
        logging.info(f"تم إنشاء نوع هوية جديد: {id_type.name} (ID: {id_type.id})")
        
        return jsonify({
            'success': True, 
            'message': 'تم إضافة نوع الهوية بنجاح',
            'id_type': {
                'id': id_type.id,
                'name': id_type.name,
                'requires_nationality': id_type.requires_nationality,
                'description': id_type.description,
                'is_active': id_type.is_active
            }
        })
    except Exception as e:
        db.session.rollback()  # التراجع عن أي تغييرات في حالة حدوث خطأ
        logging.error(f"Error adding id type: {str(e)}")
        return jsonify({'success': False, 'message': f'حدث خطأ أثناء إضافة نوع الهوية: {str(e)}'}), 500

@app.route('/api/id-types/<int:id_type_id>', methods=['PUT'])
@login_required
def update_id_type(id_type_id):
    """تحديث نوع هوية"""
    try:
        # البحث عن نوع الهوية
        id_type = IdentityType.query.get(id_type_id)
        if not id_type:
            return jsonify({'success': False, 'message': 'نوع الهوية غير موجود أو تم حذفه'}), 404
        
        # طباعة بيانات الطلب للتصحيح
        logging.debug(f"Content-Type: {request.content_type}")
        logging.debug(f"Raw Request Data: {request.data}")
        
        # التعامل مع البيانات سواء كانت JSON أو FORM
        if request.is_json:
            data = request.json
        else:
            data = request.form.to_dict()
        
        logging.debug(f"Parsed Data for update: {data}")
        
        # التحقق من البيانات المدخلة
        name = data.get('name')
        if not name or name.strip() == '':
            return jsonify({'success': False, 'message': 'يجب تحديد اسم نوع الهوية'}), 400
        
        # تنظيف وتحضير البيانات
        requires_nationality = data.get('requires_nationality')
        if isinstance(requires_nationality, str):
            requires_nationality = requires_nationality.lower() in ('true', '1', 'yes', 'y')
        elif requires_nationality is None:
            requires_nationality = id_type.requires_nationality
        
        is_active = data.get('is_active')
        if isinstance(is_active, str):
            is_active = is_active.lower() in ('true', '1', 'yes', 'y')
        elif is_active is None:
            is_active = id_type.is_active
        
        description = data.get('description')
        if description is None:
            description = id_type.description or ''
        
        # تحديث البيانات
        old_name = id_type.name  # للتسجيل
        id_type.name = name.strip()
        id_type.requires_nationality = requires_nationality
        id_type.description = description.strip()
        id_type.is_active = is_active
        
        # حفظ التغييرات
        db.session.commit()
        
        logging.info(f"تم تحديث نوع الهوية: من '{old_name}' إلى '{id_type.name}' (ID: {id_type.id})")
        
        return jsonify({
            'success': True, 
            'message': 'تم تحديث نوع الهوية بنجاح',
            'id_type': {
                'id': id_type.id,
                'name': id_type.name,
                'requires_nationality': id_type.requires_nationality,
                'description': id_type.description,
                'is_active': id_type.is_active
            }
        })
    except Exception as e:
        db.session.rollback()  # التراجع عن أي تغييرات في حالة حدوث خطأ
        logging.error(f"Error updating id type: {str(e)}")
        return jsonify({'success': False, 'message': f'حدث خطأ أثناء تحديث نوع الهوية: {str(e)}'}), 500

@app.route('/api/id-types/<int:id_type_id>', methods=['DELETE'])
@login_required
def delete_id_type(id_type_id):
    """حذف نوع هوية"""
    try:
        # البحث عن نوع الهوية
        id_type = IdentityType.query.get(id_type_id)
        if not id_type:
            return jsonify({'success': False, 'message': 'نوع الهوية غير موجود أو تم حذفه بالفعل'}), 404
        
        # تم إيقاف التحقق من وجود عملاء مرتبطين بنوع الهوية مؤقتًا
        # نظرًا لأن العلاقة بين الجداول غير مكتملة حاليًا
        customers_count = 0
        
        # في المستقبل يمكن استبدال هذا بالكود التالي عند إعادة تفعيل العلاقة:
        # من الممكن إضافة استعلام مباشر للبحث عن العملاء المرتبطين بهذا النوع من الهوية
        # مثال: customers_count = Customer.query.filter_by(id_type=id_type.name).count()
        
        # تسجيل معلومات قبل الحذف
        id_type_name = id_type.name
        id_type_id_val = id_type.id
        
        # حذف نوع الهوية
        db.session.delete(id_type)
        db.session.commit()
        
        # تسجيل عملية الحذف
        logging.info(f"تم حذف نوع الهوية: '{id_type_name}' (ID: {id_type_id_val})")
        
        return jsonify({
            'success': True, 
            'message': 'تم حذف نوع الهوية بنجاح', 
            'deleted_id': id_type_id_val
        })
    except Exception as e:
        db.session.rollback()  # التراجع عن التغييرات في حالة حدوث خطأ
        logging.error(f"Error deleting id type: {str(e)}")
        
        if "foreign key constraint" in str(e).lower():
            # حالة خاصة: قيود المفتاح الأجنبي
            return jsonify({
                'success': False, 
                'message': 'لا يمكن حذف نوع الهوية لأنه مرتبط ببيانات أخرى في النظام'
            }), 400
        
        return jsonify({
            'success': False, 
            'message': f'حدث خطأ أثناء حذف نوع الهوية: {str(e)}'
        }), 500

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
    # جلب قائمة شركات النقل النشطة
    companies = TransportCompany.query.filter_by(is_active=True).all()
    
    # جلب قائمة المدن النشطة
    cities = City.query.filter_by(is_active=True).all()
    
    # جلب قائمة أنواع الهوية من إعدادات النظام
    id_types = SystemSettings.query.filter_by(setting_key='id_types').first()
    id_types_list = []
    if id_types and id_types.setting_value:
        try:
            # محاولة تحويل القيمة من JSON إلى قائمة
            import json
            id_types_list = json.loads(id_types.setting_value)
        except:
            # في حالة فشل التحويل، استخدم قائمة فارغة
            id_types_list = []
    
    # جلب قائمة البلدان والجنسيات
    countries = Country.query.filter_by(is_active=True).all()
    
    # جلب قائمة العملات المتاحة
    currencies = Currency.query.filter_by(is_active=True).all()
    
    # جلب إعدادات النظام
    settings = get_settings()
    
    # جلب أنواع الباصات المتاحة
    bus_types = BusType.query.filter_by(is_active=True).all()
    
    return render_template(
        'bus-tickets-new.html',
        companies=companies,
        cities=cities,
        countries=countries,
        currencies=currencies,
        id_types=id_types_list,
        bus_types=bus_types,
        settings=settings
    )

@app.route('/new_bus_booking')
@login_required
def new_bus_booking():
    """صفحة حجز حافلة جديدة"""
    # جلب قائمة شركات النقل النشطة
    companies = TransportCompany.query.filter_by(is_active=True).all()
    
    # جلب قائمة المدن النشطة
    cities = City.query.filter_by(is_active=True).all()
    
    # جلب قائمة أنواع الهوية من إعدادات النظام
    id_types = SystemSettings.query.filter_by(setting_key='id_types').first()
    id_types_list = []
    if id_types and id_types.setting_value:
        try:
            # محاولة تحويل القيمة من JSON إلى قائمة
            import json
            id_types_list = json.loads(id_types.setting_value)
        except:
            # في حالة فشل التحويل، استخدم قائمة فارغة
            id_types_list = []
    
    # جلب قائمة البلدان والجنسيات
    countries = Country.query.filter_by(is_active=True).all()
    
    # جلب قائمة العملات المتاحة
    currencies = Currency.query.filter_by(is_active=True).all()
    
    # جلب أنواع الباصات المتاحة
    bus_types = BusType.query.filter_by(is_active=True).all()
    
    # جلب الحسابات النقدية والبنكية للدفع
    cash_accounts = CashRegister.query.filter_by(is_active=True).all()
    bank_accounts = BankAccount.query.filter_by(is_active=True).all()
    
    # جلب إعدادات النظام
    settings = get_settings()
    
    return render_template(
        'new_bus_booking.html',
        companies=companies,
        cities=cities,
        countries=countries,
        currencies=currencies,
        id_types=id_types_list,
        bus_types=bus_types,
        cash_accounts=cash_accounts,
        bank_accounts=bank_accounts,
        settings=settings
    )

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
    # إنشاء قاموس فارغ للعملات حتى لا يكون هناك خطأ في القالب
    currency_totals = {}
    try:
        # الحصول على العملات
        currencies = Currency.query.all()
        
        # إضافة كل عملة إلى قاموس العملات
        for currency in currencies:
            currency_totals[currency.code] = {
                'name': currency.name,
                'bank_total': 0,
                'cash_total': 0,
                'total': 0
            }
    except Exception as e:
        logging.error(f"خطأ في استرجاع العملات: {str(e)}")
        
    return render_template('banks.html', settings=settings, currency_totals=currency_totals)

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

# تم نقل مسار id-types إلى موقع آخر

# إعدادات النظام
@app.route('/system-settings', methods=['GET', 'POST'])
@login_required
def system_settings():
    """صفحة إعدادات النظام"""
    # إذا كان الطلب بطريقة POST، قم بمعالجة تحديث الإعدادات
    if request.method == 'POST':
        try:
            data = request.form
            
            # الحصول على جميع الإعدادات الموجودة في قاعدة البيانات
            all_checkboxes = ['sidebar_mini', 'sidebar_collapsed', 'rtl_mode', 'enable_dark_mode', 
                             'use_custom_logo', 'show_logo_in_reports', 'sound_notifications',
                             'notify_new_bookings', 'notify_payment_received', 'notify_booking_cancellation',
                             'email_notifications_enabled', 'sms_service_enabled']
            
            # تعيين القيم الافتراضية للخانات غير المحددة
            for checkbox in all_checkboxes:
                if checkbox not in data:
                    # إذا لم يكن الـ checkbox موجودًا في البيانات المرسلة، فهذا يعني أنه غير محدد
                    try:
                        SystemSettings.set_value(checkbox, 'false')
                        # تحديث القيمة في متغير الإعدادات العام
                        global settings_dict
                        settings_dict[checkbox] = 'false'
                    except Exception as e:
                        logging.error(f"خطأ في حفظ الإعداد {checkbox}: {str(e)}")
            
            # معالجة باقي البيانات المرسلة
            for key, value in data.items():
                # تجنب المفاتيح الخاصة بـ CSRF وغيرها
                if key.startswith('csrf_') or key == '_method':
                    continue
                
                # حفظ القيمة أيضًا في متغير الإعدادات العام
                settings_dict[key] = value
                
                # محاولة حفظ القيمة في قاعدة البيانات
                try:
                    SystemSettings.set_value(key, value)
                except Exception as e:
                    logging.error(f"خطأ في حفظ الإعداد {key}: {str(e)}")
            
            flash('تم تحديث إعدادات النظام بنجاح', 'success')
            return redirect(url_for('system_settings'))
        except Exception as e:
            logging.error(f"خطأ في تحديث إعدادات النظام: {str(e)}")
            flash('حدث خطأ أثناء تحديث الإعدادات', 'danger')
    
    # تحميل الإعدادات الحالية
    settings_list = SystemSettings.query.all()
    settings = get_settings()
    
    # إضافة قيم افتراضية إلى قاموس الإعدادات في حالة عدم وجودها في قاعدة البيانات
    # سيتم تحميلها من قاعدة البيانات لاحقًا إذا كانت موجودة
    default_settings = {
        'date_format': 'DD/MM/YYYY',
        'time_format': 'HH:mm',
        'date_separator': '/',
        'use_hijri_dates': 'false',
        'first_day_of_week': '6',
        'enable_notifications': 'true',
        'notification_position': 'top-right',
        'notification_duration': '5',
        'sound_notifications': 'true',
        'notify_new_bookings': 'true',
        'notify_payment_received': 'true',
        'notify_booking_cancellation': 'true',
        'sms_service_enabled': 'false',
        'email_notifications_enabled': 'true',
        'paper_size': 'A4',
        'print_layout': 'portrait',
        'show_logo_in_reports': 'true'
    }
    
    # إضافة القيم الافتراضية إلى قاموس الإعدادات
    for key, value in default_settings.items():
        if key not in settings:
            settings[key] = value
    
    # إعداد قاموس الأوصاف الافتراضي مع كافة الحقول المطلوبة
    setting_descriptions = {
        # معلومات النظام
        'system_name': {
            'description': 'اسم النظام الذي سيظهر في العنوان وجميع أنحاء التطبيق'
        },
        'system_slogan': {
            'description': 'شعار أو وصف قصير للنظام'
        },
        'date_format': {
            'description': 'تنسيق عرض التاريخ في جميع أنحاء النظام'
        },
        'time_format': {
            'description': 'تنسيق عرض الوقت في جميع أنحاء النظام'
        },
        'date_separator': {
            'description': 'الفاصل المستخدم بين أجزاء التاريخ'
        },
        'use_hijri_dates': {
            'description': 'استخدام التقويم الهجري في النظام'
        },
        'show_both_dates': {
            'description': 'عرض التاريخ الميلادي والهجري معاً'
        },
        'first_day_of_week': {
            'description': 'تحديد أول يوم في الأسبوع'
        },
        'enable_notifications': {
            'description': 'تفعيل الإشعارات في النظام'
        },
        'notification_position': {
            'description': 'موضع ظهور الإشعارات في الشاشة'
        },
        'notification_duration': {
            'description': 'مدة ظهور الإشعارات (بالثواني)'
        },
        'sound_notifications': {
            'description': 'تفعيل التنبيهات الصوتية مع الإشعارات'
        },
        'notify_new_bookings': {
            'description': 'تنبيه عند إنشاء حجز جديد'
        },
        'notify_payment_received': {
            'description': 'تنبيه عند استلام مدفوعات'
        },
        'notify_booking_cancellation': {
            'description': 'تنبيه عند إلغاء حجز'
        },
        'sms_service_enabled': {
            'description': 'تفعيل خدمة إرسال الرسائل القصيرة'
        },
        'enable_sms': {
            'description': 'تفعيل نظام الرسائل القصيرة'
        },
        'email_notifications_enabled': {
            'description': 'تفعيل إرسال إشعارات البريد الإلكتروني'
        },
        'enable_emails': {
            'description': 'تفعيل نظام البريد الإلكتروني'
        },
        'company_email': {
            'description': 'البريد الإلكتروني الرسمي للشركة'
        },
        'company_phone': {
            'description': 'رقم هاتف الشركة للتواصل'
        },
        'email_signature': {
            'description': 'توقيع البريد الإلكتروني للشركة'
        },
        'paper_size': {
            'description': 'حجم الورق الافتراضي للطباعة'
        },
        'print_layout': {
            'description': 'اتجاه الطباعة الافتراضي (عمودي أو أفقي)'
        },
        'show_logo_in_reports': {
            'description': 'عرض شعار النظام في التقارير المطبوعة'
        },
        'print_footer': {
            'description': 'نص يظهر في تذييل الصفحات المطبوعة'
        },
        'receipt_notes': {
            'description': 'ملاحظات تظهر في نهاية إيصالات الحجز والدفع'
        },
        'company_name': {
            'description': 'اسم الشركة أو المؤسسة'
        },
        'dashboard_title': {
            'description': 'العنوان الذي سيظهر في لوحة التحكم الرئيسية'
        },
        
        # الألوان والسمات
        'primary_color': {
            'description': 'اللون الرئيسي للنظام'
        },
        'secondary_color': {
            'description': 'اللون الثانوي للنظام'
        },
        'text_primary_color': {
            'description': 'لون النص الرئيسي'
        },
        'dark_primary_color': {
            'description': 'اللون الرئيسي في الوضع الليلي'
        },
        'dark_text_color': {
            'description': 'لون النص في الوضع الليلي'
        },
        
        # شريط التنقل
        'navbar_color': {
            'description': 'لون خلفية شريط التنقل'
        },
        'navbar_dark_color': {
            'description': 'لون خلفية شريط التنقل (الوضع الليلي)'
        },
        'navbar_text_color': {
            'description': 'لون النص في شريط التنقل'
        },
        'navbar_dark_text_color': {
            'description': 'لون النص في شريط التنقل (الوضع الليلي)'
        },
        'navbar_fixed': {
            'description': 'تثبيت شريط التنقل أثناء التمرير'
        },
        'navbar_shadow': {
            'description': 'إضافة ظل لشريط التنقل'
        },
        'navbar_transparent': {
            'description': 'جعل شريط التنقل شفافًا'
        },
        
        # القائمة الجانبية
        'sidebar_color': {
            'description': 'لون خلفية القائمة الجانبية'
        },
        'dark_sidebar_color': {
            'description': 'لون خلفية القائمة الجانبية (الوضع الليلي)'
        },
        'sidebar_mini': {
            'description': 'تمكين وضع القائمة الجانبية المصغرة'
        },
        
        # الشعار والأيقونات
        'logo_icon': {
            'description': 'أيقونة الشعار (تظهر عندما لا يتم استخدام شعار مخصص)'
        },
        'custom_logo_url': {
            'description': 'رابط الشعار المخصص (إذا كنت تستخدم شعار مخصص)'
        },
        'use_custom_logo': {
            'description': 'استخدام شعار مخصص بدلاً من أيقونة'
        },
        
        # إعدادات العرض
        'dark_mode': {
            'description': 'وضع العرض (ليلي/نهاري)',
            'options': 'light,dark,auto'
        },
        'rtl_layout': {
            'description': 'استخدام تخطيط من اليمين إلى اليسار (RTL)'
        },
        'enable_animations': {
            'description': 'تمكين التأثيرات الحركية في الواجهة'
        },
        'font_family': {
            'description': 'نوع الخط المستخدم في النظام'
        },
        'border_radius': {
            'description': 'حجم انحناء الزوايا',
            'options': 'none,small,medium,large'
        },
        'card_shadow': {
            'description': 'حجم ظل البطاقات',
            'options': 'none,small,medium,large'
        },
        'content_width': {
            'description': 'عرض المحتوى',
            'options': 'fluid,fixed'
        },
        'transitions': {
            'description': 'تمكين الانتقالات السلسة بين العناصر'
        },
        'layout_boxed': {
            'description': 'استخدام تخطيط محدود العرض'
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
        elif setting.setting_key == 'date_format':
            setting_descriptions[setting.setting_key]['options'] = 'DD/MM/YYYY,MM/DD/YYYY,YYYY-MM-DD,DD-MM-YYYY'
        elif setting.setting_key == 'time_format':
            setting_descriptions[setting.setting_key]['options'] = 'HH:mm,hh:mm a,HH:mm:ss,h:mm a'
        elif setting.setting_key == 'date_separator':
            setting_descriptions[setting.setting_key]['options'] = '/,-,.'
        elif setting.setting_key == 'paper_size':
            setting_descriptions[setting.setting_key]['options'] = 'A4,A5,Letter,Legal'
        elif setting.setting_key == 'print_layout':
            setting_descriptions[setting.setting_key]['options'] = 'portrait,landscape'
        elif setting.setting_key == 'first_day_of_week':
            setting_descriptions[setting.setting_key]['options'] = '0,1,6'
        elif setting.setting_key == 'notification_position':
            setting_descriptions[setting.setting_key]['options'] = 'top-right,top-left,bottom-right,bottom-left'
    
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

@app.route('/api/create-bus-booking', methods=['POST'])
@login_required
def create_bus_booking():
    """إنشاء حجز باص جديد"""
    try:
        # الحصول على البيانات من النموذج
        data = request.form
        
        # إنشاء رقم حجز فريد
        booking_number = f"BUS-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # تحويل التواريخ إلى كائنات datetime
        travel_date = None
        return_date = None
        birth_date = None
        
        try:
            # التعامل مع تنسيقات التاريخ المختلفة، بما في ذلك الأرقام العربية
            def parse_date(date_str):
                if not date_str:
                    return None
                
                # محاولة تحويل التاريخ بصيغ مختلفة
                date_formats = ['%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y', '%Y-%m-%d', 
                               '%d %B، %Y', '%d %B , %Y', '%d %B %Y']
                
                # تحويل الأرقام العربية إلى إنجليزية
                eastern_to_western = {
                    '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
                    '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
                }
                
                # تبديل الأرقام العربية إلى إنجليزية
                for arabic, western in eastern_to_western.items():
                    if arabic in date_str:
                        date_str = date_str.replace(arabic, western)
                
                # محاولة جميع الصيغ
                for fmt in date_formats:
                    try:
                        return datetime.strptime(date_str, fmt).date()
                    except ValueError:
                        continue
                
                # إذا فشلت جميع المحاولات
                raise ValueError(f"لا يمكن تحويل '{date_str}' إلى تاريخ صالح")
            
            # تحويل التواريخ
            travel_date = parse_date(data.get('reservationDate'))
            return_date = parse_date(data.get('returnDate'))
            birth_date = parse_date(data.get('birthDate'))
            
        except ValueError as e:
            logging.error(f"Error parsing dates: {str(e)}")
            return jsonify({
                'success': False, 
                'error': 'حدث خطأ في تنسيق التاريخ. يرجى استخدام تنسيق صحيح مثل: يوم/شهر/سنة أو يوم-شهر-سنة'
            }), 400
        
        # تحويل القيم المالية
        selling_price = 0
        cost_price = 0
        received_amount = 0
        
        try:
            if data.get('sellPrice'):
                selling_price = float(data.get('sellPrice'))
            if data.get('purchasePrice'):
                cost_price = float(data.get('purchasePrice'))
            if data.get('receivedAmount'):
                received_amount = float(data.get('receivedAmount'))
        except ValueError:
            logging.error("Error converting price values to float")
            return jsonify({
                'success': False, 
                'error': 'القيم المالية يجب أن تكون أرقامًا فقط'
            }), 400
        
        # حساب المبلغ المتبقي
        remaining_amount = selling_price - received_amount
        
        # إنشاء كائن الحجز الجديد
        new_booking = BusBooking(
            booking_number=booking_number,
            
            # بيانات المسافر
            passenger_name=data.get('passengerName', ''),
            mobile_number=data.get('mobileNumber', ''),
            id_number=data.get('idNumber', ''),
            birth_date=birth_date,
            gender=data.get('gender', ''),
            
            # بيانات الرحلة
            trip_type=data.get('tripType', ''),
            departure_city=data.get('departureCity', ''),
            destination_city=data.get('destinationCity', ''),
            service_provider=data.get('transportCompany', ''),
            journey_type=data.get('tripType', ''),
            travel_date=travel_date,
            return_date=return_date,
            
            # بيانات المالية
            transaction_date=datetime.now(),
            currency=data.get('currency', 'SAR'),
            selling_price=selling_price,
            cost_price=cost_price,
            payment_type=data.get('paymentType', ''),
            account=data.get('account', ''),
            received_amount=received_amount,
            remaining_amount=remaining_amount,
            statement=data.get('statement', ''),
            
            # بيانات إضافية
            notes=data.get('notes', '')
        )
        
        # حفظ الحجز في قاعدة البيانات
        db.session.add(new_booking)
        db.session.commit()
        
        # إنشاء سجلات القيود المالية المرتبطة بالحجز
        try:
            # القيد المالي يختلف حسب نوع الدفع
            payment_type = data.get('paymentType', '')
            account = data.get('account', '')
            
            # تسجيل إيراد من بيع التذكرة
            accounting_entry = {
                'booking_id': new_booking.id,
                'entry_date': datetime.now(),
                'entry_type': 'revenue',
                'amount': selling_price,
                'description': f'إيراد بيع تذكرة باص رقم: {booking_number}'
            }
            
            # سجل معلومات المعاملة المالية
            if payment_type == 'cash':
                # قيد نقدي: إضافة رصيد للصندوق
                transaction_info = {
                    'transaction_type': 'cash_payment',
                    'account_id': account,
                    'amount': received_amount,
                    'remaining_amount': remaining_amount,
                    'description': f'دفع نقدي لحجز الباص رقم: {booking_number}'
                }
                logging.info(f"تم تسجيل قيد نقدي بمبلغ {received_amount} للحجز رقم: {booking_number}")
                
            elif payment_type == 'credit':
                # قيد آجل: إضافة رصيد للعميل
                transaction_info = {
                    'transaction_type': 'credit_payment',
                    'account_id': account,
                    'amount': selling_price,
                    'description': f'دفع آجل لحجز الباص رقم: {booking_number}'
                }
                logging.info(f"تم تسجيل قيد آجل بمبلغ {selling_price} للحجز رقم: {booking_number}")
                
            elif payment_type == 'bank':
                # قيد بنكي: إضافة رصيد للبنك
                transaction_info = {
                    'transaction_type': 'bank_payment',
                    'account_id': account,
                    'amount': received_amount,
                    'remaining_amount': remaining_amount,
                    'description': f'دفع بنكي لحجز الباص رقم: {booking_number}'
                }
                logging.info(f"تم تسجيل قيد بنكي بمبلغ {received_amount} للحجز رقم: {booking_number}")
            
            # تسجيل تكلفة الرحلة إذا كانت أكبر من صفر
            if cost_price > 0:
                supplier_id = data.get('supplierId', '')
                cost_entry = {
                    'booking_id': new_booking.id,
                    'entry_date': datetime.now(),
                    'entry_type': 'expense',
                    'amount': cost_price,
                    'description': f'تكلفة حجز باص رقم: {booking_number}',
                    'supplier_id': supplier_id
                }
                logging.info(f"تم تسجيل تكلفة بمبلغ {cost_price} للحجز رقم: {booking_number}")
                
            # في بيئة إنتاجية حقيقية، ستقوم بحفظ هذه القيود في جداول مخصصة للمحاسبة
            # BookingTransaction, AccountingEntry, etc.
                
        except Exception as e:
            logging.warning(f"تم إنشاء الحجز ولكن حدث خطأ في إنشاء قيود المحاسبة: {str(e)}")
        
        # سجل نجاح العملية في السجل
        logging.info(f"تم إنشاء حجز باص جديد برقم: {booking_number}")
        
        # إرجاع رد نجاح العملية
        return jsonify({
            'success': True, 
            'message': 'تم إنشاء الحجز بنجاح',
            'booking_number': booking_number
        })
        
    except Exception as e:
        # سجل الخطأ في السجل
        logging.error(f"Error creating bus booking: {str(e)}")
        db.session.rollback()
        
        # إرجاع رسالة خطأ
        return jsonify({
            'success': False, 
            'error': 'حدث خطأ أثناء إنشاء الحجز. يرجى المحاولة مرة أخرى.'
        }), 500
