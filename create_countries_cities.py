from app import db, Country, City
from datetime import datetime

def create_countries_and_cities():
    """إنشاء بيانات الدول والمدن"""
    print("بدء إنشاء جداول الدول والمدن...")
    
    # تأكد من وجود جداول قاعدة البيانات
    db.create_all()

    # إنشاء سجلات الدول
    countries = [
        {"name": "المملكة العربية السعودية"},
        {"name": "الإمارات العربية المتحدة"},
        {"name": "مصر"},
        {"name": "قطر"},
        {"name": "الكويت"},
        {"name": "الأردن"}
    ]
    
    # إضافة الدول إلى قاعدة البيانات
    created_countries = {}
    for country_data in countries:
        # التحقق مما إذا كانت الدولة موجودة بالفعل
        country = Country.query.filter_by(name=country_data["name"]).first()
        if not country:
            country = Country(
                name=country_data["name"],
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(country)
            db.session.flush()  # للحصول على معرف الدولة
            print(f"تمت إضافة دولة: {country.name} (معرف: {country.id})")
        created_countries[country.name] = country.id
    
    # تطبيق التغييرات
    db.session.commit()
    
    # إنشاء سجلات المدن
    cities = [
        {"name": "الرياض", "country_name": "المملكة العربية السعودية"},
        {"name": "جدة", "country_name": "المملكة العربية السعودية"},
        {"name": "مكة المكرمة", "country_name": "المملكة العربية السعودية"},
        {"name": "المدينة المنورة", "country_name": "المملكة العربية السعودية"},
        {"name": "الدمام", "country_name": "المملكة العربية السعودية"},
        
        {"name": "دبي", "country_name": "الإمارات العربية المتحدة"},
        {"name": "أبو ظبي", "country_name": "الإمارات العربية المتحدة"},
        {"name": "الشارقة", "country_name": "الإمارات العربية المتحدة"},
        
        {"name": "القاهرة", "country_name": "مصر"},
        {"name": "الإسكندرية", "country_name": "مصر"},
        {"name": "شرم الشيخ", "country_name": "مصر"},
        
        {"name": "الدوحة", "country_name": "قطر"},
        
        {"name": "مدينة الكويت", "country_name": "الكويت"},
        
        {"name": "عمان", "country_name": "الأردن"}
    ]
    
    # إضافة المدن إلى قاعدة البيانات
    for city_data in cities:
        # التحقق مما إذا كانت المدينة موجودة بالفعل
        city = City.query.filter_by(name=city_data["name"], 
                                   country_id=created_countries[city_data["country_name"]]).first()
        if not city:
            city = City(
                name=city_data["name"],
                country_id=created_countries[city_data["country_name"]],
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(city)
            print(f"تمت إضافة مدينة: {city.name} (الدولة: {city_data['country_name']})")
    
    # تطبيق التغييرات
    db.session.commit()
    print("تم الانتهاء من إنشاء جداول الدول والمدن بنجاح!")

if __name__ == "__main__":
    create_countries_and_cities()