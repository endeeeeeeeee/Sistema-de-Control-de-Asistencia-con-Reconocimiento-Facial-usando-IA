let equipoId = null;
        const urlParams = new URLSearchParams(window.location.search);
        const codigo = urlParams.get('codigo');

        async function verificarCodigo() {
            if (!codigo) {
                mostrarError('❌ Código no válido');
                return;
            }

            try {
                const response = await fetch(`/api/dispositivos/verificar/${codigo}`);
                const data = await response.json();

                if (data.success) {
                    equipoId = data.equipo_id;
                    document.getElementById('equipoNombre').textContent = data.equipo_nombre || 'Equipo';
                    document.getElementById('infoContainer').style.display = 'block';
                    mostrarExito('✅ Dispositivo vinculado correctamente');
                } else {
                    mostrarError('❌ ' + (data.error || 'Código inválido o expirado'));
                }
            } catch (error) {
                console.error('Error:', error);
                mostrarError('❌ Error de conexión');
            }
        }

        function mostrarExito(mensaje) {
            document.getElementById('statusContainer').innerHTML = `
                <div class="status success">${mensaje}</div>
            `;
        }

        function mostrarError(mensaje) {
            document.getElementById('statusContainer').innerHTML = `
                <div class="status error">${mensaje}</div>
            `;
        }

        function abrirSesionAsistencia() {
            if (equipoId) {
                window.location.href = `/sesion-asistencia?equipo_id=${equipoId}`;
            }
        }

        // Verificar código al cargar
        verificarCodigo();