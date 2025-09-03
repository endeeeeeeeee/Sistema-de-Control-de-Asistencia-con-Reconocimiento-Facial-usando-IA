import csv
import os, cv2
import numpy as np
import pandas as pd
import datetime
import time



# tomar imagen del usuario
def TakeImage(l1, l2, haarcasecade_path, trainimage_path, message, err_screen,text_to_speech):
    if (l1 == "") and (l2==""):
        t='Por favor ingrese su Número de Matrícula y Nombre.'
        text_to_speech(t)
    elif l1=='':
        t='Por favor ingrese su Número de Matrícula.'
        text_to_speech(t)
    elif l2 == "":
        t='Por favor ingrese su Nombre.'
        text_to_speech(t)
    else:
        cam = None
        try:
            cam = cv2.VideoCapture(0)
            if not cam.isOpened():
                text_to_speech('No se pudo abrir la cámara.')
                return
            detector = cv2.CascadeClassifier(haarcasecade_path)
            Enrollment = l1
            Name = l2
            sampleNum = 0
            directory = Enrollment + "_" + Name
            path = os.path.join(trainimage_path, directory)
            os.mkdir(path)
            
            text_to_speech('Posicione su rostro frente a la cámara. Presione Q o Escape para terminar.')
            
            while True:
                ret, img = cam.read()
                if not ret:
                    text_to_speech('No se pudo leer la imagen de la cámara.')
                    break
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (212, 184, 137), 3)
                    sampleNum = sampleNum + 1
                    cv2.imwrite(
                        f"{path}/"
                        + Name
                        + "_"
                        + Enrollment
                        + "_"
                        + str(sampleNum)
                        + ".jpg",
                        gray[y : y + h, x : x + w],
                    )
                    # Mostrar contador en la imagen
                    cv2.putText(img, f'Capturando: {sampleNum}/50', (x, y-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.8, (212, 184, 137), 2)
                
                cv2.imshow("Capturando Rostro del Héroe - Presione Q para salir", img)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == 27:  # 27 es ESC
                    break
                elif sampleNum >= 50:
                    text_to_speech('Captura completada. 50 imágenes guardadas exitosamente.')
                    break
            cam.release()
            cv2.destroyAllWindows()
            row = [Enrollment, Name]
            with open(
                "StudentDetails/studentdetails.csv",
                "a+",
            ) as csvFile:
                writer = csv.writer(csvFile, delimiter=",")
                writer.writerow(row)
                csvFile.close()
            res = "Imágenes guardadas para Matrícula: " + Enrollment + " Nombre: " + Name
            message.configure(text=res)
            text_to_speech(res)
        except FileExistsError as F:
            F = "Los datos del estudiante ya existen en el sistema"
            message.configure(text=F)
            text_to_speech(F)
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            message.configure(text=error_msg)
            text_to_speech(error_msg)
        finally:
            if cam is not None:
                cam.release()
            cv2.destroyAllWindows()
