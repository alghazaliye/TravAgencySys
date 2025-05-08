/**
 * إصلاح بسيط لزر القائمة الجانبية في تطبيق وكالة السفر
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل ملف sidebar-fix.js');
    
    // إضافة مستمع للنقر المباشر على الزر الجديد المضاف
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    if (sidebarToggleBtn) {
        console.log('تم العثور على زر القائمة #sidebarToggleBtn');
        
        sidebarToggleBtn.addEventListener('click', function(event) {
            console.log('تم النقر على زر القائمة الجانبية');
            toggleSidebar();
            event.preventDefault();
            event.stopPropagation();
        });
    } else {
        console.log('لم يتم العثور على زر القائمة، سيتم إضافة زر بديل');
    }
    
    // إضافة معالج عام للصفحة بأكملها لالتقاط النقرات على الأزرار التي قد لا يتم اكتشافها بطريقة مباشرة
    document.body.addEventListener('click', function(event) {
        // التحقق مما إذا كان العنصر المنقور عليه أو أحد آبائه هو زر القائمة
        const clickedElement = event.target;
        
        // التحقق مما إذا كان العنصر المنقور هو زر القائمة أو أحد عناصره الفرعية
        if (clickedElement.closest('#sidebarToggleBtn') || 
            clickedElement.closest('.fa-bars') || 
            (clickedElement.tagName === 'I' && clickedElement.classList.contains('fa-bars'))) {
            
            console.log('تم النقر على زر القائمة من خلال المعالج العام');
            toggleSidebar();
            event.preventDefault();
            event.stopPropagation();
        }
    });
    
    // وسم مخصص للنقر السريع - احتياطي في حالة عدم عمل الزر الأساسي
    const quickFix = document.createElement('div');
    quickFix.id = 'quickFixSidebarBtn';
    quickFix.style.position = 'fixed';
    quickFix.style.top = '60px'; // تعديل الموضع ليكون أسفل الشريط العلوي
    quickFix.style.right = '10px';
    quickFix.style.zIndex = '9999';
    quickFix.style.padding = '5px 10px';
    quickFix.style.background = '#4e73df';
    quickFix.style.color = 'white';
    quickFix.style.border = 'none';
    quickFix.style.borderRadius = '4px';
    quickFix.style.cursor = 'pointer';
    quickFix.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
    quickFix.innerHTML = '<span style="font-size: 16px;"><i class="fas fa-bars"></i></span>';
    quickFix.title = 'تبديل القائمة الجانبية (بديل)';
    
    quickFix.addEventListener('click', function(event) {
        console.log('تم النقر على زر الإصلاح السريع البديل');
        toggleSidebar();
        event.stopPropagation();
    });
    
    document.body.appendChild(quickFix);
});

/**
 * تبديل حالة القائمة الجانبية
 */
function toggleSidebar() {
    // تبديل الفئات في الجسم
    document.body.classList.toggle('sidebar-collapse');
    
    if (document.body.classList.contains('sidebar-collapse')) {
        // عند إغلاق القائمة
        document.body.classList.remove('sidebar-open');
        
        // تعديل هوامش المحتوى
        setContentMargins('0');
    } else {
        // عند فتح القائمة
        document.body.classList.add('sidebar-open');
        
        // تعديل هوامش المحتوى
        setContentMargins('250px');
    }
}

/**
 * ضبط هوامش المحتوى
 */
function setContentMargins(margin) {
    const contentWrapper = document.querySelector('.content-wrapper');
    const mainHeader = document.querySelector('.main-header');
    const mainFooter = document.querySelector('.main-footer');
    
    if (contentWrapper) contentWrapper.style.marginRight = margin;
    if (mainHeader) mainHeader.style.marginRight = margin;
    if (mainFooter) mainFooter.style.marginRight = margin;
}