/**
 * إدارة القائمة الجانبية المصغرة
 * نسخة 1.0
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل ملف mini-sidebar.js');
    
    // تعيين حالة القائمة المصغرة
    setupMiniSidebar();
    
    // إضافة مستمع لتبديل حالة القائمة
    setupSidebarToggle();
    
    // تطبيق الأنماط المناسبة للأيقونات
    enhanceSidebarIcons();
});

/**
 * إعداد القائمة الجانبية المصغرة
 */
function setupMiniSidebar() {
    // التحقق مما إذا كان الجسم يحتوي على فئة sidebar-mini
    const hasMiniSidebar = document.body.classList.contains('sidebar-mini');
    
    if (hasMiniSidebar) {
        console.log('تم تفعيل وضع القائمة المصغرة');
        
        // إضافة فئة لعناصر القائمة لتحسين مظهرها في الوضع المصغر
        const navLinks = document.querySelectorAll('.nav-sidebar .nav-link');
        navLinks.forEach(link => {
            link.classList.add('mini-nav-link');
        });
        
        // تحسين مظهر الشعار في الوضع المصغر
        const brandLink = document.querySelector('.brand-link');
        if (brandLink) {
            brandLink.classList.add('mini-brand-link');
        }
    }
}

/**
 * إعداد زر تبديل القائمة
 */
function setupSidebarToggle() {
    const toggleBtn = document.getElementById('sidebarToggleBtn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            // حفظ حالة القائمة في التخزين المحلي
            const isCollapsed = document.body.classList.contains('sidebar-collapse');
            localStorage.setItem('sidebar-collapsed', isCollapsed ? 'false' : 'true');
            
            // تطبيق الأنماط بعد التبديل
            setTimeout(() => {
                enhanceSidebarIcons();
            }, 300);
        });
    }
    
    // استعادة حالة القائمة من التخزين المحلي
    const savedState = localStorage.getItem('sidebar-collapsed');
    if (savedState === 'true' && !document.body.classList.contains('sidebar-collapse')) {
        document.body.classList.add('sidebar-collapse');
    } else if (savedState === 'false' && document.body.classList.contains('sidebar-collapse')) {
        document.body.classList.remove('sidebar-collapse');
    }
}

/**
 * تحسين أيقونات القائمة الجانبية
 */
function enhanceSidebarIcons() {
    const isCollapsed = document.body.classList.contains('sidebar-collapse');
    const isMiniSidebar = document.body.classList.contains('sidebar-mini');
    
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
        });
    } else {
        // استعادة الحالة الطبيعية للأيقونات
        const navIcons = document.querySelectorAll('.nav-sidebar .nav-icon, .nav-sidebar .fas, .nav-sidebar .far, .nav-sidebar .fa');
        navIcons.forEach(icon => {
            icon.style.margin = '';
            icon.style.width = '';
            icon.style.textAlign = '';
            icon.style.fontSize = '';
        });
        
        // إظهار النص عندما تكون القائمة مفتوحة
        const navTexts = document.querySelectorAll('.nav-sidebar .nav-link p');
        navTexts.forEach(text => {
            text.style.display = '';
        });
    }
}

// استدعاء تحسين الأيقونات عند تحميل النافذة
window.addEventListener('load', function() {
    setTimeout(enhanceSidebarIcons, 500);
});

// استدعاء تحسين الأيقونات عند تغيير حجم النافذة
window.addEventListener('resize', function() {
    setTimeout(enhanceSidebarIcons, 300);
});