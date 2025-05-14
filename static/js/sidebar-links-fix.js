/**
 * إصلاح شامل لجميع روابط القائمة الجانبية
 * 
 * هذا الملف يعالج مشكلة عدم عمل روابط القائمة الجانبية
 * من خلال منع السلوك الافتراضي للروابط وإعادة التوجيه البرمجي
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('جارٍ تطبيق إصلاح روابط القائمة الجانبية...');
    
    // قائمة بجميع روابط القائمة التي تحتاج لإصلاح
    const sidebarLinks = [
        // الروابط الرئيسية
        { text: 'لوحة التحكم', route: '/' },
        { text: 'الحجوزات', isParent: true },
        { text: 'التأشيرات', isParent: true },
        { text: 'العملاء', route: '/customers' },
        { text: 'المالية', isParent: true },
        { text: 'التقارير', route: '/reports' },
        { text: 'الإعدادات', isParent: true },
        
        // تذاكر حجوزات الحافلات
        { text: 'تذاكر الطيران', route: '/airline-tickets' },
        { text: 'حجز تذاكر باص', route: '/new-bus-booking' },
        { text: 'تذاكر باص (قديم)', route: '/bus-tickets' },
        
        // التأشيرات
        { text: 'تأشيرة عمل', route: '/work-visa' },
        { text: 'زيارة عائلية', route: '/family-visit' },
        { text: 'تأشيرة عمرة', route: '/umrah-visa' },
        { text: 'ضمان عمرة', route: '/umrah-guarantee' },
        
        // المالية
        { text: 'سندات الصرف', route: '/payment-vouchers' },
        { text: 'سندات القبض', route: '/receipt-vouchers' },
        { text: 'حسابات البنوك', route: '/banks' },
        { text: 'العملات', route: '/currencies' },
        { text: 'القيود اليومية', route: '/daily-journal' },
        { text: 'الإعدادات المالية', route: '/financial-settings' },
        
        // الإعدادات
        { text: 'إعدادات النظام', route: '/system-settings' },
        { text: 'استيراد SQL Server', route: '/import-mssql' },
        { text: 'استيراد نسخة احتياطية', route: '/database/import' },
        { text: 'إعادة تعيين قاعدة البيانات', route: '/database/reset' },
        { text: 'المستخدمين', route: '/users' },
        { text: 'الموردين', route: '/suppliers' },
        { text: 'الدول', route: '/countries' },
        { text: 'المدن', route: '/cities' },
        { text: 'أنواع الهوية', route: '/id-types' }
    ];
    
    // البحث عن جميع روابط القائمة الجانبية
    const allNavLinks = document.querySelectorAll('.nav-sidebar .nav-link');
    
    // معالجة كل رابط في القائمة
    allNavLinks.forEach(link => {
        // تخطي الروابط التي ليس لها نص
        if (!link.textContent || !link.textContent.trim()) {
            return;
        }
        
        // استخراج النص من الرابط
        const linkText = link.textContent.trim();
        
        // البحث في قائمة الروابط المعرفة
        const linkConfig = sidebarLinks.find(cfg => linkText.includes(cfg.text));
        
        if (linkConfig) {
            // تحديد ما إذا كان الرابط هو عنصر أب
            if (linkConfig.isParent) {
                // إعادة تعيين الحدث
                link.addEventListener('click', function(event) {
                    event.preventDefault();
                    
                    // العثور على العنصر الأب li.has-treeview
                    const parentLi = this.closest('.has-treeview');
                    if (parentLi) {
                        // تبديل فئة menu-open
                        parentLi.classList.toggle('menu-open');
                        
                        // العثور على القائمة الفرعية
                        const submenu = parentLi.querySelector('.nav-treeview');
                        if (submenu) {
                            // تبديل عرض القائمة الفرعية
                            if (parentLi.classList.contains('menu-open')) {
                                submenu.style.display = 'block';
                                submenu.style.maxHeight = submenu.scrollHeight + 'px';
                                submenu.style.opacity = '1';
                            } else {
                                submenu.style.maxHeight = '0';
                                submenu.style.opacity = '0';
                                setTimeout(() => {
                                    submenu.style.display = 'none';
                                }, 300);
                            }
                        }
                    }
                });
            } else if (linkConfig.route) {
                // إعادة تعيين الحدث للروابط العادية
                link.href = linkConfig.route;
                
                // منع السلوك الافتراضي والتعامل مع التنقل يدويًا
                link.addEventListener('click', function(event) {
                    event.preventDefault();
                    
                    console.log('جارٍ الانتقال إلى:', linkConfig.route);
                    
                    // إضافة فئة لتمييز الرابط النشط
                    allNavLinks.forEach(l => l.classList.remove('active'));
                    this.classList.add('active');
                    
                    // الانتقال إلى الصفحة المستهدفة
                    window.location.href = linkConfig.route;
                });
            }
        }
    });
    
    // معالجة خاصة لقائمة الإعدادات
    setupSettingsMenu();
    
    // إصلاح خاص لقائمة الإعدادات
    function setupSettingsMenu() {
        // البحث عن رابط الإعدادات
        const settingsLink = Array.from(allNavLinks).find(link => 
            link.textContent && link.textContent.trim().includes('الإعدادات')
        );
        
        if (settingsLink) {
            console.log('تم العثور على قائمة الإعدادات');
            const parentLi = settingsLink.closest('.has-treeview');
            
            if (parentLi) {
                // تعيين حالة القائمة كمفتوحة
                parentLi.classList.add('menu-open');
                
                // العثور على القائمة الفرعية
                const submenu = parentLi.querySelector('.nav-treeview');
                if (submenu) {
                    // ضمان عرض القائمة الفرعية
                    submenu.style.display = 'block';
                    submenu.style.maxHeight = submenu.scrollHeight + 'px';
                    submenu.style.opacity = '1';
                    
                    // معالجة روابط القائمة الفرعية
                    const subLinks = submenu.querySelectorAll('.nav-link');
                    subLinks.forEach(subLink => {
                        // البحث عن تكوين الرابط
                        const subLinkText = subLink.textContent.trim();
                        const subLinkConfig = sidebarLinks.find(cfg => 
                            subLinkText.includes(cfg.text) && cfg.route
                        );
                        
                        if (subLinkConfig) {
                            // تعيين الوجهة الصحيحة
                            subLink.href = subLinkConfig.route;
                            
                            // إضافة معالج حدث مخصص
                            subLink.addEventListener('click', function(event) {
                                event.preventDefault();
                                
                                console.log('جارٍ الانتقال إلى:', subLinkConfig.route);
                                
                                // تحديث الرابط النشط
                                allNavLinks.forEach(l => l.classList.remove('active'));
                                subLinks.forEach(l => l.classList.remove('active'));
                                this.classList.add('active');
                                
                                // الانتقال للصفحة المطلوبة
                                window.location.href = subLinkConfig.route;
                            });
                        }
                    });
                }
            }
        }
    }
    
    // وضع علامة نشطة على الرابط الحالي
    highlightCurrentPage();
    
    // تحديد الصفحة الحالية في القائمة
    function highlightCurrentPage() {
        const currentPath = window.location.pathname;
        
        // البحث في كل الروابط
        allNavLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
                
                // إذا كان الرابط في قائمة فرعية، افتح القائمة الأب
                const parentLi = link.closest('.has-treeview');
                if (parentLi) {
                    parentLi.classList.add('menu-open');
                    
                    const submenu = parentLi.querySelector('.nav-treeview');
                    if (submenu) {
                        submenu.style.display = 'block';
                    }
                }
            }
        });
    }
    
    console.log('تم تطبيق إصلاح روابط القائمة الجانبية بنجاح');
});