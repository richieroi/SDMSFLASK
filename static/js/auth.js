document.addEventListener('DOMContentLoaded', function() {
    // Create floating shapes for visual effect on the image side
    const createFloatingShapes = () => {
        const imageSides = document.querySelectorAll('.auth-image-side');
        
        if (!imageSides.length) return;
        
        imageSides.forEach(side => {
            // Create container for shapes
            const floatingShapes = document.createElement('div');
            floatingShapes.className = 'floating-shapes';
            side.appendChild(floatingShapes);
            
            // Create 10 random shapes
            for (let i = 0; i < 10; i++) {
                const shape = document.createElement('div');
                shape.className = 'shape';
                
                // Random size between 10px and 80px
                const size = Math.floor(Math.random() * 70) + 10;
                shape.style.width = `${size}px`;
                shape.style.height = `${size}px`;
                
                // Random position
                const posX = Math.floor(Math.random() * 100);
                const posY = Math.floor(Math.random() * 100);
                shape.style.left = `${posX}%`;
                shape.style.top = `${posY}%`;
                
                // Random animation duration
                const duration = (Math.floor(Math.random() * 20) + 15);
                shape.style.animation = `float ${duration}s infinite linear`;
                
                // Random delay for animation
                const delay = (Math.floor(Math.random() * 10));
                shape.style.animationDelay = `${delay}s`;
                
                // Random opacity
                const opacity = Math.random() * 0.2 + 0.05;
                shape.style.opacity = opacity;
                
                floatingShapes.appendChild(shape);
            }
        });
    };
    
    // Initialize floating shapes
    createFloatingShapes();
    
    // Enhanced password strength meter
    const initPasswordStrength = () => {
        const passwordInput = document.getElementById('password');
        if (!passwordInput) return;
        
        const strengthBar = document.querySelector('.strength-value');
        const strengthText = document.querySelector('.strength-text');
        
        if (!strengthBar || !strengthText) return;
        
        passwordInput.addEventListener('input', function() {
            const value = this.value;
            let strength = 0;
            let message = 'Password must be at least 8 characters long';
            
            if (value.length >= 8) {
                strength += 20;
                
                // Check for lowercase letters
                if (value.match(/[a-z]/g)) {
                    strength += 20;
                }
                
                // Check for uppercase letters
                if (value.match(/[A-Z]/g)) {
                    strength += 20;
                }
                
                // Check for numbers
                if (value.match(/[0-9]/g)) {
                    strength += 20;
                }
                
                // Check for special characters
                if (value.match(/[\W]/g)) {
                    strength += 20;
                }
                
                // Determine message based on strength
                if (strength <= 40) {
                    message = 'Weak password';
                    strengthBar.style.background = 'linear-gradient(90deg, #e74c3c, #e74c3c)';
                } else if (strength <= 80) {
                    message = 'Medium strength password';
                    strengthBar.style.background = 'linear-gradient(90deg, #f39c12, #f39c12)';
                } else {
                    message = 'Strong password';
                    strengthBar.style.background = 'linear-gradient(90deg, #2ecc71, #2ecc71)';
                }
            }
            
            strengthBar.style.width = `${strength}%`;
            strengthText.textContent = message;
        });
    };
    
    // Password confirmation validation
    const initConfirmPassword = () => {
        const passwordInput = document.getElementById('password');
        const confirmInput = document.getElementById('confirm_password');
        
        if (!passwordInput || !confirmInput) return;
        
        const validateConfirmPassword = () => {
            if (confirmInput.value === '') {
                confirmInput.style.borderColor = '#ecf0f1'; // Default
                return;
            }
            
            if (confirmInput.value === passwordInput.value) {
                confirmInput.style.borderColor = '#2ecc71'; // Success
                confirmInput.style.backgroundImage = 'url("data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'24\' height=\'24\' viewBox=\'0 0 24 24\'><path fill=\'%232ecc71\' d=\'M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z\'/></svg>")';
                confirmInput.style.backgroundRepeat = 'no-repeat';
                confirmInput.style.backgroundPosition = 'right 10px center';
                confirmInput.style.backgroundSize = '20px';
            } else {
                confirmInput.style.borderColor = '#e74c3c'; // Error
                confirmInput.style.backgroundImage = 'url("data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'24\' height=\'24\' viewBox=\'0 0 24 24\'><path fill=\'%23e74c3c\' d=\'M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z\'/></svg>")';
                confirmInput.style.backgroundRepeat = 'no-repeat';
                confirmInput.style.backgroundPosition = 'right 10px center';
                confirmInput.style.backgroundSize = '20px';
            }
        };
        
        confirmInput.addEventListener('input', validateConfirmPassword);
        passwordInput.addEventListener('input', validateConfirmPassword);
    };
    
    // Form input animations and validation
    const initFormInputs = () => {
        const formInputs = document.querySelectorAll('.auth-form .form-group input');
        
        formInputs.forEach(input => {
            // Add focus animation
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('input-focus');
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('input-focus');
                
                // Simple validation for required fields
                if (this.hasAttribute('required') && this.value === '') {
                    this.parentElement.classList.add('input-error');
                } else {
                    this.parentElement.classList.remove('input-error');
                }
            });
            
            // Check if input has value on page load
            if (input.value !== '') {
                input.parentElement.classList.add('has-value');
            }
            
            // Add has-value class when typing
            input.addEventListener('input', function() {
                if (this.value !== '') {
                    this.parentElement.classList.add('has-value');
                } else {
                    this.parentElement.classList.remove('has-value');
                }
            });
        });
    };
    
    // Add page transition animations
    const initPageTransitions = () => {
        const authContainer = document.querySelector('.auth-container');
        
        if (!authContainer) return;
        
        // Add entrance animation
        setTimeout(() => {
            authContainer.classList.add('auth-container-visible');
        }, 100);
        
        // Handle form submission transitions
        const authForms = document.querySelectorAll('.auth-form');
        
        authForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                // Don't add animation if form is invalid
                if (!this.checkValidity()) return;
                
                // Prevent immediate submission to show animation
                e.preventDefault();
                
                // Add exit animation
                authContainer.classList.add('auth-container-exit');
                
                // Submit the form after animation completes
                setTimeout(() => {
                    this.submit();
                }, 400);
            });
        });
    };
    
    // Initialize all features
    initPasswordStrength();
    initConfirmPassword();
    initFormInputs();
    initPageTransitions();
});