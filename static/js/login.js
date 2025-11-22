// Toggle mostrar/ocultar contraseña
        document.getElementById('togglePassword').addEventListener('click', function() {
            const passwordInput = document.getElementById('password');
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.textContent = type === 'password' ? '👁️' : '🙈';
        });

        // Función para mostrar alertas
        function showAlert(message, type = 'error') {
            const alert = document.getElementById('alert');
            alert.textContent = message;
            alert.className = `alert alert-${type}`;
            alert.style.display = 'block';
            
            setTimeout(() => {
                alert.style.display = 'none';
            }, 5000);
        }

        // Manejo del formulario de login
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const btnLogin = document.getElementById('btnLogin');
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            const remember = document.getElementById('remember').checked;

            if (!username || !password) {
                showAlert('Por favor, completa todos los campos', 'error');
                return;
            }

            // Deshabilitar botón y mostrar loading
            btnLogin.disabled = true;
            const originalText = btnLogin.textContent;
            btnLogin.innerHTML = '<span class="loading"></span> Iniciando sesión...';

            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: username,
                        password: password
                    })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    // Guardar token
                    localStorage.setItem('authToken', data.token);
                    localStorage.setItem('user', JSON.stringify(data.user));
                    
                    if (remember) {
                        localStorage.setItem('remember', 'true');
                    }

                    showAlert('¡Inicio de sesión exitoso! Redirigiendo...', 'success');
                    
                    // Redirigir al dashboard
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                } else {
                    showAlert(data.message || 'Usuario o contraseña incorrectos', 'error');
                    btnLogin.disabled = false;
                    btnLogin.textContent = originalText;
                }
            } catch (error) {
                console.error('Error:', error);
                showAlert('Error de conexión. Por favor, intenta nuevamente.', 'error');
                btnLogin.disabled = false;
                btnLogin.textContent = originalText;
            }
        });

        // Cambiar entre login y registro
        let isLoginMode = true;
        
        document.getElementById('switchFormLink').addEventListener('click', function(e) {
            e.preventDefault();
            isLoginMode = !isLoginMode;
            
            const loginForm = document.getElementById('loginForm');
            const registerForm = document.getElementById('registerForm');
            const formTitle = document.getElementById('formTitle');
            const formSubtitle = document.getElementById('formSubtitle');
            const switchText = document.getElementById('switchText');
            const switchLink = document.getElementById('switchFormLink');
            
            if (isLoginMode) {
                // Mostrar login
                loginForm.style.display = 'block';
                registerForm.style.display = 'none';
                formTitle.textContent = 'Bienvenido';
                formSubtitle.textContent = 'Ingresa tus credenciales para continuar';
                switchText.textContent = '¿Primera vez? ';
                switchLink.textContent = 'Regístrate como docente';
            } else {
                // Mostrar registro
                loginForm.style.display = 'none';
                registerForm.style.display = 'block';
                formTitle.textContent = 'Crear Cuenta';
                formSubtitle.textContent = 'Regístrate para empezar a usar CLASS VISION';
                switchText.textContent = '¿Ya tienes cuenta? ';
                switchLink.textContent = 'Inicia sesión';
            }
        });

        // Toggle password en registro
        document.getElementById('toggleRegPassword').addEventListener('click', function() {
            const passwordInput = document.getElementById('regPassword');
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.textContent = type === 'password' ? '👁️' : '🙈';
        });

        // Manejo del formulario de registro
        document.getElementById('registerForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const btnRegister = document.getElementById('btnRegister');
            const fullName = document.getElementById('regFullName').value.trim();
            const username = document.getElementById('regUsername').value.trim();
            const password = document.getElementById('regPassword').value;
            const passwordConfirm = document.getElementById('regPasswordConfirm').value;

            if (!fullName || !username || !password) {
                showAlert('Por favor, completa todos los campos', 'error');
                return;
            }

            if (password.length < 6) {
                showAlert('La contraseña debe tener al menos 6 caracteres', 'error');
                return;
            }

            if (password !== passwordConfirm) {
                showAlert('Las contraseñas no coinciden', 'error');
                return;
            }

            btnRegister.disabled = true;
            const originalText = btnRegister.textContent;
            btnRegister.innerHTML = '<span class="loading"></span> Registrando...';

            try {
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: username,
                        password: password,
                        full_name: fullName
                    })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    showAlert('¡Registro exitoso! Iniciando sesión...', 'success');
                    
                    // Auto-login después del registro
                    localStorage.setItem('authToken', data.token);
                    localStorage.setItem('user', JSON.stringify(data.user));
                    
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1500);
                } else {
                    showAlert(data.error || 'Error en el registro', 'error');
                    btnRegister.disabled = false;
                    btnRegister.textContent = originalText;
                }
            } catch (error) {
                console.error('Error:', error);
                showAlert('Error de conexión. Por favor, intenta nuevamente.', 'error');
                btnRegister.disabled = false;
                btnRegister.textContent = originalText;
            }
        });

        // Auto-completar si hay sesión guardada
        window.addEventListener('load', function() {
            const remember = localStorage.getItem('remember');
            if (remember === 'true') {
                const user = JSON.parse(localStorage.getItem('user') || '{}');
                if (user.username) {
                    document.getElementById('username').value = user.username;
                    document.getElementById('remember').checked = true;
                }
            }
        });