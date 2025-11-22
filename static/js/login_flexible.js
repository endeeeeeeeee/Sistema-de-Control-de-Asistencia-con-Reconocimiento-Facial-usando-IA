async function login(event) {
            event.preventDefault();
            
            const alertBox = document.getElementById('alertBox');
            const codigo = document.getElementById('codigo').value.trim();
            const password = document.getElementById('password').value;

            alertBox.textContent = 'Iniciando sesión...';
            alertBox.className = 'alert active success';

            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: codigo, password: password })
                });

                const data = await response.json();

                if (data.success && data.token) {
                    localStorage.setItem('authToken', data.token);
                    localStorage.setItem('user', JSON.stringify(data.user));
                    alertBox.textContent = 'Inicio exitoso. Redirigiendo...';
                    alertBox.className = 'alert active success';
                    
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 800);
                } else {
                    alertBox.textContent = data.error || 'Código o contraseña incorrectos';
                    alertBox.className = 'alert active error';
                }
            } catch (error) {
                alertBox.textContent = 'Error de conexión. Intenta de nuevo.';
                alertBox.className = 'alert active error';
            }
        }

        // Check if already logged in - REMOVED TO PREVENT LOOP
        // The dashboard will redirect to login if no valid token
        // if (localStorage.getItem('authToken')) {
        //     window.location.href = '/dashboard';
        // }