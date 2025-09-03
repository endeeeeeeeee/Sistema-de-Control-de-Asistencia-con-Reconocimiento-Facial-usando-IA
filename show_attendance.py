import pandas as pd
from glob import glob
import os
import tkinter
import csv
import tkinter as tk
from tkinter import *

# Configuración del tema griego
GREEK_BG = "#F8F4E3"           # Beige claro
GREEK_CONTAINER = "#E6E1D4"     # Beige medio
GREEK_ACCENT = "#D4B889"        # Dorado griego
GREEK_DARK = "#A48B79"          # Marrón oscuro
GREEK_TEXT = "#4A4A4A"          # Gris oscuro
GREEK_LIGHT = "#F0EDE2"         # Casi blanco

def subjectchoose(text_to_speech):
    def calculate_attendance():
        Subject = tx.get()
        if Subject=="":
            t='Por favor ingrese el nombre de la materia.'
            text_to_speech(t)
            return
        path = os.path.join("Attendance", Subject)
        if not os.path.exists(path):
            # Crear la carpeta del sujeto si no existe y notificar
            os.makedirs(path)
            msg = f"No existen registros para '{Subject}'. Pergamino creado en Attendance\\{Subject}."
            Notifica.configure(text=msg, bg=GREEK_CONTAINER, fg=GREEK_DARK, width=50, font=("Playfair Display", 11, "bold"))
            Notifica.place(x=50, y=270)
            text_to_speech(msg)
            return
        filenames = glob(os.path.join(path, f"{Subject}*.csv"))
        if len(filenames) == 0:
            msg = f"No se encontraron pergaminos de asistencia para '{Subject}'."
            Notifica.configure(text=msg, bg=GREEK_CONTAINER, fg=GREEK_DARK, width=50, font=("Playfair Display", 11, "bold"))
            Notifica.place(x=50, y=270)
            text_to_speech(msg)
            return
        df = [pd.read_csv(f) for f in filenames]
        newdf = df[0]
        for i in range(1, len(df)):
            newdf = newdf.merge(df[i], how="outer")
        newdf.fillna(0, inplace=True)
        newdf["Asistencia"] = 0
        for i in range(len(newdf)):
            newdf["Asistencia"].iloc[i] = str(int(round(newdf.iloc[i, 2:-1].mean() * 100)))+'%'
        newdf.to_csv(os.path.join(path, "attendance.csv"), index=False)

        # Mostrar resultados con estilo griego
        root = tkinter.Tk()
        root.title("Tablas del Destino - " + Subject)
        root.configure(background=GREEK_BG)
        root.geometry("800x500")
        
        # Marco principal
        main_frame = tkinter.Frame(root, bg=GREEK_CONTAINER, relief=RIDGE, bd=5)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Título elegante
        title_label = tkinter.Label(
            main_frame,
            text=f"Pergamino de Asistencia - {Subject}",
            bg=GREEK_CONTAINER,
            fg=GREEK_TEXT,
            font=("Cinzel", 18, "bold")
        )
        title_label.pack(pady=15)
        
        # Subtítulo
        subtitle_label = tkinter.Label(
            main_frame,
            text="Los nombres inmortalizados en las tablas del destino",
            bg=GREEK_CONTAINER,
            fg=GREEK_DARK,
            font=("Playfair Display", 12, "italic")
        )
        subtitle_label.pack(pady=(0, 15))
        
        # Marco para la tabla con scroll
        table_container = tkinter.Frame(main_frame, bg=GREEK_CONTAINER)
        table_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Canvas para scroll
        canvas = tkinter.Canvas(table_container, bg=GREEK_LIGHT)
        scrollbar = tkinter.Scrollbar(table_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tkinter.Frame(canvas, bg=GREEK_LIGHT)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        cs = os.path.join(path, "attendance.csv")
        with open(cs, encoding='utf-8') as file:
            reader = csv.reader(file)
            r = 0
            for col in reader:
                c = 0
                for row in col:
                    # Estilo especial para encabezados
                    if r == 0:
                        label = tkinter.Label(
                            scrollable_frame,
                            width=15,
                            height=2,
                            fg=GREEK_TEXT,
                            font=("Cinzel", 12, "bold"),
                            bg=GREEK_ACCENT,
                            text=row,
                            relief=tkinter.RIDGE,
                            bd=2
                        )
                    else:
                        label = tkinter.Label(
                            scrollable_frame,
                            width=15,
                            height=1,
                            fg=GREEK_TEXT,
                            font=("Playfair Display", 11),
                            bg=GREEK_LIGHT if r % 2 == 0 else GREEK_BG,
                            text=row,
                            relief=tkinter.RIDGE,
                            bd=1
                        )
                    label.grid(row=r, column=c, padx=1, pady=1, sticky="ew")
                    c += 1
                r += 1
        
        # Configurar scroll y empaquetado
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        root.mainloop()
        print(newdf)

    subject = Tk()
    subject.title("Consultar las Tablas del Destino")
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
        text="Consultar las Tablas del Destino",
        bg=GREEK_CONTAINER,
        fg=GREEK_TEXT,
        font=("Cinzel", 20, "bold"),
    )
    titl.pack(pady=15)
    
    # Descripción
    desc_label = tk.Label(
        main_container,
        text="Consulte el pergamino para ver los nombres de los asistentes",
        bg=GREEK_CONTAINER,
        fg=GREEK_DARK,
        font=("Playfair Display", 14, "italic"),
    )
    desc_label.pack(pady=(0, 20))

    def Attf():
        sub = tx.get()
        if sub == "":
            t="¡Por favor ingrese el nombre de la materia!"
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

    # Etiqueta para notificaciones
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

    # Marco para botones
    button_frame = tk.Frame(main_container, bg=GREEK_CONTAINER)
    button_frame.pack(pady=20)

    fill_a = tk.Button(
        button_frame,
        text="Ver Asistencia",
        command=calculate_attendance,
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
