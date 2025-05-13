/**
 * سكربت مبسط ومحسن للقائمة الجانبية في وضع RTL
 * هذا الملف يقوم بالتحكم في سلوك القائمة الجانبية بطريقة مستقلة عن AdminLTE
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    
    // التعامل مع الحالة الأولية للقائمة
    console.log("بدء تهيئة القائمة الجانبية...");
    
    // التعريفات الرئيسية
    const body = document.body;
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const mainSidebar = document.querySelector('.main-sidebar');
    const treeviewItems = document.querySelectorAll('.nav-item.has-treeview > .nav-link');
    
    // === وظيفة تبديل القائمة الجانبية ===
    function toggleSidebar() {
        // تحديد ما إذا كنا على جهاز محمول
        const isMobile = window.innerWidth < 992;
        
        if (isMobile) {
            // إزالة فئة الطي على الأجهزة المحمولة وتبديل فئة الفتح
            body.classList.remove('sidebar-collapse');
            body.classList.toggle('sidebar-open');
            
            // إظهار/إخفاء الطبقة المعتمة
            sidebarOverlay.style.display = body.classList.contains('sidebar-open') ? 'block' : 'none';
        } else {
            // تبديل فئة الطي على أجهزة الكمبيوتر
            body.classList.toggle('sidebar-collapse');
            
            // التأكد من إزالة فئة الفتح على أجهزة الكمبيوتر
            body.classList.remove('sidebar-open');
        }
        
        // حفظ الحالة
        saveState();
        console.log("تم تبديل حالة القائمة الجانبية");
    }
    
    // === حفظ حالة القائمة ===
    function saveState() {
        try {
            localStorage.setItem('sidebar-collapsed', body.classList.contains('sidebar-collapse'));
            localStorage.setItem('sidebar-open', body.classList.contains('sidebar-open'));
        } catch (e) {
            console.error("خطأ في حفظ حالة القائمة:", e);
        }
    }
    
    // === استعادة حالة القائمة ===
    function restoreState() {
        try {
            const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
            const isOpen = localStorage.getItem('sidebar-open') === 'true';
            const isMobile = window.innerWidth < 992;
            
            // استعادة الحالة بناءً على نوع الجهاز
            if (isMobile) {
                // للأجهزة المحمولة: فقط تطبيق حالة الفتح
                if (isOpen) {
                    body.classList.add('sidebar-open');
                    sidebarOverlay.style.display = 'block';
                } else {
                    body.classList.remove('sidebar-open');
                    sidebarOverlay.style.display = 'none';
                }
                // إزالة فئة الطي على الأجهزة المحمولة
                body.classList.remove('sidebar-collapse');
            } else {
                // لأجهزة الكمبيوتر: تطبيق حالة الطي فقط
                if (isCollapsed) {
                    body.classList.add('sidebar-collapse');
                } else {
                    body.classList.remove('sidebar-collapse');
                }
                // إزالة فئة الفتح على أجهزة الكمبيوتر
                body.classList.remove('sidebar-open');
                sidebarOverlay.style.display = 'none';
            }
        } catch (e) {
            console.error("خطأ في استعادة حالة القائمة:", e);
        }
    }
    
    // === معالجة العناصر القابلة للتوسيع في القائمة ===
    function setupTreeviewItems() {
        // إضافة معالج نقر لكل عنصر قابل للتوسيع
        treeviewItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                
                // الحصول على العنصر الأب والقائمة الفرعية
                const parentItem = this.parentElement;
                const treeview = parentItem.querySelector('.nav-treeview');
                
                // تبديل حالة فتح القائمة
                parentItem.classList.toggle('menu-open');
                
                // عرض/إخفاء القائمة الفرعية
                if (treeview) {
                    if (parentItem.classList.contains('menu-open')) {
                        // عرض تدريجي
                        treeview.style.height = '0';
                        treeview.style.display = 'block';
                        treeview.style.overflow = 'hidden';
                        treeview.style.transition = 'height 0.3s ease';
                        
                        // حساب الارتفاع المطلوب
                        const height = treeview.scrollHeight;
                        
                        // تعيين الارتفاع بعد فترة زمنية قصيرة للسماح بالانتقال
                        setTimeout(() => {
                            treeview.style.height = height + 'px';
                        }, 10);
                        
                        // إزالة خصائص الانتقال بعد الانتهاء
                        setTimeout(() => {
                            treeview.style.height = '';
                            treeview.style.overflow = '';
                            treeview.style.transition = '';
                        }, 300);
                    } else {
                        // إخفاء تدريجي
                        treeview.style.height = treeview.scrollHeight + 'px';
                        treeview.style.overflow = 'hidden';
                        treeview.style.transition = 'height 0.3s ease';
                        
                        // تعيين الارتفاع إلى 0 بعد فترة زمنية قصيرة للسماح بالانتقال
                        setTimeout(() => {
                            treeview.style.height = '0';
                        }, 10);
                        
                        // إخفاء العنصر بعد الانتهاء من الانتقال
                        setTimeout(() => {
                            treeview.style.display = 'none';
                            treeview.style.height = '';
                            treeview.style.overflow = '';
                            treeview.style.transition = '';
                        }, 300);
                    }
                }
            });
        });
        
        // تهيئة حالة القوائم الفرعية المفتوحة
        document.querySelectorAll('.nav-item.has-treeview.menu-open > .nav-treeview').forEach(el => {
            el.style.display = 'block';
        });
    }
    
    // === إضافة معالجات الأحداث ===
    function setupEventListeners() {
        // معالج نقر زر التبديل
        if (sidebarToggleBtn) {
            sidebarToggleBtn.addEventListener('click', function(e) {
                e.preventDefault();
                toggleSidebar();
            });
        }
        
        // معالج نقر الطبقة المعتمة لإغلاق القائمة
        if (sidebarOverlay) {
            sidebarOverlay.addEventListener('click', function() {
                body.classList.remove('sidebar-open');
                this.style.display = 'none';
                saveState();
            });
        }
        
        // معالج تغيير حجم النافذة
        window.addEventListener('resize', function() {
            restoreState();
        });
    }
    
    // === إعداد وتهيئة القائمة الجانبية ===
    function initSidebar() {
        // ضمان ظهور القائمة الجانبية
        if (mainSidebar) {
            mainSidebar.style.visibility = 'visible';
            mainSidebar.style.display = 'block';
        }
        
        // إعداد العناصر القابلة للتوسيع
        setupTreeviewItems();
        
        // إعداد معالجات الأحداث
        setupEventListeners();
        
        // استعادة حالة القائمة
        restoreState();
        
        console.log("تم تهيئة القائمة الجانبية بنجاح");
    }
    
    // بدء التهيئة
    initSidebar();
});