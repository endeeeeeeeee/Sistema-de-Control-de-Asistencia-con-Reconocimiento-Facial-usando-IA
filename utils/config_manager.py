"""
CLASS VISION - Gestor de Configuración
Maneja la carga y acceso a la configuración del sistema
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from .logger import get_logger


class ConfigManager:
    """
    Gestor de configuración del sistema
    Carga configuración desde archivos JSON con fallback a valores por defecto
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.logger = get_logger(__name__)
            self.config_dir = Path("config")
            self.config = {}
            self.load_config()
            self.initialized = True
    
    def load_config(self):
        """Cargar configuración desde archivos JSON"""
        # Intentar cargar configuración local primero
        local_config_path = self.config_dir / "local_config.json"
        default_config_path = self.config_dir / "default_config.json"
        
        config_path = None
        
        if local_config_path.exists():
            config_path = local_config_path
            self.logger.info(f"Cargando configuración local: {local_config_path}")
        elif default_config_path.exists():
            config_path = default_config_path
            self.logger.info(f"Cargando configuración por defecto: {default_config_path}")
        else:
            self.logger.warning("No se encontró archivo de configuración, usando valores por defecto")
            self._load_default_values()
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self.logger.info("Configuración cargada exitosamente")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error al parsear JSON de configuración: {e}")
            self._load_default_values()
        except Exception as e:
            self.logger.error(f"Error al cargar configuración: {e}")
            self._load_default_values()
    
    def _load_default_values(self):
        """Cargar valores por defecto si no hay archivo de configuración"""
        self.config = {
            "app": {
                "name": "CLASS VISION",
                "version": "2.0.0"
            },
            "paths": {
                "haarcascade": "haarcascade_frontalface_default.xml",
                "training_images": "TrainingImage",
                "training_label": "TrainingImageLabel/Trainner.yml",
                "student_details": "StudentDetails/studentdetails.csv",
                "attendance": "Attendance"
            },
            "camera": {
                "default_index": 0,
                "capture_duration_seconds": 20,
                "images_per_student": 50
            },
            "recognition": {
                "confidence_threshold": 70
            },
            "logging": {
                "enabled": True,
                "level": "INFO"
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Obtener valor de configuración usando notación de punto
        
        Args:
            key_path: Ruta al valor (ej: "camera.default_index")
            default: Valor por defecto si no existe
            
        Returns:
            Valor de configuración o default
            
        Example:
            >>> config = ConfigManager()
            >>> threshold = config.get("recognition.confidence_threshold", 70)
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            self.logger.debug(f"Clave '{key_path}' no encontrada, usando default: {default}")
            return default
    
    def get_path(self, path_key: str) -> Path:
        """
        Obtener ruta como objeto Path
        
        Args:
            path_key: Clave de ruta en config.paths
            
        Returns:
            Path object
        """
        path_str = self.get(f"paths.{path_key}")
        if path_str:
            return Path(path_str)
        raise ValueError(f"Ruta '{path_key}' no encontrada en configuración")
    
    def reload(self):
        """Recargar configuración desde archivo"""
        self.logger.info("Recargando configuración...")
        self.load_config()


# Instancia singleton
_config_instance = None


def get_config() -> ConfigManager:
    """
    Obtener instancia del gestor de configuración
    
    Returns:
        ConfigManager singleton
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance
