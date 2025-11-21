"""
Servidor Web para Control Remoto de Asistencia
Universidad Nur - Sistema CLASS VISION
Permite a los docentes controlar la asistencia desde su smartphone
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_cors import CORS
import qrcode
import io
import socket
import threading
import cv2
import base64
import numpy as np
from datetime import datetime
import pandas as pd
from pathlib import Path
import json

# Importar módulos del sistema
import automatic_attendance_headless as attendance_module
import show_attendance
from auth_manager_flexible import AuthManager

# Importar blueprints nuevos
from api_routes_flexible import api_bp

app = Flask(__name__)
CORS(app)

# Agregar logging para diagnosticar
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Middleware para ver todas las peticiones
@app.before_request
def log_request_info():
    print(f'[DEBUG] Petición recibida: {request.method} {request.path}')
    logger.debug(f'Petición recibida: {request.method} {request.path}')
    logger.debug(f'Headers: {dict(request.headers)}')

@app.after_request
def log_response_info(response):
    print(f'[DEBUG] Respuesta: {response.status_code} para {request.path}')
    logger.debug(f'Respuesta: {response.status_code} para {request.path}')
    return response

# Registrar blueprints
try:
    app.register_blueprint(api_bp)
except Exception as e:
    print(f"⚠️ Advertencia: Error al registrar blueprint: {e}")

# Instancia de autenticación flexible (lazy initialization)
auth_manager = None

def get_auth_manager():
    """Obtener instancia de AuthManager (lazy initialization)"""
    global auth_manager
    if auth_manager is None:
        try:
            auth_manager = AuthManager()
        except Exception as e:
            print(f"⚠️ Advertencia: Error al inicializar AuthManager: {e}")
            # Crear una instancia dummy para evitar errores
            auth_manager = None
    return auth_manager

# Configurar en el app context para acceso desde blueprints
app.config['AUTH_MANAGER'] = get_auth_manager

BASE_DIR = Path(__file__).parent
ATTENDANCE_PATH = BASE_DIR / "Attendance"
STUDENT_DETAILS_PATH = BASE_DIR / "StudentDetails/studentdetails.csv"

# Estado global del servidor
server_state = {
    'camera_active': False,
    'current_subject': None,
    'recognized_students': [],
    'camera_thread': None
}

def get_local_ip():
    """Obtiene la IP local de la máquina"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def generate_qr_code(url):
    """Genera un código QR para el acceso móvil"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

@app.route('/')
def index():
    """Página principal - redirige a login"""
    logger.debug('Ruta / accedida')
    try:
        return redirect(url_for('login_page'))
    except Exception as e:
        logger.error(f'Error en ruta /: {e}')
        return f'<h1>Error</h1><p>{str(e)}</p>', 500

@app.route('/test')
def test():
    """Ruta de prueba simple"""
    logger.debug('Ruta /test accedida')
    return '<h1>Servidor funcionando correctamente</h1><p><a href="/login">Ir a login</a></p>'

@app.route('/ping')
def ping():
    """Ruta de ping simple sin dependencias"""
    logger.debug('Ruta /ping accedida')
    return 'pong'

@app.route('/login')
def login_page():
    """Página de login - nueva interfaz flexible"""
    logger.debug('Ruta /login accedida')
    try:
        logger.debug('Intentando renderizar template login_flexible.html')
        result = render_template('login_flexible.html')
        logger.debug('Template renderizado exitosamente')
        return result
    except Exception as e:
        logger.error(f'Error al cargar template: {e}')
        import traceback
        traceback.print_exc()
        return f'<h1>Error al cargar template</h1><p>{str(e)}</p>', 500

@app.route('/test-login')
def test_login_page():
    """Página de prueba de login"""
    return render_template('test_login.html')

@app.route('/registro-estudiante')
def registro_estudiante_page():
    """Portal público de auto-registro para estudiantes"""
    return render_template('registro_estudiante.html')

@app.route('/registro')
def registro_page():
    """Página de registro de usuarios"""
    return render_template('registro.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard principal - nueva interfaz flexible"""
    return render_template('dashboard_flexible.html')

@app.route('/equipo/<int:equipo_id>')
def equipo_page(equipo_id):
    """Página de gestión de un equipo específico"""
    return render_template('equipo.html')

@app.route('/sesion-asistencia')
def sesion_asistencia_page():
    """Página de sesión de asistencia con reconocimiento facial en vivo"""
    return render_template('sesion_asistencia.html')

@app.route('/vincular-dispositivo')
def vincular_dispositivo_page():
    """Página para vincular dispositivo móvil con código QR"""
    return render_template('vincular_dispositivo.html')

@app.route('/validar-qr')
def validar_qr_page():
    """Página para validar QR de asistencia (sin autenticación)"""
    return render_template('validar_qr.html')

@app.route('/configuracion')
def configuracion_page():
    """Configuración del sistema"""
    return render_template('configuracion.html')

# ==========================================
# RUTAS LEGACY (Redirigir a nuevo dashboard)
# ==========================================

@app.route('/materias')
def materias_page():
    """[LEGACY] Redirige a dashboard"""
    return redirect(url_for('dashboard'))

@app.route('/estudiantes')
def estudiantes_page():
    """[LEGACY] Redirige a dashboard"""
    return redirect(url_for('dashboard'))

@app.route('/tomar-asistencia')
def tomar_asistencia_page():
    """[LEGACY] Redirige a dashboard"""
    return redirect(url_for('dashboard'))

@app.route('/codigos-qr')
def codigos_qr_page():
    """[LEGACY] Redirige a dashboard"""
    return redirect(url_for('dashboard'))

@app.route('/reportes')
def reportes_page():
    """Página de reportes detallados"""
    return render_template('reportes.html')

# ==========================================
# RUTAS LEGACY (Mantener por compatibilidad)
# ==========================================

@app.route('/register-student')
def register_student_page():
    """[LEGACY] Redirige a nueva página de estudiantes"""
    return redirect(url_for('estudiantes_page'))

@app.route('/take-attendance')
def take_attendance_page():
    """[LEGACY] Redirige a nueva página de asistencia"""
    return redirect(url_for('tomar_asistencia_page'))

@app.route('/mobile')
def mobile_control():
    """[LEGACY] Control móvil (requiere autenticación)"""
    return render_template('mobile_attendance.html')

@app.route('/api/qr')
def get_qr():
    """Genera QR code para acceso rápido"""
    ip = get_local_ip()
    port = 5000
    url = f"http://{ip}:{port}"
    qr_buffer = generate_qr_code(url)
    return send_file(qr_buffer, mimetype='image/png')

@app.route('/api/subjects')
def get_subjects():
    """Obtiene la lista de materias disponibles"""
    subjects = []
    if ATTENDANCE_PATH.exists():
        for folder in ATTENDANCE_PATH.iterdir():
            if folder.is_dir():
                subjects.append(folder.name)
    return jsonify({'subjects': subjects})

@app.route('/api/students')
def get_students():
    """Obtiene la lista de estudiantes registrados"""
    try:
        students = student_manager.get_all_students()
        return jsonify({'students': students, 'total': len(students)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start-attendance', methods=['POST'])
def start_attendance():
    """Inicia el proceso de toma de asistencia"""
    try:
        data = request.json
        subject = data.get('subject')
        
        if not subject:
            return jsonify({'error': 'Materia no especificada'}), 400
        
        server_state['current_subject'] = subject
        server_state['recognized_students'] = []
        
        # Iniciar automaticAttedance en un thread
        def run_attendance():
            try:
                result = attendance_module.automatic_attendence(subject, duration=20)
                if result.get('success'):
                    server_state['recognized_students'] = [
                        s['name'] for s in result.get('students', [])
                    ]
                    print(f"✅ Asistencia completada: {result.get('total', 0)} estudiantes")
                else:
                    print(f"❌ Error en asistencia: {result.get('error', 'Unknown')}")
            except Exception as e:
                print(f"Error en asistencia automática: {e}")
        
        if server_state['camera_thread'] is None or not server_state['camera_thread'].is_alive():
            server_state['camera_thread'] = threading.Thread(target=run_attendance)
            server_state['camera_thread'].daemon = True
            server_state['camera_thread'].start()
            server_state['camera_active'] = True
            
            return jsonify({
                'success': True,
                'message': f'Asistencia iniciada para {subject}',
                'subject': subject
            })
        else:
            return jsonify({'error': 'Ya hay una sesión activa'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop-attendance', methods=['POST'])
def stop_attendance():
    """Detiene el proceso de toma de asistencia"""
    try:
        server_state['camera_active'] = False
        server_state['current_subject'] = None
        
        return jsonify({
            'success': True,
            'message': 'Asistencia detenida',
            'recognized': server_state['recognized_students']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def get_status():
    """Obtiene el estado actual del sistema"""
    return jsonify({
        'camera_active': server_state['camera_active'],
        'current_subject': server_state['current_subject'],
        'recognized_count': len(server_state['recognized_students']),
        'recognized_students': server_state['recognized_students']
    })

@app.route('/api/attendance-history/<subject>')
def get_attendance_history(subject):
    """Obtiene el historial de asistencia de una materia"""
    try:
        subject_path = ATTENDANCE_PATH / subject / "attendance.csv"
        if subject_path.exists():
            df = pd.read_csv(subject_path)
            records = df.to_dict('records')
            return jsonify({
                'subject': subject,
                'records': records,
                'total': len(records)
            })
        else:
            return jsonify({'error': 'No hay registros'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/server-info')
def server_info():
    """Información del servidor"""
    ip = get_local_ip()
    return jsonify({
        'ip': ip,
        'port': 5000,
        'url': f"http://{ip}:5000",
        'institution': 'Universidad Nur',
        'system': 'CLASS VISION',
        'version': '2.1.0'
    })

# ============================================
# ENDPOINTS DE AUTENTICACIÓN
# ============================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Registrar nuevo docente"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        full_name = data.get('full_name')
        
        if not all([username, password, full_name]):
            return jsonify({'success': False, 'error': 'Todos los campos son requeridos'}), 400
        
        user, token = auth_manager.register(username, password, full_name)
        
        if user:
            return jsonify({
                'success': True,
                'user': user,
                'token': token,
                'message': 'Registro exitoso'
            })
        else:
            return jsonify({'success': False, 'error': 'Usuario ya existe'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login de docente"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        print(f"\n=== LOGIN ATTEMPT ===")
        print(f"Username recibido: '{username}'")
        print(f"Password recibido: '{password}' (length: {len(password) if password else 0})")
        
        if not all([username, password]):
            return jsonify({'success': False, 'error': 'Usuario y contraseña requeridos'}), 400
        
        user, token = auth_manager.login(username, password)
        
        print(f"Resultado login: {'SUCCESS' if user else 'FAILED'}")
        
        if user:
            return jsonify({
                'success': True,
                'user': user,
                'token': token,
                'message': 'Login exitoso'
            })
        else:
            return jsonify({'success': False, 'error': 'Credenciales inválidas'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Cerrar sesión"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if token:
            auth_manager.logout(token)
        return jsonify({'success': True, 'message': 'Sesión cerrada'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/validate', methods=['POST'])
def validate_token():
    """Validar token de sesión"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user = auth_manager.validate_token(token)
        
        if user:
            return jsonify({'success': True, 'user': user})
        else:
            return jsonify({'success': False, 'error': 'Token inválido'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# ENDPOINTS DE GESTIÓN DE MATERIAS
# ============================================

@app.route('/api/teacher/subjects', methods=['GET'])
def get_teacher_subjects():
    """Obtener materias del docente"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user = auth_manager.validate_token(token)
        
        if not user:
            return jsonify({'success': False, 'error': 'No autorizado'}), 401
        
        subjects_data = []
        for subject_name in user.get('subjects', []):
            students = student_manager.get_students_by_subject(user['username'], subject_name)
            subjects_data.append({
                'name': subject_name,
                'student_count': len(students)
            })
        
        return jsonify({'success': True, 'subjects': subjects_data})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/teacher/subjects', methods=['POST'])
def add_teacher_subject():
    """Agregar materia al docente"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user = auth_manager.validate_token(token)
        
        if not user:
            return jsonify({'success': False, 'error': 'No autorizado'}), 401
        
        data = request.json
        subject_name = data.get('subject_name', '').strip().upper()
        
        if not subject_name:
            return jsonify({'success': False, 'error': 'Nombre de materia requerido'}), 400
        
        success = auth_manager.add_subject(user['username'], subject_name)
        
        if success:
            # Crear carpeta para la materia si no existe
            subject_path = ATTENDANCE_PATH / subject_name
            subject_path.mkdir(exist_ok=True)
            
            return jsonify({'success': True, 'message': 'Materia agregada exitosamente'})
        else:
            return jsonify({'success': False, 'error': 'Error al agregar materia'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/teacher/subjects', methods=['DELETE'])
def remove_teacher_subject():
    """Eliminar materia del docente"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user = auth_manager.validate_token(token)
        
        if not user:
            return jsonify({'success': False, 'error': 'No autorizado'}), 401
        
        data = request.json
        subject_name = data.get('subject_name')
        
        if not subject_name:
            return jsonify({'success': False, 'error': 'Nombre de materia requerido'}), 400
        
        success = auth_manager.remove_subject(user['username'], subject_name)
        
        if success:
            return jsonify({'success': True, 'message': 'Materia eliminada'})
        else:
            return jsonify({'success': False, 'error': 'Error al eliminar materia'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# ENDPOINTS DE GESTIÓN DE ESTUDIANTES
# ============================================

@app.route('/api/teacher/students/<subject>', methods=['GET'])
def get_subject_students(subject):
    """Obtener estudiantes de una materia"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user = auth_manager.validate_token(token)
        
        if not user:
            return jsonify({'success': False, 'error': 'No autorizado'}), 401
        
        students = student_manager.get_students_by_subject(user['username'], subject)
        
        return jsonify({'success': True, 'students': students})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/teacher/students/<subject>', methods=['POST'])
def add_subject_student(subject):
    """Agregar estudiante a una materia"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user = auth_manager.validate_token(token)
        
        if not user:
            return jsonify({'success': False, 'error': 'No autorizado'}), 401
        
        data = request.json
        enrollment = data.get('enrollment')
        name = data.get('name')
        
        if not all([enrollment, name]):
            return jsonify({'success': False, 'error': 'Matrícula y nombre requeridos'}), 400
        
        result = student_manager.add_student_to_subject(
            user['username'], subject, enrollment, name
        )
        
        if result.get('success'):
            return jsonify({'success': True, 'message': result.get('message', 'Estudiante agregado')})
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Error al agregar estudiante')}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/teacher/students/<subject>', methods=['DELETE'])
def remove_subject_student(subject):
    """Eliminar estudiante de una materia"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user = auth_manager.validate_token(token)
        
        if not user:
            return jsonify({'success': False, 'error': 'No autorizado'}), 401
        
        data = request.json
        enrollment = data.get('enrollment')
        
        if not enrollment:
            return jsonify({'success': False, 'error': 'Matrícula requerida'}), 400
        
        result = student_manager.remove_student_from_subject(
            user['username'], subject, enrollment
        )
        
        if result.get('success'):
            return jsonify({'success': True, 'message': result.get('message', 'Estudiante eliminado')})
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Error al eliminar estudiante')}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# ENDPOINTS PARA RECONOCIMIENTO MÓVIL
# ============================================

@app.route('/api/register-student', methods=['POST'])
def register_student():
    """Registra un nuevo estudiante con fotos y entrena el modelo"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user = auth_manager.validate_token(token)
        
        if not user:
            return jsonify({'success': False, 'error': 'No autorizado'}), 401
        
        data = request.json
        enrollment = data.get('enrollment')
        name = data.get('name')
        subject = data.get('subject')
        photos = data.get('photos', [])  # Array de base64
        
        if not all([enrollment, name, subject]) or len(photos) < 50:
            return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
        
        # 1. Crear carpeta para fotos del estudiante
        training_image_path = BASE_DIR / "TrainingImage"
        training_image_path.mkdir(exist_ok=True)
        
        # 2. Guardar fotos
        import re
        for idx, photo_data in enumerate(photos):
            # Decodificar base64
            photo_data = re.sub('^data:image/.+;base64,', '', photo_data)
            photo_bytes = base64.b64decode(photo_data)
            nparr = np.frombuffer(photo_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is not None:
                # Guardar imagen
                filename = f"{name}_{enrollment}_{idx+1}.jpg"
                filepath = training_image_path / filename
                cv2.imwrite(str(filepath), img)
        
        # 3. Agregar estudiante al CSV global
        student_data = {
            'Enrollment': [int(enrollment)],
            'Name': [name]
        }
        
        if STUDENT_DETAILS_PATH.exists():
            df = pd.read_csv(STUDENT_DETAILS_PATH)
            # Verificar si ya existe
            if not ((df['Enrollment'] == int(enrollment)).any()):
                df_new = pd.DataFrame(student_data)
                df = pd.concat([df, df_new], ignore_index=True)
                df.to_csv(STUDENT_DETAILS_PATH, index=False)
        else:
            STUDENT_DETAILS_PATH.parent.mkdir(exist_ok=True)
            df_new = pd.DataFrame(student_data)
            df_new.to_csv(STUDENT_DETAILS_PATH, index=False)
        
        # 4. Agregar estudiante a la materia del docente (SIEMPRE, incluso si ya existía en CSV)
        result = student_manager.add_student_to_subject(user['username'], subject, str(enrollment), name)
        
        if not result.get('success'):
            print(f"⚠️ Advertencia: {result.get('error', 'No se pudo agregar estudiante')}")
        
        # 5. Entrenar modelo
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        faces = []
        ids = []
        
        # Leer todas las imágenes de entrenamiento
        for image_file in training_image_path.glob("*.jpg"):
            try:
                # Extraer ID del nombre del archivo
                parts = image_file.stem.split('_')
                if len(parts) >= 2:
                    student_id = int(parts[-2])
                    
                    img = cv2.imread(str(image_file))
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    
                    # Detectar rostros
                    detected_faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    for (x, y, w, h) in detected_faces:
                        faces.append(gray[y:y+h, x:x+w])
                        ids.append(student_id)
            except:
                continue
        
        if len(faces) > 0:
            # Entrenar modelo
            recognizer.train(faces, np.array(ids))
            
            # Guardar modelo
            trainer_path = BASE_DIR / "TrainingImageLabel"
            trainer_path.mkdir(exist_ok=True)
            recognizer.write(str(trainer_path / "Trainner.yml"))
            
            return jsonify({
                'success': True,
                'message': f'Estudiante {name} registrado con {len(photos)} fotos',
                'faces_trained': len(faces)
            })
        else:
            return jsonify({'success': False, 'error': 'No se detectaron rostros en las fotos'}), 400
        
    except Exception as e:
        print(f"Error en register_student: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recognize-frame', methods=['POST'])
def recognize_frame():
    """Reconoce rostros desde una imagen capturada por el móvil"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user = auth_manager.validate_token(token)
        
        if not user:
            return jsonify({'success': False, 'error': 'No autorizado'}), 401
        
        data = request.json
        image_data = data.get('image')  # Base64
        subject = data.get('subject')
        
        if not image_data or not subject:
            return jsonify({'recognized': False, 'error': 'Datos incompletos'}), 400
        
        # Decodificar imagen base64
        import re
        image_data = re.sub('^data:image/.+;base64,', '', image_data)
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'recognized': False, 'error': 'Imagen inválida'}), 400
        
        # Cargar reconocedor
        recognizer_path = BASE_DIR / "TrainingImageLabel" / "Trainner.yml"
        if not recognizer_path.exists():
            return jsonify({'recognized': False, 'error': 'Modelo no entrenado'}), 400
        
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(str(recognizer_path))
        
        # Detectar rostros
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return jsonify({'recognized': False, 'message': 'No se detectó rostro'})
        
        # Reconocer primer rostro
        (x, y, w, h) = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        enrollment, confidence = recognizer.predict(face_roi)
        
        if confidence < 85:  # Umbral de confianza
            # Buscar estudiante en CSV
            if STUDENT_DETAILS_PATH.exists():
                df = pd.read_csv(STUDENT_DETAILS_PATH)
                student = df[df['Enrollment'] == enrollment]
                
                if not student.empty:
                    name = student.iloc[0]['Name']
                    
                    # Registrar asistencia
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    subject_path = ATTENDANCE_PATH / subject
                    subject_path.mkdir(exist_ok=True)
                    attendance_file = subject_path / "attendance.csv"
                    
                    # Agregar registro
                    attendance_data = {
                        'Enrollment': [enrollment],
                        'Name': [name],
                        'Date': [timestamp.split()[0]],
                        'Time': [timestamp.split()[1]]
                    }
                    
                    if attendance_file.exists():
                        df_att = pd.read_csv(attendance_file)
                        # Verificar si ya tiene asistencia hoy
                        today = timestamp.split()[0]
                        already_present = ((df_att['Enrollment'] == enrollment) & (df_att['Date'] == today)).any()
                        
                        if not already_present:
                            df_new = pd.DataFrame(attendance_data)
                            df_att = pd.concat([df_att, df_new], ignore_index=True)
                            df_att.to_csv(attendance_file, index=False)
                            
                            return jsonify({
                                'recognized': True,
                                'name': name,
                                'enrollment': str(enrollment),
                                'confidence': float(confidence)
                            })
                        else:
                            return jsonify({'recognized': False, 'message': 'Ya registrado hoy'})
                    else:
                        df_new = pd.DataFrame(attendance_data)
                        df_new.to_csv(attendance_file, index=False)
                        
                        return jsonify({
                            'recognized': True,
                            'name': name,
                            'enrollment': str(enrollment),
                            'confidence': float(confidence)
                        })
        
        return jsonify({'recognized': False, 'message': 'Rostro no reconocido'})
        
    except Exception as e:
        print(f"Error en recognize_frame: {e}")
        return jsonify({'recognized': False, 'error': str(e)}), 500


# ============================================================================
# NUEVOS ENDPOINTS PARA POSTGRESQL
# ============================================================================

@app.route('/api/assistant/command', methods=['POST'])
def assistant_command():
    """Procesar comando del asistente virtual"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user = auth_manager.validate_token(token)
        
        if not user:
            return jsonify({'success': False, 'error': 'No autorizado'}), 401
        
        data = request.json
        comando = data.get('comando', '').lower()
        
        # Importar asistente
        from assistant_virtual import AsistenteVirtual
        from database_models import DatabaseManager
        import os
        
        db_manager = DatabaseManager(os.getenv('DATABASE_URL'))
        asistente = AsistenteVirtual(db_manager)
        
        # Procesar comando
        respuesta = asistente.procesar_comando(comando, usuario_id=user.get('id'))
        
        return jsonify({
            'success': True,
            'respuesta': respuesta
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Obtener estadísticas del dashboard"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user = auth_manager.validate_token(token)
        
        if not user:
            return jsonify({'success': False, 'error': 'No autorizado'}), 401
        
        from database_models import Materia, Inscripcion, AsistenciaLog, PersonalAdmin
        from sqlalchemy import func
        from datetime import date
        
        session = auth_manager.db.get_session()
        
        try:
            # Obtener ID del docente
            docente = session.query(PersonalAdmin).filter_by(username=user['username']).first()
            if not docente:
                return jsonify({'success': False, 'error': 'Docente no encontrado'}), 404
            
            # Contar materias activas
            total_materias = session.query(func.count(Materia.id)).filter_by(
                id_docente=docente.id,
                activo=True
            ).scalar() or 0
            
            # Contar estudiantes inscritos
            total_estudiantes = session.query(func.count(Inscripcion.id.distinct())).join(
                Materia
            ).filter(
                Materia.id_docente == docente.id,
                Materia.activo == True,
                Inscripcion.estado == 'ACTIVO'
            ).scalar() or 0
            
            # Contar asistencias de hoy
            hoy = date.today()
            asistencias_hoy = session.query(func.count(AsistenciaLog.id)).join(
                Inscripcion
            ).join(
                Materia
            ).filter(
                Materia.id_docente == docente.id,
                AsistenciaLog.fecha == hoy,
                AsistenciaLog.estado.in_(['PRESENTE', 'TARDANZA'])
            ).scalar() or 0
            
            # Calcular promedio
            total_asistencias = session.query(func.count(AsistenciaLog.id)).join(
                Inscripcion
            ).join(
                Materia
            ).filter(
                Materia.id_docente == docente.id,
                AsistenciaLog.estado.in_(['PRESENTE', 'TARDANZA'])
            ).scalar() or 0
            
            total_registros = session.query(func.count(AsistenciaLog.id)).join(
                Inscripcion
            ).join(
                Materia
            ).filter(
                Materia.id_docente == docente.id
            ).scalar() or 1
            
            porcentaje = round((total_asistencias / total_registros) * 100, 1) if total_registros > 0 else 0
            
            return jsonify({
                'success': True,
                'stats': {
                    'total_materias': total_materias,
                    'total_estudiantes': total_estudiantes,
                    'asistencias_hoy': asistencias_hoy,
                    'porcentaje_asistencia': porcentaje
                }
            })
            
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def start_server(port=5001, debug=False):
    """Inicia el servidor web"""
    ip = get_local_ip()
    print(f"\n{'='*60}")
    print(f"UNIVERSIDAD NUR - CLASS VISION")
    print(f"Servidor Movil Iniciado")
    print(f"{'='*60}")
    print(f"\nAccede desde tu smartphone:")
    print(f"   http://{ip}:{port}")
    print(f"\nEscanea el codigo QR:")
    print(f"   http://{ip}:{port}/api/qr")
    print(f"{'='*60}\n")
    
    # Crear carpeta templates si no existe
    templates_dir = BASE_DIR / "templates"
    templates_dir.mkdir(exist_ok=True)
    
    # Ejecutar sin SSL para compatibilidad con navegadores móviles
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)

if __name__ == "__main__":
    start_server()
