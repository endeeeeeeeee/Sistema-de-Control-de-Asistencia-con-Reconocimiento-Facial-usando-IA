# Sistema de Control de Asistencia con Reconocimiento Facial

Este es un sistema de control de asistencia que utiliza reconocimiento facial para identificar a los estudiantes y registrar su asistencia.

## Autores

- Itzan Valdivia
- Ender Rosales

## Características

*   **Registro de Estudiantes:** Registra nuevos estudiantes con su ID, nombre y tomando fotos para el entrenamiento del modelo.
*   **Entrenamiento de Modelo:** Entrena un modelo de reconocimiento facial con las imágenes de los estudiantes registrados.
*   **Toma de Asistencia Automática:** Inicia la cámara y reconoce a los estudiantes para marcar su asistencia automáticamente.
*   **Toma de Asistencia Manual:** Permite tomar asistencia manualmente en caso de que el reconocimiento facial falle.
*   **Visualización de Asistencia:** Muestra la asistencia registrada en un archivo CSV.

## Requisitos Previos

Asegúrate de tener Python instalado en tu sistema. Puedes descargarlo desde [python.org](https://www.python.org/downloads/).

## Instalación

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/endeeeeeeeee/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA.git
    cd "Sistema de Control de Asistencia con Reconocimiento Facial usando IA"
    ```

2.  **Crea un entorno virtual:**
    ```bash
    python -m venv .venv
    ```

3.  **Activa el entorno virtual:**
    *   En Windows:
        ```bash
        .venv\Scripts\activate
        ```
    *   En macOS y Linux:
        ```bash
        source .venv/bin/activate
        ```

4.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Uso

1.  **Registra Estudiantes:**
    Ejecuta `takeImage.py` para registrar nuevos estudiantes. Se te pedirá el ID y el nombre del estudiante. El sistema tomará 60 fotos del estudiante.

2.  **Entrena el Modelo:**
    Ejecuta `trainImage.py` para entrenar el modelo de reconocimiento facial con las imágenes tomadas en el paso anterior.

3.  **Toma de Asistencia:**
    *   **Automática:** Ejecuta `automaticAttedance.py` para iniciar la cámara y tomar asistencia automáticamente.
    *   **Manual:** Ejecuta `takemanually.py` para tomar asistencia manualmente.

4.  **Verifica la Asistencia:**
    Ejecuta `show_attendance.py` para ver los registros de asistencia.

## Contribuciones

Las contribuciones son bienvenidas. Si tienes alguna idea o sugerencia, por favor abre un "issue" o envía un "pull request".