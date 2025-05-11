/**
 * مدير القائمة الجانبية الموحّد - لحل مشكلة تكرار الأيقونات
 * الإصدار 1.0
 */

// إنشاء متغير عام للإشارة إلى أن الأيقونات قد تمت معالجتها
window.sidebarIconsFixed = false;

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل مدير القائمة الجانبية الموحد');

    // التأكد من أن هذا الملف هو فقط من سيقوم بمعالجة الأيقونات
    document.body.setAttribute('data-sidebar-manager-active', 'true');

    // إزالة الأيقونات المكررة من جميع روابط القائمة
    cleanupSidebarIcons();

    // إضافة المستمعات للنقر على زر تبديل القائمة
    setupSidebarToggle();

    // تطبيق حالة التصغير استنادًا إلى التخزين المحلي
    restoreSidebarState();
});

/**
 * تنظيف أيقونات القائمة الجانبية وإزالة التكرار
 */
function cleanupSidebarIcons() {
    // إذا كانت هناك عملية إصلاح جارية، نتجاهلها
    if (window.sidebarIconsFixed) {
        return;
    }

    // تحديد أننا بدأنا عملية إصلاح الأيقونات
    window.sidebarIconsFixed = true;

    console.log('بدء تنظيف أيقونات القائمة الجانبية...');

    // الحصول على جميع عناصر القائمة
    const navLinks = document.querySelectorAll('.nav-sidebar .nav-link');

    // عداد للإحصائيات
    let iconsRemoved = 0;
    let linksProcessed = 0;

    navLinks.forEach(link => {
        // التعامل مع كل رابط على حدة
        linksProcessed++;

        // إيجاد جميع الأيقونات في الرابط
        const icons = link.querySelectorAll('i.nav-icon, i.fas, i.far, i.fa, i.fab');

        // إذا كان هناك أكثر من أيقونة واحدة، نحتفظ فقط بالأولى
        if (icons.length > 1) {
            // الاحتفاظ بالأيقونة الأولى وإزالة الباقي
            const firstIcon = icons[0];
            
            // وضع علامة على الأيقونة الأولى للإشارة إلى أنها الأصلية
            firstIcon.setAttribute('data-original-icon', 'true');
            
            // إزالة باقي الأيقونات
            for (let i = 1; i < icons.length; i++) {
                icons[i].remove();
                iconsRemoved++;
            }
        }

        // تنسيق الأيقونة المتبقية (إن وجدت)
        const remainingIcon = link.querySelector('i.nav-icon, i.fas, i.far, i.fa, i.fab');
        if (remainingIcon) {
            // تطبيق الأنماط الموحدة على الأيقونة
            remainingIcon.style.display = 'inline-flex';
            remainingIcon.style.alignItems = 'center';
            remainingIcon.style.justifyContent = 'center';
            remainingIcon.style.visibility = 'visible';
            remainingIcon.style.width = '2rem';
            remainingIcon.style.height = '2rem';
            remainingIcon.style.marginLeft = '0.7rem';
            remainingIcon.style.marginRight = '0';
            remainingIcon.style.textAlign = 'center';
            remainingIcon.style.fontSize = '1.25rem';
            remainingIcon.style.color = 'inherit';
        }

        // وضع علامة على الرابط للإشارة إلى أنه تم معالجته
        link.setAttribute('data-icons-cleaned', 'true');
    });

    console.log(`تم معالجة ${linksProcessed} رابط وإزالة ${iconsRemoved} أيقونة مكررة`);
}

/**
 * إعداد زر تبديل القائمة الجانبية
 */
function setupSidebarToggle() {
    // البحث عن كافة أزرار تبديل القائمة في الصفحة
    const toggleButtons = document.querySelectorAll('[data-widget="pushmenu"], .sidebar-toggle, #sidebarToggleBtn, #mainMenuToggleBtn');
    
    toggleButtons.forEach(button => {
        // التحقق مما إذا كان الزر قد تم معالجته مسبقًا
        if (button.hasAttribute('data-toggle-listener-added')) {
            return;
        }
        
        // إضافة مستمع للنقر على الزر
        button.addEventListener('click', function(e) {
            e.preventDefault();
            toggleSidebar();
        });
        
        // وضع علامة على الزر للإشارة إلى أنه تم معالجته
        button.setAttribute('data-toggle-listener-added', 'true');
    });
}

/**
 * تبديل حالة القائمة الجانبية
 */
function toggleSidebar() {
    // تبديل فئة sidebar-collapse
    document.body.classList.toggle('sidebar-collapse');
    
    // تحديد حالة القائمة الحالية
    const isCollapsed = document.body.classList.contains('sidebar-collapse');
    
    // تحديث العناصر المرتبطة بحالة القائمة
    updateSidebarElements(isCollapsed);
    
    // حفظ الحالة في التخزين المحلي
    localStorage.setItem('sidebar-collapsed', isCollapsed ? 'true' : 'false');
}

/**
 * تحديث عناصر القائمة الجانبية بناءً على حالة التصغير
 */
function updateSidebarElements(isCollapsed) {
    const windowWidth = window.innerWidth;
    const sidebar = document.querySelector('.main-sidebar');
    const contentWrapper = document.querySelector('.content-wrapper');
    const mainHeader = document.querySelector('.main-header');
    const mainFooter = document.querySelector('.main-footer');
    
    // تغيير عرض القائمة الجانبية
    if (sidebar) {
        sidebar.style.transition = 'width 0.3s ease-in-out, margin 0.3s ease-in-out';
        sidebar.style.width = isCollapsed ? '4.6rem' : '250px';
    }
    
    // تغيير هوامش المحتوى على الشاشات الكبيرة
    if (windowWidth >= 768) {
        const margin = isCollapsed ? '4.6rem' : '250px';
        if (contentWrapper) contentWrapper.style.marginRight = margin;
        if (mainHeader) mainHeader.style.marginRight = margin;
        if (mainFooter) mainFooter.style.marginRight = margin;
    }
    
    // إذا كانت القائمة مصغرة
    if (document.body.classList.contains('sidebar-mini')) {
        if (isCollapsed) {
            // إخفاء النص في القائمة المطوية
            const navTexts = document.querySelectorAll('.nav-sidebar .nav-link p');
            navTexts.forEach(text => {
                text.style.display = 'none';
                text.style.opacity = '0';
                text.style.visibility = 'hidden';
            });
            
            // تعديل مظهر الروابط
            const navLinks = document.querySelectorAll('.nav-sidebar .nav-link');
            navLinks.forEach(link => {
                link.style.textAlign = 'center';
                link.style.padding = '0.75rem 0.5rem';
            });
        } else {
            // إظهار النص في القائمة المفتوحة
            const navTexts = document.querySelectorAll('.nav-sidebar .nav-link p');
            navTexts.forEach(text => {
                text.style.display = '';
                text.style.opacity = '1';
                text.style.visibility = 'visible';
            });
            
            // إعادة مظهر الروابط
            const navLinks = document.querySelectorAll('.nav-sidebar .nav-link');
            navLinks.forEach(link => {
                link.style.textAlign = '';
                link.style.padding = '';
            });
        }
    }
}

/**
 * استعادة حالة القائمة الجانبية من التخزين المحلي
 */
function restoreSidebarState() {
    const savedState = localStorage.getItem('sidebar-collapsed');
    
    if (savedState === 'true' && !document.body.classList.contains('sidebar-collapse')) {
        document.body.classList.add('sidebar-collapse');
        updateSidebarElements(true);
    } else if (savedState === 'false' && document.body.classList.contains('sidebar-collapse')) {
        document.body.classList.remove('sidebar-collapse');
        updateSidebarElements(false);
    }
}

// استدعاء تنظيف الأيقونات عند تغيير حجم النافذة
window.addEventListener('resize', function() {
    updateSidebarElements(document.body.classList.contains('sidebar-collapse'));
});

// تجاهل محاولات إصلاح الأيقونات من ملفات أخرى
window.preventOtherSidebarFixers = function() {
    // استبدال وظائف الإصلاح الأخرى بوظائف فارغة
    if (window.fixSidebarIcons && window.fixSidebarIcons !== cleanupSidebarIcons) {
        const originalFunction = window.fixSidebarIcons;
        window.fixSidebarIcons = function() {
            console.log('تم تجاهل محاولة إصلاح من مصدر آخر');
            return;
        };
    }
};

// تنفيذ الوظيفة مباشرة لتجاهل المصلحات الأخرى
window.preventOtherSidebarFixers();