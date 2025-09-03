# Face Recognition Attendance System

This is an attendance management system that uses facial recognition to identify students and record their attendance.

## Authors

- Itzan Valdivia
- Ender Rosales

## Features

*   **Student Registration:** Register new students with their ID, name, and by taking photos for model training.
*   **Model Training:** Train a facial recognition model with the images of registered students.
*   **Automatic Attendance:** Starts the camera and recognizes students to mark their attendance automatically.
*   **Manual Attendance:** Allows taking attendance manually in case facial recognition fails.
*   **View Attendance:** Displays the recorded attendance from a CSV file.

## Prerequisites

Make sure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/endeeeeeeeee/Sistema-de-Control-de-Asistencia-con-Reconocimiento-Facial-usando-IA.git
    cd "Sistema de Control de Asistencia con Reconocimiento Facial usando IA"
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**
    *   On Windows:
        ```bash
        .venv\Scripts\activate
        ```
    *   On macOS and Linux:
        ```bash
        source .venv/bin/activate
        ```

4.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Register Students:**
    Run `takeImage.py` to register new students. You will be prompted for the student's ID and name. The system will take 60 pictures of the student.

2.  **Train the Model:**
    Run `trainImage.py` to train the facial recognition model with the images taken in the previous step.

3.  **Take Attendance:**
    *   **Automatic:** Run `automaticAttedance.py` to start the camera and take attendance automatically.
    *   **Manual:** Run `takemanually.py` to take attendance manually.

4.  **View Attendance:**
    Run `show_attendance.py` to view the attendance records.

## Contributing

Contributions are welcome. If you have any ideas or suggestions, please open an issue or submit a pull request.