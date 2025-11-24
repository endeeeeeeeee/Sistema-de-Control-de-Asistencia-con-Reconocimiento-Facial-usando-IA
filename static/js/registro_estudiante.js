let currentStep = 1;
        let stream = null;
        let capturedPhotos = [];  // Array para múltiples fotos
        let currentPhotoIndex = 0;
        const TOTAL_PHOTOS = 50;  // Total de fotos a capturar
        let captureInterval = null;

        function showAlert(message, type) {
            const alert = document.getElementById('alert');
            alert.textContent = message;
            alert.className = `alert alert-${type}`;
            alert.style.display = 'block';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 5000);
        }

        function updateStepIndicators() {
            for (let i = 1; i <= 3; i++) {
                const indicator = document.getElementById(`stepIndicator${i}`);
                indicator.classList.remove('active', 'completed');
                if (i < currentStep) {
                    indicator.classList.add('completed');
                } else if (i === currentStep) {
                    indicator.classList.add('active');
                }
            }
        }

        function nextStep(step) {
            // Validar paso actual
            if (step === 1) {
                const nombre = document.getElementById('nombreCompleto').value.trim();
                const cedula = document.getElementById('cedula').value.trim();
                const telefono = document.getElementById('telefono').value.trim();
                const fechaNacimiento = document.getElementById('fechaNacimiento').value;
                const genero = document.getElementById('genero').value;
                const password = document.getElementById('password').value;
                const confirmPassword = document.getElementById('confirmPassword').value;

                if (!nombre || !cedula || !telefono || !fechaNacimiento || !genero || !password || !confirmPassword) {
                    showAlert('Por favor completa los campos obligatorios', 'error');
                    return;
                }

                if (password !== confirmPassword) {
                    showAlert('Las contraseñas no coinciden', 'error');
                    return;
                }

                if (password.length < 6) {
                    showAlert('La contraseña debe tener al menos 6 caracteres', 'error');
                    return;
                }
            }

            if (step === 2) {
                if (!capturedPhotos || capturedPhotos.length < TOTAL_PHOTOS) {
                    showAlert(`Por favor completa la captura de las ${TOTAL_PHOTOS} fotos. Capturas actuales: ${capturedPhotos ? capturedPhotos.length : 0}`, 'error');
                    return;
                }
            }

            // Ocultar paso actual
            document.getElementById(`step${step}`).classList.remove('active');
            
            // Mostrar siguiente paso
            currentStep = step + 1;
            document.getElementById(`step${currentStep}`).classList.add('active');
            updateStepIndicators();

            // Si es el paso 3, llenar resumen
            if (currentStep === 3) {
                document.getElementById('summaryName').textContent = document.getElementById('nombreCompleto').value;
                document.getElementById('summaryCedula').textContent = document.getElementById('cedula').value;
                document.getElementById('summaryEmail').textContent = document.getElementById('email').value || 'No proporcionado';
                document.getElementById('summaryPhone').textContent = document.getElementById('telefono').value;
                document.getElementById('summaryPhoto').src = capturedPhotos[0] || '';
            }

            window.scrollTo(0, 0);
        }

        function prevStep(step) {
            document.getElementById(`step${step}`).classList.remove('active');
            currentStep = step - 1;
            document.getElementById(`step${currentStep}`).classList.add('active');
            updateStepIndicators();
            window.scrollTo(0, 0);
        }

        async function startCapture() {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { 
                        width: { ideal: 1280 },
                        height: { ideal: 720 },
                        facingMode: 'user'
                    } 
                });
                
                const video = document.getElementById('video');
                video.srcObject = stream;
                video.style.display = 'block';
                
                document.getElementById('btnStartCamera').style.display = 'none';
                document.getElementById('captureProgress').style.display = 'block';
                document.getElementById('captureInstructions').style.display = 'block';
                
                // Resetear
                currentPhotoIndex = 0;
                capturedPhotos = [];
                
                // Esperar a que el video esté listo
                video.onloadedmetadata = () => {
                    // Iniciar captura automática después de 1 segundo
                    setTimeout(() => {
                        startAutomaticCapture();
                    }, 1000);
                };
                
            } catch (error) {
                showAlert('Error al acceder a la cámara. Por favor verifica los permisos.', 'error');
            }
        }

        function startAutomaticCapture() {
            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');
            const context = canvas.getContext('2d');
            
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            showAlert('¡Capturando fotos! Mueve ligeramente tu cabeza en diferentes direcciones...', 'success');
            
            // Capturar una foto cada 200ms (50 fotos en 10 segundos)
            captureInterval = setInterval(() => {
                if (currentPhotoIndex >= TOTAL_PHOTOS) {
                    clearInterval(captureInterval);
                    finishCapture();
                    return;
                }
                
                // Capturar foto
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                const photoData = canvas.toDataURL('image/jpeg', 0.7);
                capturedPhotos.push(photoData);
                
                currentPhotoIndex++;
                updateProgress();
                
            }, 200); // Una foto cada 200ms
        }

        function updateProgress() {
            document.getElementById('photoCount').textContent = currentPhotoIndex;
            const progressBar = document.getElementById('progressBar');
            const percentage = (currentPhotoIndex / TOTAL_PHOTOS) * 100;
            progressBar.style.width = percentage + '%';
        }

        function finishCapture() {
            const video = document.getElementById('video');
            
            showAlert('¡Perfecto! 50 fotos capturadas exitosamente', 'success');
            
            // Mostrar preview de la primera foto
            const preview = document.getElementById('photoPreview');
            preview.src = capturedPhotos[0];
            preview.style.display = 'block';
            
            // Ocultar video
            video.style.display = 'none';
            
            // Mostrar botón de reiniciar y habilitar siguiente
            document.getElementById('btnRetake').style.display = 'block';
            document.getElementById('btnNextStep2').disabled = false;
            document.getElementById('captureProgress').style.display = 'none';
            document.getElementById('captureInstructions').style.display = 'none';
            
            // Detener cámara
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        }

        function retakeAllPhotos() {
            // Limpiar
            if (captureInterval) {
                clearInterval(captureInterval);
            }
            
            capturedPhotos = [];
            currentPhotoIndex = 0;
            
            document.getElementById('photoPreview').style.display = 'none';
            document.getElementById('btnRetake').style.display = 'none';
            document.getElementById('btnNextStep2').disabled = true;
            document.getElementById('progressBar').style.width = '0%';
            
            // Reiniciar
            startCapture();
        }

        async function registerStudent() {
            console.log('=== REGISTRO ESTUDIANTE INICIADO ===');
            
            const btnRegister = document.getElementById('btnRegister');
            if (!btnRegister) {
                console.error('Botón de registro no encontrado');
                return;
            }
            
            btnRegister.disabled = true;
            btnRegister.textContent = '⏳ Registrando...';

            // Validar que hay fotos capturadas
            if (!capturedPhotos || capturedPhotos.length === 0) {
                showAlert('Error: No se han capturado fotos. Por favor regresa y captura las fotos.', 'error');
                btnRegister.disabled = false;
                btnRegister.textContent = '✅ Confirmar Registro';
                return;
            }

            console.log(`Total de fotos capturadas: ${capturedPhotos.length}`);

            try {
                const payload = {
                    nombre_completo: document.getElementById('nombreCompleto').value,
                    cedula: document.getElementById('cedula').value,
                    telefono: document.getElementById('telefono').value,
                    email: document.getElementById('email').value || null,
                    fecha_nacimiento: document.getElementById('fechaNacimiento').value,
                    genero: document.getElementById('genero').value,
                    password: document.getElementById('password').value,
                    fotos_base64: capturedPhotos,  // Enviar array de fotos
                    foto_base64: capturedPhotos[0]  // Mantener compatibilidad con foto principal
                };

                console.log('Datos a enviar:', {
                    ...payload,
                    password: '***',
                    fotos_base64: `[${capturedPhotos.length} fotos]`,
                    foto_base64: 'base64...'
                });

                const response = await fetch('/api/auth/registro', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });

                console.log('Respuesta recibida:', response.status, response.statusText);

                // Verificar si la respuesta es JSON antes de parsear
                const contentType = response.headers.get('content-type');
                let data;
                
                if (contentType && contentType.includes('application/json')) {
                    data = await response.json();
                } else {
                    // Si no es JSON, probablemente es HTML (error del servidor)
                    const text = await response.text();
                    console.error('Respuesta no JSON recibida:', text.substring(0, 200));
                    
                    if (response.status === 413) {
                        showAlert('Error: El tamaño de los datos es demasiado grande. Por favor, reduce el número de fotos o su calidad.', 'error');
                    } else {
                        showAlert('Error del servidor: ' + response.status + ' ' + response.statusText, 'error');
                    }
                    btnRegister.disabled = false;
                    btnRegister.textContent = '✅ Confirmar Registro';
                    return;
                }

                console.log('Datos de respuesta:', data);

                if (response.ok && data.success) {
                    showAlert('¡Registro exitoso!', 'success');
                    // Mostrar paso de éxito
                    document.getElementById('step3').classList.remove('active');
                    document.getElementById('step4').classList.add('active');
                } else {
                    // Manejar errores específicos
                    if (response.status === 413) {
                        showAlert(data.error || 'El tamaño de los datos es demasiado grande. Por favor, reduce el número de fotos.', 'error');
                    } else {
                        showAlert(data.error || 'Error en el registro', 'error');
                    }
                    btnRegister.disabled = false;
                    btnRegister.textContent = '✅ Confirmar Registro';
                }
            } catch (error) {
                console.error('Error en registerStudent:', error);
                
                // Manejar errores de parsing JSON
                if (error instanceof SyntaxError && error.message.includes('JSON')) {
                    showAlert('Error: El servidor respondió con un formato incorrecto. Por favor, intenta con menos fotos.', 'error');
                } else {
                    showAlert('Error de conexión: ' + error.message, 'error');
                }
                btnRegister.disabled = false;
                btnRegister.textContent = '✅ Confirmar Registro';
            }
        }