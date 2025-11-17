"""
Módulo de asistencia automática sin GUI
Para uso con servidor móvil
Universidad Nur - CLASS VISION
"""

import cv2
import numpy as np
import pandas as pd
import datetime
import time
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
HAARCASCADE_PATH = BASE_DIR / "haarcascade_frontalface_default.xml"
TRAINING_LABEL_PATH = BASE_DIR / "TrainingImageLabel/Trainner.yml"
STUDENT_DETAILS_PATH = BASE_DIR / "StudentDetails/studentdetails.csv"
ATTENDANCE_PATH = BASE_DIR / "Attendance"

class AttendanceRecognizer:
    def __init__(self):
        self.recognizer = None
        self.face_cascade = None
        self.df_students = None
        self.camera = None
        self.is_running = False
        self.recognized_students = []
        
    def initialize(self):
        """Inicializa el reconocedor y carga el modelo"""
        try:
            # Crear reconocedor LBPH con múltiples intentos
            recognizer_created = False
            try:
                self.recognizer = cv2.face.LBPHFaceRecognizer_create()
                recognizer_created = True
            except AttributeError:
                pass
            
            if not recognizer_created:
                try:
                    self.recognizer = cv2.face_LBPHFaceRecognizer.create()
                    recognizer_created = True
                except:
                    pass
            
            if not recognizer_created:
                try:
                    self.recognizer = cv2.face.createLBPHFaceRecognizer()
                    recognizer_created = True
                except:
                    pass
            
            if not recognizer_created:
                raise ImportError(
                    "No se pudo crear el reconocedor LBPH. "
                    "Asegúrate de tener instalado opencv-contrib-python: "
                    "pip install opencv-contrib-python"
                )
            
            # Cargar modelo entrenado
            if not TRAINING_LABEL_PATH.exists():
                raise FileNotFoundError("Modelo no encontrado. Entrene el modelo primero.")
            
            self.recognizer.read(str(TRAINING_LABEL_PATH))
            
            # Cargar Haar Cascade
            self.face_cascade = cv2.CascadeClassifier(str(HAARCASCADE_PATH))
            
            # Cargar datos de estudiantes
            if not STUDENT_DETAILS_PATH.exists():
                raise FileNotFoundError("Archivo de estudiantes no encontrado.")
            
            self.df_students = pd.read_csv(STUDENT_DETAILS_PATH)
            
            return True
            
        except Exception as e:
            print(f"Error inicializando reconocedor: {e}")
            return False
    
    def start_camera(self):
        """Inicia la cámara"""
        try:
            # Intentar diferentes backends
            for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]:
                try:
                    self.camera = cv2.VideoCapture(0, backend)
                except:
                    self.camera = cv2.VideoCapture(0)
                
                if self.camera is not None and self.camera.isOpened():
                    return True
            
            return False
        except Exception as e:
            print(f"Error abriendo cámara: {e}")
            return False
    
    def recognize_faces(self, subject, duration=20):
        """
        Reconoce rostros durante un tiempo especificado
        
        Args:
            subject: Nombre de la materia
            duration: Duración en segundos (default 20)
            
        Returns:
            dict con información de la asistencia
        """
        if not self.initialize():
            return {"success": False, "error": "Error al inicializar reconocedor"}
        
        if not self.start_camera():
            return {"success": False, "error": "No se pudo abrir la cámara"}
        
        self.is_running = True
        self.recognized_students = []
        
        col_names = ["Enrollment", "Name"]
        attendance = pd.DataFrame(columns=col_names)
        
        start_time = time.time()
        end_time = start_time + duration
        
        print(f"Iniciando reconocimiento para {subject} durante {duration} segundos...")
        
        try:
            while time.time() < end_time and self.is_running:
                ret, frame = self.camera.read()
                
                if not ret or frame is None:
                    continue
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)
                
                for (x, y, w, h) in faces:
                    face_roi = gray[y:y+h, x:x+w]
                    student_id, confidence = self.recognizer.predict(face_roi)
                    
                    # Umbral de confianza
                    if confidence < 70:
                        # Buscar nombre del estudiante
                        student_data = self.df_students.loc[
                            self.df_students["Enrollment"] == student_id
                        ]
                        
                        if len(student_data) > 0:
                            student_name = student_data["Name"].values[0]
                            
                            # Agregar si no está ya en la lista
                            if student_id not in attendance["Enrollment"].values:
                                attendance.loc[len(attendance)] = [student_id, student_name]
                                self.recognized_students.append({
                                    "id": int(student_id),
                                    "name": student_name,
                                    "confidence": float(confidence)
                                })
                                print(f"✅ Reconocido: {student_name} (ID: {student_id}, Conf: {confidence:.2f})")
                
                # Pequeña pausa para no saturar CPU
                time.sleep(0.1)
            
            # Guardar asistencia
            if len(attendance) > 0:
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                hour, minute, second = timeStamp.split(":")
                
                attendance[date] = 1
                
                # Crear carpeta de materia si no existe
                subject_path = ATTENDANCE_PATH / subject
                subject_path.mkdir(parents=True, exist_ok=True)
                
                # Nombre del archivo
                filename = subject_path / f"{subject}_{date}_{hour}-{minute}-{second}.csv"
                
                # Guardar CSV
                attendance = attendance.drop_duplicates(["Enrollment"], keep="first")
                attendance.to_csv(filename, index=False)
                
                print(f"✅ Asistencia guardada: {filename}")
                print(f"Total reconocidos: {len(attendance)}")
                
                return {
                    "success": True,
                    "subject": subject,
                    "total": len(attendance),
                    "students": self.recognized_students,
                    "filename": str(filename),
                    "date": date,
                    "time": timeStamp
                }
            else:
                return {
                    "success": False,
                    "error": "No se reconocieron estudiantes"
                }
                
        except Exception as e:
            print(f"Error durante reconocimiento: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            self.stop()
    
    def stop(self):
        """Detiene el reconocimiento y libera recursos"""
        self.is_running = False
        if self.camera is not None:
            self.camera.release()
        cv2.destroyAllWindows()
        print("Reconocimiento detenido")

# Instancia global para uso desde el servidor
_recognizer_instance = None

def get_recognizer():
    """Obtiene o crea la instancia del reconocedor"""
    global _recognizer_instance
    if _recognizer_instance is None:
        _recognizer_instance = AttendanceRecognizer()
    return _recognizer_instance

def automatic_attendence(subject, duration=20):
    """
    Función de compatibilidad con la interfaz original
    
    Args:
        subject: Nombre de la materia
        duration: Duración en segundos
        
    Returns:
        dict con resultado
    """
    recognizer = get_recognizer()
    return recognizer.recognize_faces(subject, duration)

if __name__ == "__main__":
    # Prueba
    result = automatic_attendence("TEST", duration=10)
    print(result)
