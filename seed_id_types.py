"""
إنشاء البيانات الأساسية لجدول أنواع الهوية
"""
from app import app, db
from models import IdentityType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_identity_types():
    """إنشاء البيانات الأساسية لجدول أنواع الهوية"""
    try:
        # التحقق من وجود بيانات في جدول أنواع الهوية
        if IdentityType.query.count() > 0:
            logger.info("جدول أنواع الهوية يحتوي على بيانات بالفعل")
            return
        
        # قائمة بأنواع الهوية الأساسية
        identity_types_data = [
            {
                'name': 'جواز سفر',
                'requires_nationality': True,
                'description': 'جواز سفر لأي دولة',
                'is_active': True
            },
            {
                'name': 'بطاقة هوية وطنية',
                'requires_nationality': False,
                'description': 'بطاقة الهوية الوطنية للمواطنين',
                'is_active': True
            },
            {
                'name': 'إقامة',
                'requires_nationality': True,
                'description': 'إقامة للمقيمين',
                'is_active': True
            },
            {
                'name': 'رخصة قيادة',
                'requires_nationality': False,
                'description': 'رخصة قيادة محلية أو دولية',
                'is_active': True
            },
            {
                'name': 'تأشيرة',
                'requires_nationality': True,
                'description': 'تأشيرة زيارة أو عمل',
                'is_active': True
            }
        ]
        
        # إضافة البيانات
        for type_data in identity_types_data:
            identity_type = IdentityType()
            identity_type.name = type_data['name']
            identity_type.requires_nationality = type_data['requires_nationality']
            identity_type.description = type_data['description']
            identity_type.is_active = type_data['is_active']
            db.session.add(identity_type)
        
        db.session.commit()
        logger.info("تم إنشاء البيانات الأساسية لجدول أنواع الهوية بنجاح")
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"حدث خطأ أثناء إنشاء البيانات الأساسية لجدول أنواع الهوية: {str(e)}")

# تنفيذ الدالة إذا تم تشغيل الملف مباشرة
if __name__ == '__main__':
    with app.app_context():
        seed_identity_types()