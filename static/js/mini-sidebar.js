/**
 * إدارة القائمة الجانبية المصغرة
 * نسخة 2.1 - تحسينات إضافية للأداء والمظهر مع تجنب تكرار الأزرار
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل ملف mini-sidebar.js - الإصدار المحسن 2.1');
    
    // نحن لا ننشئ أزرار جديدة، فقط نتكامل مع الأزرار الموجودة
    
    // التحقق مما إذا كان هناك زر تبديل موجود مسبقًا
    const existingToggleBtn = document.getElementById('sidebarToggleBtn');
    if (existingToggleBtn) {
        console.log('تم العثور على زر تبديل القائمة الموجود #sidebarToggleBtn');
        existingToggleBtn.setAttribute('data-mini-sidebar-integrated', 'true');
    }
    
    // تعيين حالة القائمة المصغرة
    setupMiniSidebar();
    
    // استدعاء setupSidebarToggle تحت ظروف معينة فقط
    setupSidebarToggle();
    
    // تطبيق الأنماط المناسبة للأيقونات
    enhanceSidebarIcons();
    
    // استدعاء تحسين أيقونات القائمة الجانبية بعد فترة قصيرة للتأكد من تطبيق التغييرات
    setTimeout(enhanceSidebarIcons, 500);
});

/**
 * إعداد القائمة الجانبية المصغرة مع تحسينات الأداء
 */
function setupMiniSidebar() {
    // التحقق مما إذا كان الجسم يحتوي على فئة sidebar-mini
    const hasMiniSidebar = document.body.classList.contains('sidebar-mini');
    
    if (hasMiniSidebar) {
        console.log('تم تفعيل وضع القائمة المصغرة');
        
        // إضافة فئة للجسم لتسهيل تطبيق الأنماط
        document.body.classList.add('with-mini-sidebar');
        
        // إضافة فئة لعناصر القائمة لتحسين مظهرها في الوضع المصغر
        const navLinks = document.querySelectorAll('.nav-sidebar .nav-link');
        navLinks.forEach(link => {
            link.classList.add('mini-nav-link');
            
            // إضافة عناصر البيانات لتحسين وظيفة التحويم
            const text = link.querySelector('p');
            if (text) {
                const textContent = text.textContent || text.innerText;
                link.setAttribute('data-original-text', textContent);
                link.setAttribute('title', textContent);
            }
        });
        
        // تحسين مظهر الشعار في الوضع المصغر
        const brandLink = document.querySelector('.brand-link');
        if (brandLink) {
            brandLink.classList.add('mini-brand-link');
        }
        
        // تحسين عرض الأيقونات
        fixSidebarIcons();
        
        // إضافة فئة للعناصر التي تحتوي على قوائم فرعية
        const treeItems = document.querySelectorAll('.nav-sidebar .nav-item.has-treeview');
        treeItems.forEach(item => {
            item.classList.add('mini-treeview');
        });
    }
}

/**
 * إصلاح أيقونات القائمة الجانبية
 */
function fixSidebarIcons() {
    // تحسين مظهر أيقونات القائمة
    const navIcons = document.querySelectorAll('.nav-sidebar .nav-link > i');
    navIcons.forEach(icon => {
        if (!icon.classList.contains('mini-sidebar-ready')) {
            icon.classList.add('mini-sidebar-ready');
            icon.style.fontSize = '1.25rem';
            icon.style.textAlign = 'center';
            icon.style.transition = 'all 0.3s ease';
        }
    });
}

/**
 * تكامل مع أزرار تبديل القائمة الجانبية الموجودة مسبقاً
 * هذه الوظيفة لم تعد تنشئ أزرار جديدة، بل تتكامل مع الأزرار الموجودة
 */
function setupSidebarToggle() {
    // هذه الوظيفة تم إزالتها لتجنب تكرار الأزرار
    // بدلاً من ذلك، نستخدم الأزرار التي تم إنشاؤها بواسطة sidebar-fix.js
    
    // استعادة حالة القائمة من التخزين المحلي
    restoreSidebarState();
    
    // البحث عن جميع أزرار تبديل القائمة الجانبية الموجودة مسبقاً
    const allToggleBtns = document.querySelectorAll('[data-widget="pushmenu"], .sidebar-toggle, #sidebarToggleBtn');
    allToggleBtns.forEach(btn => {
        // إضافة مستمع لتحديث أنماط الأيقونات بعد النقر
        btn.addEventListener('click', function() {
            // استدعاء تحسين الأيقونات بعد تبديل القائمة
            setTimeout(enhanceSidebarIcons, 10);
        });
    });
}

/**
 * تبديل حالة القائمة الجانبية
 * هذه الوظيفة تتكامل الآن مع الأحداث التي تطلقها sidebar-fix.js
 */
function toggleSidebar() {
    // لا نقوم بتبديل الفئة هنا لأن ذلك يتم بواسطة sidebar-fix.js
    // بدلاً من ذلك، نستمع للتغييرات ونقوم بتطبيق الأنماط المخصصة
    
    // تحديد حالة القائمة الحالية
    const isCollapsed = document.body.classList.contains('sidebar-collapse');
    
    // حفظ الحالة في التخزين المحلي
    localStorage.setItem('sidebar-collapsed', isCollapsed ? 'true' : 'false');
    
    // تطبيق تغييرات إضافية بناءً على حالة التصغير
    if (isCollapsed) {
        document.body.classList.add('sidebar-is-mini');
        document.body.classList.remove('sidebar-is-expanded');
    } else {
        document.body.classList.remove('sidebar-is-mini');
        document.body.classList.add('sidebar-is-expanded');
    }
    
    // تطبيق تحسينات الأيقونات
    enhanceSidebarIcons();
}

// إضافة مستمع للأحداث لاستقبال إشعارات من sidebar-fix.js
document.addEventListener('sidebar-toggled', function() {
    // تنفيذ تحسينات الأيقونات عند تغيير حالة القائمة
    setTimeout(toggleSidebar, 10);
});

/**
 * استعادة حالة القائمة الجانبية
 */
function restoreSidebarState() {
    const savedState = localStorage.getItem('sidebar-collapsed');
    const isMiniSidebar = document.body.classList.contains('sidebar-mini');
    
    // عدم استعادة الحالة إذا كانت القائمة المصغرة غير مفعلة
    if (!isMiniSidebar) return;
    
    if (savedState === 'true' && !document.body.classList.contains('sidebar-collapse')) {
        // تطبيق حالة الطي
        document.body.classList.add('sidebar-collapse');
        document.body.classList.add('sidebar-is-mini');
        document.body.classList.remove('sidebar-is-expanded');
    } else if (savedState === 'false' && document.body.classList.contains('sidebar-collapse')) {
        // تطبيق حالة التوسيع
        document.body.classList.remove('sidebar-collapse');
        document.body.classList.remove('sidebar-is-mini');
        document.body.classList.add('sidebar-is-expanded');
    }
    
    // تطبيق التأثيرات المرئية المناسبة
    enhanceSidebarIcons();
}

/**
 * تحسين أيقونات القائمة الجانبية
 */
function enhanceSidebarIcons() {
    const isCollapsed = document.body.classList.contains('sidebar-collapse');
    const isMiniSidebar = document.body.classList.contains('sidebar-mini');
    
    if (!isMiniSidebar) return;
    
    // تعديل عرض القائمة الجانبية
    const sidebar = document.querySelector('.main-sidebar');
    if (sidebar) {
        sidebar.style.transition = 'width 0.3s ease-in-out, margin 0.3s ease-in-out';
        sidebar.style.width = isCollapsed ? '4.6rem' : '250px';
    }
    
    // تعديل هوامش المحتوى
    const contentWrapper = document.querySelector('.content-wrapper');
    const mainHeader = document.querySelector('.main-header');
    const mainFooter = document.querySelector('.main-footer');
    
    if (window.innerWidth >= 768) {  // تطبيق فقط للشاشات المتوسطة والكبيرة
        if (contentWrapper) contentWrapper.style.marginRight = isCollapsed ? '4.6rem' : '250px';
        if (mainHeader) mainHeader.style.marginRight = isCollapsed ? '4.6rem' : '250px';
        if (mainFooter) mainFooter.style.marginRight = isCollapsed ? '4.6rem' : '250px';
    }
    
    if (isMiniSidebar && isCollapsed) {
        // تحسين الأيقونات عندما تكون القائمة مطوية
        const navIcons = document.querySelectorAll('.nav-sidebar .nav-icon, .nav-sidebar .fas, .nav-sidebar .far, .nav-sidebar .fa');
        navIcons.forEach(icon => {
            icon.style.margin = '0 auto';
            icon.style.width = '100%';
            icon.style.textAlign = 'center';
            icon.style.fontSize = '1.25rem';
        });
        
        // إخفاء النص عندما تكون القائمة مطوية
        const navTexts = document.querySelectorAll('.nav-sidebar .nav-link p');
        navTexts.forEach(text => {
            text.style.display = 'none';
            text.style.opacity = '0';
            text.style.visibility = 'hidden';
        });
        
        // تعديل شكل الرابط ليكون مركزًا
        const navLinks = document.querySelectorAll('.nav-sidebar .nav-link');
        navLinks.forEach(link => {
            link.style.textAlign = 'center';
            link.style.padding = '0.75rem 0.5rem';
        });
    } else {
        // استعادة الحالة الطبيعية للأيقونات والنصوص
        const navIcons = document.querySelectorAll('.nav-sidebar .nav-icon, .nav-sidebar .fas, .nav-sidebar .far, .nav-sidebar .fa');
        navIcons.forEach(icon => {
            icon.style.margin = '';
            icon.style.width = '';
            icon.style.textAlign = '';
        });
        
        // إظهار النص عندما تكون القائمة مفتوحة
        const navTexts = document.querySelectorAll('.nav-sidebar .nav-link p');
        navTexts.forEach(text => {
            text.style.display = '';
            text.style.opacity = '1';
            text.style.visibility = 'visible';
        });
        
        // إعادة تعيين شكل الرابط
        const navLinks = document.querySelectorAll('.nav-sidebar .nav-link');
        navLinks.forEach(link => {
            link.style.textAlign = '';
            link.style.padding = '';
        });
    }
}

// استدعاء تحسين الأيقونات عند تحميل النافذة
window.addEventListener('load', function() {
    setTimeout(enhanceSidebarIcons, 100);
    setTimeout(fixSidebarIcons, 200);
});

// استدعاء تحسين الأيقونات عند تغيير حجم النافذة
window.addEventListener('resize', function() {
    setTimeout(enhanceSidebarIcons, 100);
});