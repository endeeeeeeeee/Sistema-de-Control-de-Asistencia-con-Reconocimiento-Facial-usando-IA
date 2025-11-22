const API_BASE = '/api';
let codigoQR = null;
let stream = null;

document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    codigoQR = urlParams.get('codigo') || urlParams.get('code');

    if (!codigoQR) {
        showError('No se proporcionó código QR');
        return;
    }

    // Paso 1: Verificar validez del QR
    await verificarQR(codigoQR);
});

async function verificarQR(code) {
    try {
        const response = await fetch(`${API_BASE}/qr/verificar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ codigo_qr: code })
        });

        const data = await response.json();

        if (data.success) {
            // QR válido, proceder a captura facial
            mostrarCamaraFacial(data);
        } else {
            showError(data.error || 'Código QR inválido');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Error de conexión. Por favor intenta de nuevo.');
    }
}

let reconocimientoInterval = null;
let intentosReconocimiento = 0;
const MAX_INTENTOS = 30; // 30 intentos (15 segundos con intervalo de 500ms)

async function mostrarCamaraFacial(datosQR) {
    // Ocultar loading y mostrar cámara
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('cameraState').style.display = 'block';
    
    // Mostrar información del usuario
    document.getElementById('cameraUsuario').textContent = datosQR.usuario;
    document.getElementById('cameraEquipo').textContent = datosQR.equipo;
    
    // Iniciar cámara
    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                facingMode: 'user',
                width: { ideal: 640 },
                height: { ideal: 480 }
            } 
        });
        
        const video = document.getElementById('videoPreview');
        video.srcObject = stream;
        
        // Esperar a que el video esté listo
        video.onloadedmetadata = () => {
            console.log('✅ Cámara iniciada correctamente');
            
            // Ocultar botón de captura manual
            document.getElementById('captureBtn').style.display = 'none';
            
            // Mostrar mensaje de escaneo automático
            const scanningMsg = document.createElement('p');
            scanningMsg.id = 'scanningMessage';
            scanningMsg.style.textAlign = 'center';
            scanningMsg.style.color = '#2196F3';
            scanningMsg.style.fontWeight = 'bold';
            scanningMsg.style.margin = '15px 0';
            scanningMsg.innerHTML = '🔄 Escaneando rostro automáticamente...<br><small>Mantén tu rostro frente a la cámara</small>';
            document.getElementById('cameraContainer').after(scanningMsg);
            
            // Iniciar reconocimiento automático después de 2 segundos
            setTimeout(() => {
                iniciarReconocimientoAutomatico();
            }, 2000);
        };
        
    } catch (error) {
        console.error('Error al acceder a la cámara:', error);
        showError('No se pudo acceder a la cámara. Verifica los permisos.');
    }
}

async function iniciarReconocimientoAutomatico() {
    console.log('🎯 Iniciando reconocimiento automático...');
    
    reconocimientoInterval = setInterval(async () => {
        intentosReconocimiento++;
        
        if (intentosReconocimiento > MAX_INTENTOS) {
            detenerReconocimiento();
            showError('No se pudo reconocer tu rostro después de varios intentos. Intenta con mejor iluminación.');
            return;
        }
        
        console.log(`Intento ${intentosReconocimiento}/${MAX_INTENTOS}`);
        await capturarYValidarAutomatico();
        
    }, 500); // Cada 500ms
}

function detenerReconocimiento() {
    if (reconocimientoInterval) {
        clearInterval(reconocimientoInterval);
        reconocimientoInterval = null;
    }
}

async function capturarYValidarAutomatico() {
    const video = document.getElementById('videoPreview');
    const canvas = document.getElementById('canvas');
    
    // Verificar que el video esté listo
    if (!video || video.readyState !== 4) {
        return;
    }
    
    try {
        // Configurar canvas al tamaño del video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Capturar frame del video
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convertir a base64
        const imagenBase64 = canvas.toDataURL('image/jpeg', 0.8);
        
        // Enviar a backend para validación facial
        const response = await fetch(`${API_BASE}/qr/confirmar-asistencia`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                codigo_qr: codigoQR,
                imagen: imagenBase64
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // ¡Rostro reconocido! Detener escaneo
            detenerReconocimiento();
            
            // Detener cámara
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
            
            console.log('✅ Rostro reconocido y asistencia registrada');
            showSuccess(data);
        } else if (response.status === 403) {
            // Rostro detectado pero no reconocido - continuar intentando
            console.log(`⚠️ Intento ${intentosReconocimiento}: ${data.error}`);
            
            // Actualizar mensaje de escaneo
            const scanningMsg = document.getElementById('scanningMessage');
            if (scanningMsg) {
                scanningMsg.innerHTML = `🔄 Escaneando... (Intento ${intentosReconocimiento}/${MAX_INTENTOS})<br><small>${data.error}</small>`;
            }
        } else if (response.status === 400) {
            // No se detectó rostro - continuar intentando
            console.log(`⚠️ Intento ${intentosReconocimiento}: No se detectó rostro`);
        } else {
            // Otro error - detener
            detenerReconocimiento();
            
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
            
            showError(data.error || 'Error al validar el rostro');
        }
        
    } catch (error) {
        console.error('Error en reconocimiento automático:', error);
        // No detenemos el escaneo por errores de red temporales
    }
}

function showSuccess(data) {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('cameraState').style.display = 'none';
    document.getElementById('errorState').style.display = 'none';

    document.getElementById('successUsuario').textContent = data.usuario;
    document.getElementById('successEquipo').textContent = data.equipo;
    document.getElementById('successConfianza').textContent = data.confianza ? `${data.confianza}%` : 'N/A';
    document.getElementById('successFecha').textContent = new Date().toLocaleString('es-BO', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    document.getElementById('successState').style.display = 'block';
}

function showError(message) {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('cameraState').style.display = 'none';
    document.getElementById('successState').style.display = 'none';

    document.getElementById('errorMessage').innerHTML = `<strong>Error:</strong><br>${message}`;
    document.getElementById('errorState').style.display = 'block';
    
    // Detener cámara si está activa
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
}