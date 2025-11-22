const token = localStorage.getItem('authToken');
        const user = JSON.parse(localStorage.getItem('user') || '{}');

        if (!token) {
            window.location.href = '/login';
        }

        // Modal
        const modal = document.getElementById('modalNewMateria');
        document.getElementById('btnNewMateria').addEventListener('click', () => {
            modal.classList.add('active');
        });
        document.getElementById('btnCancelModal').addEventListener('click', () => {
            modal.classList.remove('active');
        });

        // Cargar materias
        async function loadMaterias() {
            try {
                const response = await fetch('/api/teacher/subjects', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                const container = document.getElementById('materiasContainer');

                if (response.ok) {
                    const data = await response.json();
                    
                    if (data.subjects && data.subjects.length > 0) {
                        container.innerHTML = '<div class="materias-grid">' +
                            data.subjects.map(materia => `
                                <div class="materia-card">
                                    <div class="materia-header">
                                        <div class="materia-code">${materia.codigo_materia}</div>
                                        <div class="materia-name">${materia.nombre}</div>
                                        <div class="materia-level">${materia.nivel || 'Sin nivel especificado'}</div>
                                    </div>
                                    <div class="materia-schedule">
                                        ${(materia.dia_semana || []).map(dia => `<span class="schedule-day">${dia}</span>`).join('')}
                                    </div>
                                    <div class="materia-stats">
                                        <div class="stat">
                                            <div class="stat-value">${materia.total_estudiantes || 0}</div>
                                            <div class="stat-label">Estudiantes</div>
                                        </div>
                                        <div class="stat">
                                            <div class="stat-value">${materia.hora_inicio || '--:--'}</div>
                                            <div class="stat-label">Inicio</div>
                                        </div>
                                        <div class="stat">
                                            <div class="stat-value">${materia.tolerancia_minutos || 15}m</div>
                                            <div class="stat-label">Tolerancia</div>
                                        </div>
                                    </div>
                                    <div class="materia-actions">
                                        <a href="/asistencia/tomar?materia=${materia.id}" class="btn-action btn-attendance">
                                            📸 Asistencia
                                        </a>
                                        <a href="/materias/${materia.id}/estudiantes" class="btn-action btn-students">
                                            👥 Ver Estudiantes
                                        </a>
                                    </div>
                                </div>
                            `).join('') +
                        '</div>';
                    } else {
                        container.innerHTML = `
                            <div class="empty-state">
                                <div class="empty-state-icon">📚</div>
                                <h2>No tienes materias asignadas</h2>
                                <p>Crea tu primera materia para comenzar a tomar asistencia</p>
                                <button class="btn btn-primary" onclick="document.getElementById('btnNewMateria').click()">
                                    ➕ Crear Primera Materia
                                </button>
                            </div>
                        `;
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('materiasContainer').innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">❌</div>
                        <h2>Error al cargar materias</h2>
                        <p>${error.message}</p>
                    </div>
                `;
            }
        }

        // Crear materia
        document.getElementById('formNewMateria').addEventListener('submit', async (e) => {
            e.preventDefault();

            const diasCheckboxes = document.querySelectorAll('input[name="dias"]:checked');
            const dias = Array.from(diasCheckboxes).map(cb => cb.value);

            if (dias.length === 0) {
                alert('Selecciona al menos un día de clase');
                return;
            }

            const materiaData = {
                codigo_materia: document.getElementById('codigo').value,
                nombre: document.getElementById('nombre').value,
                nivel: document.getElementById('nivel').value || null,
                dia_semana: dias,
                hora_inicio: document.getElementById('horaInicio').value,
                hora_fin: document.getElementById('horaFin').value,
                tolerancia_minutos: parseInt(document.getElementById('tolerancia').value) || 15
            };

            try {
                const response = await fetch('/api/teacher/subjects', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(materiaData)
                });

                if (response.ok) {
                    modal.classList.remove('active');
                    document.getElementById('formNewMateria').reset();
                    loadMaterias();
                    alert('✅ Materia creada exitosamente');
                } else {
                    const error = await response.json();
                    alert('❌ Error: ' + (error.message || 'No se pudo crear la materia'));
                }
            } catch (error) {
                console.error('Error:', error);
                alert('❌ Error al crear materia');
            }
        });

        // Cargar al iniciar
        loadMaterias();