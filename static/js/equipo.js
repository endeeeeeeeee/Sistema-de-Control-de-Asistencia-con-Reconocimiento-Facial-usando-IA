const API_BASE = '/api';
        let authToken = localStorage.getItem('authToken');
        let currentTeam = null;
        const teamId = window.location.pathname.split('/').pop();

        document.addEventListener('DOMContentLoaded', async () => {
            if (!authToken) {
                window.location.href = '/login';
                return;
            }
            await loadTeamDetails();
        });

        async function loadTeamDetails() {
            try {
                const response = await fetch(`${API_BASE}/equipos/${teamId}`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                const data = await response.json();

                if (data.success) {
                    currentTeam = data;
                    renderTeam(data);
                } else {
                    alert(data.error || 'Error al cargar equipo');
                    window.location.href = '/dashboard';
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error de conexión');
            }
        }

        async function renderTeam(data) {
            const { equipo, miembros } = data;

            // Header
            document.getElementById('teamName').textContent = equipo.nombre_equipo;
            document.getElementById('teamDescription').textContent = equipo.descripcion || 'Sin descripción';
            document.getElementById('invitationCode').textContent = equipo.codigo_invitacion;

            // Type Badge
            const typeBadge = document.getElementById('teamTypeBadge');
            typeBadge.textContent = equipo.tipo_equipo.toUpperCase();
            typeBadge.className = `meta-badge type-${equipo.tipo_equipo}`;

            // Role Badge
            const roleBadge = document.getElementById('myRoleBadge');
            const roleText = {
                'lider': 'LÍDER',
                'co-lider': '🎖️ CO-LÍDER',
                'miembro': '👤 MIEMBRO'
            }[equipo.mi_rol] || equipo.mi_rol.toUpperCase();
            roleBadge.textContent = roleText;
            roleBadge.className = `meta-badge role-${equipo.mi_rol}`;

            // Members Table
            renderMembers(miembros);

            // Leader Actions
            if (equipo.mi_rol === 'lider' || equipo.mi_rol === 'co-lider') {
                document.getElementById('leaderActions').style.display = 'block';
                
                // Mostrar toggle de guardería si aplica
                if (equipo.tipo_equipo === 'guarderia') {
                    document.getElementById('modoGuarderiaContainer').style.display = 'block';
                }
            }

            // Show content FIRST
            document.getElementById('loading').style.display = 'none';
            document.getElementById('teamContent').style.display = 'block';
            
            // Cargar estadísticas en tiempo real (sin bloquear)
            loadRealTimeStats();
            
            // Actualizar stats cada 30 segundos
            setInterval(loadRealTimeStats, 30000);
        }

        async function loadRealTimeStats() {
            try {
                const response = await fetch(`${API_BASE}/equipos/${teamId}/stats`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                const data = await response.json();

                if (data.success) {
                    document.getElementById('totalMiembros').textContent = data.stats.total_miembros;
                    document.getElementById('asistenciasHoy').textContent = data.stats.asistencias_hoy;
                    document.getElementById('promedioAsistencia').textContent = `${data.stats.promedio_asistencia}%`;
                }
            } catch (error) {
                console.error('Error cargando estadísticas:', error);
                // Mostrar valores por defecto si falla
                document.getElementById('totalMiembros').textContent = '0';
                document.getElementById('asistenciasHoy').textContent = '0';
                document.getElementById('promedioAsistencia').textContent = '0%';
            }
        }

        function renderMembers(miembros) {
            const container = document.getElementById('membersContent');

            if (miembros.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon"></div>
                        <p>No hay miembros en este equipo</p>
                    </div>
                `;
                return;
            }

            let html = `
                <table class="members-table">
                    <thead>
                        <tr>
                            <th>Código</th>
                            <th>Nombre</th>
                            <th>Rol</th>
                            <th>Asistencias</th>
                            <th>%</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            miembros.forEach(member => {
                const roleClass = `role-${member.rol}`;
                const roleText = {
                    'lider': 'Líder',
                    'co-lider': '🎖️ Co-Líder',
                    'miembro': '👤 Miembro'
                }[member.rol] || member.rol;

                // Obtener membresia_id del currentTeam
                const memberData = currentTeam.miembros.find(m => m.id === member.id);
                const membresiaId = memberData ? memberData.id : member.id;

                html += `
                    <tr>
                        <td><strong>${member.codigo_usuario}</strong></td>
                        <td>${member.nombre_completo}</td>
                        <td><span class="role-badge ${roleClass}">${roleText}</span></td>
                        <td>${member.asistencias_totales} / ${member.asistencias_totales + member.faltas_totales}</td>
                        <td>${Math.round(member.porcentaje_asistencia)}%</td>
                        <td>
                            ${canManageMember(member.rol) ? `
                                <button class="btn btn-primary btn-sm" onclick="changeRole('${member.codigo_usuario}', '${member.rol}')" style="background: #6366f1; margin-right: 4px;">
                                    👤 Cambiar Rol
                                </button>
                                <button class="btn btn-danger btn-sm" onclick="removeMember('${member.codigo_usuario}', '${member.nombre_completo}')">
                                    Remover
                                </button>
                            ` : '-'}
                        </td>
                    </tr>
                `;
            });

            html += `
                    </tbody>
                </table>
            `;

            container.innerHTML = html;
        }

        function canManageMember(memberRole) {
            if (!currentTeam) return false;
            const myRole = currentTeam.equipo.mi_rol;

            // Solo líder puede remover
            if (myRole === 'lider') {
                return memberRole !== 'lider'; // No puede removerse a sí mismo
            }
            return false;
        }

        async function removeMember(codigoUsuario, nombreCompleto) {
            if (!confirm(`¿Estás seguro de remover a ${nombreCompleto} del equipo?`)) {
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/equipos/${teamId}/miembros/by-codigo/${codigoUsuario}`, {
                    method: 'DELETE',
                    headers: { 
                        'Authorization': `Bearer ${authToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showNotification(data.message, 'success');
                    setTimeout(() => {
                        loadTeamDetails(); // Recargar miembros después de 1 seg
                    }, 1000);
                } else {
                    showNotification('Error: ' + (data.error || 'No se pudo remover el miembro'), 'error');
                }
            } catch (error) {
                showNotification('Error de conexión', 'error');
                console.error('Error:', error);
            }
        }

        async function changeRole(codigoUsuario, currentRole) {
            const roles = ['miembro', 'co-lider', 'lider'];
            const roleNames = {
                'miembro': 'Miembro',
                'co-lider': 'Co-Líder',
                'lider': 'Líder'
            };
            
            let options = roles.filter(r => r !== currentRole)
                .map(r => `${r}: ${roleNames[r]}`)
                .join('\n');
            
            const nuevoRol = prompt(`Cambiar rol del miembro:\n\nOpciones:\n${options}\n\nIngresa el nuevo rol (miembro/co-lider/lider):`);
            
            if (!nuevoRol || !roles.includes(nuevoRol)) {
                showNotification('Rol inválido', 'error');
                return;
            }
            
            if (nuevoRol === currentRole) {
                showNotification('El miembro ya tiene ese rol', 'info');
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/equipos/${teamId}/miembros/by-codigo/${codigoUsuario}/rol`, {
                    method: 'PUT',
                    headers: { 
                        'Authorization': `Bearer ${authToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ rol: nuevoRol })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showNotification(data.message, 'success');
                    setTimeout(() => {
                        loadTeamDetails(); // Recargar miembros después de 1 seg
                    }, 1000);
                } else {
                    showNotification('Error: ' + (data.error || 'No se pudo cambiar el rol'), 'error');
                }
            } catch (error) {
                showNotification('Error de conexión', 'error');
                console.error('Error:', error);
            }
        }

        function toggleModoGuarderia(isActive) {
            if (isActive) {
                showNotification('🔒 MODO GUARDERÍA ACTIVADO\n\n🚧 Demo Visual - Funcionalidad completa requeriría:\n• Base de datos de tutores autorizados\n• Reconocimiento facial dual (tutor + niño)\n• Sistema de alertas y notificaciones\n• Registro fotográfico de cada salida\n\n👶 Pensado para máxima seguridad infantil', 'info');
            } else {
                showNotification('🔓 Modo Guardería desactivado - Sistema estándar de asistencia', 'info');
            }
        }

        function showNotification(message, type = 'info') {
            const colors = {
                success: '#10b981',
                error: '#ef4444',
                info: '#6366f1',
                warning: '#f59e0b'
            };
            
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${colors[type]};
                color: white;
                padding: 16px 24px;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.3);
                z-index: 10000;
                max-width: 350px;
                animation: slideIn 0.3s ease;
                white-space: pre-line;
            `;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }

        async function editTeam() {
            const nuevoNombre = prompt('Nuevo nombre del equipo:', currentTeam?.nombre_equipo || '');
            
            if (!nuevoNombre || nuevoNombre.trim() === '') {
                return;
            }
            
            const nuevaDescripcion = prompt('Nueva descripción (opcional):', currentTeam?.descripcion || '');

            try {
                const response = await fetch(`${API_BASE}/equipos/${teamId}/editar`, {
                    method: 'PUT',
                    headers: { 
                        'Authorization': `Bearer ${authToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ 
                        nombre_equipo: nuevoNombre,
                        descripcion: nuevaDescripcion
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert(data.message);
                    loadTeamDetails(); // Recargar detalles
                } else {
                    alert('Error: ' + (data.error || 'No se pudo editar el equipo'));
                }
            } catch (error) {
                alert('Error de conexión');
                console.error('Error:', error);
            }
        }

        let isDeletingTeam = false;

        async function confirmDeleteTeam() {
            if (isDeletingTeam) {
                alert('Ya se está eliminando el equipo, por favor espera...');
                return;
            }

            if (!confirm('¿Estás seguro de eliminar este equipo? Esta acción no se puede deshacer.')) {
                return;
            }
            
            if (!confirm('ÚLTIMA ADVERTENCIA: Se eliminarán todos los miembros y registros de asistencia. ¿Continuar?')) {
                return;
            }
            
            isDeletingTeam = true;
            const deleteBtn = document.querySelector('.btn-danger[onclick="confirmDeleteTeam()"]');
            if (deleteBtn) {
                deleteBtn.disabled = true;
                deleteBtn.textContent = 'Eliminando...';
            }
            
            console.log('Eliminando equipo con ID:', teamId);
            console.log('Token:', authToken ? 'Presente' : 'Ausente');
            
            try {
                const response = await fetch(`${API_BASE}/equipos/${teamId}`, {
                    method: 'DELETE',
                    headers: { 
                        'Authorization': `Bearer ${authToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                console.log('Response status:', response.status);
                
                const data = await response.json();
                console.log('Response data:', data);
                
                if (data.success) {
                    alert(data.message);
                    window.location.href = '/dashboard';
                } else {
                    alert('Error: ' + (data.error || 'No se pudo eliminar el equipo'));
                    isDeletingTeam = false;
                    if (deleteBtn) {
                        deleteBtn.disabled = false;
                        deleteBtn.textContent = 'Eliminar Equipo';
                    }
                }
            } catch (error) {
                alert('Error de conexión al eliminar el equipo');
                console.error('Error completo:', error);
                isDeletingTeam = false;
                if (deleteBtn) {
                    deleteBtn.disabled = false;
                    deleteBtn.textContent = 'Eliminar Equipo';
                }
            }
        }

        // =====================================================
        // GENERAR QR INDIVIDUAL
        // =====================================================

        let qrExpirationTimer = null;

        async function generateIndividualQR(usuarioId, nombreUsuario) {
            try {
                const response = await fetch(`${API_BASE}/qr/generar-individual`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${authToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        equipo_id: parseInt(teamId),
                        usuario_id: usuarioId,
                        duracion_minutos: 5
                    })
                });

                const data = await response.json();

                if (data.success) {
                    showQRModal(data);
                } else {
                    alert(data.error || 'No se pudo generar el QR');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error de conexión al generar QR');
            }
        }

        function showQRModal(qrData) {
            // Calcular tiempo restante
            const expiraEn = new Date(qrData.expira_en);
            const ahora = new Date();
            const tiempoRestante = Math.floor((expiraEn - ahora) / 1000); // segundos

            // Crear modal
            const modal = document.createElement('div');
            modal.id = 'qrModal';
            modal.innerHTML = `
                <div style="
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0,0,0,0.8);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 10000;
                    padding: 20px;
                ">
                    <div style="
                        background: white;
                        border-radius: 16px;
                        padding: 32px;
                        max-width: 500px;
                        width: 100%;
                        text-align: center;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    ">
                        <h2 style="margin: 0 0 16px; color: #1e293b;">🎫 QR de Un Solo Uso</h2>
                        <p style="color: #64748b; margin-bottom: 24px;">
                            Para: <strong>${qrData.usuario_nombre}</strong>
                        </p>

                        <!-- QR Code -->
                        <div id="qrcode" style="
                            background: white;
                            padding: 20px;
                            border-radius: 12px;
                            border: 2px solid #e2e8f0;
                            margin-bottom: 24px;
                            display: inline-block;
                        "></div>

                        <!-- Código manual -->
                        <div style="
                            background: #f8fafc;
                            padding: 16px;
                            border-radius: 8px;
                            margin-bottom: 16px;
                        ">
                            <p style="margin: 0 0 8px; color: #64748b; font-size: 14px;">
                                Código Manual:
                            </p>
                            <code style="
                                font-size: 16px;
                                font-weight: 600;
                                color: #1e293b;
                                letter-spacing: 2px;
                            ">${qrData.qr_code}</code>
                        </div>

                        <!-- Cuenta regresiva -->
                        <div style="
                            background: #fef3c7;
                            padding: 12px;
                            border-radius: 8px;
                            margin-bottom: 24px;
                        ">
                            <p style="margin: 0; color: #92400e; font-size: 14px;">
                                ⏱️ Expira en: <strong id="qrTimer">${tiempoRestante}s</strong>
                            </p>
                        </div>

                        <!-- Botones -->
                        <div style="display: flex; gap: 12px; justify-content: center;">
                            <button onclick="copyQRCode('${qrData.qr_code}')" style="
                                padding: 12px 24px;
                                background: #6366f1;
                                color: white;
                                border: none;
                                border-radius: 8px;
                                font-size: 14px;
                                font-weight: 600;
                                cursor: pointer;
                            ">
                                Copiar Código
                            </button>
                            <button onclick="closeQRModal()" style="
                                padding: 12px 24px;
                                background: #e2e8f0;
                                color: #1e293b;
                                border: none;
                                border-radius: 8px;
                                font-size: 14px;
                                font-weight: 600;
                                cursor: pointer;
                            ">
                                Cerrar
                            </button>
                        </div>

                        <p style="margin: 16px 0 0; color: #94a3b8; font-size: 12px;">
                            Este QR solo se puede usar UNA VEZ
                        </p>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

            // Generar QR con QRCode.js
            const qrcode = new QRCode(document.getElementById('qrcode'), {
                text: `${window.location.origin}/validar-qr?code=${qrData.qr_code}`,
                width: 256,
                height: 256,
                colorDark: '#1e293b',
                colorLight: '#ffffff',
                correctLevel: QRCode.CorrectLevel.H
            });

            // Iniciar cuenta regresiva
            startQRTimer(tiempoRestante);
        }

        function startQRTimer(segundosRestantes) {
            const timerElement = document.getElementById('qrTimer');
            let segundos = segundosRestantes;

            if (qrExpirationTimer) {
                clearInterval(qrExpirationTimer);
            }

            qrExpirationTimer = setInterval(() => {
                segundos--;

                if (segundos <= 0) {
                    clearInterval(qrExpirationTimer);
                    timerElement.textContent = 'EXPIRADO';
                    timerElement.parentElement.style.background = '#fee2e2';
                    timerElement.parentElement.style.color = '#991b1b';
                    return;
                }

                const minutos = Math.floor(segundos / 60);
                const segs = segundos % 60;
                timerElement.textContent = `${minutos}:${segs.toString().padStart(2, '0')}`;
            }, 1000);
        }

        function copyQRCode(code) {
            navigator.clipboard.writeText(code).then(() => {
                alert('Código copiado al portapapeles');
            }).catch(err => {
                console.error('Error:', err);
                alert('No se pudo copiar el código');
            });
        }

        function closeQRModal() {
            const modal = document.getElementById('qrModal');
            if (modal) {
                modal.remove();
            }
            if (qrExpirationTimer) {
                clearInterval(qrExpirationTimer);
                qrExpirationTimer = null;
            }
        }

        // =====================================================
        // INICIAR SESIÓN DE ASISTENCIA
        // =====================================================

        function iniciarSesionAsistencia() {
            if (!currentTeam || !currentTeam.equipo) {
                alert('❌ Error: No se pudo cargar la información del equipo');
                return;
            }

            // Redirigir a la página de sesión de asistencia
            window.location.href = `/sesion-asistencia?equipo_id=${teamId}`;
        }

        async function generarQRVinculacion() {
            try {
                const response = await fetch(`${API_BASE}/dispositivos/vincular`, {
                    method: 'POST',
                    headers: { 
                        'Authorization': `Bearer ${authToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ equipo_id: teamId })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Crear modal para mostrar QR
                    const modal = document.createElement('div');
                    modal.style.cssText = `
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background: rgba(0,0,0,0.7);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        z-index: 10000;
                    `;
                    
                    modal.innerHTML = `
                        <div style="background: white; padding: 32px; border-radius: 16px; max-width: 500px; text-align: center;">
                            <h2 style="color: #1e293b; margin-bottom: 16px;">Vincular Dispositivo Móvil</h2>
                            <p style="color: #64748b; margin-bottom: 24px;">
                                Escanea este código QR con tu celular para convertirlo en controlador de asistencia
                            </p>
                            <img src="${data.qr_base64}" style="width: 280px; height: 280px; border: 4px solid #6366f1; border-radius: 12px; margin-bottom: 16px;">
                            <div style="background: #fef3c7; padding: 12px; border-radius: 8px; margin-bottom: 20px;">
                                <p style="margin: 0; color: #92400e; font-size: 14px;">
                                    ⏱️ Expira en: <strong>${data.expira_en} minutos</strong>
                                </p>
                            </div>
                            <p style="font-size: 12px; color: #64748b; margin-bottom: 20px;">
                                Código: <code style="background: #f1f5f9; padding: 4px 8px; border-radius: 4px; font-family: monospace;">${data.codigo}</code>
                            </p>
                            <button onclick="this.parentElement.parentElement.remove()" style="
                                padding: 12px 32px;
                                background: #6366f1;
                                color: white;
                                border: none;
                                border-radius: 8px;
                                font-size: 16px;
                                cursor: pointer;
                                font-weight: 600;
                            ">Cerrar</button>
                        </div>
                    `;
                    
                    document.body.appendChild(modal);
                } else {
                    alert('❌ Error: ' + (data.error || 'No se pudo generar el QR'));
                }
            } catch (error) {
                alert('❌ Error de conexión');
                console.error('Error:', error);
            }
        }

        function verReportes() {
            // Ir a reportes con filtro pre-seleccionado del equipo
            window.location.href = `/reportes?equipo_id=${teamId}`;
        }