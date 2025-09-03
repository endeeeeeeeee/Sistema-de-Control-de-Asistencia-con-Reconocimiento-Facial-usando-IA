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
import tkinter.font as font
import pyttsx3

# módulos del proyecto
import show_attendance
import takeImage
import trainImage
import automaticAttedance

# engine = pyttsx3.init()
# engine.say("¡Bienvenido a CLASS VISION!")
# engine.say("Por favor, explore sus opciones..")
# engine.runAndWait()


def text_to_speech(user_text):
    engine = pyttsx3.init()
    # Configurar idioma en español si está disponible
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
            engine.setProperty('voice', voice.id)
            break
    engine.say(user_text)
    engine.runAndWait()


haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimagelabel_path = (
    "./TrainingImageLabel/Trainner.yml"
)
trainimage_path = "/TrainingImage"
if not os.path.exists(trainimage_path):
    os.makedirs(trainimage_path)

studentdetail_path = (
    "./StudentDetails/studentdetails.csv"
)
attendance_path = "Attendance"

window = Tk()
window.title("CLASS VISION - Sistema de Asistencia")
window.geometry("1280x720")
window.state('zoomed')  # Maximizar ventana
dialog_title = "SALIR"
dialog_text = "¿Está seguro que desea cerrar?"

# Configuración del tema griego
GREEK_BG = "#F8F4E3"           # Beige claro
GREEK_CONTAINER = "#E6E1D4"     # Beige medio
GREEK_ACCENT = "#D4B889"        # Dorado griego
GREEK_DARK = "#A48B79"          # Marrón oscuro
GREEK_TEXT = "#4A4A4A"          # Gris oscuro
GREEK_LIGHT = "#F0EDE2"         # Casi blanco

window.configure(background=GREEK_BG)


# to destroy screen
def del_sc1():
    sc1.destroy()


# mensaje de error para nombre y número
def err_screen():
    global sc1
    sc1 = tk.Tk()
    sc1.geometry("500x150")
    sc1.iconbitmap("AMS.ico")
    sc1.title("¡Atención!")
    sc1.configure(background=GREEK_CONTAINER)
    sc1.resizable(0, 0)
    
    # Marco decorativo
    frame = tk.Frame(sc1, bg=GREEK_CONTAINER, relief=RIDGE, bd=3)
    frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
    
    tk.Label(
        frame,
        text="¡Se requiere Número de Matrícula y Nombre!",
        fg=GREEK_TEXT,
        bg=GREEK_CONTAINER,
        font=("Cinzel", 14, "bold"),
        wraplength=450
    ).pack(pady=20)
    
    tk.Button(
        frame,
        text="ENTENDIDO",
        command=del_sc1,
        fg=GREEK_TEXT,
        bg=GREEK_ACCENT,
        width=12,
        height=1,
        activebackground=GREEK_DARK,
        activeforeground=GREEK_LIGHT,
        font=("Cinzel", 12, "bold"),
        relief=RIDGE,
        bd=2
    ).pack(pady=10)

def testVal(inStr, acttyp):
    if acttyp == "1":  # insert
        if not inStr.isdigit():
            return False
    return True


logo = Image.open("UI_Image/0001.png")
logo = logo.resize((60, 57), Image.LANCZOS)
logo1 = ImageTk.PhotoImage(logo)

# Marco principal decorativo estilo griego
main_frame = tk.Frame(window, bg=GREEK_CONTAINER, relief=RIDGE, bd=5)
main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

# Encabezado con estilo griego
header_frame = tk.Frame(main_frame, bg=GREEK_CONTAINER, height=100)
header_frame.pack(fill=X, padx=10, pady=10)
header_frame.pack_propagate(False)

l1 = tk.Label(header_frame, image=logo1, bg=GREEK_CONTAINER)
l1.place(x=580, y=15)

# Título principal con fuente elegante
title_label = tk.Label(
    header_frame, 
    text="CLASS VISION", 
    bg=GREEK_CONTAINER, 
    fg=GREEK_TEXT, 
    font=("Cinzel", 42, "bold")
)
title_label.place(x=660, y=20)

# Subtítulo elegante
subtitle = tk.Label(
    main_frame,
    text="El vasto Olimpo de CLASS VISION le da la bienvenida",
    bg=GREEK_CONTAINER,
    fg=GREEK_DARK,
    bd=5,
    font=("Playfair Display", 18, "italic"),
)
subtitle.pack(pady=(0, 20))


# Marco para las opciones principales estilo griego
options_frame = tk.Frame(main_frame, bg=GREEK_CONTAINER)
options_frame.pack(expand=True, fill=BOTH, padx=20, pady=20)

# Cargar y redimensionar imágenes con mejor calidad
ri = Image.open("UI_Image/register.png")
ri = ri.resize((80, 80), Image.LANCZOS)
r = ImageTk.PhotoImage(ri)

ai = Image.open("UI_Image/attendance.png")
ai = ai.resize((80, 80), Image.LANCZOS)
a = ImageTk.PhotoImage(ai)

vi = Image.open("UI_Image/verifyy.png")
vi = vi.resize((80, 80), Image.LANCZOS)
v = ImageTk.PhotoImage(vi)

# Crear marcos para cada opción con estilo griego
def create_greek_option_frame(parent, image, title, subtitle, x_pos):
    frame = tk.Frame(parent, bg=GREEK_LIGHT, relief=RIDGE, bd=3, cursor="hand2")
    frame.place(x=x_pos, y=50, width=280, height=320)
    
    # Efecto hover
    def on_enter(e):
        frame.configure(bg=GREEK_ACCENT)
        title_lbl.configure(bg=GREEK_ACCENT)
        subtitle_lbl.configure(bg=GREEK_ACCENT)
    
    def on_leave(e):
        frame.configure(bg=GREEK_LIGHT)
        title_lbl.configure(bg=GREEK_LIGHT)
        subtitle_lbl.configure(bg=GREEK_LIGHT)
    
    frame.bind("<Enter>", on_enter)
    frame.bind("<Leave>", on_leave)
    
    # Imagen
    img_label = tk.Label(frame, image=image, bg=GREEK_LIGHT)
    img_label.pack(pady=(30, 20))
    img_label.bind("<Enter>", on_enter)
    img_label.bind("<Leave>", on_leave)
    
    # Título
    title_lbl = tk.Label(frame, text=title, bg=GREEK_LIGHT, fg=GREEK_TEXT, 
                        font=("Cinzel", 14, "bold"), wraplength=250)
    title_lbl.pack(pady=(0, 10))
    title_lbl.bind("<Enter>", on_enter)
    title_lbl.bind("<Leave>", on_leave)
    
    # Subtítulo
    subtitle_lbl = tk.Label(frame, text=subtitle, bg=GREEK_LIGHT, fg=GREEK_DARK, 
                           font=("Playfair Display", 10), wraplength=250)
    subtitle_lbl.pack(pady=(0, 20))
    subtitle_lbl.bind("<Enter>", on_enter)
    subtitle_lbl.bind("<Leave>", on_leave)
    
    return frame

# Crear las tres opciones principales
register_frame = create_greek_option_frame(
    options_frame, r, 
    "Inscribir un Nuevo Héroe", 
    "Registre el rostro divino de un nuevo estudiante en los anales del sistema",
    100
)

attendance_frame = create_greek_option_frame(
    options_frame, v,
    "Convocar el Verbo de los Héroes", 
    "Tome asistencia automática reconociendo los rostros de los estudiantes",
    400
)

view_frame = create_greek_option_frame(
    options_frame, a,
    "Consultar las Tablas del Destino", 
    "Visualice los registros de asistencia en formato de pergamino divino",
    700
)


def TakeImageUI():
    ImageUI = Tk()
    ImageUI.title("Inscribir Nuevo Héroe - CLASS VISION")
    ImageUI.geometry("900x600")
    ImageUI.configure(background=GREEK_BG)
    ImageUI.resizable(0, 0)
    
    # Marco principal estilo griego
    main_container = tk.Frame(ImageUI, bg=GREEK_CONTAINER, relief=RIDGE, bd=5)
    main_container.pack(fill=BOTH, expand=True, padx=20, pady=20)
    
    # Encabezado elegante
    header = tk.Frame(main_container, bg=GREEK_CONTAINER, height=80)
    header.pack(fill=X, padx=10, pady=10)
    header.pack_propagate(False)
    
    title_label = tk.Label(
        header, text="Inscribir un Nuevo Héroe", 
        bg=GREEK_CONTAINER, fg=GREEK_TEXT, 
        font=("Cinzel", 28, "bold")
    )
    title_label.pack(pady=15)

    # Descripción
    desc_label = tk.Label(
        main_container,
        text="Escriba las crónicas del estudiante para su inmortalidad en el sistema",
        bg=GREEK_CONTAINER,
        fg=GREEK_DARK,
        bd=5,
        font=("Playfair Display", 14, "italic"),
    )
    desc_label.pack(pady=(0, 30))

    # Marco para formulario
    form_frame = tk.Frame(main_container, bg=GREEK_CONTAINER)
    form_frame.pack(expand=True, padx=50)

    # Número de matrícula
    lbl1 = tk.Label(
        form_frame,
        text="Códice de Matrícula",
        width=18,
        height=2,
        bg=GREEK_LIGHT,
        fg=GREEK_TEXT,
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
        bg=GREEK_BG,
        fg=GREEK_TEXT,
        relief=RIDGE,
        font=("Playfair Display", 14),
        insertbackground=GREEK_TEXT
    )
    txt1.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
    txt1["validatecommand"] = (txt1.register(testVal), "%P", "%d")

    # Nombre
    lbl2 = tk.Label(
        form_frame,
        text="Nombre del Héroe",
        width=18,
        height=2,
        bg=GREEK_LIGHT,
        fg=GREEK_TEXT,
        bd=3,
        relief=RIDGE,
        font=("Cinzel", 12, "bold"),
    )
    lbl2.grid(row=1, column=0, padx=10, pady=15, sticky="ew")
    
    txt2 = tk.Entry(
        form_frame,
        width=20,
        bd=3,
        bg=GREEK_BG,
        fg=GREEK_TEXT,
        relief=RIDGE,
        font=("Playfair Display", 14),
        insertbackground=GREEK_TEXT
    )
    txt2.grid(row=1, column=1, padx=10, pady=15, sticky="ew")

    # Notificaciones
    lbl3 = tk.Label(
        form_frame,
        text="Oráculo",
        width=18,
        height=2,
        bg=GREEK_LIGHT,
        fg=GREEK_TEXT,
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
        bg=GREEK_BG,
        fg=GREEK_DARK,
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
            haarcasecade_path,
            trainimage_path,
            message,
            err_screen,
            text_to_speech,
        )
        txt1.delete(0, "end")
        txt2.delete(0, "end")

    def train_image():
        trainImage.TrainImage(
            haarcasecade_path,
            trainimage_path,
            trainimagelabel_path,
            message,
            text_to_speech,
        )

    # Marco para botones
    button_frame = tk.Frame(main_container, bg=GREEK_CONTAINER)
    button_frame.pack(pady=30)

    # Botón tomar imagen
    takeImg = tk.Button(
        button_frame,
        text="Invocar el Rostro",
        command=take_image,
        bd=3,
        font=("Cinzel", 14, "bold"),
        bg=GREEK_ACCENT,
        fg=GREEK_TEXT,
        height=2,
        width=18,
        relief=RIDGE,
        activebackground=GREEK_DARK,
        activeforeground=GREEK_LIGHT,
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
        bg=GREEK_ACCENT,
        fg=GREEK_TEXT,
        height=2,
        width=18,
        relief=RIDGE,
        activebackground=GREEK_DARK,
        activeforeground=GREEK_LIGHT,
        cursor="hand2"
    )
    trainImg.grid(row=0, column=1, padx=15)


# Eventos de clic para los marcos
def on_register_click(event):
    TakeImageUI()

def on_attendance_click(event):
    automaticAttedance.subjectChoose(text_to_speech)

def on_view_click(event):
    show_attendance.subjectchoose(text_to_speech)

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
button_frame = tk.Frame(main_frame, bg=GREEK_CONTAINER)
button_frame.pack(side=BOTTOM, pady=30)

def create_greek_button(parent, text, command, width=20):
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bd=3,
        font=("Cinzel", 14, "bold"),
        bg=GREEK_ACCENT,
        fg=GREEK_TEXT,
        height=2,
        width=width,
        relief=RIDGE,
        activebackground=GREEK_DARK,
        activeforeground=GREEK_LIGHT,
        cursor="hand2"
    )
    return btn

# Botón de salida
exit_btn = create_greek_button(button_frame, "ABANDONAR EL OLIMPO", quit)
exit_btn.pack()


window.mainloop()
