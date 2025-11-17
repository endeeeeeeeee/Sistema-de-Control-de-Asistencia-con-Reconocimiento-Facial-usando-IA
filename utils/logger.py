"""
CLASS VISION - Sistema de Logging Profesional
Proporciona funcionalidades de logging con rotación de archivos y formato consistente
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional


class ClassVisionLogger:
    """Logger personalizado para CLASS VISION"""
    
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self.initialized = False
    
    def setup(self, config: dict = None):
        """
        Configurar el sistema de logging
        
        Args:
            config: Diccionario con configuración de logging
        """
        if self.initialized:
            return
        
        # Configuración por defecto
        if config is None:
            config = {
                'enabled': True,
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file_rotation': True,
                'max_bytes': 10485760,  # 10MB
                'backup_count': 5
            }
        
        if not config.get('enabled', True):
            return
        
        # Configurar el logger raíz
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, config.get('level', 'INFO')))
        
        # Formato
        formatter = logging.Formatter(
            config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler de consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # Handler de archivo con rotación
        if config.get('file_rotation', True):
            log_file = self.log_dir / f"classvision_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=config.get('max_bytes', 10485760),
                backupCount=config.get('backup_count', 5),
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        self.initialized = True
        
        # Log inicial
        logger = self.get_logger('ClassVision')
        logger.info("="*60)
        logger.info("CLASS VISION - Sistema de Asistencia Iniciado")
        logger.info(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Obtener un logger con el nombre especificado
        
        Args:
            name: Nombre del logger
            
        Returns:
            Logger configurado
        """
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        return self._loggers[name]


# Instancia singleton
_logger_instance = ClassVisionLogger()


def setup_logging(config: dict = None):
    """
    Configurar el sistema de logging
    
    Args:
        config: Diccionario con configuración de logging
    """
    _logger_instance.setup(config)


def get_logger(name: str) -> logging.Logger:
    """
    Obtener un logger con el nombre especificado
    
    Args:
        name: Nombre del módulo/clase
        
    Returns:
        Logger configurado
    
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Mensaje informativo")
        >>> logger.error("Error crítico")
    """
    return _logger_instance.get_logger(name)
