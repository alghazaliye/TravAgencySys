/**
 * ملف مخصص لإصلاح مشكلة زر القائمة الجانبية في تطبيق وكالة السفر
 */

document.addEventListener('DOMContentLoaded', function() {
    // الحصول على زر القائمة الجانبية
    const sidebarToggleBtn = document.querySelector('[data-widget="pushmenu"]');
    
    if (sidebarToggleBtn) {
        // إزالة أي مستمعات حدث مضافة سابقًا
        const newSidebarToggleBtn = sidebarToggleBtn.cloneNode(true);
        sidebarToggleBtn.parentNode.replaceChild(newSidebarToggleBtn, sidebarToggleBtn);
        
        // إضافة معالج حدث جديد
        newSidebarToggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // تبديل حالة الجسم
            if (document.body.classList.contains('sidebar-collapse')) {
                document.body.classList.remove('sidebar-collapse');
                document.body.classList.add('sidebar-open');
            } else {
                document.body.classList.remove('sidebar-open');
                document.body.classList.add('sidebar-collapse');
            }
            
            // تغيير أنماط CSS الخاصة بالشريط الجانبي والمحتوى
            adjustSidebarAndContent();
            
            // تخزين الحالة في localStorage
            localStorage.setItem('sidebar-state', 
                document.body.classList.contains('sidebar-collapse') ? 'collapsed' : 'expanded');
        });
        
        // استعادة حالة الشريط الجانبي من localStorage عند تحميل الصفحة
        const savedState = localStorage.getItem('sidebar-state');
        if (savedState === 'collapsed') {
            document.body.classList.add('sidebar-collapse');
            document.body.classList.remove('sidebar-open');
        } else if (savedState === 'expanded') {
            document.body.classList.remove('sidebar-collapse');
            document.body.classList.add('sidebar-open');
        }
        
        // تعديل الأنماط الأولية
        adjustSidebarAndContent();
    }
    
    // مراقبة تغييرات الشاشة
    window.addEventListener('resize', adjustSidebarAndContent);
});

/**
 * ضبط مظهر الشريط الجانبي والمحتوى بناءً على حالة القائمة
 */
function adjustSidebarAndContent() {
    const contentWrapper = document.querySelector('.content-wrapper');
    const mainHeader = document.querySelector('.main-header');
    const mainFooter = document.querySelector('.main-footer');
    const mainSidebar = document.querySelector('.main-sidebar');
    
    // إذا كانت الشاشة صغيرة (وضع الهاتف)
    if (window.innerWidth <= 767.98) {
        // إعدادات الهاتف
        if (mainSidebar) {
            mainSidebar.style.position = 'fixed';
            mainSidebar.style.right = document.body.classList.contains('sidebar-open') ? '0' : '-250px';
            mainSidebar.style.transition = 'right 0.3s ease-in-out';
        }
        
        if (contentWrapper) contentWrapper.style.marginRight = '0';
        if (mainHeader) mainHeader.style.marginRight = '0';
        if (mainFooter) mainFooter.style.marginRight = '0';
    } else {
        // إعدادات الكمبيوتر
        if (mainSidebar) {
            mainSidebar.style.position = 'fixed';
            mainSidebar.style.right = '0';
        }
        
        // تطبيق الهوامش بناءً على حالة الشريط الجانبي
        const margin = document.body.classList.contains('sidebar-collapse') ? '0' : '250px';
        
        if (contentWrapper) {
            contentWrapper.style.marginRight = margin;
            contentWrapper.style.transition = 'margin-right 0.3s ease-in-out';
        }
        
        if (mainHeader) {
            mainHeader.style.marginRight = margin;
            mainHeader.style.transition = 'margin-right 0.3s ease-in-out';
        }
        
        if (mainFooter) {
            mainFooter.style.marginRight = margin;
            mainFooter.style.transition = 'margin-right 0.3s ease-in-out';
        }
    }
}