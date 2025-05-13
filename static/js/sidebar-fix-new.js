/**
 * إصلاح محسّن للقائمة الجانبية وأزرار التنقل 
 * نسخة 3.0 (2025) - تحسينات شاملة للقائمة الجانبية
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل ملف sidebar-fix - النسخة المحدثة 3.0');
    
    // تعريف متغير للتحكم في حالة القائمة
    let isProcessing = false;
    
    // إصلاح مشكلة الأيقونات المتكررة في القائمة
    function fixSidebarIcons() {
        document.querySelectorAll('.nav-sidebar .nav-link').forEach(link => {
            // إزالة الأيقونات المتكررة إن وجدت
            const icons = link.querySelectorAll('i');
            if (icons.length > 1) {
                // الاحتفاظ بالأيقونة الأولى فقط
                for (let i = 1; i < icons.length; i++) {
                    icons[i].remove();
                }
            }
            
            // تحسين مظهر الأيقونة المتبقية
            const icon = link.querySelector('i');
            if (icon) {
                icon.style.visibility = 'visible';
                icon.style.display = 'inline-flex';
                icon.style.alignItems = 'center';
                icon.style.justifyContent = 'center';
                icon.style.width = '1.6rem';
                icon.style.marginLeft = '0.7rem';
                icon.style.marginRight = '0';
                icon.style.textAlign = 'center';
            }
        });
    }
    
    // الاستماع إلى أحداث النقر على أزرار تبديل القائمة الجانبية
    document.querySelectorAll('[data-widget="pushmenu"]').forEach(button => {
        button.addEventListener('click', function(event) {
            if (!isProcessing) {
                isProcessing = true;
                toggleSidebar();
                event.preventDefault();
                
                // منع التكرار السريع للنقرات
                setTimeout(() => {
                    isProcessing = false;
                }, 300);
            }
        });
    });
    
    // تطبيق التصحيحات فور تحميل الصفحة
    fixSidebarIcons();
    applyResponsiveSettings();
    
    // مراقبة تغييرات حجم النافذة
    window.addEventListener('resize', applyResponsiveSettings);
    
    // تبديل حالة القائمة الجانبية
    function toggleSidebar() {
        const windowWidth = window.innerWidth;
        document.body.classList.toggle('sidebar-collapse');
        
        if (document.body.classList.contains('sidebar-collapse')) {
            document.body.classList.remove('sidebar-open');
            
            if (windowWidth >= 768) {
                setContentMargins('4.6rem');
            } else {
                setContentMargins('0');
                
                // إغلاق القائمة على الشاشات الصغيرة
                const sidebar = document.querySelector('.main-sidebar');
                if (sidebar) {
                    sidebar.style.right = '-250px';
                }
            }
        } else {
            document.body.classList.add('sidebar-open');
            
            if (windowWidth >= 768) {
                setContentMargins('250px');
            }
            
            // إظهار القائمة على الشاشات الصغيرة
            const sidebar = document.querySelector('.main-sidebar');
            if (sidebar) {
                sidebar.style.right = '0';
            }
        }
        
        // تخزين حالة القائمة
        saveMenuState();
        
        // تطبيق الإصلاحات
        setTimeout(fixSidebarIcons, 50);
    }
    
    // ضبط هوامش المحتوى
    function setContentMargins(margin) {
        if (window.innerWidth < 768) return;
        
        const contentWrapper = document.querySelector('.content-wrapper');
        const mainHeader = document.querySelector('.main-header');
        const mainFooter = document.querySelector('.main-footer');
        
        if (contentWrapper) contentWrapper.style.marginRight = margin;
        if (mainHeader) mainHeader.style.marginRight = margin;
        if (mainFooter) mainFooter.style.marginRight = margin;
    }
    
    // تطبيق إعدادات التجاوب مع أحجام الشاشة المختلفة
    function applyResponsiveSettings() {
        const windowWidth = window.innerWidth;
        const sidebar = document.querySelector('.main-sidebar');
        if (!sidebar) return;
        
        if (windowWidth < 768) {
            // إعدادات الشاشات الصغيرة
            if (document.body.classList.contains('sidebar-open')) {
                sidebar.style.right = '0';
            } else {
                sidebar.style.right = '-250px';
            }
            
            setContentMargins('0');
        } else {
            // إعدادات الشاشات المتوسطة والكبيرة
            sidebar.style.right = '0';
            
            if (document.body.classList.contains('sidebar-collapse')) {
                sidebar.style.width = '4.6rem';
                setContentMargins('4.6rem');
            } else {
                sidebar.style.width = '250px';
                setContentMargins('250px');
            }
        }
    }
    
    // حفظ حالة القائمة
    function saveMenuState() {
        const state = document.body.classList.contains('sidebar-collapse') ? 'collapsed' : 'expanded';
        localStorage.setItem('sidebar-state', state);
    }
    
    // استعادة حالة القائمة من التخزين المحلي
    function restoreMenuState() {
        const savedState = localStorage.getItem('sidebar-state');
        const windowWidth = window.innerWidth;
        
        if (windowWidth < 768) {
            // دائمًا نبدأ بإغلاق القائمة على الشاشات الصغيرة
            document.body.classList.add('sidebar-collapse');
            document.body.classList.remove('sidebar-open');
            return;
        }
        
        if (savedState === 'collapsed') {
            document.body.classList.add('sidebar-collapse');
            document.body.classList.remove('sidebar-open');
            setContentMargins('4.6rem');
        } else {
            document.body.classList.remove('sidebar-collapse');
            document.body.classList.add('sidebar-open');
            setContentMargins('250px');
        }
        
        applyResponsiveSettings();
    }
    
    // استعادة الحالة السابقة
    restoreMenuState();
});