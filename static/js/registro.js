async function register(event) {
            event.preventDefault();
            
            const alertBox = document.getElementById('alertBox');
            
            const nombre = document.getElementById('nombre').value.trim();
            const cedula = document.getElementById('cedula').value.trim();
            const telefono = document.getElementById('telefono').value.trim();
            const email = document.getElementById('email').value.trim();
            const fecha_nacimiento = document.getElementById('fecha_nacimiento').value;
            const genero = document.getElementById('genero').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            if (password !== confirmPassword) {
                alertBox.textContent = 'Las contraseñas no coinciden';
                alertBox.className = 'alert active error';
                return;
            }

            alertBox.textContent = 'Creando cuenta...';
            alertBox.className = 'alert active success';

            try {
                const response = await fetch('/api/auth/registro', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        nombre_completo: nombre,
                        cedula: cedula,
                        telefono: telefono,
                        email: email || null,
                        fecha_nacimiento: fecha_nacimiento,
                        genero: genero,
                        password: password
                    })
                });

                const data = await response.json();

                if (data.success) {
                    alertBox.textContent = `Cuenta creada exitosamente. Tu código es: ${data.codigo_usuario}`;
                    alertBox.className = 'alert active success';
                    
                    document.getElementById('registerForm').reset();
                    
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 3000);
                } else {
                    alertBox.textContent = data.error || 'Error al crear la cuenta';
                    alertBox.className = 'alert active error';
                }
            } catch (error) {
                alertBox.textContent = 'Error de conexión. Intenta de nuevo.';
                alertBox.className = 'alert active error';
            }
        }

        // Check if already logged in
        if (localStorage.getItem('authToken')) {
            window.location.href = '/dashboard';
        }