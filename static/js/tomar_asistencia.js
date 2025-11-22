const token = localStorage.getItem('authToken');
        if (!token) window.location.href = '/login';

        let stream = null;
        let recognitionInterval = null;
        let currentMateria = null;
        let attendanceData = [];

        // Cargar materias
        async function loadMaterias() {
            try {
                const response = await fetch('/api/teacher/subjects', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    const data = await response.json();
                    const select = document.getElementById('materiaSelect');
                    
                    if (data.subjects && data.subjects.length > 0) {
                        select.innerHTML = '<option value="">Selecciona una materia...</option>' +
                            data.subjects.map(m => 
                                `<option value="${m.id}">${m.nombre} (${m.codigo_materia})</option>`
                            ).join('');
                    } else {
                        select.innerHTML = '<option value="">No tienes materias asignadas</option>';
                    }
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }

        // Seleccionar materia
        document.getElementById('materiaSelect').addEventListener('change', async (e) => {
            currentMateria = e.target.value;
            if (currentMateria) {
                await loadStudentsList();
            }
        });

        // Cargar lista de estudiantes
        async function loadStudentsList() {
            try {
                const response = await fetch(`/api/subjects/${currentMateria}/students`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    const data = await response.json();
                    attendanceData = data.students.map(s => ({
                        id: s.id,
                        nombre: s.nombre_completo,
                        codigo: s.codigo_estudiante,
                        estado: 'AUSENTE',
                        hora: null
                    }));
                    updateAttendanceList();
                    document.getElementById('btnFinishSession').disabled = false;
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }

        // Actualizar lista visual
        function updateAttendanceList() {
            const container = document.getElementById('attendanceList');
            container.innerHTML = attendanceData.map(s => `
                <div class="attendance-item ${s.estado.toLowerCase()}">
                    <div>
                        <div class="student-name">${s.nombre}</div>
                        <div class="student-time">${s.codigo} ${s.hora ? '• ' + s.hora : ''}</div>
                    </div>
                    <span class="status-badge ${s.estado.toLowerCase()}">${s.estado}</span>
                </div>
            `).join('');

            // Actualizar contadores
            const presente = attendanceData.filter(s => s.estado === 'PRESENTE').length;
            const tardanza = attendanceData.filter(s => s.estado === 'TARDANZA').length;
            const ausente = attendanceData.filter(s => s.estado === 'AUSENTE').length;
            
            document.getElementById('countPresente').textContent = presente;
            document.getElementById('countTardanza').textContent = tardanza;
            document.getElementById('countAusente').textContent = ausente;
        }

        // Iniciar cámara
        document.getElementById('btnStartCamera').addEventListener('click', async () => {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { width: 640, height: 480 } 
                });
                document.getElementById('video').srcObject = stream;
                document.getElementById('btnStartRecognition').disabled = false;
                document.getElementById('btnStartCamera').disabled = true;
                showAlert('Cámara iniciada correctamente', 'success');
            } catch (error) {
                showAlert('Error al acceder a la cámara', 'error');
            }
        });

        // Iniciar reconocimiento
        document.getElementById('btnStartRecognition').addEventListener('click', () => {
            if (!currentMateria) {
                showAlert('Debes seleccionar una materia primero', 'warning');
                return;
            }

            document.getElementById('btnStartRecognition').disabled = true;
            document.getElementById('btnStopRecognition').disabled = false;
            showAlert('Reconocimiento activo - Acerca tu rostro a la cámara', 'success');

            // Simular reconocimiento cada 3 segundos
            recognitionInterval = setInterval(async () => {
                await captureAndRecognize();
            }, 3000);
        });

        // Detener reconocimiento
        document.getElementById('btnStopRecognition').addEventListener('click', () => {
            clearInterval(recognitionInterval);
            document.getElementById('btnStartRecognition').disabled = false;
            document.getElementById('btnStopRecognition').disabled = true;
            showAlert('Reconocimiento detenido', 'warning');
        });

        // Capturar y reconocer
        async function captureAndRecognize() {
            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            
            const imageData = canvas.toDataURL('image/jpeg');

            try {
                const response = await fetch('/api/attendance/recognize', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        materia_id: currentMateria,
                        image_base64: imageData
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.recognized && data.student_id) {
                        markAttendance(data.student_id, data.estado || 'PRESENTE');
                        showAlert(`${data.student_name} - ${data.estado}`, 'success');
                    }
                }
            } catch (error) {
                console.error('Error en reconocimiento:', error);
            }
        }

        // Marcar asistencia
        function markAttendance(studentId, estado) {
            const student = attendanceData.find(s => s.id === studentId);
            if (student && student.estado === 'AUSENTE') {
                student.estado = estado;
                student.hora = new Date().toLocaleTimeString('es-ES', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                });
                updateAttendanceList();
            }
        }

        // Finalizar sesión
        document.getElementById('btnFinishSession').addEventListener('click', async () => {
            if (!confirm('¿Finalizar sesión de asistencia?')) return;

            try {
                const response = await fetch('/api/attendance/finish', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        materia_id: currentMateria,
                        attendance: attendanceData
                    })
                });

                if (response.ok) {
                    showAlert('Sesión guardada exitosamente', 'success');
                    setTimeout(() => window.location.href = '/dashboard', 2000);
                }
            } catch (error) {
                showAlert('❌ Error al guardar sesión', 'error');
            }
        });

        // Mostrar alertas
        function showAlert(message, type = 'success') {
            const container = document.getElementById('alertContainer');
            container.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
            setTimeout(() => container.innerHTML = '', 5000);
        }

        // Manual y QR
        document.getElementById('btnManualAttendance').addEventListener('click', () => {
            window.location.href = '/asistencia/manual';
        });

        document.getElementById('btnQRCode').addEventListener('click', () => {
            window.location.href = '/asistencia/codigos-qr';
        });

        // Inicializar
        loadMaterias();

        // Cleanup
        window.addEventListener('beforeunload', () => {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
            if (recognitionInterval) {
                clearInterval(recognitionInterval);
            }
        });