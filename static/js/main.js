/* Amar Honda Care — Main JS */

// Auto-dismiss alerts after 4s
document.querySelectorAll('.alert.alert-dismissible').forEach(el => {
    setTimeout(() => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
        if (bsAlert) bsAlert.close();
    }, 4000);
});

// Preserve sidebar scroll position or scroll active item into view
document.addEventListener('DOMContentLoaded', () => {
    const sidebarNav = document.querySelector('.sidebar-nav');
    if (sidebarNav) {
        // Restore scroll position from sessionStorage
        const scrollPosition = sessionStorage.getItem('sidebarScrollPosition');
        if (scrollPosition !== null) {
            sidebarNav.scrollTop = parseInt(scrollPosition, 10);
        } else {
            // Fallback: Scroll the active link into view on fresh load
            const activeLink = sidebarNav.querySelector('.nav-link.active');
            if (activeLink) {
                activeLink.scrollIntoView({ block: 'nearest' });
            }
        }

        // Save scroll position when any link in the sidebar is clicked
        sidebarNav.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                sessionStorage.setItem('sidebarScrollPosition', sidebarNav.scrollTop);
            });
        });

        // Clear scroll position when logo/brand is clicked (resets to top)
        const brandLink = document.querySelector('.sidebar-brand a');
        if (brandLink) {
            brandLink.addEventListener('click', () => {
                sessionStorage.removeItem('sidebarScrollPosition');
            });
        }
    }
});

