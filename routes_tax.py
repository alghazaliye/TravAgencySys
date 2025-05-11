"""
مسارات خاصة بإدارة التقارير الضريبية
"""
import os
import json
import uuid
from datetime import datetime, date, time, timedelta
from flask import render_template, request, jsonify, flash, redirect, url_for, Response
from flask_login import login_required, current_user
from sqlalchemy import desc, and_, or_, func
import tempfile
import logging

from app import app, db
from models import Account, JournalEntry, JournalLine, AccountTransaction, TaxReport, TaxReportDetail, TaxSettings

# تكوين سجل الأحداث
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/tax/management', methods=['GET'])
@login_required
def tax_management():
    """صفحة إدارة التقارير الضريبية"""
    # استلام المعلمات من الاستعلام
    selected_year = int(request.args.get('year', datetime.now().year))
    selected_tax_type = request.args.get('tax_type', 'all')
    selected_status = request.args.get('status', 'all')
    
    # إنشاء استعلام أساسي
    query = TaxReport.query
    
    # تطبيق المرشحات
    query = query.filter(TaxReport.year == selected_year)
    
    if selected_tax_type != 'all':
        query = query.filter(TaxReport.report_type == selected_tax_type)
    
    if selected_status != 'all':
        query = query.filter(TaxReport.status == selected_status)
    
    # جلب التقارير الضريبية
    tax_reports = query.order_by(desc(TaxReport.end_date)).all()
    
    # حساب إجمالي ضريبة القيمة المضافة المستحقة
    total_vat_due = db.session.query(func.sum(TaxReport.net_vat)).filter(
        TaxReport.report_type == 'VAT',
        TaxReport.year == selected_year,
        TaxReport.status.in_(['submitted', 'approved'])
    ).scalar() or 0
    
    # حساب إجمالي ضريبة المدخلات
    total_input_vat = db.session.query(func.sum(TaxReport.vat_on_purchases)).filter(
        TaxReport.report_type == 'VAT',
        TaxReport.year == selected_year
    ).scalar() or 0
    
    # حساب إجمالي ضريبة المخرجات
    total_output_vat = db.session.query(func.sum(TaxReport.vat_on_sales)).filter(
        TaxReport.report_type == 'VAT',
        TaxReport.year == selected_year
    ).scalar() or 0
    
    # حساب عدد التقارير المتأخرة
    today = date.today()
    overdue_reports = db.session.query(func.count(TaxReport.id)).filter(
        TaxReport.report_type == 'VAT',
        TaxReport.end_date < today,
        TaxReport.status == 'draft'
    ).scalar() or 0
    
    # إعداد بيانات الرسوم البيانية لاتجاهات ضريبة القيمة المضافة
    vat_trends = {
        'labels': [],
        'output_vat': [],
        'input_vat': [],
        'net_vat': []
    }
    
    # جلب البيانات الربع سنوية لضريبة القيمة المضافة
    quarters = ['الربع الأول', 'الربع الثاني', 'الربع الثالث', 'الربع الرابع']
    
    for quarter in range(1, 5):
        vat_trends['labels'].append(quarters[quarter-1])
        
        # البحث عن تقرير ربع سنوي
        quarterly_report = TaxReport.query.filter(
            TaxReport.report_type == 'VAT',
            TaxReport.year == selected_year,
            TaxReport.quarter == quarter
        ).first()
        
        if quarterly_report:
            vat_trends['output_vat'].append(float(quarterly_report.vat_on_sales))
            vat_trends['input_vat'].append(float(quarterly_report.vat_on_purchases))
            vat_trends['net_vat'].append(float(quarterly_report.net_vat))
        else:
            # إذا لم يكن هناك تقرير، استخدم القيم المجمعة من التقارير الشهرية
            output_vat = db.session.query(func.sum(TaxReport.vat_on_sales)).filter(
                TaxReport.report_type == 'VAT',
                TaxReport.year == selected_year,
                TaxReport.month.in_([(quarter-1)*3+1, (quarter-1)*3+2, (quarter-1)*3+3])
            ).scalar() or 0
            
            input_vat = db.session.query(func.sum(TaxReport.vat_on_purchases)).filter(
                TaxReport.report_type == 'VAT',
                TaxReport.year == selected_year,
                TaxReport.month.in_([(quarter-1)*3+1, (quarter-1)*3+2, (quarter-1)*3+3])
            ).scalar() or 0
            
            net_vat = float(output_vat) - float(input_vat)
            
            vat_trends['output_vat'].append(float(output_vat))
            vat_trends['input_vat'].append(float(input_vat))
            vat_trends['net_vat'].append(net_vat)
    
    return render_template('tax-management.html',
                           current_year=datetime.now().year,
                           selected_year=selected_year,
                           selected_tax_type=selected_tax_type,
                           selected_status=selected_status,
                           tax_reports=tax_reports,
                           total_vat_due=total_vat_due,
                           total_input_vat=total_input_vat,
                           total_output_vat=total_output_vat,
                           overdue_reports=overdue_reports,
                           vat_trends=vat_trends)


@app.route('/tax/create', methods=['GET', 'POST'])
@login_required
def create_tax_report():
    """إنشاء تقرير ضريبي جديد"""
    if request.method == 'POST':
        # جلب البيانات من النموذج
        report_type = request.form.get('report_type')
        period_type = request.form.get('period_type')
        year = int(request.form.get('year'))
        month = None
        quarter = None
        
        if period_type == 'monthly':
            month = int(request.form.get('month'))
        elif period_type == 'quarterly':
            quarter = int(request.form.get('quarter'))
        
        # تحديد تاريخ بداية ونهاية الفترة
        start_date = None
        end_date = None
        
        if period_type == 'monthly':
            # الفترة الشهرية
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year, 12, 31)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
        elif period_type == 'quarterly':
            # الفترة ربع السنوية
            start_month = (quarter - 1) * 3 + 1
            end_month = start_month + 2
            start_date = date(year, start_month, 1)
            if end_month == 12:
                end_date = date(year, 12, 31)
            else:
                end_date = date(year, end_month + 1, 1) - timedelta(days=1)
        else:
            # الفترة السنوية
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
        
        # جلب البيانات المالية من النموذج
        total_sales = float(request.form.get('total_sales') or 0)
        vat_on_sales = float(request.form.get('vat_on_sales') or 0)
        total_purchases = float(request.form.get('total_purchases') or 0)
        vat_on_purchases = float(request.form.get('vat_on_purchases') or 0)
        net_vat = float(request.form.get('net_vat') or 0)
        status = request.form.get('status', 'draft')
        reference_number = request.form.get('reference_number')
        notes = request.form.get('notes')
        
        # التحقق من وجود تقرير مشابه
        existing_report = TaxReport.query.filter(
            TaxReport.report_type == report_type,
            TaxReport.year == year,
            TaxReport.month == month,
            TaxReport.quarter == quarter
        ).first()
        
        if existing_report:
            flash('يوجد تقرير ضريبي مشابه لنفس الفترة!', 'warning')
            return redirect(url_for('create_tax_report'))
        
        # إنشاء تقرير ضريبي جديد
        new_report = TaxReport(
            report_type=report_type,
            year=year,
            month=month,
            quarter=quarter,
            start_date=start_date,
            end_date=end_date,
            total_sales=total_sales,
            total_purchases=total_purchases,
            vat_on_sales=vat_on_sales,
            vat_on_purchases=vat_on_purchases,
            net_vat=net_vat,
            status=status,
            reference_number=reference_number,
            notes=notes,
            created_by=current_user.id
        )
        
        if status == 'submitted' or status == 'approved':
            new_report.submission_date = datetime.now()
        
        db.session.add(new_report)
        db.session.commit()
        
        flash('تم إنشاء التقرير الضريبي بنجاح!', 'success')
        return redirect(url_for('tax_management'))
    
    # جلب معدل ضريبة القيمة المضافة
    vat_rate = TaxSettings.get_vat_rate()
    
    return render_template('tax-report-form.html',
                           current_year=datetime.now().year,
                           report=None,
                           title='إنشاء تقرير ضريبي جديد',
                           action='create',
                           vat_rate=vat_rate)


@app.route('/tax/edit/<int:report_id>', methods=['GET', 'POST'])
@login_required
def edit_tax_report(report_id):
    """تعديل تقرير ضريبي موجود"""
    report = TaxReport.query.get_or_404(report_id)
    
    if request.method == 'POST':
        # جلب البيانات من النموذج
        report_type = request.form.get('report_type')
        period_type = request.form.get('period_type')
        year = int(request.form.get('year'))
        month = None
        quarter = None
        
        if period_type == 'monthly':
            month = int(request.form.get('month'))
        elif period_type == 'quarterly':
            quarter = int(request.form.get('quarter'))
        
        # تحديد تاريخ بداية ونهاية الفترة
        start_date = None
        end_date = None
        
        if period_type == 'monthly':
            # الفترة الشهرية
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year, 12, 31)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
        elif period_type == 'quarterly':
            # الفترة ربع السنوية
            start_month = (quarter - 1) * 3 + 1
            end_month = start_month + 2
            start_date = date(year, start_month, 1)
            if end_month == 12:
                end_date = date(year, 12, 31)
            else:
                end_date = date(year, end_month + 1, 1) - timedelta(days=1)
        else:
            # الفترة السنوية
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
        
        # جلب البيانات المالية من النموذج
        total_sales = float(request.form.get('total_sales') or 0)
        vat_on_sales = float(request.form.get('vat_on_sales') or 0)
        total_purchases = float(request.form.get('total_purchases') or 0)
        vat_on_purchases = float(request.form.get('vat_on_purchases') or 0)
        net_vat = float(request.form.get('net_vat') or 0)
        status = request.form.get('status', 'draft')
        reference_number = request.form.get('reference_number')
        notes = request.form.get('notes')
        
        # التحقق من وجود تقرير مشابه (غير التقرير الحالي)
        existing_report = TaxReport.query.filter(
            TaxReport.report_type == report_type,
            TaxReport.year == year,
            TaxReport.month == month,
            TaxReport.quarter == quarter,
            TaxReport.id != report_id
        ).first()
        
        if existing_report:
            flash('يوجد تقرير ضريبي مشابه لنفس الفترة!', 'warning')
            return redirect(url_for('edit_tax_report', report_id=report_id))
        
        # تحديث التقرير الضريبي
        report.report_type = report_type
        report.year = year
        report.month = month
        report.quarter = quarter
        report.start_date = start_date
        report.end_date = end_date
        report.total_sales = total_sales
        report.total_purchases = total_purchases
        report.vat_on_sales = vat_on_sales
        report.vat_on_purchases = vat_on_purchases
        report.net_vat = net_vat
        
        # تحديث حالة التقرير
        old_status = report.status
        report.status = status
        
        # إذا تم تغيير الحالة إلى مقدم أو معتمد، قم بتحديث تاريخ التقديم
        if (status == 'submitted' or status == 'approved') and old_status == 'draft':
            report.submission_date = datetime.now()
        
        report.reference_number = reference_number
        report.notes = notes
        
        db.session.commit()
        
        flash('تم تحديث التقرير الضريبي بنجاح!', 'success')
        return redirect(url_for('tax_management'))
    
    # جلب معدل ضريبة القيمة المضافة
    vat_rate = TaxSettings.get_vat_rate()
    
    return render_template('tax-report-form.html',
                           current_year=datetime.now().year,
                           report=report,
                           title='تعديل التقرير الضريبي',
                           action='edit',
                           vat_rate=vat_rate)


@app.route('/tax/view/<int:report_id>')
@login_required
def view_tax_report(report_id):
    """عرض تفاصيل التقرير الضريبي"""
    report = TaxReport.query.get_or_404(report_id)
    
    # جلب تفاصيل التقرير
    details = TaxReportDetail.query.filter_by(tax_report_id=report_id).order_by(TaxReportDetail.transaction_date).all()
    
    # إعداد بيانات للرسم البياني
    chart_data = {
        'labels': ['ضريبة المخرجات', 'ضريبة المدخلات'],
        'values': [float(report.vat_on_sales), float(report.vat_on_purchases)]
    }
    
    return render_template('tax-report-details.html',
                           report=report,
                           details=details,
                           chart_data=chart_data)


@app.route('/tax/delete/<int:report_id>', methods=['POST'])
@login_required
def delete_tax_report(report_id):
    """حذف تقرير ضريبي"""
    report = TaxReport.query.get_or_404(report_id)
    
    # لا يمكن حذف التقارير المقدمة أو المعتمدة
    if report.status in ['submitted', 'approved']:
        flash('لا يمكن حذف التقارير المقدمة أو المعتمدة!', 'danger')
        return redirect(url_for('tax_management'))
    
    # حذف تفاصيل التقرير أولاً
    TaxReportDetail.query.filter_by(tax_report_id=report_id).delete()
    
    # ثم حذف التقرير نفسه
    db.session.delete(report)
    db.session.commit()
    
    flash('تم حذف التقرير الضريبي بنجاح!', 'success')
    return redirect(url_for('tax_management'))


@app.route('/tax/generate-pdf/<int:report_id>')
@login_required
def generate_tax_report_pdf(report_id):
    """توليد ملف PDF للتقرير الضريبي"""
    report = TaxReport.query.get_or_404(report_id)
    
    try:
        import io
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # إعداد الخط العربي
        # تحميل خط عربي (يجب توفيره في المشروع)
        arabic_font_path = os.path.join(app.root_path, 'static', 'fonts', 'NotoSansArabic-Regular.ttf')
        if os.path.exists(arabic_font_path):
            pdfmetrics.registerFont(TTFont('Arabic', arabic_font_path))
        else:
            # استخدام خط افتراضي إذا لم يتم العثور على الخط العربي
            logger.warning("لم يتم العثور على ملف الخط العربي. سيتم استخدام الخط الافتراضي.")
        
        # إنشاء بيانات PDF في الذاكرة
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        
        # إعداد الصفحة
        width, height = A4
        
        # استخدام الخط العربي إذا كان متاحًا
        if os.path.exists(arabic_font_path):
            p.setFont('Arabic', 14)
        else:
            p.setFont('Helvetica', 14)
        
        # عنوان التقرير
        p.drawString(width - 150, height - 50, "تقرير ضريبة القيمة المضافة")
        
        # معلومات التقرير
        p.setFont('Helvetica', 12)
        p.drawString(width - 150, height - 80, f"الفترة: {report.period_name}")
        p.drawString(width - 150, height - 100, f"من: {report.start_date.strftime('%Y-%m-%d')}")
        p.drawString(width - 150, height - 120, f"إلى: {report.end_date.strftime('%Y-%m-%d')}")
        p.drawString(width - 150, height - 140, f"الحالة: {report.status}")
        
        # بيانات الضريبة
        p.drawString(width - 150, height - 180, f"إجمالي المبيعات: {report.total_sales} ريال")
        p.drawString(width - 150, height - 200, f"ضريبة المخرجات: {report.vat_on_sales} ريال")
        p.drawString(width - 150, height - 220, f"إجمالي المشتريات: {report.total_purchases} ريال")
        p.drawString(width - 150, height - 240, f"ضريبة المدخلات: {report.vat_on_purchases} ريال")
        p.drawString(width - 150, height - 260, f"صافي الضريبة: {report.net_vat} ريال")
        
        # معلومات إضافية
        if report.reference_number:
            p.drawString(width - 150, height - 300, f"رقم المرجع: {report.reference_number}")
        
        if report.submission_date:
            p.drawString(width - 150, height - 320, f"تاريخ التقديم: {report.submission_date.strftime('%Y-%m-%d')}")
        
        if report.notes:
            p.drawString(width - 150, height - 350, "ملاحظات:")
            # تقسيم الملاحظات إلى أسطر متعددة إذا كانت طويلة
            lines = report.notes.split('\n')
            y_position = height - 370
            for line in lines:
                p.drawString(width - 170, y_position, line)
                y_position -= 20
        
        # إنهاء الصفحة وإغلاق PDF
        p.showPage()
        p.save()
        
        buffer.seek(0)
        
        # إرجاع ملف PDF
        return Response(
            buffer.getvalue(),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment;filename=tax_report_{report_id}.pdf',
                'Content-Type': 'application/pdf'
            }
        )
    
    except Exception as e:
        logger.error(f"خطأ أثناء إنشاء ملف PDF: {str(e)}")
        flash('حدث خطأ أثناء إنشاء ملف PDF.', 'danger')
        return redirect(url_for('view_tax_report', report_id=report_id))


@app.route('/tax/settings', methods=['GET', 'POST'])
@login_required
def tax_settings():
    """إعدادات الضرائب"""
    if request.method == 'POST':
        # جلب البيانات من النموذج
        vat_rate = float(request.form.get('vat_rate'))
        company_tax_number = request.form.get('company_tax_number')
        tax_authority = request.form.get('tax_authority', 'هيئة الزكاة والضريبة والجمارك')
        reporting_frequency = request.form.get('reporting_frequency', 'quarterly')
        
        # البحث عن إعدادات ضريبة القيمة المضافة
        vat_settings = TaxSettings.query.filter_by(tax_type='VAT').first()
        
        if vat_settings:
            # تحديث الإعدادات الموجودة
            vat_settings.tax_rate = vat_rate
            vat_settings.company_tax_number = company_tax_number
            vat_settings.tax_authority = tax_authority
            vat_settings.reporting_frequency = reporting_frequency
        else:
            # إنشاء إعدادات جديدة
            vat_settings = TaxSettings(
                tax_type='VAT',
                tax_rate=vat_rate,
                company_tax_number=company_tax_number,
                tax_authority=tax_authority,
                reporting_frequency=reporting_frequency,
                is_active=True,
                description='ضريبة القيمة المضافة'
            )
            db.session.add(vat_settings)
        
        db.session.commit()
        
        flash('تم حفظ إعدادات الضريبة بنجاح!', 'success')
        return redirect(url_for('tax_settings'))
    
    # جلب إعدادات الضريبة الحالية
    vat_settings = TaxSettings.query.filter_by(tax_type='VAT').first()
    
    if not vat_settings:
        # إنشاء إعدادات افتراضية
        vat_settings = {
            'tax_rate': 15.0,
            'company_tax_number': '',
            'tax_authority': 'هيئة الزكاة والضريبة والجمارك',
            'reporting_frequency': 'quarterly'
        }
    
    return render_template('tax-settings.html',
                           vat_settings=vat_settings)


def seed_tax_settings():
    """تهيئة إعدادات الضرائب الأساسية"""
    # التحقق من وجود إعدادات ضريبة القيمة المضافة
    vat_settings = TaxSettings.query.filter_by(tax_type='VAT').first()
    
    if not vat_settings:
        # إنشاء إعدادات ضريبة القيمة المضافة الافتراضية
        vat_settings = TaxSettings(
            tax_type='VAT',
            tax_rate=15.0,
            company_tax_number='',
            tax_authority='هيئة الزكاة والضريبة والجمارك',
            reporting_frequency='quarterly',
            is_active=True,
            description='ضريبة القيمة المضافة'
        )
        db.session.add(vat_settings)
        db.session.commit()
        logger.info("تم إنشاء إعدادات ضريبة القيمة المضافة الافتراضية")
    
    return True