const API_BASE = window.location.origin + '/api';
        const authToken = localStorage.getItem('authToken');
        let currentData = [];

        // Verificar autenticación
        if (!authToken) {
            window.location.href = '/login';
        }

        // Inicializar
        async function init() {
            await cargarEquipos();
            
            // Si viene con equipo_id en URL, pre-seleccionar
            const urlParams = new URLSearchParams(window.location.search);
            const equipoId = urlParams.get('equipo_id');
            
            if (equipoId) {
                document.getElementById('equipoFilter').value = equipoId;
            }

            // Establecer fechas por defecto (últimos 7 días)
            const hoy = new Date();
            const hace7dias = new Date();
            hace7dias.setDate(hoy.getDate() - 7);
            
            document.getElementById('fechaFin').value = hoy.toISOString().split('T')[0];
            document.getElementById('fechaInicio').value = hace7dias.toISOString().split('T')[0];

            // Cargar datos
            await aplicarFiltros();
        }

        async function cargarEquipos() {
            try {
                const response = await fetch(`${API_BASE}/equipos`, {
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    }
                });
                
                const data = await response.json();
                
                if (data.success && data.equipos) {
                    const select = document.getElementById('equipoFilter');
                    data.equipos.forEach(equipo => {
                        const option = document.createElement('option');
                        option.value = equipo.id;
                        option.textContent = equipo.nombre_equipo;
                        select.appendChild(option);
                    });
                }
            } catch (error) {
                console.error('Error cargando equipos:', error);
            }
        }

        async function aplicarFiltros() {
            const equipoId = document.getElementById('equipoFilter').value;
            const fechaInicio = document.getElementById('fechaInicio').value;
            const fechaFin = document.getElementById('fechaFin').value;

            // Construir query string
            const params = new URLSearchParams();
            if (equipoId) params.append('equipo_id', equipoId);
            if (fechaInicio) params.append('fecha_inicio', fechaInicio);
            if (fechaFin) params.append('fecha_fin', fechaFin);

            // Mostrar loading
            document.getElementById('loadingState').style.display = 'block';
            document.getElementById('emptyState').style.display = 'none';
            document.getElementById('tableContainer').style.display = 'none';
            document.getElementById('statsGrid').style.display = 'none';

            try {
                const response = await fetch(`${API_BASE}/reportes/asistencias?${params}`, {
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentData = data.asistencias;
                    renderTable(currentData);
                    calcularEstadisticas(currentData);
                } else {
                    showNotification('Error: ' + data.error, 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('Error al cargar datos', 'error');
            } finally {
                document.getElementById('loadingState').style.display = 'none';
            }
        }

        function renderTable(asistencias) {
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';

            if (asistencias.length === 0) {
                document.getElementById('emptyState').style.display = 'block';
                document.getElementById('tableContainer').style.display = 'none';
                return;
            }

            document.getElementById('tableContainer').style.display = 'block';
            document.getElementById('tableTitle').textContent = `Registro de Asistencias (${asistencias.length} registros)`;

            asistencias.forEach(asistencia => {
                const row = document.createElement('tr');
                
                // Badge para método
                let metodoBadge = '';
                if (asistencia.metodo_entrada === 'reconocimiento_facial') {
                    metodoBadge = '<span class="badge badge-success">🤖 Facial</span>';
                } else if (asistencia.metodo_entrada === 'qr') {
                    metodoBadge = '<span class="badge badge-info">📱 QR</span>';
                } else {
                    metodoBadge = '<span class="badge badge-warning">✋ Manual</span>';
                }

                // Badge para estado
                let estadoBadge = '';
                if (asistencia.estado === 'presente') {
                    estadoBadge = '<span class="badge badge-success">Presente</span>';
                } else if (asistencia.estado === 'tardanza') {
                    estadoBadge = '<span class="badge badge-warning">⏰ Tarde</span>';
                } else {
                    estadoBadge = '<span class="badge badge-warning">' + asistencia.estado + '</span>';
                }

                row.innerHTML = `
                    <td>${formatDate(asistencia.fecha)}</td>
                    <td>${asistencia.hora_entrada || '-'}</td>
                    <td><strong>${asistencia.codigo_usuario}</strong></td>
                    <td>${asistencia.nombre_completo}</td>
                    <td>${asistencia.equipo}</td>
                    <td>${metodoBadge}</td>
                    <td>${estadoBadge}</td>
                `;
                
                tbody.appendChild(row);
            });
        }

        function calcularEstadisticas(asistencias) {
            if (asistencias.length === 0) {
                document.getElementById('statsGrid').style.display = 'none';
                return;
            }

            document.getElementById('statsGrid').style.display = 'grid';

            // Total asistencias
            document.getElementById('totalAsistencias').textContent = asistencias.length;

            // Días únicos
            const fechasUnicas = new Set(asistencias.map(a => a.fecha));
            document.getElementById('totalDias').textContent = fechasUnicas.size;

            // Equipos activos
            const equiposUnicos = new Set(asistencias.map(a => a.equipo));
            document.getElementById('equiposActivos').textContent = equiposUnicos.size;

            // Promedio diario
            const promedio = fechasUnicas.size > 0 ? Math.round(asistencias.length / fechasUnicas.size) : 0;
            document.getElementById('promedioDiario').textContent = promedio;
        }

        function formatDate(dateString) {
            if (!dateString) return '-';
            const date = new Date(dateString);
            return date.toLocaleDateString('es-ES', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            });
        }

        function limpiarFiltros() {
            document.getElementById('equipoFilter').value = '';
            document.getElementById('fechaInicio').value = '';
            document.getElementById('fechaFin').value = '';
            aplicarFiltros();
        }

        async function exportarExcel() {
            if (currentData.length === 0) {
                showNotification('No hay datos para exportar', 'warning');
                return;
            }

            const equipoId = document.getElementById('equipoFilter').value || null;
            const fechaInicio = document.getElementById('fechaInicio').value || null;
            const fechaFin = document.getElementById('fechaFin').value || null;

            try {
                const response = await fetch(`${API_BASE}/reportes/export/excel`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${authToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        equipo_id: equipoId,
                        fecha_inicio: fechaInicio,
                        fecha_fin: fechaFin
                    })
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `asistencias_${new Date().getTime()}.xlsx`;
                    a.click();
                    showNotification('✅ Excel exportado correctamente', 'success');
                } else {
                    showNotification('❌ Error al exportar', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('❌ Error al exportar', 'error');
            }
        }

        async function exportarPDF() {
            if (currentData.length === 0) {
                showNotification('⚠️ No hay datos para exportar', 'warning');
                return;
            }

            const equipoId = document.getElementById('equipoFilter').value || null;
            const fechaInicio = document.getElementById('fechaInicio').value || null;
            const fechaFin = document.getElementById('fechaFin').value || null;

            try {
                const response = await fetch(`${API_BASE}/reportes/export/pdf`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${authToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        equipo_id: equipoId,
                        fecha_inicio: fechaInicio,
                        fecha_fin: fechaFin
                    })
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `asistencias_${new Date().getTime()}.pdf`;
                    a.click();
                    showNotification('✅ PDF exportado correctamente', 'success');
                } else {
                    showNotification('❌ Error al exportar', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('❌ Error al exportar', 'error');
            }
        }

        function volverDashboard() {
            window.location.href = '/dashboard';
        }

        function showNotification(message, type) {
            const colors = {
                success: '#10b981',
                error: '#ef4444',
                warning: '#f59e0b',
                info: '#3b82f6'
            };

            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.style.background = colors[type] || colors.info;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }

        // Inicializar al cargar
        init();