$(function () {
    'use strict';
    
    // Initialize Select2 Elements
    $('.select2').select2();
    
    // Initialize DataTables
    $('.datatable').DataTable({
        "paging": true,
        "lengthChange": true,
        "searching": true,
        "ordering": true,
        "info": true,
        "autoWidth": false,
        "responsive": true,
        "language": {
            "sProcessing": "جارٍ التحميل...",
            "sLengthMenu": "أظهر _MENU_ مدخلات",
            "sZeroRecords": "لم يعثر على أية سجلات",
            "sInfo": "إظهار _START_ إلى _END_ من أصل _TOTAL_ مدخل",
            "sInfoEmpty": "يعرض 0 إلى 0 من أصل 0 سجل",
            "sInfoFiltered": "(منتقاة من مجموع _MAX_ مدخل)",
            "sInfoPostFix": "",
            "sSearch": "ابحث:",
            "sUrl": "",
            "oPaginate": {
                "sFirst": "الأول",
                "sPrevious": "السابق",
                "sNext": "التالي",
                "sLast": "الأخير"
            }
        }
    });
    
    // Initialize datepicker with RTL support
    $('.datepicker').datepicker({
        autoclose: true,
        format: 'yyyy-mm-dd',
        rtl: true,
        language: 'ar',
        orientation: "bottom auto"
    });
    
    // Sidebar menu active state
    var currentUrl = window.location.href;
    $('.nav-sidebar .nav-link').each(function () {
        if (currentUrl.indexOf($(this).attr('href')) > -1) {
            $(this).addClass('active');
            $(this).closest('.has-treeview').addClass('menu-open');
            $(this).closest('.has-treeview').find('.nav-link').first().addClass('active');
        }
    });
    
    // Print button in reports
    $('#printReport').on('click', function() {
        window.print();
    });
    
    // Form validation
    $('.needs-validation').submit(function(event) {
        var form = $(this);
        if (form[0].checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
        }
        form.addClass('was-validated');
    });
    
    // Dashboard charts (if on dashboard page)
    if ($('#salesChart').length) {
        var salesChartCanvas = $('#salesChart').get(0).getContext('2d');
        var salesChart = new Chart(salesChartCanvas, {
            type: 'line',
            data: {
                labels: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو'],
                datasets: [
                    {
                        label: 'تذاكر الطيران',
                        backgroundColor: 'rgba(44, 123, 229, 0.2)',
                        borderColor: 'rgba(44, 123, 229, 1)',
                        pointRadius: 3,
                        pointBackgroundColor: 'rgba(44, 123, 229, 1)',
                        pointBorderColor: '#ffffff',
                        pointHoverRadius: 5,
                        pointHoverBackgroundColor: '#ffffff',
                        pointHoverBorderColor: 'rgba(44, 123, 229, 1)',
                        data: [65, 59, 80, 81, 56, 55, 40]
                    },
                    {
                        label: 'تأشيرات',
                        backgroundColor: 'rgba(33, 200, 122, 0.2)',
                        borderColor: 'rgba(33, 200, 122, 1)',
                        pointRadius: 3,
                        pointBackgroundColor: 'rgba(33, 200, 122, 1)',
                        pointBorderColor: '#ffffff',
                        pointHoverRadius: 5,
                        pointHoverBackgroundColor: '#ffffff',
                        pointHoverBorderColor: 'rgba(33, 200, 122, 1)',
                        data: [28, 48, 40, 19, 86, 27, 90]
                    }
                ]
            },
            options: {
                maintainAspectRatio: false,
                responsive: true,
                tooltips: {
                    mode: 'index',
                    intersect: false,
                },
                hover: {
                    mode: 'nearest',
                    intersect: true
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        grid: {
                            display: true
                        }
                    }
                }
            }
        });
    }
    
    // Customer distribution by service type (if on dashboard)
    if ($('#pieChart').length) {
        var pieChartCanvas = $('#pieChart').get(0).getContext('2d');
        var pieChart = new Chart(pieChartCanvas, {
            type: 'doughnut',
            data: {
                labels: [
                    'تذاكر طيران',
                    'تأشيرات عمل',
                    'تأشيرات عمرة',
                    'زيارات عائلية',
                    'تذاكر باصات'
                ],
                datasets: [
                    {
                        data: [30, 25, 20, 15, 10],
                        backgroundColor: [
                            '#2c7be5',
                            '#21c87a',
                            '#f5803e',
                            '#6db7c6',
                            '#ffbc42'
                        ],
                    }
                ]
            },
            options: {
                maintainAspectRatio: false,
                responsive: true,
            }
        });
    }
    
    // Currency exchange rate updates
    $('.currency-value').on('change', function() {
        // This would normally fetch updated rates from an API
        console.log('Currency value changed');
    });
    
    // For modals to clear form data when closed
    $('.modal').on('hidden.bs.modal', function() {
        $(this).find('form').trigger('reset');
        $(this).find('form').removeClass('was-validated');
    });

    // File input customization
    $('.custom-file-input').on('change', function() {
        var fileName = $(this).val().split('\\').pop();
        $(this).next('.custom-file-label').addClass("selected").html(fileName);
    });
});
