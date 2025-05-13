/**
 * ملف مخصص لإصلاح مشاكل القائمة الجانبية في وضع RTL
 * يقوم هذا الملف بتجاوز سلوك AdminLTE الافتراضي لضمان عمل القائمة بشكل صحيح في واجهة RTL
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    
    console.log("تهيئة إصلاحات القائمة الجانبية RTL");
    
    // إعداد زر تبديل عرض القائمة الجانبية
    function setupSidebarToggle() {
        const toggleButtons = document.querySelectorAll('.nav-link[data-widget="pushmenu"]');
        
        toggleButtons.forEach(btn => {
            // إزالة معالج الحدث الافتراضي الذي قد يتسبب في مشاكل
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
            
            // إضافة معالج جديد للنقر
            newBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const body = document.querySelector('body');
                console.log("وضع القائمة قبل النقر:", body.classList.contains('sidebar-collapse') ? "مطوية" : "مفتوحة");
                
                // تبديل الفئة لتطبيق/إزالة وضع الطي
                body.classList.toggle('sidebar-collapse');
                
                console.log("وضع القائمة بعد النقر:", body.classList.contains('sidebar-collapse') ? "مطوية" : "مفتوحة");
                
                // تخزين حالة القائمة في التخزين المحلي
                localStorage.setItem('sidebar-collapse', body.classList.contains('sidebar-collapse'));
            });
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