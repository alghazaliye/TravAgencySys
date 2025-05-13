/**
 * ملف مخصص لإصلاح مشاكل القائمة الجانبية في وضع RTL
 * يقوم هذا الملف بتجاوز سلوك AdminLTE الافتراضي لضمان عمل القائمة بشكل صحيح في واجهة RTL
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    
    console.log("تهيئة إصلاحات القائمة الجانبية RTL");
    
    // التأكد من وجود jQuery
    if (typeof jQuery === 'undefined') {
        console.error('jQuery غير متوفر، وهو مطلوب لإصلاحات القائمة الجانبية!');
        return;
    }
    
    // إعداد زر تبديل عرض القائمة الجانبية - نسخة محسّنة كليًا
    function setupSidebarToggle() {
        // الحصول على زر التبديل مباشرة
        const $toggleBtn = $('#sidebarToggleBtn, .sidebar-toggle-btn, .nav-link[data-widget="pushmenu"]');
        
        // إضافة تأثير بصري لزر التبديل عند التفاعل
        $toggleBtn.hover(
            function() { $(this).css('transform', 'scale(1.05)'); },
            function() { $(this).css('transform', 'scale(1)'); }
        );
        
        // إزالة أي معالجات أحداث سابقة
        $toggleBtn.off('click');
        
        // إضافة معالج نقر محسّن
        $toggleBtn.on('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // تأثير نقر بصري
            $(this).css('transform', 'scale(0.95)');
            setTimeout(() => $(this).css('transform', 'scale(1)'), 200);
            
            const body = $('body');
            const isCollapsed = body.hasClass('sidebar-collapse');
            const isOpen = body.hasClass('sidebar-open');
            
            // تسجيل وضع القائمة قبل النقر
            console.log("وضع القائمة قبل النقر:", isCollapsed ? "مطوية" : "مفتوحة");
            
            // للأجهزة المحمولة (أقل من 992 بيكسل)
            if (window.innerWidth < 992) {
                // إزالة وضع الطي على الأجهزة المحمولة
                if (isCollapsed) body.removeClass('sidebar-collapse');
                
                // تبديل وضع الفتح
                body.toggleClass('sidebar-open');
                
                // إضافة وإزالة الخلفية المعتمة
                if (!body.hasClass('sidebar-open')) {
                    $('#sidebar-overlay').fadeOut(300, function() {
                        $(this).remove();
                    });
                } else {
                    $('<div id="sidebar-overlay"></div>')
                        .css({
                            position: 'fixed',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            background: 'rgba(0,0,0,0.5)',
                            zIndex: 1037,
                            opacity: 0
                        })
                        .appendTo('body')
                        .on('click', function() {
                            body.removeClass('sidebar-open');
                            $(this).fadeOut(300, function() {
                                $(this).remove();
                            });
                        })
                        .animate({opacity: 1}, 300);
                }
            } 
            // للأجهزة المكتبية (أكبر من أو يساوي 992 بيكسل)
            else {
                // تبديل وضع الطي فقط للأجهزة المكتبية
                body.toggleClass('sidebar-collapse');
                
                // تأكيد إزالة وضع الفتح على الأجهزة المكتبية
                if (isOpen) body.removeClass('sidebar-open');
                
                // تحديث أنماط القائمة بناءً على حالة الطي
                if (body.hasClass('sidebar-collapse')) {
                    $('.main-sidebar').css('width', '4.6rem');
                    $('.content-wrapper, .main-header, .main-footer').css('margin-right', '4.6rem');
                } else {
                    $('.main-sidebar').css('width', '250px');
                    $('.content-wrapper, .main-header, .main-footer').css('margin-right', '250px');
                }
            }
            
            // تحديث وضع أيقونة التبديل (اختياري)
            updateToggleIcon();
            
            // تسجيل وضع القائمة بعد النقر
            console.log("وضع القائمة بعد النقر:", 
                         body.hasClass('sidebar-collapse') ? "مطوية" : 
                         body.hasClass('sidebar-open') ? "مفتوحة على الموبايل" : "مفتوحة");
            
            // حفظ الحالة المحدثة في التخزين المحلي
            try {
                localStorage.setItem('sidebar-collapse', body.hasClass('sidebar-collapse'));
                localStorage.setItem('sidebar-open', body.hasClass('sidebar-open'));
            } catch(e) {
                console.error("خطأ في حفظ حالة القائمة:", e);
            }
        });
        
        // دالة لتحديث أيقونة زر التبديل
        function updateToggleIcon() {
            const $icon = $toggleBtn.find('i');
            if ($('body').hasClass('sidebar-collapse') || $('body').hasClass('sidebar-open')) {
                if ($icon.hasClass('fa-bars')) {
                    $icon.removeClass('fa-bars').addClass('fa-times');
                }
            } else {
                if ($icon.hasClass('fa-times')) {
                    $icon.removeClass('fa-times').addClass('fa-bars');
                }
            }
        }
        
        // تأكيد تفعيل وظيفة التبديل
        console.log("تم تفعيل وظيفة تبديل القائمة الجانبية");
    }
    
    // استعادة حالة القائمة من التخزين المحلي
    function restoreSidebarState() {
        try {
            const savedCollapseState = localStorage.getItem('sidebar-collapse');
            const savedOpenState = localStorage.getItem('sidebar-open');
            const body = $('body');
            
            console.log("حالة القائمة المحفوظة - Collapse:", savedCollapseState);
            console.log("حالة القائمة المحفوظة - Open:", savedOpenState);
            
            // تطبيق الحالة المحفوظة بناءً على حجم الشاشة
            if (window.innerWidth >= 992) {
                // للأجهزة المكتبية، استعادة حالة الطي فقط
                if (savedCollapseState === 'true') {
                    body.addClass('sidebar-collapse');
                } else if (savedCollapseState === 'false') {
                    body.removeClass('sidebar-collapse');
                }
            } else {
                // للأجهزة المحمولة، استعادة حالة الفتح وإزالة حالة الطي
                if (savedOpenState === 'true') {
                    body.addClass('sidebar-open');
                } else {
                    body.removeClass('sidebar-open');
                }
                // نزيل حالة الطي على الموبايل لتجنب المشاكل
                body.removeClass('sidebar-collapse');
            }
        } catch(e) {
            console.error("خطأ في استعادة حالة القائمة:", e);
        }
    }
    
    // إصلاح محسّن لسلوك العناصر القابلة للتوسيع في القائمة
    function fixTreeviewItems() {
        // استخدام jQuery لمزيد من الاتساق
        $('.nav-item.has-treeview > .nav-link').off('click').on('click', function(e) {
            e.preventDefault();
            
            const $item = $(this).parent('.nav-item.has-treeview');
            const $treeview = $item.find('.nav-treeview').first();
            
            // تبديل حالة فتح القائمة
            $item.toggleClass('menu-open');
            
            // عرض/إخفاء القائمة الفرعية بسلاسة باستخدام انيميشن jQuery
            if ($item.hasClass('menu-open')) {
                $treeview.slideDown(300);
            } else {
                $treeview.slideUp(300);
            }
        });
        
        // تهيئة حالة القوائم المفتوحة
        $('.nav-item.has-treeview.menu-open > .nav-treeview').show();
        
        console.log("تم إصلاح سلوك عناصر القائمة القابلة للتوسيع");
    }
    
    // إصلاح محسّن لسلوك تحريك القائمة الجانبية على الشاشات الصغيرة
    function fixMobileMenu() {
        // إغلاق القائمة عند النقر خارجها على الجوال باستخدام jQuery
        $(document).on('click', function(e) {
            if (window.innerWidth < 992 && $('body').hasClass('sidebar-open')) {
                const $sidebar = $('.main-sidebar');
                const $toggleButtons = $('.nav-link[data-widget="pushmenu"], #sidebarToggleBtn, .sidebar-toggle-btn');
                
                // التحقق من أن النقر ليس على القائمة ولا على زر التبديل
                if (!$sidebar.is(e.target) && $sidebar.has(e.target).length === 0 && 
                    !$toggleButtons.is(e.target) && $toggleButtons.has(e.target).length === 0) {
                    $('body').removeClass('sidebar-open');
                }
            }
        });
    }
    
    // تعزيز القائمة الجانبية عند التحميل
    function enhanceSidebar() {
        // تأكد من أن القائمة الجانبية مرئية
        $('.main-sidebar').css({
            'display': 'block',
            'visibility': 'visible'
        });
        
        // إصلاح أنماط القائمة الفرعية
        $('.nav-treeview').each(function() {
            if ($(this).parent('.nav-item').hasClass('menu-open')) {
                $(this).css('display', 'block');
            } else {
                $(this).css('display', 'none');
            }
        });
    }
    
    // تهيئة جميع الإصلاحات
    enhanceSidebar();
    setupSidebarToggle();
    restoreSidebarState();
    fixTreeviewItems();
    fixMobileMenu();
    
    // إضافة معالج خاص لزر تبديل القائمة الجانبية
    $('#sidebarToggleBtn').css('cursor', 'pointer').attr('title', 'تبديل القائمة الجانبية');
    
    // عند تغيير حجم النافذة، تحديث سلوك القائمة
    $(window).on('resize', function() {
        restoreSidebarState(); // مهم لتعديل حالة القائمة بناءً على حجم الشاشة الجديد
        fixMobileMenu();
    });
    
    console.log("تم تطبيق إصلاحات القائمة الجانبية بنجاح");
});