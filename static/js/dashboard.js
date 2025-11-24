// Verificar autenticación
        const token = localStorage.getItem('authToken');
        const user = JSON.parse(localStorage.getItem('user') || '{}');

        if (!token) {
            window.location.href = '/login';
        }

        // Cargar información del usuario
        document.getElementById('userName').textContent = user.full_name || 'Usuario';
        document.getElementById('userRole').textContent = user.rol || 'Docente';
        document.getElementById('userAvatar').textContent = (user.full_name || 'U').charAt(0).toUpperCase();

        // Fecha actual
        const currentDate = new Date().toLocaleDateString('es-ES', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        document.getElementById('currentDate').textContent = currentDate.charAt(0).toUpperCase() + currentDate.slice(1);

        // Logout
        document.getElementById('logoutBtn').addEventListener('click', function(e) {
            e.preventDefault();
            localStorage.removeItem('authToken');
            localStorage.removeItem('user');
            window.location.href = '/login';
        });

        // Cargar estadísticas
        async function loadStats() {
            try {
                const response = await fetch('/api/stats/dashboard', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    document.getElementById('totalMaterias').textContent = data.total_materias || 0;
                    document.getElementById('totalEstudiantes').textContent = data.total_estudiantes || 0;
                    document.getElementById('asistenciasHoy').textContent = data.asistencias_hoy || 0;
                    document.getElementById('porcentajeAsistencia').textContent = `${data.porcentaje_asistencia || 0}%`;
                }
            } catch (error) {
                console.error('Error cargando estadísticas:', error);
            }
        }

        // Cargar materias
        async function loadMaterias() {
            try {
                const response = await fetch('/api/teacher/subjects', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    const container = document.getElementById('materiasContainer');
                    
                    if (data.subjects && data.subjects.length > 0) {
                        container.innerHTML = '<div class="materia-list">' +
                            data.subjects.slice(0, 3).map(materia => `
                                <div class="materia-item">
                                    <div class="materia-info">
                                        <h4>${materia.nombre}</h4>
                                        <p>${materia.codigo_materia} • ${materia.nivel}</p>
                                    </div>
                                    <div class="materia-stats">
                                        <div>
                                            <div class="materia-stat-value">${materia.total_estudiantes || 0}</div>
                                            <div class="materia-stat-label">Estudiantes</div>
                                        </div>
                                    </div>
                                </div>
                            `).join('') +
                        '</div>';
                    } else {
                        container.innerHTML = '<p style="text-align: center; color: #6B7280; padding: 20px;">No tienes materias asignadas</p>';
                    }
                }
            } catch (error) {
                console.error('Error cargando materias:', error);
                document.getElementById('materiasContainer').innerHTML = '<p style="text-align: center; color: #EF4444; padding: 20px;">Error al cargar materias</p>';
            }
        }

        // Cargar alertas
        async function loadAlertas() {
            try {
                const response = await fetch('/api/alertas/recientes', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                const container = document.getElementById('alertasContainer');
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.alertas && data.alertas.length > 0) {
                        container.innerHTML = '<p style="text-align: center; color: #6B7280; padding: 20px;">No hay alertas recientes</p>';
                    } else {
                        container.innerHTML = '<p style="text-align: center; color: #10B981; padding: 20px;">✅ Todo está en orden</p>';
                    }
                } else {
                    container.innerHTML = '<p style="text-align: center; color: #10B981; padding: 20px;">✅ Todo está en orden</p>';
                }
            } catch (error) {
                document.getElementById('alertasContainer').innerHTML = '<p style="text-align: center; color: #10B981; padding: 20px;">✅ Todo está en orden</p>';
            }
        }

        // Cargar todo al iniciar
        window.addEventListener('load', function() {
            loadStats();
            loadMaterias();
            loadAlertas();
        });
