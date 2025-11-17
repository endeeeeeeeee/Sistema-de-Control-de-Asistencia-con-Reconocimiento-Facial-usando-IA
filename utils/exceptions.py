"""
CLASS VISION - Excepciones Personalizadas
Define excepciones específicas del sistema para mejor manejo de errores
"""


class ClassVisionError(Exception):
    """Excepción base para todas las excepciones de CLASS VISION"""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class CameraError(ClassVisionError):
    """Excepción relacionada con la cámara"""
    pass


class ModelError(ClassVisionError):
    """Excepción relacionada con el modelo de IA"""
    pass


class ConfigError(ClassVisionError):
    """Excepción relacionada con la configuración"""
    pass


class StudentDataError(ClassVisionError):
    """Excepción relacionada con datos de estudiantes"""
    pass


class AttendanceError(ClassVisionError):
    """Excepción relacionada con registro de asistencia"""
    pass


class ValidationError(ClassVisionError):
    """Excepción relacionada con validación de datos"""
    pass
