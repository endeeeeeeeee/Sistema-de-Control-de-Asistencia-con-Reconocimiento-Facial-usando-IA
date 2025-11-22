const token = localStorage.getItem('authToken');
        if (!token) window.location.href = '/login';

        let selectedStudent = null;

        // Modal
        const modal = document.getElementById('modalNewStudent');
        document.getElementById('btnNewStudent').addEventListener('click', () => {
            modal.classList.add('active');
            loadMaterias();
        });
        document.getElementById('btnCancelModal').addEventListener('click', () => {
            modal.classList.remove('active');
            resetForm();
        });

        // Cargar materias del docente
        async function loadMaterias() {
            try {
                const response = await fetch('/api/teacher/subjects', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    const data = await response.json();
                    const select = document.getElementById('selectMateria');
                    select.innerHTML = '<option value="">-- Selecciona una materia --</option>';
                    
                    data.subjects.forEach(materia => {
                        const option = document.createElement('option');
                        option.value = materia.id;
                        option.textContent = `${materia.nombre} - ${materia.codigo}`;
                        select.appendChild(option);
                    });
                }
            } catch (error) {
                console.error('Error cargando materias:', error);
            }
        }

        // Buscar estudiante por código
        document.getElementById('btnBuscar').addEventListener('click', async () => {
            const codigo = document.getElementById('codigoEstudiante').value.trim();
            
            if (!codigo) {
                alert('⚠️ Ingresa el código del estudiante');
                return;
            }

            try {
                const response = await fetch(`/api/students/search?codigo=${encodeURIComponent(codigo)}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    const data = await response.json();
                    selectedStudent = data.estudiante;
                    
                    // Mostrar información
                    document.getElementById('infoNombre').textContent = selectedStudent.nombre_completo;
                    document.getElementById('infoEmail').textContent = selectedStudent.email || '-';
                    document.getElementById('infoTelefono').textContent = selectedStudent.telefono || '-';
                    document.getElementById('infoMaterias').textContent = selectedStudent.total_materias || 0;
                    document.getElementById('studentInfo').style.display = 'block';
                    document.getElementById('btnSubmit').disabled = false;
                } else {
                    const error = await response.json();
                    alert(`❌ ${error.error || 'Estudiante no encontrado'}`);
                    resetStudentInfo();
                }
            } catch (error) {
                alert('❌ Error al buscar estudiante');
                console.error(error);
            }
        });

        function resetStudentInfo() {
            selectedStudent = null;
            document.getElementById('studentInfo').style.display = 'none';
            document.getElementById('btnSubmit').disabled = true;
        }

        function resetForm() {
            document.getElementById('formNewStudent').reset();
            resetStudentInfo();
        }

        // Cargar estudiantes
        async function loadStudents() {
            try {
                const response = await fetch('/api/students', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                const container = document.getElementById('studentsContainer');

                if (response.ok) {
                    const data = await response.json();
                    
                    if (data.students && data.students.length > 0) {
                        container.innerHTML = `
                            <table>
                                <thead>
                                    <tr>
                                        <th>Estudiante</th>
                                        <th>CI</th>
                                        <th>Email</th>
                                        <th>Estado</th>
                                        <th>Materias</th>
                                        <th>Acciones</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${data.students.map(s => `
                                        <tr>
                                            <td>
                                                <div class="student-info">
                                                    <div class="student-avatar">${s.nombre_completo.charAt(0)}</div>
                                                    <div>
                                                        <div class="student-name">${s.nombre_completo}</div>
                                                        <div class="student-code">${s.codigo_estudiante}</div>
                                                    </div>
                                                </div>
                                            </td>
                                            <td>${s.ci || '--'}</td>
                                            <td>${s.email || '--'}</td>
                                            <td><span class="badge badge-success">ACTIVO</span></td>
                                            <td>${s.total_materias || 0}</td>
                                            <td>
                                                <div class="actions">
                                                    <a href="/estudiantes/${s.id}" class="btn btn-secondary btn-small">Ver</a>
                                                </div>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        `;
                    } else {
                        container.innerHTML = `
                            <div class="empty-state">
                                <div class="empty-state-icon">👥</div>
                                <h2>No hay estudiantes registrados</h2>
                                <p>Registra tu primer estudiante para comenzar</p>
                            </div>
                        `;
                    }
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }

        // Inscribir estudiante
        document.getElementById('formNewStudent').addEventListener('submit', async (e) => {
            e.preventDefault();

            if (!selectedStudent) {
                alert('❌ Primero busca un estudiante');
                return;
            }

            const materiaId = document.getElementById('selectMateria').value;
            if (!materiaId) {
                alert('❌ Selecciona una materia');
                return;
            }

            const enrollData = {
                codigo_estudiante: selectedStudent.codigo_estudiante,
                materia_id: parseInt(materiaId)
            };

            try {
                const response = await fetch('/api/students', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(enrollData)
                });

                if (response.ok) {
                    const result = await response.json();
                    modal.classList.remove('active');
                    resetForm();
                    loadStudents();
                    alert(`✅ ${result.message || 'Estudiante inscrito exitosamente'}`);
                } else {
                    const error = await response.json();
                    alert('❌ Error: ' + (error.error || 'No se pudo inscribir'));
                }
            } catch (error) {
                console.error('Error:', error);
                alert('❌ Error al inscribir estudiante');
            }
        });

        // Búsqueda
        document.getElementById('searchInput').addEventListener('input', (e) => {
            const search = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(search) ? '' : 'none';
            });
        });

        loadStudents();