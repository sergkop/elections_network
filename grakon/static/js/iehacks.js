$(function() {
    if (window.PIE) {
        $('.ym-hlist ul li a, .ym-hlist ul li strong, .button, .breadcrumbs, .breadcrumbs ul li a, .breadcrumbs ul li strong, .breadcrumbs ul li a:focus, .breadcrumbs ul li a:hover').each(function() {
            PIE.attach(this);
        });
    }
});