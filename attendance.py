import tkinter as tk
from tkinter import *
import os
import cv2
import shutil
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import tkinter.font as font
from pathlib import Path

# módulos del proyecto
import show_attendance
import takeImage
import trainImage
import automaticAttedance

# Configuración de rutas
BASE_DIR = Path(__file__).parent
HAARCASCADE_PATH = BASE_DIR / "haarcascade_frontalface_default.xml"
TRAINING_LABEL_PATH = BASE_DIR / "TrainingImageLabel/Trainner.yml"
TRAINING_IMAGE_PATH = BASE_DIR / "TrainingImage"
STUDENT_DETAILS_PATH = BASE_DIR / "StudentDetails/studentdetails.csv"
ATTENDANCE_PATH = BASE_DIR / "Attendance"

# Crear directorios necesarios
TRAINING_IMAGE_PATH.mkdir(exist_ok=True)
(BASE_DIR / "TrainingImageLabel").mkdir(exist_ok=True)
(BASE_DIR / "StudentDetails").mkdir(exist_ok=True)
(BASE_DIR / "Attendance").mkdir(exist_ok=True)
(BASE_DIR / "UI_Image").mkdir(exist_ok=True)

# Configuración del tema griego
THEME = {
    'BG': "#F8F4E3",           # Beige claro
    'CONTAINER': "#E6E1D4",    # Beige medio  
    'ACCENT': "#D4B889",       # Dorado griego
    'DARK': "#A48B79",         # Marrón oscuro
    'TEXT': "#4A4A4A",         # Gris oscuro
    'LIGHT': "#F0EDE2"         # Casi blanco
}

class ClassVisionApp:
    def __init__(self):
        self.window = Tk()
        self.setup_window()
        self.setup_tts()
        self.load_images()  # Nuevo método
        self.create_main_interface()
    
    def load_images(self):
        # Cargar y almacenar imágenes como atributos de la clase
        self.logo = Image.open("UI_Image/0001.png")
        self.logo = self.logo.resize((60, 57), Image.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(self.logo)

        # Cargar y redimensionar imágenes con mejor calidad
        ri = Image.open("UI_Image/register.png")
        ri = ri.resize((80, 80), Image.LANCZOS)
        self.register_photo = ImageTk.PhotoImage(ri)

        ai = Image.open("UI_Image/attendance.png")
        ai = ai.resize((80, 80), Image.LANCZOS)
        self.attendance_photo = ImageTk.PhotoImage(ai)

        vi = Image.open("UI_Image/verifyy.png")
        vi = vi.resize((80, 80), Image.LANCZOS)
        self.verify_photo = ImageTk.PhotoImage(vi)

    def setup_window(self):
        self.window.title("CLASS VISION - Sistema de Asistencia")
        self.window.geometry("1280x720")
        self.window.state('zoomed')
        self.window.configure(background=THEME['BG'])
    
    def setup_tts(self):
        self.engine = None
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            print("Motor TTS iniciado correctamente")
        except Exception as e:
            print(f"No se pudo inicializar el motor TTS: {str(e)}")
            print("El sistema funcionará sin soporte de voz")
    
    def text_to_speech(self, text):
        print(f"Mensaje del sistema: {text}")  # Siempre mostrar en consola
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Error al reproducir audio: {str(e)}")

    def create_greek_style_button(self, parent, text, command, width=20):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bd=3,
            font=("Cinzel", 14, "bold"),
            bg=THEME['ACCENT'],
            fg=THEME['TEXT'],
            height=2,
            width=width,
            relief=RIDGE,
            activebackground=THEME['DARK'],
            activeforeground=THEME['LIGHT'],
            cursor="hand2"
        )

    def create_greek_option_frame(self, parent, image, title, subtitle, x_pos):
        frame = tk.Frame(parent, bg=THEME['LIGHT'], relief=RIDGE, bd=3, cursor="hand2")
        frame.place(x=x_pos, y=50, width=280, height=320)
        
        def on_enter(e):
            for widget in frame.winfo_children():
                widget.configure(bg=THEME['ACCENT'])
            frame.configure(bg=THEME['ACCENT'])
            
        def on_leave(e):
            for widget in frame.winfo_children():
                widget.configure(bg=THEME['LIGHT'])
            frame.configure(bg=THEME['LIGHT'])
        
        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)
        
        # Imagen
        img_label = tk.Label(frame, image=image, bg=THEME['LIGHT'])
        img_label.pack(pady=(30, 20))
        img_label.bind("<Enter>", on_enter)
        img_label.bind("<Leave>", on_leave)
        
        # Título
        title_lbl = tk.Label(frame, text=title, bg=THEME['LIGHT'], fg=THEME['TEXT'], 
                        font=("Cinzel", 14, "bold"), wraplength=250)
        title_lbl.pack(pady=(0, 10))
        title_lbl.bind("<Enter>", on_enter)
        title_lbl.bind("<Leave>", on_leave)
        
        # Subtítulo
        subtitle_lbl = tk.Label(frame, text=subtitle, bg=THEME['LIGHT'], fg=THEME['DARK'], 
                           font=("Playfair Display", 10), wraplength=250)
        subtitle_lbl.pack(pady=(0, 20))
        subtitle_lbl.bind("<Enter>", on_enter)
        subtitle_lbl.bind("<Leave>", on_leave)
        
        return frame

    def create_main_interface(self):
        # Crear marco principal
        main_frame = tk.Frame(self.window, bg=THEME['CONTAINER'], relief=RIDGE, bd=5)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Crear encabezado
        header_frame = tk.Frame(main_frame, bg=THEME['CONTAINER'], height=100)
        header_frame.pack(fill=X, padx=10, pady=10)
        header_frame.pack_propagate(False)

        l1 = tk.Label(header_frame, image=self.logo_photo, bg=THEME['CONTAINER'])
        l1.place(x=580, y=15)

        title_label = tk.Label(
            header_frame, 
            text="CLASS VISION", 
            bg=THEME['CONTAINER'], 
            fg=THEME['TEXT'], 
            font=("Cinzel", 42, "bold")
        )
        title_label.place(x=660, y=20)

        # Subtítulo elegante
        subtitle = tk.Label(
            main_frame,
            text="El vasto Olimpo de CLASS VISION le da la bienvenida",
            bg=THEME['CONTAINER'],
            fg=THEME['DARK'],
            bd=5,
            font=("Playfair Display", 18, "italic"),
        )
        subtitle.pack(pady=(0, 20))

        # Marco para las opciones principales estilo griego
        options_frame = tk.Frame(main_frame, bg=THEME['CONTAINER'])
        options_frame.pack(expand=True, fill=BOTH, padx=20, pady=20)

        # Crear marcos para cada opción con estilo griego
        register_frame = self.create_greek_option_frame(
            options_frame, self.register_photo, 
            "Inscribir un Nuevo Héroe", 
            "Registre el rostro divino de un nuevo estudiante en los anales del sistema",
            100
        )

        attendance_frame = self.create_greek_option_frame(
            options_frame, self.verify_photo,
            "Convocar el Verbo de los Héroes", 
            "Tome asistencia automática reconociendo los rostros de los estudiantes",
            400
        )

        view_frame = self.create_greek_option_frame(
            options_frame, self.attendance_photo,
            "Consultar las Tablas del Destino", 
            "Visualice los registros de asistencia en formato de pergamino divino",
            700
        )


        def TakeImageUI():
            ImageUI = Tk()
            ImageUI.title("Inscribir Nuevo Héroe - CLASS VISION")
            ImageUI.geometry("900x600")
            ImageUI.configure(background=THEME['BG'])
            ImageUI.resizable(0, 0)
            
            # Marco principal estilo griego
            main_container = tk.Frame(ImageUI, bg=THEME['CONTAINER'], relief=RIDGE, bd=5)
            main_container.pack(fill=BOTH, expand=True, padx=20, pady=20)
            
            # Encabezado elegante
            header = tk.Frame(main_container, bg=THEME['CONTAINER'], height=80)
            header.pack(fill=X, padx=10, pady=10)
            header.pack_propagate(False)
            
            title_label = tk.Label(
                header, text="Inscribir un Nuevo Héroe", 
                bg=THEME['CONTAINER'], fg=THEME['TEXT'], 
                font=("Cinzel", 28, "bold")
            )
            title_label.pack(pady=15)

            # Descripción
            desc_label = tk.Label(
                main_container,
                text="Escriba las crónicas del estudiante para su inmortalidad en el sistema",
                bg=THEME['CONTAINER'],
                fg=THEME['DARK'],
                bd=5,
                font=("Playfair Display", 14, "italic"),
            )
            desc_label.pack(pady=(0, 30))

            # Marco para formulario
            form_frame = tk.Frame(main_container, bg=THEME['CONTAINER'])
            form_frame.pack(expand=True, padx=50)

            # Número de matrícula
            lbl1 = tk.Label(
                form_frame,
                text="Códice de Matrícula",
                width=18,
                height=2,
                bg=THEME['LIGHT'],
                fg=THEME['TEXT'],
                bd=3,
                relief=RIDGE,
                font=("Cinzel", 12, "bold"),
            )
            lbl1.grid(row=0, column=0, padx=10, pady=15, sticky="ew")
            
            txt1 = tk.Entry(
                form_frame,
                width=20,
                bd=3,
                validate="key",
                bg=THEME['BG'],
                fg=THEME['TEXT'],
                relief=RIDGE,
                font=("Playfair Display", 14),
                insertbackground=THEME['TEXT']
            )
            txt1.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
            txt1["validatecommand"] = (txt1.register(self.testVal), "%P", "%d")

            # Nombre
            lbl2 = tk.Label(
                form_frame,
                text="Nombre del Héroe",
                width=18,
                height=2,
                bg=THEME['LIGHT'],
                fg=THEME['TEXT'],
                bd=3,
                relief=RIDGE,
                font=("Cinzel", 12, "bold"),
            )
            lbl2.grid(row=1, column=0, padx=10, pady=15, sticky="ew")
            
            txt2 = tk.Entry(
                form_frame,
                width=20,
                bd=3,
                bg=THEME['BG'],
                fg=THEME['TEXT'],
                relief=RIDGE,
                font=("Playfair Display", 14),
                insertbackground=THEME['TEXT']
            )
            txt2.grid(row=1, column=1, padx=10, pady=15, sticky="ew")

            # Notificaciones
            lbl3 = tk.Label(
                form_frame,
                text="Oráculo",
                width=18,
                height=2,
                bg=THEME['LIGHT'],
                fg=THEME['TEXT'],
                bd=3,
                relief=RIDGE,
                font=("Cinzel", 12, "bold"),
            )
            lbl3.grid(row=2, column=0, padx=10, pady=15, sticky="new")

            message = tk.Label(
                form_frame,
                text="Los dioses aguardan su comando...",
                width=35,
                height=3,
                bd=3,
                bg=THEME['BG'],
                fg=THEME['DARK'],
                relief=RIDGE,
                font=("Playfair Display", 11),
                wraplength=300,
                justify=LEFT
            )
            message.grid(row=2, column=1, padx=10, pady=15, sticky="ew")

            # Configurar columnas para que se expandan
            form_frame.columnconfigure(0, weight=1)
            form_frame.columnconfigure(1, weight=2)

            def take_image():
                l1 = txt1.get()
                l2 = txt2.get()
                takeImage.TakeImage(
                    l1,
                    l2,
                    HAARCASCADE_PATH,
                    TRAINING_IMAGE_PATH,
                    message,
                    self.err_screen,
                    self.text_to_speech,
                )
                txt1.delete(0, "end")
                txt2.delete(0, "end")

            def train_image():
                trainImage.TrainImage(
                    HAARCASCADE_PATH,
                    TRAINING_IMAGE_PATH,
                    TRAINING_LABEL_PATH,
                    message,
                    self.text_to_speech,
                )

            # Marco para botones
            button_frame = tk.Frame(main_container, bg=THEME['CONTAINER'])
            button_frame.pack(pady=30)

            # Botón tomar imagen
            takeImg = tk.Button(
                button_frame,
                text="Invocar el Rostro",
                command=take_image,
                bd=3,
                font=("Cinzel", 14, "bold"),
                bg=THEME['ACCENT'],
                fg=THEME['TEXT'],
                height=2,
                width=18,
                relief=RIDGE,
                activebackground=THEME['DARK'],
                activeforeground=THEME['LIGHT'],
                cursor="hand2"
            )
            takeImg.grid(row=0, column=0, padx=15)

            # Botón entrenar imagen
            trainImg = tk.Button(
                button_frame,
                text="Grabar el Conocimiento",
                command=train_image,
                bd=3,
                font=("Cinzel", 14, "bold"),
                bg=THEME['ACCENT'],
                fg=THEME['TEXT'],
                height=2,
                width=18,
                relief=RIDGE,
                activebackground=THEME['DARK'],
                activeforeground=THEME['LIGHT'],
                cursor="hand2"
            )
            trainImg.grid(row=0, column=1, padx=15)


        # Eventos de clic para los marcos
        def on_register_click(event):
            TakeImageUI()

        def on_attendance_click(event):
            automaticAttedance.subjectChoose(self.text_to_speech)

        def on_view_click(event):
            show_attendance.subjectchoose(self.text_to_speech)

        # Bindear eventos de clic
        register_frame.bind("<Button-1>", on_register_click)
        attendance_frame.bind("<Button-1>", on_attendance_click) 
        view_frame.bind("<Button-1>", on_view_click)

        # Hacer que todos los widgets dentro de los marcos también respondan al clic
        def bind_all_children(widget, event, command):
            widget.bind(event, command)
            for child in widget.winfo_children():
                bind_all_children(child, event, command)

        bind_all_children(register_frame, "<Button-1>", on_register_click)
        bind_all_children(attendance_frame, "<Button-1>", on_attendance_click)
        bind_all_children(view_frame, "<Button-1>", on_view_click)

        # Botones principales estilo griego
        button_frame = tk.Frame(main_frame, bg=THEME['CONTAINER'])
        button_frame.pack(side=BOTTOM, pady=30)

        exit_btn = self.create_greek_style_button(button_frame, "ABANDONAR EL OLIMPO", self.window.quit)
        exit_btn.pack()

    def run(self):
        self.window.mainloop()

    def testVal(self, inStr, acttyp):
        if acttyp == "1":  # insert
            if not inStr.isdigit():
                return False
        return True
    
    def err_screen(self):
        sc1 = tk.Tk()
        sc1.geometry("500x150")
        sc1.title("¡Atención!")
        sc1.configure(background=THEME['CONTAINER'])
        sc1.resizable(0, 0)
        
        # Marco decorativo
        frame = tk.Frame(sc1, bg=THEME['CONTAINER'], relief=RIDGE, bd=3)
        frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(
            frame,
            text="¡Se requiere Número de Matrícula y Nombre!",
            fg=THEME['TEXT'],
            bg=THEME['CONTAINER'],
            font=("Cinzel", 14, "bold"),
            wraplength=450
        ).pack(pady=20)
        
        def del_sc1():
            sc1.destroy()
        
        tk.Button(
            frame,
            text="ENTENDIDO",
            command=del_sc1,
            fg=THEME['TEXT'],
            bg=THEME['ACCENT'],
            width=12,
            height=1,
            activebackground=THEME['DARK'],
            activeforeground=THEME['LIGHT'],
            font=("Cinzel", 12, "bold"),
            relief=RIDGE,
            bd=2
        ).pack(pady=10)

if __name__ == "__main__":
    app = ClassVisionApp()
    app.run()
