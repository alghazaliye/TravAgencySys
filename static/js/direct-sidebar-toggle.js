/**
 * ملف JavaScript مبسط لضمان تبديل القائمة الجانبية
 * يعمل هذا الملف مباشرة دون تعقيدات للتأكد من استجابة القائمة للنقر
 */

document.addEventListener('DOMContentLoaded', function() {
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
        document.body.classList.toggle('sidebar-collapse');
        
        const sidebar = document.querySelector('.main-sidebar');
        
        if (sidebar) {
            if (document.body.classList.contains('sidebar-collapse')) {
                // طي القائمة
                if (window.innerWidth >= 768) {
                    sidebar.style.width = '4.6rem';
                    
                    // تعديل هوامش المحتوى
                    document.querySelectorAll('.content-wrapper, .main-header, .main-footer').forEach(element => {
                        element.style.marginRight = '4.6rem';
                    });
                } else {
                    // إخفاء القائمة على الشاشات الصغيرة
                    sidebar.style.right = '-250px';
                    
                    document.querySelectorAll('.content-wrapper, .main-header, .main-footer').forEach(element => {
                        element.style.marginRight = '0';
                    });
                }
                
                // إخفاء نص القائمة
                document.querySelectorAll('.nav-sidebar .nav-link p').forEach(element => {
                    element.style.display = 'none';
                });
            } else {
                // توسيع القائمة
                sidebar.style.width = '250px';
                sidebar.style.right = '0';
                
                if (window.innerWidth >= 768) {
                    // تعديل هوامش المحتوى
                    document.querySelectorAll('.content-wrapper, .main-header, .main-footer').forEach(element => {
                        element.style.marginRight = '250px';
                    });
                }
                
                // إظهار نص القائمة
                document.querySelectorAll('.nav-sidebar .nav-link p').forEach(element => {
                    element.style.display = 'block';
                });
            }
        }
        
        // حفظ حالة القائمة في التخزين المحلي
        localStorage.setItem('sidebar-state', document.body.classList.contains('sidebar-collapse') ? 'collapsed' : 'expanded');
    }
});