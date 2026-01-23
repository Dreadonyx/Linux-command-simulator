/**
 * VNB Portal - Login Page Script
 */

document.addEventListener('DOMContentLoaded', () => {
    const elements = {
        form: document.getElementById('loginForm'),
        username: document.getElementById('username'),
        password: document.getElementById('password'),
        togglePassword: document.getElementById('togglePassword'),
        loginBtn: document.getElementById('loginBtn'),
        toast: document.getElementById('toast'),
        toastMessage: document.querySelector('.toast-message'),
        toastIcon: document.querySelector('.toast-icon'),
        eyeOpen: document.querySelector('.eye-open'),
        eyeClosed: document.querySelector('.eye-closed'),
        btnText: document.querySelector('.btn-text'),
        btnLoader: document.querySelector('.btn-loader')
    };

    // Toggle password visibility
    elements.togglePassword.addEventListener('click', () => {
        const isPassword = elements.password.type === 'password';
        elements.password.type = isPassword ? 'text' : 'password';
        elements.eyeOpen.classList.toggle('hidden', !isPassword);
        elements.eyeClosed.classList.toggle('hidden', isPassword);
    });

    // Form submission
    elements.form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = elements.username.value.trim();
        const password = elements.password.value;

        // Validate
        if (!username) {
            showToast('Please enter a username', 'error');
            return;
        }
        if (!password || password.length < 4) {
            showToast('Password must be at least 4 characters', 'error');
            return;
        }

        // Show loading
        setLoadingState(true);

        // Simulate login
        setTimeout(() => {
            // Store user in localStorage
            const users = JSON.parse(localStorage.getItem('vnb_users') || '{}');

            if (users[username] && users[username] === password) {
                localStorage.setItem('vnb_loggedIn', 'true');
                localStorage.setItem('vnb_currentUser', username);
                showToast('Login successful!', 'success');

                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1000);
            } else if (users[username]) {
                showToast('Incorrect password', 'error');
                setLoadingState(false);
            } else {
                showToast('User not found. Please sign up.', 'error');
                setLoadingState(false);
            }
        }, 1000);
    });

    function setLoadingState(isLoading) {
        elements.loginBtn.disabled = isLoading;
        elements.btnText.classList.toggle('hidden', isLoading);
        elements.btnLoader.classList.toggle('hidden', !isLoading);
    }

    function showToast(message, type = 'success') {
        elements.toastMessage.textContent = message;
        elements.toast.classList.remove('error');

        if (type === 'error') {
            elements.toast.classList.add('error');
            elements.toastIcon.innerHTML = `
                <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="12" y1="9" x2="12" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="12" y1="17" x2="12.01" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            `;
        } else {
            elements.toastIcon.innerHTML = `
                <path d="M22 11.08V12a10 10 0 11-5.93-9.14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M22 4L12 14.01l-3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            `;
        }

        elements.toast.classList.remove('hidden');
        setTimeout(() => elements.toast.classList.add('show'), 10);

        setTimeout(() => {
            elements.toast.classList.remove('show');
            setTimeout(() => elements.toast.classList.add('hidden'), 300);
        }, 3000);
    }
});
