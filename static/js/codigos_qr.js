const token = localStorage.getItem('authToken');
        if (!token) window.location.href = '/login';

        let currentQR = null;

        // Cargar materias
        async function loadMaterias() {
            try {
                const response = await fetch('/api/teacher/subjects', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    const data = await response.json();
                    const options = data.subjects.map(m => 
                        `<option value="${m.id}">${m.nombre} (${m.codigo_materia})</option>`
                    ).join('');

                    document.getElementById('materiaVirtual').innerHTML = options;
                    document.getElementById('materiaNumerico').innerHTML = options;
                    document.getElementById('materiaEnlace').innerHTML = options;
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }

        // Generar QR Virtual
        document.getElementById('formVirtual').addEventListener('submit', async (e) => {
            e.preventDefault();
            await generarCodigo('QR_CLASE_VIRTUAL', {
                materia_id: document.getElementById('materiaVirtual').value,
                duracion_minutos: parseInt(document.getElementById('duracionVirtual').value)
            });
        });

        // Generar Código Numérico
        document.getElementById('formNumerico').addEventListener('submit', async (e) => {
            e.preventDefault();
            await generarCodigo('CODIGO_NUMERICO', {
                materia_id: document.getElementById('materiaNumerico').value,
                duracion_minutos: parseInt(document.getElementById('duracionNumerico').value)
            });
        });

        // Generar Enlace
        document.getElementById('formEnlace').addEventListener('submit', async (e) => {
            e.preventDefault();
            await generarCodigo('ENLACE_UNICO', {
                materia_id: document.getElementById('materiaEnlace').value,
                duracion_minutos: parseInt(document.getElementById('duracionEnlace').value)
            });
        });

        // Función general para generar códigos
        async function generarCodigo(tipo, data) {
            try {
                const response = await fetch('/api/codes/generate', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ tipo, ...data })
                });

                if (response.ok) {
                    const result = await response.json();
                    currentQR = result;
                    mostrarQR(result);
                    showAlert('✅ Código generado exitosamente', 'success');
                    loadActiveCodes();
                } else {
                    showAlert('❌ Error al generar código', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showAlert('❌ Error de conexión', 'error');
            }
        }

        // Mostrar QR generado
        function mostrarQR(data) {
            document.getElementById('qrPreviewContainer').style.display = 'block';
            document.getElementById('qrTipo').textContent = data.tipo;
            document.getElementById('qrCodigo').textContent = data.codigo;
            document.getElementById('qrExpiracion').textContent = new Date(data.valido_hasta).toLocaleString('es-ES');
            document.getElementById('qrMateria').textContent = data.materia_nombre || '';

            // Generar QR con librería
            const canvas = document.getElementById('qrCanvas');
            QRCode.toCanvas(canvas, data.codigo, {
                width: 250,
                margin: 2,
                color: {
                    dark: '#023859',
                    light: '#FFFFFF'
                }
            });

            // Scroll al preview
            document.getElementById('qrPreviewContainer').scrollIntoView({ behavior: 'smooth' });
        }

        // Descargar QR
        document.getElementById('btnDescargarQR').addEventListener('click', () => {
            const canvas = document.getElementById('qrCanvas');
            const link = document.createElement('a');
            link.download = `QR_${currentQR.codigo}.png`;
            link.href = canvas.toDataURL();
            link.click();
        });

        // Compartir
        document.getElementById('btnCompartir').addEventListener('click', async () => {
            const text = `Código de asistencia: ${currentQR.codigo}\nVálido hasta: ${new Date(currentQR.valido_hasta).toLocaleString('es-ES')}`;
            
            if (navigator.share) {
                await navigator.share({ text });
            } else {
                navigator.clipboard.writeText(text);
                showAlert('📋 Código copiado al portapapeles', 'success');
            }
        });

        // Nuevo código
        document.getElementById('btnNuevo').addEventListener('click', () => {
            document.getElementById('qrPreviewContainer').style.display = 'none';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });

        // Cargar códigos activos
        async function loadActiveCodes() {
            try {
                const response = await fetch('/api/codes/active', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    const data = await response.json();
                    const container = document.getElementById('activeCodesContainer');
                    
                    if (data.codes && data.codes.length > 0) {
                        container.innerHTML = data.codes.map(code => {
                            const isExpired = new Date(code.valido_hasta) < new Date();
                            return `
                                <div class="qr-item">
                                    <div class="qr-item-info">
                                        <h4>${code.tipo}</h4>
                                        <p>Código: <strong>${code.codigo}</strong> • Expira: ${new Date(code.valido_hasta).toLocaleString('es-ES')}</p>
                                    </div>
                                    <span class="badge ${isExpired ? 'badge-error' : 'badge-success'}">
                                        ${isExpired ? 'Expirado' : 'Activo'}
                                    </span>
                                </div>
                            `;
                        }).join('');
                    } else {
                        container.innerHTML = '<p style="text-align: center; color: #6B7280; padding: 40px;">No hay códigos activos</p>';
                    }
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }

        // Alertas
        function showAlert(message, type) {
            const container = document.getElementById('alertContainer');
            container.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
            setTimeout(() => container.innerHTML = '', 5000);
        }

        // Inicializar
        loadMaterias();
        loadActiveCodes();

        // Actualizar códigos cada minuto
        setInterval(loadActiveCodes, 60000);