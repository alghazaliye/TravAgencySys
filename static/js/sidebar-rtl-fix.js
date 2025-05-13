/**
 * ملف مخصص لإصلاح مشاكل القائمة الجانبية في وضع RTL
 * يقوم هذا الملف بتجاوز سلوك AdminLTE الافتراضي لضمان عمل القائمة بشكل صحيح في واجهة RTL
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    
    console.log("تهيئة إصلاحات القائمة الجانبية RTL");
    
    // إعداد زر تبديل عرض القائمة الجانبية
    function setupSidebarToggle() {
        // تحديد جميع أزرار تبديل القائمة
        $('.nav-link[data-widget="pushmenu"]').off('click').on('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // الحصول على حالة القائمة الحالية
            const body = $('body');
            const isSidebarCollapsed = body.hasClass('sidebar-collapse');
            
            console.log("وضع القائمة قبل النقر:", isSidebarCollapsed ? "مطوية" : "مفتوحة");
            
            // تبديل حالة القائمة
            body.toggleClass('sidebar-collapse');
            
            // سجل الحالة الجديدة
            console.log("وضع القائمة بعد النقر:", body.hasClass('sidebar-collapse') ? "مطوية" : "مفتوحة");
            
            // حفظ حالة القائمة في التخزين المحلي
            try {
                localStorage.setItem('sidebar-collapse', body.hasClass('sidebar-collapse'));
            } catch(e) {
                console.error("خطأ في حفظ حالة القائمة:", e);
            }
        });
    }
    
    // استعادة حالة القائمة من التخزين المحلي
    function restoreSidebarState() {
        const savedState = localStorage.getItem('sidebar-collapse');
        const body = document.querySelector('body');
        
        // تطبيق الحالة المحفوظة فقط إذا كانت موجودة
        if (savedState !== null) {
            const shouldCollapse = savedState === 'true';
            
            // ضمان تطابق حالة الصفحة مع الحالة المحفوظة
            if (shouldCollapse && !body.classList.contains('sidebar-collapse')) {
                body.classList.add('sidebar-collapse');
            } else if (!shouldCollapse && body.classList.contains('sidebar-collapse')) {
                body.classList.remove('sidebar-collapse');
            }
            
            console.log("تم استعادة حالة القائمة:", shouldCollapse ? "مطوية" : "مفتوحة");
        }
    }
    
    // إصلاح سلوك العناصر القابلة للتوسيع في القائمة
    function fixTreeviewItems() {
        const treeviewItems = document.querySelectorAll('.nav-item.has-treeview');
        
        treeviewItems.forEach(item => {
            // إعادة تعيين معالج النقر لضمان التوافق مع RTL
            const navLink = item.querySelector('.nav-link');
            
            if (navLink) {
                // إزالة معالج الحدث الأصلي
                const newNavLink = navLink.cloneNode(true);
                navLink.parentNode.replaceChild(newNavLink, navLink);
                
                // إضافة معالج جديد
                newNavLink.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    // معالجة حالة فتح/إغلاق العنصر
                    item.classList.toggle('menu-open');
                    
                    // عرض/إخفاء القائمة الفرعية بسلاسة
                    const treeview = item.querySelector('.nav-treeview');
                    if (treeview) {
                        if (item.classList.contains('menu-open')) {
                            treeview.style.display = 'block';
                        } else {
                            treeview.style.display = 'none';
                        }
                    }
                });
            }
        });
    }
    
    // إصلاح سلوك تحريك القائمة الجانبية على الشاشات الصغيرة
    function fixMobileMenu() {
        // التعامل مع فتح القائمة على الأجهزة المحمولة
        const toggleButtons = document.querySelectorAll('.nav-link[data-widget="pushmenu"]');
        
        toggleButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                if (window.innerWidth < 992) {
                    document.body.classList.toggle('sidebar-open');
                }
            });
        });
        
        // إغلاق القائمة عند النقر خارجها على الجوال
        document.addEventListener('click', function(event) {
            if (window.innerWidth < 992 && document.body.classList.contains('sidebar-open')) {
                // التحقق من أن النقر ليس على القائمة ولا على زر التبديل
                const sidebar = document.querySelector('.main-sidebar');
                const toggleButtons = Array.from(document.querySelectorAll('.nav-link[data-widget="pushmenu"]'));
                
                const isClickInsideSidebar = sidebar.contains(event.target);
                const isClickOnToggle = toggleButtons.some(btn => btn.contains(event.target));
                
                if (!isClickInsideSidebar && !isClickOnToggle) {
                    document.body.classList.remove('sidebar-open');
                }
            }
        });
    }
    
    // تهيئة جميع الإصلاحات
    setupSidebarToggle();
    restoreSidebarState();
    fixTreeviewItems();
    fixMobileMenu();
    
    // عند تغيير حجم النافذة، تحديث سلوك القائمة إذا لزم الأمر
    window.addEventListener('resize', function() {
        fixMobileMenu();
    });
    
    console.log("تم تطبيق إصلاحات القائمة الجانبية بنجاح");
});