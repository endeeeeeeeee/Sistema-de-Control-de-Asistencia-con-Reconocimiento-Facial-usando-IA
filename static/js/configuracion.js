const token = localStorage.getItem('authToken');
        if (!token) window.location.href = '/login';

        // Seleccionar modo
        document.querySelectorAll('.mode-card').forEach(card => {
            card.addEventListener('click', function() {
                document.querySelectorAll('.mode-card').forEach(c => c.classList.remove('active'));
                this.classList.add('active');
                document.getElementById('modoOperacion').value = this.dataset.mode;
            });
        });

        // Aplicar modo oscuro desde localStorage
        const darkMode = localStorage.getItem('darkMode') === 'true';
        document.getElementById('modoOscuro').checked = darkMode;
        if (darkMode) {
            document.body.classList.add('dark-mode');
        }

        // Toggle modo oscuro
        document.getElementById('modoOscuro').addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('darkMode', 'true');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('darkMode', 'false');
            }
        });

        // Cargar configuración actual
        async function loadConfig() {
            try {
                const response = await fetch('/api/config', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    const config = await response.json();
                    
                    // General
                    document.getElementById('nombreInstitucion').value = config.nombre_institucion || '';
                    document.querySelector(`[data-mode="${config.modo_operacion}"]`)?.click();
                    
                    // Reglas
                    const reglas = config.reglas_json || {};
                    document.getElementById('toleranciaMinutos').value = reglas.tolerancia_minutos || 15;
                    document.getElementById('minimoAsistencia').value = reglas.minimo_asistencia || 75;
                    document.getElementById('umbralDesercion').value = reglas.umbral_desercion || 3;

                    document.getElementById('permitirJustificacionEstudiante').checked = reglas.permitir_justificacion || false;
                    document.getElementById('notificacionTutores').checked = reglas.notificacion_tutores || false;
                    document.getElementById('gamificacionActiva').checked = reglas.gamificacion_activa || false;
                    
                    // Facial
                    document.getElementById('umbralConfianza').value = reglas.umbral_confianza || 85;
                    document.getElementById('umbralLiveness').value = reglas.umbral_liveness || 70;
                    document.getElementById('detectarLiveness').checked = reglas.detectar_liveness || false;
                    document.getElementById('guardarFotosAsistencia').checked = reglas.guardar_fotos || false;
                    
                    // QR Uso Único
                    document.getElementById('qrUsoUnico').checked = reglas.qr_uso_unico !== false;
                    
                    document.getElementById('lastUpdate').textContent = new Date(config.updated_at).toLocaleString('es-ES');
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }

        // Guardar General
        document.getElementById('formGeneral').addEventListener('submit', async (e) => {
            e.preventDefault();
            await saveConfig({
                nombre_institucion: document.getElementById('nombreInstitucion').value,
                modo_operacion: document.getElementById('modoOperacion').value
            }, 'general');
        });

        // Guardar Reglas
        document.getElementById('formReglas').addEventListener('submit', async (e) => {
            e.preventDefault();
            await saveConfig({
                reglas_json: {
                    tolerancia_minutos: parseInt(document.getElementById('toleranciaMinutos').value),
                    minimo_asistencia: parseInt(document.getElementById('minimoAsistencia').value),
                    umbral_desercion: parseInt(document.getElementById('umbralDesercion').value),
                    qr_uso_unico: document.getElementById('qrUsoUnico').checked,
                    permitir_justificacion: document.getElementById('permitirJustificacionEstudiante').checked,
                    notificacion_tutores: document.getElementById('notificacionTutores').checked,
                    gamificacion_activa: document.getElementById('gamificacionActiva').checked
                }
            }, 'reglas');
        });

        // Guardar Facial
        document.getElementById('formFacial').addEventListener('submit', async (e) => {
            e.preventDefault();
            const reglas = {
                umbral_confianza: parseInt(document.getElementById('umbralConfianza').value),
                umbral_liveness: parseInt(document.getElementById('umbralLiveness').value),
                detectar_liveness: document.getElementById('detectarLiveness').checked,
                guardar_fotos: document.getElementById('guardarFotosAsistencia').checked
            };
            await saveConfig({ reglas_json: reglas }, 'facial');
        });



        // Función general para guardar
        async function saveConfig(data, tipo) {
            try {
                const response = await fetch('/api/config', {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    showAlert(`✅ Configuración de ${tipo} guardada exitosamente`, 'success');
                    loadConfig();
                } else {
                    showAlert('❌ Error al guardar configuración', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showAlert('❌ Error de conexión', 'error');
            }
        }



        // Alertas
        function showAlert(message, type) {
            const container = document.getElementById('alertContainer');
            container.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
            setTimeout(() => container.innerHTML = '', 5000);
        }

        // Inicializar
        loadConfig();