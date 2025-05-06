/**
 * نظام الإشعارات
 * يتيح هذا النظام إدارة وعرض الإشعارات عند إجراء أي تغييرات في النظام
 */

// مصفوفة للإشعارات
let notifications = [];

// كائن لإدارة الإشعارات
const NotificationManager = {
    // إضافة إشعار جديد
    addNotification: function(type, message, details = '', module = '') {
        const notification = {
            id: Date.now(), // رقم فريد للإشعار
            type: type, // نوع الإشعار (success, info, warning, danger)
            message: message, // رسالة الإشعار
            details: details, // تفاصيل إضافية
            module: module, // اسم الوحدة المرتبطة بالإشعار
            timestamp: new Date(), // وقت الإشعار
            read: false // حالة الإشعار (مقروء/غير مقروء)
        };
        
        // إضافة الإشعار لقائمة الإشعارات
        notifications.unshift(notification);
        
        // تحديث عداد الإشعارات وواجهة المستخدم
        this.updateNotificationCount();
        this.updateNotificationUI();
        
        // عرض إشعار منبثق للمستخدم (Toast)
        this.showToast(notification);
        
        // في التطبيق الحقيقي: حفظ الإشعار في قاعدة البيانات أو localStorage
        this.saveNotifications();
        
        return notification;
    },
    
    // تحديث عدد الإشعارات غير المقروءة
    updateNotificationCount: function() {
        const unreadCount = notifications.filter(n => !n.read).length;
        const badge = document.querySelector('.notification-badge');
        
        if (badge) {
            if (unreadCount > 0) {
                badge.textContent = unreadCount;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }
    },
    
    // تحديث قائمة الإشعارات في واجهة المستخدم
    updateNotificationUI: function() {
        const container = document.querySelector('.notification-list');
        
        if (!container) return;
        
        // تحديث عنوان الإشعارات
        const header = document.querySelector('.notification-header');
        if (header) {
            const count = notifications.length;
            header.textContent = count + ' إشعار';
        }
        
        // مسح محتوى القائمة الحالية
        container.innerHTML = '';
        
        // إضافة كل إشعار للقائمة
        if (notifications.length === 0) {
            container.innerHTML = '<div class="dropdown-item text-center">لا توجد إشعارات</div>';
        } else {
            // إضافة أحدث 5 إشعارات
            const recent = notifications.slice(0, 5);
            
            for (const notification of recent) {
                let icon = 'far fa-bell';
                
                // اختيار الأيقونة حسب نوع الإشعار
                switch (notification.type) {
                    case 'success':
                        icon = 'fas fa-check-circle text-success';
                        break;
                    case 'warning':
                        icon = 'fas fa-exclamation-triangle text-warning';
                        break;
                    case 'danger':
                        icon = 'fas fa-times-circle text-danger';
                        break;
                    case 'info':
                        icon = 'fas fa-info-circle text-info';
                        break;
                }
                
                // تنسيق التاريخ
                const date = notification.timestamp;
                const timeAgo = this.timeAgo(date);
                
                // إنشاء عنصر الإشعار
                const notificationItem = document.createElement('a');
                notificationItem.href = '#';
                notificationItem.className = 'dropdown-item' + (notification.read ? '' : ' unread');
                notificationItem.dataset.id = notification.id;
                notificationItem.onclick = function() {
                    NotificationManager.markAsRead(notification.id);
                    return false;
                };
                
                notificationItem.innerHTML = `
                    <i class="${icon} ml-2"></i> 
                    <span>${notification.message}</span>
                    <span class="float-left text-muted text-sm">${timeAgo}</span>
                `;
                
                container.appendChild(notificationItem);
                
                // إضافة فاصل بعد كل إشعار (ما عدا الأخير)
                if (notification !== recent[recent.length - 1]) {
                    const divider = document.createElement('div');
                    divider.className = 'dropdown-divider';
                    container.appendChild(divider);
                }
            }
            
            // إضافة رابط عرض جميع الإشعارات
            if (notifications.length > 5) {
                const divider = document.createElement('div');
                divider.className = 'dropdown-divider';
                container.appendChild(divider);
                
                const viewAllLink = document.createElement('a');
                viewAllLink.href = '#';
                viewAllLink.className = 'dropdown-item dropdown-footer';
                viewAllLink.textContent = 'عرض جميع الإشعارات';
                container.appendChild(viewAllLink);
            }
        }
    },
    
    // وضع علامة "مقروء" على الإشعار
    markAsRead: function(notificationId) {
        const notification = notifications.find(n => n.id == notificationId);
        
        if (notification) {
            notification.read = true;
            this.updateNotificationCount();
            this.updateNotificationUI();
            this.saveNotifications();
        }
    },
    
    // وضع علامة "مقروء" على جميع الإشعارات
    markAllAsRead: function() {
        for (const notification of notifications) {
            notification.read = true;
        }
        
        this.updateNotificationCount();
        this.updateNotificationUI();
        this.saveNotifications();
    },
    
    // حذف إشعار
    removeNotification: function(notificationId) {
        notifications = notifications.filter(n => n.id != notificationId);
        this.updateNotificationCount();
        this.updateNotificationUI();
        this.saveNotifications();
    },
    
    // حذف جميع الإشعارات
    clearAllNotifications: function() {
        notifications = [];
        this.updateNotificationCount();
        this.updateNotificationUI();
        this.saveNotifications();
    },
    
    // حفظ الإشعارات في localStorage
    saveNotifications: function() {
        if (typeof Storage !== 'undefined') {
            localStorage.setItem('notifications', JSON.stringify(notifications));
        }
    },
    
    // استرجاع الإشعارات من localStorage
    loadNotifications: function() {
        if (typeof Storage !== 'undefined') {
            const savedNotifications = localStorage.getItem('notifications');
            
            if (savedNotifications) {
                try {
                    notifications = JSON.parse(savedNotifications);
                    
                    // تحويل التواريخ من النصوص إلى كائنات Date
                    for (const notification of notifications) {
                        notification.timestamp = new Date(notification.timestamp);
                    }
                    
                    this.updateNotificationCount();
                    this.updateNotificationUI();
                } catch (e) {
                    console.error('خطأ في تحميل الإشعارات:', e);
                }
            }
        }
    },
    
    // إظهار إشعار Toast
    showToast: function(notification) {
        if (typeof Swal === 'undefined') {
            console.log('SweetAlert2 غير موجود. لا يمكن عرض الإشعار المنبثق.');
            return;
        }
        
        // تعيين الأيقونة حسب نوع الإشعار
        let icon = notification.type;
        if (icon === 'danger') icon = 'error';
        
        // عرض إشعار منبثق
        const Toast = Swal.mixin({
            toast: true,
            position: 'top-start',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer);
                toast.addEventListener('mouseleave', Swal.resumeTimer);
            }
        });
        
        Toast.fire({
            icon: icon,
            title: notification.message
        });
    },
    
    // حساب الوقت المنقضي منذ وقت معين
    timeAgo: function(date) {
        const now = new Date();
        const secondsAgo = Math.floor((now - date) / 1000);
        
        if (secondsAgo < 60) {
            return 'منذ ' + secondsAgo + ' ثانية';
        }
        
        const minutesAgo = Math.floor(secondsAgo / 60);
        
        if (minutesAgo < 60) {
            return 'منذ ' + minutesAgo + ' دقيقة';
        }
        
        const hoursAgo = Math.floor(minutesAgo / 60);
        
        if (hoursAgo < 24) {
            return 'منذ ' + hoursAgo + ' ساعة';
        }
        
        const daysAgo = Math.floor(hoursAgo / 24);
        
        if (daysAgo < 30) {
            return 'منذ ' + daysAgo + ' يوم';
        }
        
        return date.toLocaleDateString('ar-SA');
    }
};

// إضافة إشعارات تجريبية
function addSampleNotifications() {
    NotificationManager.addNotification('success', 'تم إضافة تأشيرة عمرة جديدة', 'تأشيرة برقم #123456', 'تأشيرات العمرة');
    NotificationManager.addNotification('info', 'تم تعديل بيانات عميل', 'عميل رقم #7890', 'إدارة العملاء');
    NotificationManager.addNotification('warning', 'تأشيرة على وشك الانتهاء', 'متبقي 5 أيام لتأشيرة رقم #5678', 'تأشيرات العمرة');
}

// تحميل الإشعارات عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    NotificationManager.loadNotifications();
    
    // إضافة مستمع لزر "وضع علامة على الكل كمقروءة"
    const markAllReadBtn = document.getElementById('mark-all-read');
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            NotificationManager.markAllAsRead();
        });
    }
    
    // في بيئة التطوير فقط: إضافة إشعارات تجريبية إذا لم تكن هناك إشعارات
    if (notifications.length === 0) {
        addSampleNotifications();
    }
});

// تصدير كائن إدارة الإشعارات للاستخدام في الملفات الأخرى
window.NotificationManager = NotificationManager;