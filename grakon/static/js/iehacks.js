$(function() {

    if (window.PIE) {
        $('.ym-hlist ul li a, .ym-hlist ul li strong, .main-buttons div, .main-buttons-blue a, #login_btn, .breadcrumbs, .ui-button, .column_header, .ym-clearfix').each(function() {
            PIE.attach(this);
        });
    }
});