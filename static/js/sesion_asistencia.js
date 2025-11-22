const API_BASE = '/api';
        let videoStream = null;
        let reconocimientoInterval = null;
        let sesionActual = null;
        let reconocidos = new Set();
        let timerInterval = null;
        let tiempoInicio = null;
        let actualizacionInterval = null;
        const equipoId = new URLSearchParams(window.location.search).get('equipo_id');

        // Cargar datos del equipo
        async function cargarEquipo() {
            try {
                const token = localStorage.getItem('authToken');
                const response = await fetch(`${API_BASE}/equipos/${equipoId}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                const data = await response.json();
                if (data.success) {
                    document.getElementById('equipoNombre').textContent = data.equipo.nombre_equipo;
                    document.getElementById('totalMiembros').textContent = data.miembros.length;
                }
            } catch (error) {
                console.error('Error cargando equipo:', error);
            }
        }

        // Iniciar cámara
        async function iniciarCamara() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { 
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    } 
                });
                videoStream = stream;
                document.getElementById('videoElement').srcObject = stream;
                return true;
            } catch (error) {
                console.error('Error accediendo a la cámara:', error);
                showAlert('No se pudo acceder a la cámara', 'error');
                return false;
            }
        }

        // Iniciar sesión de asistencia
        async function iniciarSesion() {
            try {
                const token = localStorage.getItem('authToken');

                // Verificar si hay sesión activa primero
                const checkResponse = await fetch(`${API_BASE}/sesiones/activa/${equipoId}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                const checkData = await checkResponse.json();
                
                if (checkData.success && checkData.sesion_activa) {
                    const confirmar = confirm('Ya hay una sesión activa para este equipo. ¿Deseas continuar con esa sesión?');
                    if (confirmar) {
                        sesionActual = checkData.sesion_id;
                        
                        // Iniciar cámara
                        const camaraOk = await iniciarCamara();
                        if (!camaraOk) return;
                        
                        // Actualizar UI
                        document.getElementById('statusIndicator').className = 'status active';
                        document.getElementById('statusIndicator').textContent = '🟢 Sesión Activa';
                        document.getElementById('btnIniciar').style.display = 'none';
                        document.getElementById('btnDetener').style.display = 'inline-block';
                        document.getElementById('btnMostrarQR').style.display = 'block';

                        showAlert('Continuando sesión activa...', 'success');
                        iniciarReconocimientoAutomatico();
                        tiempoInicio = Date.now();
                        iniciarTimer();
                        cargarAsistenciasExistentes();
                        iniciarActualizacionPeriodica();
                        return;
                    } else {
                        return;
                    }
                }

                // Iniciar cámara
                const camaraOk = await iniciarCamara();
                if (!camaraOk) return;

                // Crear sesión en backend
                const response = await fetch(`${API_BASE}/sesiones/iniciar`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        equipo_id: parseInt(equipoId),
                        duracion_minutos: 30
                    })
                });

                const data = await response.json();
                if (data.success) {
                    sesionActual = data.sesion_id;
                    
                    // Actualizar UI
                    document.getElementById('statusIndicator').className = 'status active';
                    document.getElementById('statusIndicator').textContent = '🟢 Sesión Activa';
                    document.getElementById('btnIniciar').style.display = 'none';
                    document.getElementById('btnDetener').style.display = 'inline-block';

                    showAlert('Sesión iniciada. El reconocimiento comenzará automáticamente.', 'success');

                    // Iniciar reconocimiento automático
                    iniciarReconocimientoAutomatico();
                    
                    // Iniciar timer
                    tiempoInicio = Date.now();
                    iniciarTimer();
                    
                    // Cargar asistencias existentes y activar actualización periódica
                    cargarAsistenciasExistentes();
                    iniciarActualizacionPeriodica();
                } else {
                    showAlert(data.error, 'error');
                }
            } catch (error) {
                console.error('Error iniciando sesión:', error);
                showAlert('Error iniciando sesión', 'error');
            }
        }

        // Detener sesión
        async function detenerSesion() {
            try {
                console.log('🛑 Deteniendo sesión...', sesionActual);
                const token = localStorage.getItem('authToken');

                // Detener reconocimiento
                if (reconocimientoInterval) {
                    clearInterval(reconocimientoInterval);
                    reconocimientoInterval = null;
                    console.log('✅ Reconocimiento detenido');
                }

                // Detener timer
                if (timerInterval) {
                    clearInterval(timerInterval);
                    timerInterval = null;
                    console.log('✅ Timer detenido');
                }
                
                // Detener actualización periódica
                if (actualizacionInterval) {
                    clearInterval(actualizacionInterval);
                    actualizacionInterval = null;
                    console.log('✅ Actualización periódica detenida');
                }

                // Detener cámara
                if (videoStream) {
                    videoStream.getTracks().forEach(track => track.stop());
                    videoStream = null;
                    console.log('✅ Cámara detenida');
                }

                // Detener sesión en backend
                if (sesionActual) {
                    console.log('📡 Enviando petición al backend...');
                    console.log('URL completa:', `${API_BASE}/sesiones/${sesionActual}/detener`);
                    console.log('Token presente:', token ? 'Sí' : 'No');
                    
                    try {
                        const response = await fetch(`${API_BASE}/sesiones/${sesionActual}/detener`, {
                            method: 'POST',
                            headers: { 
                                'Authorization': `Bearer ${token}`,
                                'Content-Type': 'application/json'
                            }
                        });

                        console.log('📥 Status HTTP:', response.status, response.statusText);

                        if (!response.ok) {
                            console.error('❌ Respuesta no OK:', response.status);
                            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                        }

                        const data = await response.json();
                        console.log('📦 Datos del backend:', data);

                        if (!data.success) {
                            console.error('❌ Backend retornó success=false:', data.error);
                            showAlert('Error del servidor: ' + (data.error || 'Error desconocido'), 'error');
                            // Continuar con actualización de UI
                        }
                        
                        console.log('✅ Sesión detenida en el backend');
                    } catch (fetchError) {
                        console.error('❌ Error en fetch:', fetchError.message);
                        showAlert('⚠️ Error de conexión: ' + fetchError.message + '. La sesión se detendrá localmente.', 'warning');
                        // Continuar con la actualización de UI
                    }
                    
                    sesionActual = null;
                } else {
                    console.log('⚠️ No había sesión activa');
                }

                // Actualizar UI
                document.getElementById('statusIndicator').className = 'status inactive';
                document.getElementById('statusIndicator').textContent = '🔴 Cámara Inactiva';
                document.getElementById('btnIniciar').style.display = 'inline-block';
                document.getElementById('btnDetener').style.display = 'none';

                showAlert('✅ Sesión finalizada correctamente', 'success');
            } catch (error) {
                console.error('❌ Error deteniendo sesión:', error);
                showAlert('Error al detener sesión: ' + error.message, 'error');
            }
        }

        // Iniciar reconocimiento automático
        function iniciarReconocimientoAutomatico() {
            reconocimientoInterval = setInterval(async () => {
                await capturarYReconocer();
            }, 2000); // Reconocer cada 2 segundos
        }

        // Capturar frame y enviar a reconocimiento
        async function capturarYReconocer() {
            try {
                console.log('🔍 Capturando frame para reconocimiento...');
                const video = document.getElementById('videoElement');
                const canvas = document.getElementById('canvas');
                const context = canvas.getContext('2d');

                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                context.drawImage(video, 0, 0, canvas.width, canvas.height);

                const imagenBase64 = canvas.toDataURL('image/jpeg', 0.8);
                console.log('📸 Frame capturado, tamaño:', imagenBase64.length, 'caracteres');

                const token = localStorage.getItem('authToken');
                console.log('🔑 Token:', token ? 'OK' : 'NO ENCONTRADO');
                console.log('🆔 Sesión ID:', sesionActual);

                const response = await fetch(`${API_BASE}/facial/reconocer-frame`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        imagen: imagenBase64,
                        sesion_id: sesionActual
                    })
                });

                console.log('📡 Respuesta HTTP:', response.status);
                const data = await response.json();
                console.log('📦 Datos recibidos:', data);

                if (data.success && data.reconocido && !data.ya_registrado) {
                    console.log('✅ Usuario reconocido:', data.nombre);
                    agregarReconocido(data);
                } else if (data.mensaje) {
                    console.log('ℹ️', data.mensaje);
                }
            } catch (error) {
                console.error('❌ Error en reconocimiento:', error);
            }
        }

        // Agregar usuario reconocido a la lista
        function agregarReconocido(data) {
            if (reconocidos.has(data.codigo)) return;

            reconocidos.add(data.codigo);

            const container = document.getElementById('reconocidosContainer');
            const item = document.createElement('div');
            item.className = 'recognized-item';
            item.innerHTML = `
                <div class="icon">✅</div>
                <div class="info">
                    <div class="name">${data.nombre}</div>
                    <div class="time">${new Date().toLocaleTimeString()}</div>
                </div>
                <div class="confidence">${data.confianza.toFixed(1)}%</div>
            `;

            container.insertBefore(item, container.firstChild);

            // Actualizar contador
            document.getElementById('totalReconocidos').textContent = reconocidos.size;

            // Mostrar alerta
            showAlert(data.mensaje, 'success', 3000);
        }

        // Timer
        function iniciarTimer() {
            timerInterval = setInterval(() => {
                const ahora = Date.now();
                const transcurrido = Math.floor((ahora - tiempoInicio) / 1000);
                const minutos = Math.floor(transcurrido / 60);
                const segundos = transcurrido % 60;
                document.getElementById('timer').textContent = 
                    `${String(minutos).padStart(2, '0')}:${String(segundos).padStart(2, '0')}`;
            }, 1000);
        }

        // Mostrar alerta
        function showAlert(message, type, duration = 5000) {
            const alert = document.getElementById('alert');
            alert.textContent = message;
            alert.className = `alert alert-${type} active`;
            
            setTimeout(() => {
                alert.classList.remove('active');
            }, duration);
        }

        // Volver al dashboard
        function volverDashboard() {
            if (sesionActual) {
                if (confirm('¿Deseas finalizar la sesión?')) {
                    detenerSesion();
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 500);
                }
            } else {
                window.location.href = '/dashboard';
            }
        }

        // Inicializar
        window.addEventListener('DOMContentLoaded', () => {
            if (!equipoId) {
                showAlert('ID de equipo no especificado', 'error');
                setTimeout(() => window.location.href = '/dashboard', 2000);
                return;
            }

            cargarEquipo();
        });

        // Limpiar al salir
        window.addEventListener('beforeunload', () => {
            if (sesionActual) {
                detenerSesion();
            }
        });

        // ===== FUNCIONALIDAD QR INDIVIDUAL PARA VIRTUALES =====
        let qrActual = null;
        let qrTimerInterval = null;
        let qrObject = null;
        let miembrosEquipo = [];

        // Cargar miembros del equipo
        async function cargarMiembrosParaQR() {
            try {
                const token = localStorage.getItem('authToken');
                const response = await fetch(`${API_BASE}/equipos/${equipoId}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const data = await response.json();
                
                if (data.success) {
                    miembrosEquipo = data.miembros;
                    renderizarMiembros(miembrosEquipo);
                }
            } catch (error) {
                console.error('Error cargando miembros:', error);
            }
        }

        // Renderizar lista de miembros
        function renderizarMiembros(miembros) {
            const select = document.getElementById('selectMiembro');
            select.innerHTML = '<option value="">Seleccionar estudiante...</option>';
            
            miembros.forEach(miembro => {
                const option = document.createElement('option');
                option.value = miembro.id;
                option.textContent = `${miembro.nombre_completo} (${miembro.codigo_usuario})`;
                option.dataset.nombre = miembro.nombre_completo.toLowerCase();
                option.dataset.codigo = miembro.codigo_usuario.toLowerCase();
                select.appendChild(option);
            });
        }

        // Filtrar miembros por búsqueda
        function filtrarMiembros() {
            const searchText = document.getElementById('searchMiembro').value.toLowerCase();
            
            if (searchText === '') {
                renderizarMiembros(miembrosEquipo);
                return;
            }
            
            const filtrados = miembrosEquipo.filter(miembro => 
                miembro.nombre_completo.toLowerCase().includes(searchText) ||
                miembro.codigo_usuario.toLowerCase().includes(searchText)
            );
            
            renderizarMiembros(filtrados);
        }

        // Mostrar/Ocultar sección QR
        function toggleQRSection() {
            const section = document.getElementById('qrSection');
            const btn = document.getElementById('btnMostrarQR');
            
            if (section.style.display === 'none') {
                section.style.display = 'block';
                btn.textContent = '📱 Ocultar QR Individual';
                cargarMiembrosParaQR();
            } else {
                section.style.display = 'none';
                btn.textContent = '📱 QR Individual Virtual';
                document.getElementById('qrContainer').style.display = 'none';
            }
        }

        // Generar QR individual
        async function generarQRIndividual() {
            const selectMiembro = document.getElementById('selectMiembro');
            const usuarioId = selectMiembro.value;
            
            if (!usuarioId) {
                showAlert('Selecciona un estudiante primero', 'error');
                return;
            }
            
            const miembro = miembrosEquipo.find(m => m.id == usuarioId);
            
            try {
                const token = localStorage.getItem('authToken');
                const response = await fetch(`${API_BASE}/qr/generar-individual`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        equipo_id: parseInt(equipoId),
                        usuario_id: parseInt(usuarioId),
                        duracion_minutos: 5
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    qrActual = data;
                    mostrarQRIndividual(data.qr_code, data.expira_en, miembro.nombre_completo);
                    iniciarTimerQR(data.expira_en);
                    showAlert(`QR generado para ${miembro.nombre_completo}`, 'success');
                } else {
                    showAlert('Error: ' + data.error, 'error');
                }
            } catch (error) {
                console.error('Error generando QR:', error);
                showAlert('Error de conexión al generar QR', 'error');
            }
        }

        // Mostrar QR en el contenedor
        function mostrarQRIndividual(codigo, expiraEn, nombre) {
            const container = document.getElementById('qrContainer');
            const qrCodeDiv = document.getElementById('qrCode');
            
            // Limpiar QR anterior
            qrCodeDiv.innerHTML = '';
            
            // Mostrar contenedor
            container.style.display = 'flex';
            
            // Crear nuevo QR con URL completa para validación
            const urlValidacion = `${window.location.origin}/validar-qr?codigo=${codigo}`;
            
            qrObject = new QRCode(qrCodeDiv, {
                text: urlValidacion,
                width: 200,
                height: 200,
                colorDark: "#0c4a6e",
                colorLight: "#ffffff",
                correctLevel: QRCode.CorrectLevel.H
            });
            
            // Mostrar nombre
            document.getElementById('qrNombre').textContent = nombre;
        }

        // Timer del QR
        function iniciarTimerQR(expiraEn) {
            if (qrTimerInterval) {
                clearInterval(qrTimerInterval);
            }

            qrTimerInterval = setInterval(() => {
                const ahora = new Date();
                const expira = new Date(expiraEn);
                const diff = Math.floor((expira - ahora) / 1000);

                if (diff <= 0) {
                    clearInterval(qrTimerInterval);
                    document.getElementById('qrTimer').textContent = '⚠️ EXPIRADO';
                    showAlert('El QR ha expirado', 'warning');
                } else {
                    const minutos = Math.floor(diff / 60);
                    const segundos = diff % 60;
                    document.getElementById('qrTimer').textContent = 
                        `${String(minutos).padStart(2, '0')}:${String(segundos).padStart(2, '0')}`;
                }
            }, 1000);
        }

        // Cargar asistencias existentes
        async function cargarAsistenciasExistentes() {
            try {
                const token = localStorage.getItem('authToken');
                const response = await fetch(`${API_BASE}/equipos/${equipoId}/asistencias-hoy`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                const data = await response.json();
                if (data.success && data.asistencias) {
                    data.asistencias.forEach(asistencia => {
                        if (!reconocidos.has(asistencia.codigo_usuario)) {
                            agregarReconocido({
                                codigo: asistencia.codigo_usuario,
                                nombre: asistencia.nombre_completo,
                                confianza: 100,
                                mensaje: 'Asistencia registrada'
                            });
                        }
                    });
                }
            } catch (error) {
                console.error('Error cargando asistencias:', error);
            }
        }

        // Iniciar actualización periódica cada 5 segundos
        function iniciarActualizacionPeriodica() {
            if (actualizacionInterval) {
                clearInterval(actualizacionInterval);
            }
            
            actualizacionInterval = setInterval(() => {
                cargarAsistenciasExistentes();
            }, 5000); // Actualizar cada 5 segundos
        }

        // Mostrar botón QR cuando se inicia sesión
        const originalIniciarSesion = iniciarSesion;
        iniciarSesion = async function() {
            await originalIniciarSesion();
            document.getElementById('btnMostrarQR').style.display = 'block';
        };