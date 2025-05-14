# تكوين قاعدة البيانات

## الوصف
تم تحديث النظام ليدعم نوعين من قواعد البيانات:
1. **PostgreSQL** (الإعداد الافتراضي)
2. **MySQL**

## كيفية التبديل بين أنواع قواعد البيانات
يمكن التبديل بين أنواع قواعد البيانات عن طريق ضبط متغير البيئة `DB_TYPE`.

### لاستخدام MySQL
```
export DB_TYPE=mysql
export MYSQL_HOST=host_server
export MYSQL_PORT=3306
export DB_USER=mysql_user
export DB_PASSWORD=mysql_password
export DB_DATABASE=travelagency
```

### لاستخدام PostgreSQL (الافتراضي)
```
export DB_TYPE=postgresql  # أو احذف متغير البيئة DB_TYPE تمامًا
export DB_HOST=localhost  # أو استخدم DATABASE_URL مباشرة
export POSTGRES_PORT=5432
export DB_USER=postgres_user
export DB_PASSWORD=postgres_password
export DB_DATABASE=travelagency
```

## ملاحظات هامة
- النظام يستخدم تلقائيًا متغير البيئة `DATABASE_URL` إذا كان موجودًا عند استخدام PostgreSQL
- يمكن استخدام الإعدادات الافتراضية إذا لم يتم توفير متغيرات البيئة المطلوبة
- يجب التأكد من تثبيت المكتبات الضرورية لنوع قاعدة البيانات المستخدم