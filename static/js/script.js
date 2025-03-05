document.addEventListener('DOMContentLoaded', function() {
    // Fade out flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    if (flashMessages) {
        setTimeout(() => {
            flashMessages.forEach(msg => {
                msg.style.opacity = '0';
                msg.style.transform = 'translateY(-10px)';
                msg.style.transition = 'opacity 0.5s, transform 0.5s';
            });
        }, 5000);
    }
    
    // Add active state to navigation links based on current page
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active-link');
        }
    });
    
    // Add form input animations
    const formInputs = document.querySelectorAll('.form-group input, .form-group textarea');
    formInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('input-active');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('input-active');
        });
    });

    // Mobile menu toggle if present
    const menuToggle = document.querySelector('.navbar-toggle');
    const navbarLinksElement = document.querySelector('.navbar-links');
    
    if (menuToggle && navbarLinks) {
        menuToggle.addEventListener('click', function() {
            navbarLinksElement.classList.toggle('show');
        });
    }
    
    // Close flash messages when clicking the close button
    const closeButtons = document.querySelectorAll('.flash-message .close');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.style.display = 'none';
        });
    });

    // Fix dropdown menu behavior
    const userMenu = document.querySelector('.user-menu');
    if (userMenu) {
        // Toggle menu on click instead of hover
        userMenu.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            userMenu.classList.toggle('active');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!userMenu.contains(e.target)) {
                userMenu.classList.remove('active');
            }
        });
        
        // Prevent menu from closing when clicking inside dropdown
        const userMenuContent = userMenu.querySelector('.user-menu-content');
        if (userMenuContent) {
            userMenuContent.addEventListener('click', function(e) {
                // Only stop propagation if not clicking on a link
                if (e.target.tagName !== 'A') {
                    e.stopPropagation();
                }
            });
        }
        
        // Make sure the user menu dropdown is working properly
        const userMenuLinks = document.querySelectorAll('.user-menu-content a');
        userMenuLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                // Allow the default action to proceed (follow the link)
                // Just stop the click from closing the menu before the navigation
                e.stopPropagation();
            });
        });
    }

    // User menu fix for mobile
    const userMenus = document.querySelectorAll('.user-menu');
    if (window.innerWidth <= 768) {
        userMenus.forEach(menu => {
            menu.addEventListener('click', function(e) {
                this.classList.toggle('active');
                e.stopPropagation();
            });
            
            document.addEventListener('click', function() {
                menu.classList.remove('active');
            });
        });
    }

    // Mobile navigation
    const navbarToggle = document.getElementById('navbarToggle');
    const navbarLinks = document.getElementById('navbarLinks');
    
    if (navbarToggle && navbarLinks) {
        navbarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            navbarLinks.classList.toggle('show');
        });
    }
    
    // User menu dropdown
    const userMenuDuplicate = document.querySelector('.user-menu');
    if (userMenuDuplicate) {
        userMenuDuplicate.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            this.classList.toggle('active');
        });
        
        // Close when clicking outside
        document.addEventListener('click', function(e) {
            if (userMenuDuplicate.classList.contains('active') && !userMenuDuplicate.contains(e.target)) {
                userMenuDuplicate.classList.remove('active');
            }
        });
    }
});
