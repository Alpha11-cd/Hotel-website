document.addEventListener('DOMContentLoaded', function () {
    // Initialize AOS animations if present
    if (typeof AOS !== 'undefined') {
        AOS.refresh();
    }

    // Set active navigation link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});

