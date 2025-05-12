/*!
 * AdminLTE v3.1.0 Custom RTL Support
 * MIT License
 */
(function ($) {
  'use strict'

  // القائمة الجانبية
  $(document).ready(function () {
    console.log("تهيئة AdminLTE RTL");
    
    // تعطيل ردود الفعل النشطة
    $('[data-widget="pushmenu"]').off('click');
    
    // إعادة تعريف زر القائمة مع ردود فعل مخصصة
    $('[data-widget="pushmenu"]').on('click', function (e) {
      e.preventDefault();
      
      var isCollapsed = $('body').hasClass('sidebar-collapse');
      console.log("وضع القائمة قبل النقر:", isCollapsed ? "مطوية" : "مفتوحة");
      
      // تبديل طي القائمة
      $('body').toggleClass('sidebar-collapse');
      
      // تبديل طبقة المحتوى للهواتف المحمولة
      if (window.innerWidth <= 992) {
        $('body').toggleClass('sidebar-open');
      }
      
      isCollapsed = $('body').hasClass('sidebar-collapse');
      console.log("وضع القائمة بعد النقر:", isCollapsed ? "مطوية" : "مفتوحة");
    });
    
    // ضبط مظهر RTL
    $('.main-sidebar').css({
      'right': '0',
      'left': 'auto'
    });
    
    // ضبط هوامش المحتوى
    adjustContentMargins();
    
    // استجابة لتغيير حجم النافذة
    $(window).resize(function () {
      adjustContentMargins();
    });
  });

  // ضبط هوامش المحتوى للـ RTL
  function adjustContentMargins() {
    var isCollapsed = $('body').hasClass('sidebar-collapse');
    var marginRight = isCollapsed ? '4.6rem' : '250px';
    
    // ضبط هوامش المحتوى للـ RTL
    if (window.innerWidth > 992) {
      $('.content-wrapper, .main-header, .main-footer').css({
        'margin-right': marginRight,
        'margin-left': '0'
      });
    } else {
      $('.content-wrapper, .main-header, .main-footer').css({
        'margin-right': '0',
        'margin-left': '0'
      });
    }
  }

})(jQuery)