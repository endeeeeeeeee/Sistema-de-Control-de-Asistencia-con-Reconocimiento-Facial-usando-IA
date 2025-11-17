"""
Servidor Web para Control Remoto de Asistencia
Universidad Nur - Sistema CLASS VISION
Permite a los docentes controlar la asistencia desde su smartphone
"""

from flask import Flask, render_template, request, jsonify, send_file
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

app = Flask(__name__)
CORS(app)

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
    """Página principal móvil"""
    return render_template('mobile_index.html')

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
        if STUDENT_DETAILS_PATH.exists():
            df = pd.read_csv(STUDENT_DETAILS_PATH)
            students = df.to_dict('records')
            return jsonify({'students': students, 'total': len(students)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'students': [], 'total': 0})

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

def start_server(port=5000, debug=False):
    """Inicia el servidor web"""
    ip = get_local_ip()
    print(f"\n{'='*60}")
    print(f"🎓 UNIVERSIDAD NUR - CLASS VISION")
    print(f"📱 Servidor Móvil Iniciado")
    print(f"{'='*60}")
    print(f"\n🌐 Accede desde tu smartphone:")
    print(f"   http://{ip}:{port}")
    print(f"\n📱 Escanea el código QR:")
    print(f"   http://{ip}:{port}/api/qr")
    print(f"\n{'='*60}\n")
    
    # Crear carpeta templates si no existe
    templates_dir = BASE_DIR / "templates"
    templates_dir.mkdir(exist_ok=True)
    
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)

if __name__ == "__main__":
    start_server()
