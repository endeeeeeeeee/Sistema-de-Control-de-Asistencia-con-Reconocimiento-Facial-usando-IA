# Configuración de CLASS VISION

Este directorio contiene los archivos de configuración del sistema.

## Archivos

- `default_config.json`: Configuración por defecto del sistema
- `local_config.json`: Configuración local (no se sube a Git, personalizable por usuario)

## Uso

Para personalizar la configuración, copia `default_config.json` a `local_config.json` y modifica los valores según necesites.

```bash
cp config/default_config.json config/local_config.json
```

El sistema cargará automáticamente `local_config.json` si existe, de lo contrario usará `default_config.json`.

## Parámetros Importantes

### Camera
- `capture_duration_seconds`: Tiempo de captura para asistencia (por defecto: 20 segundos)
- `images_per_student`: Número de fotos por estudiante durante registro (por defecto: 50)

### Recognition
- `confidence_threshold`: Umbral de confianza para reconocimiento (por defecto: 70)
  - Valores más bajos = más estricto
  - Valores más altos = más permisivo

### TTS (Text-to-Speech)
- `enabled`: Activar/desactivar síntesis de voz
- `language`: Idioma de la voz

### Logging
- `level`: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `enabled`: Activar/desactivar logs
