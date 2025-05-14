"""
وحدة النماذج - تعريف جميع نماذج النظام
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms import SelectField, DateField, DecimalField, HiddenField, IntegerField, RadioField
from decimal import Decimal
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from wtforms.widgets import DateInput
from datetime import date

# نموذج تسجيل الدخول
class LoginForm(FlaskForm):
    """نموذج تسجيل الدخول"""
    username = StringField('اسم المستخدم', validators=[DataRequired(message='الرجاء إدخال اسم المستخدم')])
    password = PasswordField('كلمة المرور', validators=[DataRequired(message='الرجاء إدخال كلمة المرور')])
    remember_me = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')

# نموذج إنشاء مستخدم جديد
class CreateUserForm(FlaskForm):
    """نموذج إنشاء مستخدم جديد"""
    username = StringField('اسم المستخدم', validators=[
        DataRequired(message='الرجاء إدخال اسم المستخدم'),
        Length(min=4, message='اسم المستخدم يجب أن يكون 4 أحرف على الأقل')
    ])
    email = StringField('البريد الإلكتروني', validators=[
        DataRequired(message='الرجاء إدخال البريد الإلكتروني'),
        Email(message='الرجاء إدخال بريد إلكتروني صحيح')
    ])
    full_name = StringField('الاسم الكامل', validators=[DataRequired(message='الرجاء إدخال الاسم الكامل')])
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(message='الرجاء إدخال كلمة المرور'),
        Length(min=6, message='كلمة المرور يجب أن تكون 6 أحرف على الأقل')
    ])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[
        DataRequired(message='الرجاء تأكيد كلمة المرور'),
        EqualTo('password', message='كلمة المرور وتأكيدها غير متطابقين')
    ])
    is_admin = BooleanField('مسؤول النظام')
    active = BooleanField('مستخدم نشط', default=True)
    submit = SubmitField('إنشاء المستخدم')

# نموذج تعديل مستخدم
class EditUserForm(FlaskForm):
    """نموذج تعديل بيانات مستخدم"""
    username = StringField('اسم المستخدم', render_kw={'readonly': True})
    email = StringField('البريد الإلكتروني', validators=[
        DataRequired(message='الرجاء إدخال البريد الإلكتروني'),
        Email(message='الرجاء إدخال بريد إلكتروني صحيح')
    ])
    full_name = StringField('الاسم الكامل', validators=[DataRequired(message='الرجاء إدخال الاسم الكامل')])
    password = PasswordField('كلمة المرور الجديدة (اترك فارغاً للاحتفاظ بالحالية)', validators=[
        Optional(),
        Length(min=6, message='كلمة المرور يجب أن تكون 6 أحرف على الأقل')
    ])
    confirm_password = PasswordField('تأكيد كلمة المرور الجديدة', validators=[
        EqualTo('password', message='كلمة المرور وتأكيدها غير متطابقين')
    ])
    is_admin = BooleanField('مسؤول النظام')
    active = BooleanField('مستخدم نشط')
    submit = SubmitField('حفظ التغييرات')

# نموذج تغيير كلمة المرور
class ChangePasswordForm(FlaskForm):
    """نموذج تغيير كلمة المرور"""
    current_password = PasswordField('كلمة المرور الحالية', validators=[
        DataRequired(message='الرجاء إدخال كلمة المرور الحالية')
    ])
    new_password = PasswordField('كلمة المرور الجديدة', validators=[
        DataRequired(message='الرجاء إدخال كلمة المرور الجديدة'),
        Length(min=6, message='كلمة المرور يجب أن تكون 6 أحرف على الأقل')
    ])
    confirm_password = PasswordField('تأكيد كلمة المرور الجديدة', validators=[
        DataRequired(message='الرجاء تأكيد كلمة المرور الجديدة'),
        EqualTo('new_password', message='كلمة المرور وتأكيدها غير متطابقين')
    ])
    submit = SubmitField('تغيير كلمة المرور')

# نموذج بيانات العميل
class CustomerForm(FlaskForm):
    """نموذج بيانات العميل"""
    full_name = StringField('الاسم الكامل', validators=[DataRequired(message='الرجاء إدخال اسم العميل')])
    mobile = StringField('رقم الجوال', validators=[DataRequired(message='الرجاء إدخال رقم الجوال')])
    email = StringField('البريد الإلكتروني', validators=[
        Optional(),
        Email(message='الرجاء إدخال بريد إلكتروني صحيح')
    ])
    id_type = SelectField('نوع الهوية', validators=[DataRequired(message='الرجاء اختيار نوع الهوية')])
    id_number = StringField('رقم الهوية', validators=[DataRequired(message='الرجاء إدخال رقم الهوية')])
    nationality = StringField('الجنسية', validators=[DataRequired(message='الرجاء إدخال الجنسية')])
    birth_date = DateField('تاريخ الميلاد', widget=DateInput(), validators=[Optional()])
    gender = SelectField('الجنس', choices=[('male', 'ذكر'), ('female', 'أنثى')], validators=[Optional()])
    address = TextAreaField('العنوان', validators=[Optional()])
    id_issue_date = DateField('تاريخ الإصدار', widget=DateInput(), validators=[Optional()])
    id_expiry_date = DateField('تاريخ الانتهاء', widget=DateInput(), validators=[Optional()])
    id_issue_place = StringField('مكان الإصدار', validators=[Optional()])
    notes = TextAreaField('ملاحظات', validators=[Optional()])
    submit = SubmitField('حفظ')

    def validate_id_expiry_date(self, field):
        """التحقق من تاريخ انتهاء الهوية"""
        if field.data and field.data < date.today():
            raise ValidationError('تاريخ انتهاء الهوية منتهي الصلاحية')

# نموذج حجز حافلة
class BusBookingForm(FlaskForm):
    """نموذج حجز حافلة"""
    # بيانات المسافر
    passenger_name = StringField('اسم المسافر', validators=[DataRequired(message='الرجاء إدخال اسم المسافر')])
    mobile_number = StringField('رقم الجوال', validators=[DataRequired(message='الرجاء إدخال رقم الجوال')])
    id_number = StringField('رقم الهوية', validators=[Optional()])
    birth_date = DateField('تاريخ الميلاد', widget=DateInput(), validators=[Optional()])
    gender = SelectField('الجنس', choices=[('male', 'ذكر'), ('female', 'أنثى')], validators=[Optional()])
    
    # بيانات الحجز
    trip_type = SelectField('نوع الرحلة', choices=[('regular', 'عادي'), ('tourism', 'سياحي')])
    departure_city = SelectField('مدينة المغادرة', validators=[DataRequired(message='الرجاء اختيار مدينة المغادرة')])
    destination_city = SelectField('مدينة الوصول', validators=[DataRequired(message='الرجاء اختيار مدينة الوصول')])
    service_provider = SelectField('مزود الخدمة', validators=[DataRequired(message='الرجاء اختيار مزود الخدمة')])
    journey_type = SelectField('نوع الرحلة', choices=[('one_way', 'ذهاب فقط'), ('round_trip', 'ذهاب وعودة')])
    travel_date = DateField('تاريخ السفر', widget=DateInput(), validators=[DataRequired(message='الرجاء اختيار تاريخ السفر')])
    return_date = DateField('تاريخ العودة', widget=DateInput(), validators=[Optional()])
    
    # البيانات المالية
    currency = SelectField('العملة', validators=[DataRequired(message='الرجاء اختيار العملة')])
    selling_price = DecimalField('سعر البيع', validators=[DataRequired(message='الرجاء إدخال سعر البيع')])
    cost_price = DecimalField('سعر التكلفة', validators=[DataRequired(message='الرجاء إدخال سعر التكلفة')])
    payment_type = SelectField('نوع الدفع', choices=[
        ('cash', 'نقداً'), 
        ('credit', 'آجل'), 
        ('bank_transfer', 'تحويل بنكي')
    ])
    account = SelectField('الحساب', validators=[DataRequired(message='الرجاء اختيار الحساب')])
    received_amount = DecimalField('المبلغ المستلم', default=Decimal('0'))
    statement = TextAreaField('البيان', validators=[Optional()])
    
    submit = SubmitField('حفظ الحجز')
    
    def validate_return_date(self, field):
        """التحقق من تاريخ العودة إذا كانت الرحلة ذهاب وعودة"""
        if self.journey_type.data == 'round_trip' and not field.data:
            raise ValidationError('الرجاء إدخال تاريخ العودة للرحلات ذهاب وعودة')
        if field.data and self.travel_date.data and field.data < self.travel_date.data:
            raise ValidationError('تاريخ العودة يجب أن يكون بعد تاريخ السفر')

# نموذج سند قبض
class ReceiptVoucherForm(FlaskForm):
    """نموذج سند قبض"""
    transaction_date = DateField('تاريخ السند', widget=DateInput(), default=date.today, 
                                validators=[DataRequired(message='الرجاء إدخال تاريخ السند')])
    account_id = SelectField('الحساب', coerce=int, validators=[DataRequired(message='الرجاء اختيار الحساب')])
    amount = DecimalField('المبلغ', validators=[DataRequired(message='الرجاء إدخال المبلغ')])
    currency_id = SelectField('العملة', coerce=int, validators=[DataRequired(message='الرجاء اختيار العملة')])
    payment_method = SelectField('طريقة الدفع', choices=[
        ('cash', 'نقداً'), 
        ('bank_transfer', 'تحويل بنكي'),
        ('check', 'شيك'),
        ('credit_card', 'بطاقة ائتمان')
    ])
    reference_number = StringField('رقم المرجع', validators=[Optional()])
    description = TextAreaField('البيان', validators=[DataRequired(message='الرجاء إدخال البيان')])
    cash_register_id = SelectField('الصندوق', coerce=int)
    submit = SubmitField('حفظ')

# نموذج سند صرف
class PaymentVoucherForm(FlaskForm):
    """نموذج سند صرف"""
    transaction_date = DateField('تاريخ السند', widget=DateInput(), default=date.today, 
                                validators=[DataRequired(message='الرجاء إدخال تاريخ السند')])
    account_id = SelectField('الحساب', coerce=int, validators=[DataRequired(message='الرجاء اختيار الحساب')])
    amount = DecimalField('المبلغ', validators=[DataRequired(message='الرجاء إدخال المبلغ')])
    currency_id = SelectField('العملة', coerce=int, validators=[DataRequired(message='الرجاء اختيار العملة')])
    payment_method = SelectField('طريقة الدفع', choices=[
        ('cash', 'نقداً'), 
        ('bank_transfer', 'تحويل بنكي'),
        ('check', 'شيك'),
        ('credit_card', 'بطاقة ائتمان')
    ])
    reference_number = StringField('رقم المرجع', validators=[Optional()])
    description = TextAreaField('البيان', validators=[DataRequired(message='الرجاء إدخال البيان')])
    cash_register_id = SelectField('الصندوق', coerce=int)
    submit = SubmitField('حفظ')

# نموذج قيد يومية محاسبي
class JournalEntryForm(FlaskForm):
    """نموذج قيد يومية محاسبي"""
    transaction_date = DateField('تاريخ القيد', widget=DateInput(), default=date.today, 
                              validators=[DataRequired(message='الرجاء إدخال تاريخ القيد')])
    reference_number = StringField('رقم المرجع', validators=[Optional()])
    description = TextAreaField('البيان', validators=[DataRequired(message='الرجاء إدخال البيان')])
    currency_id = SelectField('العملة', coerce=int, validators=[DataRequired(message='الرجاء اختيار العملة')])
    submit = SubmitField('حفظ')

# نموذج بند قيد محاسبي
class JournalLineForm(FlaskForm):
    """نموذج بند قيد محاسبي"""
    account_id = SelectField('الحساب', coerce=int, validators=[DataRequired(message='الرجاء اختيار الحساب')])
    debit_amount = DecimalField('مدين', default=0.0)
    credit_amount = DecimalField('دائن', default=0.0)
    description = TextAreaField('البيان', validators=[Optional()])
    submit = SubmitField('إضافة البند')