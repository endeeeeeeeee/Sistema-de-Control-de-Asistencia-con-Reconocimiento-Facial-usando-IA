import csv
import os, cv2
import numpy as np
import pandas as pd
import datetime
import time
from PIL import ImageTk, Image


# Entrenar Imagen
def TrainImage(haarcasecade_path, trainimage_path, trainimagelabel_path, message,text_to_speech):
    # Crear reconocedor LBPH de forma robusta para diferentes versiones de OpenCV
    recognizer = None
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
    except Exception:
        try:
            recognizer = cv2.face.LBPHFaceRecognizer.create()
        except Exception:
            try:
                recognizer = cv2.face.createLBPHFaceRecognizer()
            except Exception as e:
                error_msg = f"OpenCV no tiene el módulo face/LBPH: {e}"
                message.configure(text=error_msg)
                text_to_speech("Error creando el reconocedor. Verifica que opencv-contrib-python esté instalado.")
                return
    
    message.configure(text="Iniciando entrenamiento del modelo...")
    text_to_speech("Los dioses están procesando el conocimiento facial...")
    
    detector = cv2.CascadeClassifier(haarcasecade_path)
    faces, Id = getImagesAndLables(trainimage_path)
    
    if len(faces) == 0:
        error_msg = "No se encontraron imágenes para entrenar. Registre algunos estudiantes primero."
        message.configure(text=error_msg)
        text_to_speech(error_msg)
        return
    
    recognizer.train(faces, np.array(Id))
    recognizer.save(trainimagelabel_path)
    res = "Modelo entrenado exitosamente con " + str(len(set(Id))) + " héroes registrados"
    message.configure(text=res)
    text_to_speech("El conocimiento divino ha sido grabado en los anales del sistema.")


def getImagesAndLables(path):
    if not os.path.exists(path):
        return [], []
        
    # imagePath = [os.path.join(path, f) for d in os.listdir(path) for f in d]
    newdir = [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    imagePath = []
    
    for directory in newdir:
        for f in os.listdir(directory):
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                imagePath.append(os.path.join(directory, f))
    
    faces = []
    Ids = []
    for imagePath_single in imagePath:
        try:
            pilImage = Image.open(imagePath_single).convert("L")
            imageNp = np.array(pilImage, "uint8")
            Id = int(os.path.split(imagePath_single)[-1].split("_")[1])
            faces.append(imageNp)
            Ids.append(Id)
        except Exception as e:
            print(f"Error procesando imagen {imagePath_single}: {e}")
            continue
    return faces, Ids
