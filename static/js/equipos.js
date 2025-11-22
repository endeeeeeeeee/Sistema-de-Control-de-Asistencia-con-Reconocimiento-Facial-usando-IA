// =====================================================
// EQUIPOS - CLASS VISION
// =====================================================

const token = localStorage.getItem('authToken');
const user = JSON.parse(localStorage.getItem('user') || '{}');

// Verificar autenticación
if (!token) {
    window.location.href = '/login';
}

// =====================================================
// INICIALIZACIÓN
// =====================================================

document.addEventListener('DOMContentLoaded', function() {
    // Cargar información del usuario
    const userName = user.nombre_completo || user.full_name || 'Usuario';
    document.getElementById('userName').textContent = userName;
    document.getElementById('userCode').textContent = user.codigo_usuario || 'USER-XXXX-XXX';
    
    // Avatar inicial
    const avatarElement = document.getElementById('userAvatar');
    if (avatarElement) {
        avatarElement.textContent = userName.charAt(0).toUpperCase();
    }
    
    // Cargar datos
    loadEquipos();
    loadStats();
});

// =====================================================
// LOGOUT
// =====================================================

function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    window.location.href = '/login';
}

// =====================================================
// CARGAR ESTADÍSTICAS
// =====================================================

async function loadStats() {
    try {
        const response = await fetch('/api/equipos', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const data = await response.json();
            const equipos = data.equipos || [];
            
            // Total de equipos
            document.getElementById('totalEquipos').textContent = equipos.length;
            
            // Equipos que lidero
            const equiposLidero = equipos.filter(eq => eq.mi_rol === 'lider').length;
            document.getElementById('equiposLidero').textContent = equiposLidero;
            
            // Asistencias hoy (dummy por ahora)
            document.getElementById('asistenciasHoy').textContent = '0';
        }
    } catch (error) {
        console.error('Error cargando estadísticas:', error);
    }
}

// =====================================================
// CARGAR EQUIPOS
// =====================================================

async function loadEquipos() {
    const loadingElement = document.getElementById('loadingTeams');
    const containerElement = document.getElementById('equiposContainer');
    const emptyElement = document.getElementById('emptyTeams');
    
    if (!loadingElement || !containerElement || !emptyElement) {
        console.error('Elementos del DOM no encontrados');
        return;
    }
    
    try {
        loadingElement.style.display = 'block';
        containerElement.style.display = 'none';
        emptyElement.style.display = 'none';
        
        const response = await fetch('/api/equipos', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            throw new Error('Error al obtener equipos');
        }

        const data = await response.json();
        
        loadingElement.style.display = 'none';
        
        if (data.success && data.equipos && data.equipos.length > 0) {
            renderEquipos(data.equipos);
            containerElement.style.display = 'grid';
        } else {
            emptyElement.style.display = 'block';
        }
        
    } catch (error) {
        console.error('Error cargando equipos:', error);
        loadingElement.style.display = 'none';
        emptyElement.style.display = 'block';
        showAlert('Error al cargar equipos: ' + error.message, 'error');
    }
}

// =====================================================
// RENDERIZAR EQUIPOS
// =====================================================

function renderEquipos(equipos) {
    const container = document.getElementById('equiposContainer');
    
    container.innerHTML = equipos.map(equipo => `
        <div class="team-card">
            <div class="team-header">
                <div>
                    <h3 class="team-name">${escapeHtml(equipo.nombre_equipo)}</h3>
                    <p class="team-type">${getTipoEquipoLabel(equipo.tipo_equipo)}</p>
                </div>
                <span class="team-badge ${equipo.mi_rol === 'lider' ? 'badge-leader' : 'badge-member'}">
                    ${equipo.mi_rol === 'lider' ? '👑 Líder' : '👤 Miembro'}
                </span>
            </div>
            
            ${equipo.descripcion ? `<p class="team-description">${escapeHtml(equipo.descripcion)}</p>` : ''}
            
            <div class="team-stats">
                <div class="team-stat">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                        <circle cx="9" cy="7" r="4"></circle>
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                        <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                    </svg>
                    <span>${equipo.total_miembros} miembros</span>
                </div>
                <div class="team-stat">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="16" y1="2" x2="16" y2="6"></line>
                        <line x1="8" y1="2" x2="8" y2="6"></line>
                        <line x1="3" y1="10" x2="21" y2="10"></line>
                    </svg>
                    <span>${formatDate(equipo.fecha_creacion)}</span>
                </div>
            </div>
            
            <div class="team-code">
                <span>Código: <strong>${equipo.codigo_invitacion}</strong></span>
                <button class="btn-icon" onclick="copyCode('${equipo.codigo_invitacion}')" title="Copiar código">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
                </button>
            </div>
            
            <div class="team-actions">
                <button class="btn btn-outline" onclick="viewTeamDetails(${equipo.id})">Ver Detalles</button>
                ${equipo.mi_rol === 'lider' ? `
                    <button class="btn btn-danger" onclick="deleteTeam(${equipo.id}, '${escapeHtml(equipo.nombre_equipo)}')">Eliminar</button>
                ` : ''}
            </div>
        </div>
    `).join('');
}

// =====================================================
// CREAR EQUIPO
// =====================================================

function openCreateTeamModal() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>Crear Nuevo Equipo</h2>
                <button class="btn-close" onclick="this.closest('.modal-overlay').remove()">&times;</button>
            </div>
            
            <form id="createTeamForm" onsubmit="handleCreateTeam(event)">
                <div class="form-group">
                    <label for="teamName">Nombre del Equipo *</label>
                    <input type="text" id="teamName" class="form-input" required maxlength="200" 
                           placeholder="Ej: Programación Avanzada 2024">
                </div>
                
                <div class="form-group">
                    <label for="teamType">Tipo de Equipo *</label>
                    <select id="teamType" class="form-input" required>
                        <option value="universidad">Universidad</option>
                        <option value="colegio">Colegio</option>
                        <option value="empresa">Empresa</option>
                        <option value="gym">Gimnasio</option>
                        <option value="guarderia">Guardería</option>
                        <option value="otro">Otro</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="teamDescription">Descripción</label>
                    <textarea id="teamDescription" class="form-input" rows="3" 
                              placeholder="Descripción breve del equipo..."></textarea>
                </div>
                
                <div id="createTeamAlert"></div>
                
                <div class="modal-actions">
                    <button type="button" class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">
                        Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary">
                        Crear Equipo
                    </button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    document.getElementById('teamName').focus();
}

async function handleCreateTeam(event) {
    event.preventDefault();
    
    const nombre = document.getElementById('teamName').value.trim();
    const tipo = document.getElementById('teamType').value;
    const descripcion = document.getElementById('teamDescription').value.trim();
    const alertDiv = document.getElementById('createTeamAlert');
    
    try {
        const response = await fetch('/api/equipos', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                nombre_equipo: nombre,
                tipo_equipo: tipo,
                descripcion: descripcion
            })
        });

        const data = await response.json();
        
        if (data.success) {
            alertDiv.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
            
            setTimeout(() => {
                document.querySelector('.modal-overlay').remove();
                loadEquipos();
                loadStats();
            }, 1500);
        } else {
            alertDiv.innerHTML = `<div class="alert alert-error">${data.error || 'Error al crear equipo'}</div>`;
        }
        
    } catch (error) {
        alertDiv.innerHTML = `<div class="alert alert-error">Error: ${error.message}</div>`;
    }
}

// =====================================================
// UNIRSE A EQUIPO
// =====================================================

async function joinTeam() {
    const input = document.getElementById('joinCode');
    const codigo = input.value.trim().toUpperCase();
    const alertDiv = document.getElementById('joinAlert');
    
    if (!codigo) {
        alertDiv.innerHTML = '<div class="alert alert-error">Ingresa un código de invitación</div>';
        return;
    }
    
    try {
        const response = await fetch('/api/equipos/unirse', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                codigo_invitacion: codigo
            })
        });

        const data = await response.json();
        
        if (data.success) {
            alertDiv.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
            input.value = '';
            
            setTimeout(() => {
                alertDiv.innerHTML = '';
                loadEquipos();
                loadStats();
            }, 2000);
        } else {
            alertDiv.innerHTML = `<div class="alert alert-error">${data.error}</div>`;
        }
        
    } catch (error) {
        alertDiv.innerHTML = `<div class="alert alert-error">Error: ${error.message}</div>`;
    }
}

// =====================================================
// VER DETALLES DEL EQUIPO
// =====================================================

async function viewTeamDetails(equipoId) {
    try {
        const response = await fetch(`/api/equipos/${equipoId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            throw new Error('Error al obtener detalles');
        }

        const data = await response.json();
        
        if (data.success) {
            showTeamDetailsModal(data.equipo, data.miembros);
        }
        
    } catch (error) {
        showAlert('Error al cargar detalles: ' + error.message, 'error');
    }
}

function showTeamDetailsModal(equipo, miembros) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content modal-large">
            <div class="modal-header">
                <div>
                    <h2>${escapeHtml(equipo.nombre_equipo)}</h2>
                    <p style="color: var(--gray-600); margin-top: 4px;">${getTipoEquipoLabel(equipo.tipo_equipo)}</p>
                </div>
                <button class="btn-close" onclick="this.closest('.modal-overlay').remove()">&times;</button>
            </div>
            
            <div class="modal-body">
                ${equipo.descripcion ? `<p style="margin-bottom: 20px;">${escapeHtml(equipo.descripcion)}</p>` : ''}
                
                <div class="team-details-grid">
                    <div class="detail-item">
                        <strong>Código de Invitación:</strong>
                        <span>${equipo.codigo_invitacion} 
                            <button class="btn-icon" onclick="copyCode('${equipo.codigo_invitacion}')" title="Copiar">
                                📋
                            </button>
                        </span>
                    </div>
                    <div class="detail-item">
                        <strong>Creado por:</strong>
                        <span>${escapeHtml(equipo.creador_nombre)}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Fecha de Creación:</strong>
                        <span>${formatDate(equipo.fecha_creacion)}</span>
                    </div>
                    <div class="detail-item">
                        <strong>Tu Rol:</strong>
                        <span class="team-badge ${equipo.mi_rol === 'lider' ? 'badge-leader' : 'badge-member'}">
                            ${equipo.mi_rol === 'lider' ? '👑 Líder' : '👤 Miembro'}
                        </span>
                    </div>
                </div>
                
                <h3 style="margin: 24px 0 12px;">Miembros del Equipo (${miembros.length})</h3>
                
                <div class="members-list">
                    ${miembros.map(miembro => `
                        <div class="member-item">
                            <div class="member-avatar">
                                ${miembro.nombre_completo.charAt(0).toUpperCase()}
                            </div>
                            <div class="member-info">
                                <div class="member-name">${escapeHtml(miembro.nombre_completo)}</div>
                                <div class="member-email">${escapeHtml(miembro.email)}</div>
                                <div class="member-code">${miembro.codigo_usuario}</div>
                            </div>
                            <div class="member-stats">
                                <span class="team-badge ${miembro.rol === 'lider' ? 'badge-leader' : 'badge-member'}">
                                    ${miembro.rol === 'lider' ? '👑 Líder' : '👤 Miembro'}
                                </span>
                                <div style="font-size: 12px; color: var(--gray-600); margin-top: 4px;">
                                    ${miembro.asistencias_totales} asistencias • ${miembro.porcentaje_asistencia.toFixed(1)}%
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="modal-footer">
                <button class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cerrar</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// =====================================================
// ELIMINAR EQUIPO
// =====================================================

async function deleteTeam(equipoId, nombreEquipo) {
    if (!confirm(`¿Estás seguro de que quieres eliminar el equipo "${nombreEquipo}"?\n\nEsta acción no se puede deshacer.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/equipos/${equipoId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            loadEquipos();
            loadStats();
        } else {
            showAlert(data.error || 'Error al eliminar equipo', 'error');
        }
        
    } catch (error) {
        showAlert('Error: ' + error.message, 'error');
    }
}

// =====================================================
// UTILIDADES
// =====================================================

function copyCode(codigo) {
    navigator.clipboard.writeText(codigo).then(() => {
        showAlert(`Código ${codigo} copiado al portapapeles`, 'success');
    }).catch(() => {
        showAlert('Error al copiar código', 'error');
    });
}

function showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-float`;
    alert.textContent = message;
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => alert.remove(), 300);
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    });
}

function getTipoEquipoLabel(tipo) {
    const labels = {
        'universidad': '🎓 Universidad',
        'colegio': '🏫 Colegio',
        'empresa': '💼 Empresa',
        'gym': '💪 Gimnasio',
        'guarderia': '👶 Guardería',
        'otro': '📁 Otro'
    };
    return labels[tipo] || tipo;
}
