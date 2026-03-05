/* Amar Honda Care — Main JS */

// Auto-dismiss alerts after 4s
document.querySelectorAll('.alert.alert-dismissible').forEach(el => {
    setTimeout(() => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
        if (bsAlert) bsAlert.close();
    }, 4000);
});

// Active sidebar link highlight based on URL
(function() {
    const path = window.location.pathname;
    document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href && href !== '/' && path.startsWith(href)) {
            link.classList.add('active');
        }
    });
})();
