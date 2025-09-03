import tkinter as tk
from tkinter import *
import os, cv2
import shutil
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import tkinter.ttk as tkk
import tkinter.font as font

# Configuración del tema griego
GREEK_BG = "#F8F4E3"           # Beige claro
GREEK_CONTAINER = "#E6E1D4"     # Beige medio
GREEK_ACCENT = "#D4B889"        # Dorado griego
GREEK_DARK = "#A48B79"          # Marrón oscuro
GREEK_TEXT = "#4A4A4A"          # Gris oscuro
GREEK_LIGHT = "#F0EDE2"         # Casi blanco

haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimagelabel_path = (
    "TrainingImageLabel\\Trainner.yml"
)
trainimage_path = "TrainingImage"
studentdetail_path = (
    "StudentDetails\\studentdetails.csv"
)
attendance_path = "Attendance"
# para elegir materia y llenar asistencia
def subjectChoose(text_to_speech):
    def FillAttendance():
        sub = tx.get()
        now = time.time()
        future = now + 20
        print(now)
        print(future)
        if sub == "":
            t = "¡Por favor ingrese el nombre de la materia!"
            text_to_speech(t)
        else:
            try:
                # Crear reconocedor LBPH de forma robusta
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
                            e_msg = f"OpenCV no tiene el módulo face/LBPH: {e}"
                            Notifica.configure(
                                text=e_msg,
                                bg=GREEK_CONTAINER,
                                fg=GREEK_TEXT,
                                width=45,
                                font=("Playfair Display", 12, "bold"),
                            )
                            Notifica.place(x=20, y=250)
                            text_to_speech("Error creando reconocedor. Asegúrate de tener opencv-contrib-python instalado.")
                            return
                try:
                    recognizer.read(trainimagelabel_path)
                except:
                    e = "Modelo no encontrado, por favor entrene el modelo primero"
                    Notifica.configure(
                        text=e,
                        bg=GREEK_CONTAINER,
                        fg=GREEK_TEXT,
                        width=35,
                        font=("Playfair Display", 13, "bold"),
                    )
                    Notifica.place(x=20, y=250)
                    text_to_speech(e)
                    return
                    
                facecasCade = cv2.CascadeClassifier(haarcasecade_path)
                # Validar que el archivo de estudiantes exista antes de continuar
                if not os.path.exists(studentdetail_path):
                    e = "Archivo 'StudentDetails/studentdetails.csv' no encontrado. Registre un estudiante primero."
                    Notifica.configure(
                        text=e,
                        bg=GREEK_CONTAINER,
                        fg=GREEK_TEXT,
                        width=35,
                        font=("Playfair Display", 12, "bold"),
                    )
                    Notifica.place(x=20, y=250)
                    text_to_speech(e)
                    return
                    
                df = pd.read_csv(studentdetail_path)
                # Intentar abrir la cámara con distintos backends en Windows
                cam = None
                for backend in [getattr(cv2, "CAP_DSHOW", 700), getattr(cv2, "CAP_MSMF", 1400), getattr(cv2, "CAP_ANY", 0)]:
                    try:
                        cam = cv2.VideoCapture(0, backend)
                    except Exception:
                        cam = cv2.VideoCapture(0)
                    if cam is not None and cam.isOpened():
                        break
                        
                if cam is None or not cam.isOpened():
                    e = "No se pudo abrir la cámara. Cierra otras apps que la usen y revisa permisos de Windows."
                    Notifica.configure(
                        text=e,
                        bg=GREEK_CONTAINER,
                        fg=GREEK_TEXT,
                        width=35,
                        font=("Playfair Display", 12, "bold"),
                    )
                    Notifica.place(x=20, y=250)
                    text_to_speech(e)
                    return
                    
                font_cv = cv2.FONT_HERSHEY_SIMPLEX
                col_names = ["Enrollment", "Name"]
                attendance = pd.DataFrame(columns=col_names)
                
                text_to_speech("Iniciando toma de asistencia. Posiciónense frente a la cámara.")
                
                while True:
                    ret, im = cam.read()
                    if not ret or im is None:
                        # No frame disponible todavía; continuar intentando
                        if time.time() > future:
                            break
                        continue
                    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                    faces = facecasCade.detectMultiScale(gray, 1.2, 5)
                    for (x, y, w, h) in faces:
                        global Id

                        Id, conf = recognizer.predict(gray[y : y + h, x : x + w])
                        if conf < 70:
                            print(conf)
                            global Subject
                            global aa
                            global date
                            global timeStamp
                            Subject = tx.get()
                            ts = time.time()
                            date = datetime.datetime.fromtimestamp(ts).strftime(
                                "%Y-%m-%d"
                            )
                            timeStamp = datetime.datetime.fromtimestamp(ts).strftime(
                                "%H:%M:%S"
                            )
                            aa = df.loc[df["Enrollment"] == Id]["Name"].values
                            global tt
                            tt = str(Id) + "-" + str(aa[0]) if len(aa) > 0 else str(Id)
                            attendance.loc[len(attendance)] = [
                                Id,
                                aa[0] if len(aa) > 0 else "Desconocido",
                            ]
                            cv2.rectangle(im, (x, y), (x + w, y + h), (212, 184, 137), 4)
                            cv2.putText(
                                im, str(tt), (x + h, y), font_cv, 1, (74, 74, 74), 4
                            )
                        else:
                            Id = "Desconocido"
                            tt = str(Id)
                            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 25, 255), 7)
                            cv2.putText(
                                im, str(tt), (x + h, y), font_cv, 1, (0, 25, 255), 4
                            )
                    if time.time() > future:
                        break

                    attendance = attendance.drop_duplicates(
                        ["Enrollment"], keep="first"
                    )
                    cv2.imshow("Registrando Asistencia... Presione ESC para salir", im)
                    key = cv2.waitKey(30) & 0xFF
                    if key == 27:
                        break

                ts = time.time()
                print(aa)
                attendance[date] = 1
                date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                Hour, Minute, Second = timeStamp.split(":")
                
                path = os.path.join(attendance_path, Subject)
                if not os.path.exists(path):
                    os.makedirs(path)
                fileName = (
                    f"{path}/"
                    + Subject
                    + "_"
                    + date
                    + "_"
                    + Hour
                    + "-"
                    + Minute
                    + "-"
                    + Second
                    + ".csv"
                )
                attendance = attendance.drop_duplicates(["Enrollment"], keep="first")
                print(attendance)
                attendance.to_csv(fileName, index=False)

                m = "Asistencia registrada exitosamente para " + Subject
                Notifica.configure(
                    text=m,
                    bg=GREEK_CONTAINER,
                    fg=GREEK_TEXT,
                    width=35,
                    relief=RIDGE,
                    bd=3,
                    font=("Playfair Display", 13, "bold"),
                )
                text_to_speech(m)

                Notifica.place(x=20, y=250)

                cam.release()
                cv2.destroyAllWindows()

                # Mostrar resultados
                import csv
                import tkinter

                root = tkinter.Tk()
                root.title("Asistencia de " + Subject)
                root.configure(background=GREEK_CONTAINER)
                root.geometry("600x400")
                
                # Marco principal
                main_frame = tkinter.Frame(root, bg=GREEK_CONTAINER, relief=RIDGE, bd=3)
                main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
                
                # Título
                title_label = tkinter.Label(
                    main_frame,
                    text=f"Pergamino de Asistencia - {Subject}",
                    bg=GREEK_CONTAINER,
                    fg=GREEK_TEXT,
                    font=("Cinzel", 16, "bold")
                )
                title_label.pack(pady=10)
                
                # Marco para la tabla
                table_frame = tkinter.Frame(main_frame, bg=GREEK_LIGHT, relief=RIDGE, bd=2)
                table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
                
                cs = fileName
                print(cs)
                with open(cs, newline="") as file:
                    reader = csv.reader(file)
                    r = 0

                    for col in reader:
                        c = 0
                        for row in col:
                            label = tkinter.Label(
                                table_frame,
                                width=15,
                                height=1,
                                fg=GREEK_TEXT,
                                font=("Playfair Display", 12, "bold"),
                                bg=GREEK_LIGHT if r == 0 else GREEK_BG,
                                text=row,
                                relief=tkinter.RIDGE,
                                bd=1
                            )
                            label.grid(row=r, column=c, padx=1, pady=1)
                            c += 1
                        r += 1
                root.mainloop()
                print(attendance)
            except Exception as ex:
                f = "No se encontró rostro para la asistencia: " + str(ex)
                text_to_speech("No se detectaron rostros válidos")
                Notifica.configure(
                    text=f,
                    bg=GREEK_CONTAINER,
                    fg=GREEK_TEXT,
                    width=40,
                    font=("Playfair Display", 11, "bold"),
                )
                Notifica.place(x=20, y=250)
                cv2.destroyAllWindows()

    ###ventana es el marco para elegir materia
    subject = Tk()
    subject.title("Convocar el Verbo de los Héroes")
    subject.geometry("700x400")
    subject.resizable(0, 0)
    subject.configure(background=GREEK_BG)
    
    # Marco principal estilo griego
    main_container = tk.Frame(subject, bg=GREEK_CONTAINER, relief=RIDGE, bd=5)
    main_container.pack(fill=BOTH, expand=True, padx=20, pady=20)
    
    # Encabezado
    header_frame = tk.Frame(main_container, bg=GREEK_CONTAINER, height=80)
    header_frame.pack(fill=X, padx=10, pady=10)
    header_frame.pack_propagate(False)
    
    titl = tk.Label(
        header_frame,
        text="Convocar el Verbo de los Héroes",
        bg=GREEK_CONTAINER,
        fg=GREEK_TEXT,
        font=("Cinzel", 22, "bold"),
    )
    titl.pack(pady=15)
    
    # Descripción
    desc_label = tk.Label(
        main_container,
        text="Proclame el nombre del saber para convocar a los estudiantes",
        bg=GREEK_CONTAINER,
        fg=GREEK_DARK,
        font=("Playfair Display", 14, "italic"),
    )
    desc_label.pack(pady=(0, 20))
    
    # Etiqueta de notificación
    Notifica = tk.Label(
        main_container,
        text="",
        bg=GREEK_CONTAINER,
        fg=GREEK_TEXT,
        width=50,
        height=3,
        font=("Playfair Display", 12, "bold"),
        wraplength=400
    )

    def Attf():
        sub = tx.get()
        if sub == "":
            t = "¡Por favor ingrese el nombre de la materia!"
            text_to_speech(t)
        else:
            folder = os.path.join("Attendance", sub)
            if not os.path.exists(folder):
                os.makedirs(folder)
                msg = f"Pergamino creado: Attendance\\{sub}. Aún no hay registros."
                Notifica.configure(text=msg, bg=GREEK_CONTAINER, fg=GREEK_DARK, width=50, font=("Playfair Display", 11, "bold"))
                Notifica.place(x=50, y=270)
                text_to_speech(msg)
                return
            try:
                os.startfile(folder)
            except FileNotFoundError:
                msg = f"No se pudo abrir la carpeta: {folder}"
                Notifica.configure(text=msg, bg=GREEK_CONTAINER, fg=GREEK_TEXT, width=50, font=("Playfair Display", 11, "bold"))
                Notifica.place(x=50, y=270)
                text_to_speech(msg)

    # Marco para formulario
    form_frame = tk.Frame(main_container, bg=GREEK_CONTAINER)
    form_frame.pack(pady=20)

    sub_label = tk.Label(
        form_frame,
        text="Materia",
        width=12,
        height=2,
        bg=GREEK_LIGHT,
        fg=GREEK_TEXT,
        bd=3,
        relief=RIDGE,
        font=("Cinzel", 14, "bold"),
    )
    sub_label.grid(row=0, column=0, padx=10, pady=10)

    tx = tk.Entry(
        form_frame,
        width=18,
        bd=3,
        bg=GREEK_BG,
        fg=GREEK_TEXT,
        relief=RIDGE,
        font=("Playfair Display", 16, "bold"),
        insertbackground=GREEK_TEXT
    )
    tx.grid(row=0, column=1, padx=10, pady=10)

    # Marco para botones
    button_frame = tk.Frame(main_container, bg=GREEK_CONTAINER)
    button_frame.pack(pady=20)

    fill_a = tk.Button(
        button_frame,
        text="Registrar Asistencia",
        command=FillAttendance,
        bd=3,
        font=("Cinzel", 12, "bold"),
        bg=GREEK_ACCENT,
        fg=GREEK_TEXT,
        height=2,
        width=18,
        relief=RIDGE,
        activebackground=GREEK_DARK,
        activeforeground=GREEK_LIGHT,
        cursor="hand2"
    )
    fill_a.grid(row=0, column=0, padx=10)

    attf = tk.Button(
        button_frame,
        text="Ver Pergaminos",
        command=Attf,
        bd=3,
        font=("Cinzel", 12, "bold"),
        bg=GREEK_ACCENT,
        fg=GREEK_TEXT,
        height=2,
        width=15,
        relief=RIDGE,
        activebackground=GREEK_DARK,
        activeforeground=GREEK_LIGHT,
        cursor="hand2"
    )
    attf.grid(row=0, column=1, padx=10)
    
    subject.mainloop()
