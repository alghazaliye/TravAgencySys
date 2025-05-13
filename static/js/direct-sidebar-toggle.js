/**
 * ملف JavaScript مبسط لضمان تبديل القائمة الجانبية
 * يعمل هذا الملف مباشرة دون تعقيدات للتأكد من استجابة القائمة للنقر في وضع RTL
 * تم تحسينه لتجنب المشكلات في المتصفحات المختلفة
 */

document.addEventListener('DOMContentLoaded', function() {
    // استعادة حالة القائمة المحفوظة سابقًا
    const savedState = localStorage.getItem('sidebar-state');
    if (savedState === 'collapsed') {
        document.body.classList.add('sidebar-collapse');
        applyCollapsedStyles();
    } else {
        document.body.classList.remove('sidebar-collapse');
        applyExpandedStyles();
    }

    // حدث النقر على زر القائمة الجانبية
    const toggleBtn = document.getElementById('sidebarToggleBtn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            toggleSidebar();
        });
    }
    
    // أي زر آخر له السمة data-widget="pushmenu"
    document.querySelectorAll('[data-widget="pushmenu"]').forEach(function(element) {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            toggleSidebar();
        });
    });
    
    // وظيفة تبديل القائمة
    function toggleSidebar() {
        // تبديل الفئة للجسم
        const wasCollapsed = document.body.classList.contains('sidebar-collapse');
        document.body.classList.toggle('sidebar-collapse');
        
        if (!wasCollapsed) {
            // التبديل إلى وضع الطي
            applyCollapsedStyles();
        } else {
            // التبديل إلى وضع التوسيع
            applyExpandedStyles();
        }
        
        // حفظ حالة القائمة في التخزين المحلي
        localStorage.setItem('sidebar-state', 
            document.body.classList.contains('sidebar-collapse') ? 'collapsed' : 'expanded');
    }
    
    // تطبيق أنماط وضع الطي
    function applyCollapsedStyles() {
        const sidebar = document.querySelector('.main-sidebar');
        if (!sidebar) return;
        
        // إعدادات القائمة المطوية
        sidebar.style.transition = 'all 0.3s ease-in-out';
        
        if (window.innerWidth >= 768) {
            // للشاشات المتوسطة والكبيرة
            sidebar.style.width = '4.6rem';
            
            // تعديل هوامش المحتوى
            document.querySelectorAll('.content-wrapper, .main-header, .main-footer').forEach(element => {
                element.style.transition = 'margin-right 0.3s ease-in-out';
                element.style.marginRight = '4.6rem';
            });
        } else {
            // للشاشات الصغيرة
            sidebar.style.transform = 'translateX(250px)';
            sidebar.style.right = '-250px';
            
            document.querySelectorAll('.content-wrapper, .main-header, .main-footer').forEach(element => {
                element.style.marginRight = '0';
            });
        }
        
        // إخفاء نص القائمة
        document.querySelectorAll('.nav-sidebar .nav-link p').forEach(element => {
            element.style.opacity = '0';
            element.style.display = 'none';
        });
        
        // تعديل حجم اللوجو
        const brandText = document.querySelector('.brand-text');
        if (brandText) {
            brandText.style.opacity = '0';
            brandText.style.display = 'none';
        }
    }
    
    // تطبيق أنماط وضع التوسيع
    function applyExpandedStyles() {
        const sidebar = document.querySelector('.main-sidebar');
        if (!sidebar) return;
        
        // إعدادات القائمة الموسعة
        sidebar.style.transition = 'all 0.3s ease-in-out';
        sidebar.style.width = '250px';
        sidebar.style.right = '0';
        sidebar.style.transform = 'translateX(0)';
        
        if (window.innerWidth >= 768) {
            // تعديل هوامش المحتوى
            document.querySelectorAll('.content-wrapper, .main-header, .main-footer').forEach(element => {
                element.style.transition = 'margin-right 0.3s ease-in-out';
                element.style.marginRight = '250px';
            });
        }
        
        // إظهار نص القائمة
        document.querySelectorAll('.nav-sidebar .nav-link p').forEach(element => {
            element.style.display = 'block';
            setTimeout(() => {
                element.style.opacity = '1';
            }, 50);
        });
        
        // إظهار نص اللوجو
        const brandText = document.querySelector('.brand-text');
        if (brandText) {
            brandText.style.display = 'inline-block';
            setTimeout(() => {
                brandText.style.opacity = '1';
            }, 50);
        }
    }
    
    // إعادة تطبيق الأنماط عند تغيير حجم النافذة
    window.addEventListener('resize', function() {
        if (document.body.classList.contains('sidebar-collapse')) {
            applyCollapsedStyles();
        } else {
            applyExpandedStyles();
        }
    });
});