import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from random import *
from PIL import Image, ImageTk
import os
import subprocess

class Fractales:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Fractales control")
        # Obtoene el ancho y alto de la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Establecer las dimensiones de la ventana
        window_width = 0.9 * screen_width  # 90% del ancho de la pantalla
        window_height = 0.8 * screen_height  #80% del alto de la pantalla

        self.root.geometry(f"{int(window_width)}x{int(window_height)}")
        base_path = os.path.dirname(__file__)
        self.icon_path = os.path.abspath(os.path.join(base_path, ".", "img", "car2.png"))
        self.root.iconphoto(False, tk.PhotoImage(file=self.icon_path))
        self.estado_color = tk.StringVar(value="blue")  # Por defecto azul
        self.create_widgets()

    def create_widgets(self):

        # Cargar los iconos utilizados
        base_path = os.path.dirname(__file__)
        img_path = os.path.abspath(os.path.join(base_path, ".", "img"))
        
        self.triangulo_img = Image.open(os.path.join(img_path, "tria.png"))
        self.triangulo_img2 = Image.open(os.path.join(img_path, "tri.png"))
        self.cuadrado_img = Image.open(os.path.join(img_path, "cua.png"))
        self.cuadrado_img2 = Image.open(os.path.join(img_path, "cuav.png"))
        self.guardar_img = Image.open(os.path.join(img_path, "gua.png"))
        self.goma_img = Image.open(os.path.join(img_path, "gom.png"))
        self.lupa_img = Image.open(os.path.join(img_path, "lup.png"))

        # Redimensionar los iconos si es necesario
        self.triangulo_img = self.triangulo_img.resize((30, 20))  # Ajusta el tamaño según tus necesidades
        self.triangulo_img2 = self.triangulo_img2.resize((30, 20))  # Ajusta el tamaño según tus necesidades
        self.cuadrado_img = self.cuadrado_img.resize((30, 20))  # Ajusta el tamaño según tus necesidades
        self.cuadrado_img2 = self.cuadrado_img2.resize((30, 20))
        self.guardar_img = self.guardar_img.resize((30, 30))
        self.goma_img = self.goma_img.resize((15, 15))
        self.lupa_img = self.lupa_img.resize((15, 15))

        # Convertir los iconos a un formato compatible con Tkinter
        self.triangulo_icono = ImageTk.PhotoImage(self.triangulo_img)
        self.triangulo_icono2 = ImageTk.PhotoImage(self.triangulo_img2)
        self.cuadrado_icono = ImageTk.PhotoImage(self.cuadrado_img)
        self.cuadrado_icono2 = ImageTk.PhotoImage(self.cuadrado_img2)
        self.guardar_icono = ImageTk.PhotoImage(self.guardar_img)
        self.goma_icono = ImageTk.PhotoImage(self.goma_img)
        self.lupa_icono = ImageTk.PhotoImage(self.lupa_img)

        self.frame1 = tk.Frame(self.root)#Se crea la instancia a la clase Frame que realiz el marco
        self.frame1.pack(pady=20)#Coloca dentro de la ventana principal con un relleno vertical de 20 píxeles.

        self.limpiar_btn = tk.Button(self.frame1, text="Limpiar Grafico", state=tk.DISABLED, image=self.goma_icono , command=self.limpiar_grafico)
        self.limpiar_btn.pack(side=tk.LEFT, padx=10)

        self.label = tk.Label(self.frame1, text="Seleccione un archivo:")#Se crea la instancia de la clase Label que muestra el texto "Seleccione un archivo:"
        self.label.pack(side=tk.LEFT)#Coloca la etiqueta dentro del marco, alineándola a la izquierda.

        #Se crea la instancia de la clase Entry que permite al usuario ingresar texto, ademas de que el numero 50 establece el ancho del cuadro de entrada en 50 caracteres
        self.filepath_entry = tk.Entry(self.frame1, width=50)
        self.filepath_entry.pack(side=tk.LEFT)#Coloca el cuadro de entrada dentro del marco, siendo con alineacion a la izquierda

        #Se hace referencia a los botones correspondientes, al igual que de esta forma se establecen las respectivas funciones
        self.browse_btn = tk.Button(self.frame1, text="Buscar", command=self.browse_file, compound=tk.LEFT, image=self.lupa_icono)
        self.browse_btn.pack(side=tk.LEFT, padx=5)

        self.guardar_btn = tk.Button(self.frame1, image=self.guardar_icono, command=self.save_fractal)
        self.guardar_btn.pack(side=tk.LEFT, padx=5)

        self.frame2 = tk.Frame(self.root)
        self.frame2.pack(fill=tk.BOTH, expand=True)

        # Subframe para el selector de tipo de señal
        self.selector_frame = tk.Frame(self.frame2)
        self.selector_frame.pack(side=tk.TOP, anchor='w', padx=30, pady=(10, 5))


        self.selector_label = tk.Label(self.selector_frame, text="Selecciona el tipo de señal a ingresar:")
        self.selector_label.pack(side=tk.TOP, anchor='w')

        self.opcion_estado = tk.StringVar(value="control")
        self.menu_selector = ttk.Combobox(self.selector_frame, textvariable=self.opcion_estado, values=["control", "paciente"], state="readonly")
        self.menu_selector.bind("<<ComboboxSelected>>", lambda e: self.cambiar_estado(self.opcion_estado.get()))
        self.menu_selector.pack(side=tk.TOP, anchor='w')


        self.triangulo_btn = tk.Button(self.frame2, image=self.triangulo_icono, state=tk.DISABLED, command=self.generar_grafica)
        self.triangulo_btn.pack(side=tk.LEFT, padx=10)

        self.cuadrado_btn = tk.Button(self.frame2, image=self.cuadrado_icono, state=tk.DISABLED, command=self.generar_grafica)
        self.cuadrado_btn.pack(side=tk.LEFT, padx=10)

        self.aleatorio_btn = tk.Button(self.frame2, text="Aleatorio", state=tk.DISABLED, command=self.generar_grafica, compound=tk.LEFT, image=self.triangulo_icono2)
        self.aleatorio_btn.pack(side=tk.LEFT, padx=10)

        self.aleatoriocuadrado_btn = tk.Button(self.frame2, text="Aleatorio", state=tk.DISABLED, command=self.generar_grafica, compound=tk.LEFT, image=self.cuadrado_icono2)
        self.aleatoriocuadrado_btn.pack(side=tk.LEFT, padx=10)

        self.canvas = None
        self.fig = None
        self.ax = None

    def cambiar_estado(self, seleccion):
        if seleccion == "control":
            self.estado_color.set("blue")
        elif seleccion == "paciente":
            self.estado_color.set("red")

    def browse_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Archivo de texto", "*.txt")])
        self.filepath_entry.delete(0, tk.END)
        self.filepath_entry.insert(tk.END, filepath)
        self.clear_graph()

        # Llamar a generar_grafica después de leer el archivo
        self.generar_grafica()

    def clear_graph(self):
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.triangulo_btn.config(state=tk.DISABLED)
            self.cuadrado_btn.config(state=tk.DISABLED)
            self.aleatorio_btn.config(state=tk.DISABLED)
            self.aleatoriocuadrado_btn.config(state=tk.DISABLED)
            self.limpiar_btn.config(state=tk.NORMAL)

    def generar_grafica(self):
        filepath = self.filepath_entry.get()
        try:
            data = pd.read_csv(filepath, sep='\t', header=None)[:100000]

            p = len(data)
            x = range(p)
            z = np.zeros((p,))
            Y = np.column_stack((x, data, z))

            self.fig = plt.Figure(figsize=(6, 4), dpi=100)
            self.ax = self.fig.add_subplot(111)

            self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame2)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            self.triangulo_btn.config(state=tk.NORMAL)
            self.cuadrado_btn.config(state=tk.NORMAL)
            self.aleatorio_btn.config(state=tk.NORMAL)
            self.aleatoriocuadrado_btn.config(state=tk.NORMAL)
            self.limpiar_btn.config(state=tk.NORMAL)

            def on_triangulo_click():
                # Función para dibujar un fractal de triángulo
                self.triangulo(p, Y)

            def on_cuadrado_click():
                # Función para dibujar un fractal de cuadrado
                self.cuadrado(p, Y)

            def on_aleatorio_click():
                # Función para dibujar un fractal aleatorio
                self.aleatorio(p, Y)

            def on_aleatoriocuadrado_click():
                # Función para dibujar un fractal aleatoriocuadrado
                self.aleatoriocuadrado(p, Y)

            self.triangulo_btn.config(command=on_triangulo_click)
            self.cuadrado_btn.config(command=on_cuadrado_click)
            self.aleatorio_btn.config(command=on_aleatorio_click)
            self.aleatoriocuadrado_btn.config(command=on_aleatoriocuadrado_click)

        except Exception as e:
            messagebox.showerror("Error", "Antes de generar la gráfica por favor seleccione un archivo.")

    def triangulo(self, p, Y):
        t = p // 3

        Y2 = Y[Y[:, 1].argsort()]

        for f in range(t):
            Y2[f][2] = 1

        for f in range(t, t * 2):
            Y2[f][2] = 2

        for f in range(t * 2, t * 3):
            Y2[f][2] = 3

        B1 = Y2[Y2[:, 0].argsort()]

        p1 = [0, 0]
        p2 = [1, 0]
        p3 = [0.5, 1]
        fractal = np.zeros((p, 3))

        initial = [0.5, 0.5]

        for f in range(p):
            if B1[f][2] == 1:
                initial = np.mean([p1, initial], axis=0)
                fractal[f][0] = initial[0]
                fractal[f][1] = initial[1]
            elif B1[f][2] == 2:
                initial = np.mean([p2, initial], axis=0)
                fractal[f][0] = initial[0]
                fractal[f][1] = initial[1]
            elif B1[f][2] == 3:
                initial = np.mean([p3, initial], axis=0)
                fractal[f][0] = initial[0]
                fractal[f][1] = initial[1]
            else:
                print('Unknown method.')
                print(f)

        self.ax.clear()
        self.ax.plot(fractal[:, 0], fractal[:, 1], linestyle='None', marker=".", markersize=1, color=self.estado_color.get())
        self.canvas.draw()

    def cuadrado(self, p, Y):
        t = p // 4

        Y2 = Y[Y[:, 1].argsort()]

        for f in range(t):
            Y2[f][2] = 1

        for f in range(t, t * 2):
            Y2[f][2] = 2

        for f in range(t * 2, t * 3):
            Y2[f][2] = 3

        for f in range(t * 3, t * 4):
            Y2[f][2] = 4

        B1 = Y2[Y2[:, 0].argsort()]

        p1 = [0, 0]
        p2 = [1, 0]
        p3 = [0, 1]
        p4 = [1, 1]
        fractal = np.zeros((p, 3))

        initial = [0.5, 0.5]

        for f in range(p):
            if B1[f][2] == 1:
                initial = np.mean([p1, initial], axis=0)
                fractal[f][0] = initial[0]
                fractal[f][1] = initial[1]
            elif B1[f][2] == 2:
                initial = np.mean([p2, initial], axis=0)
                fractal[f][0] = initial[0]
                fractal[f][1] = initial[1]
            elif B1[f][2] == 3:
                initial = np.mean([p3, initial], axis=0)
                fractal[f][0] = initial[0]
                fractal[f][1] = initial[1]
            elif B1[f][2] == 4:
                initial = np.mean([p4, initial], axis=0)
                fractal[f][0] = initial[0]
                fractal[f][1] = initial[1]
            else:
                print('Unknown method.')
                print(f)

        self.ax.clear()
        self.ax.plot(fractal[:, 0], fractal[:, 1], linestyle='None', marker=".", markersize=1, color=self.estado_color.get())
        self.canvas.draw()
    
    def aleatorio(self, p, Y):

        np.random.shuffle (Y)# Hace la señal aleatoria

        t= p // 3
        for f in range (t):
            Y[f][2]=1
        
        for f in range (t, t * 2):
            Y[f][2]=2

        for f in range (t*2, t * 3):
            Y[f][2]=3
        
        B1 = Y[Y[:, 0].argsort()]
        
        p1=[0, 0]
        p2=[1, 0]
        p3=[0.5, 1]

        fractal = np.zeros((p, 3))
        
        initial=[0.5, 0.5]

        for f in range(p):
            if B1[f][2]==1:
                initial = np.mean([p1, initial], axis=0)
                fractal[f][0] = initial[0]
                fractal[f][1] = initial[1]
            elif B1[f][2] == 2:
                initial = np.mean([p2, initial], axis=0)
                fractal[f][0] = initial[0]
                fractal[f][1] = initial[1]
            elif B1[f][2] == 3:
                initial = np.mean([p3, initial], axis=0)
                fractal[f][0] = initial[0]
                fractal[f][1] = initial[1]
        self.ax.clear()
        self.ax.plot(fractal[:, 0], fractal[:, 1], linestyle='None', marker=".", markersize=1, color='green')
        self.canvas.draw()
    
    def aleatoriocuadrado(self, p, Y):
        global ax
        np.random.shuffle(Y)  # Revuelve los puntos de forma aleatoria

        t = p // 4
        for f in range(t):
            Y[f][2] = 1

        for f in range(t, t * 2):
            Y[f][2] = 2

        for f in range(t * 2, t * 3):
            Y[f][2] = 3

        for f in range(t * 3, t * 4):
            Y[f][2] = 4

        B1 = Y[Y[:, 0].argsort()]

        p1 = [0, 0]
        p2 = [1, 0]
        p3 = [0, 1]
        p4 = [1, 1]
        fractal = np.zeros((p, 3))

        initial = [0.5, 0.5]

        for f in range(p):
            if B1[f][2] == 1:
                initial = np.mean([p1, initial], axis=0)
                fractal[f][0] = initial[0]
                fractal[f][1] = initial[1]
            elif B1[f][2] == 2:
                initial = np.mean([p2, initial], axis=0)
                fractal[f][0] = initial[0]
                fractal[f][1] = initial[1]
            elif B1[f][2] == 3:
                initial = np.mean([p3, initial], axis=0)
                fractal[f][0] = initial[0]
                fractal[f][1] = initial[1]
            elif B1[f][2] == 4:
                initial = np.mean([p4, initial], axis=0)
                fractal[f][0] = initial[0]
                fractal[f][1] = initial[1]
            else:
                print('Unknown method.')
                print(f)
        self.ax.clear()
        self.ax.plot(fractal[:, 0], fractal[:, 1], linestyle='None', marker=".", markersize=1, color='green')
        self.canvas.draw()

    def save_fractal(self):
        global canvas
        
        # Verificar si hay un gráfico generado en el lienzo
        if self.canvas is not None:
            # Abrir un cuadro de diálogo para guardar la imagen
            self.filepath = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("Imagen JPG", "*.jpg")])
            if self.filepath:
                # Obtener la imagen del lienzo y guardarla en el archivo especificado
                self.canvas.figure.savefig(self.filepath)
                messagebox.showinfo("Guardado", "La imagen se ha guardado exitosamente.")
            else:
                messagebox.showinfo("Cancelado", "El guardado de la imagen ha sido cancelado.")
        else:
            messagebox.showerror("Error", "No hay gráfico generado.")

    def limpiar_grafico(self):
        self.clear_graph()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Fractales()
    app.run()
