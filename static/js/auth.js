// Function to switch between login and register tabs
function switchTab(tab) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tab links
    document.querySelectorAll('.tab-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Show the selected tab content
    document.getElementById(tab + '-tab').classList.add('active');
    
    // Set the selected tab link as active
    document.querySelectorAll('.tab-link').forEach(link => {
        if (link.textContent.toLowerCase().includes(tab.toLowerCase())) {
            link.classList.add('active');
        }
    });
}

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Form validation for login
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            let isValid = true;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            // Email validation
            if (!email) {
                showError('email-error', 'Email address is required.');
                isValid = false;
            } else if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) {
                showError('email-error', 'Please enter a valid email address.');
                isValid = false;
            } else {
                hideError('email-error');
            }
            
            // Password validation
            if (!password) {
                showError('password-error', 'Password is required.');
                isValid = false;
            } else {
                hideError('password-error');
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    }
    
    // Form validation for registration
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            let isValid = true;
            const email = document.getElementById('reg-email').value;
            const password = document.getElementById('reg-password').value;
            const confirmPassword = document.getElementById('reg-confirm-password').value;
            
            // Email validation
            if (!email) {
                showError('reg-email-error', 'Email address is required.');
                isValid = false;
            } else if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) {
                showError('reg-email-error', 'Please enter a valid email address.');
                isValid = false;
            } else {
                hideError('reg-email-error');
            }
            
            // Password validation
            if (!password) {
                showError('reg-password-error', 'Password is required.');
                isValid = false;
            } else {
                hideError('reg-password-error');
            }
            
            // Confirm password validation
            if (!confirmPassword) {
                showError('reg-confirm-password-error', 'Please confirm your password.');
                isValid = false;
            } else if (password !== confirmPassword) {
                showError('reg-confirm-password-error', 'Passwords do not match.');
                isValid = false;
            } else {
                hideError('reg-confirm-password-error');
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    }
    
    // Clear errors on input
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            const errorId = this.id + '-error';
            hideError(errorId);
        });
    });
    
    // Add animation class to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.classList.add('fade-in');
    });
});

// Helper function to show error message
function showError(elementId, message) {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
}

// Helper function to hide error message
function hideError(elementId) {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.style.display = 'none';
    }
} 