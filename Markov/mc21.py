import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QFileDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QIODevice, QBuffer
from PIL import Image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from random import *
import pyqtgraph as pg  
import seaborn as sns
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from grupos import Comparar
from scipy.stats import mannwhitneyu

# Define la variable basedir que hace referencia al directorio actual
basedir = os.path.dirname(__file__)

class Markov(QMainWindow):
    def __init__(self, root=None):
        super().__init__()
        self.initUI()
        self.p = None
        self.Y = None
        self.LIMA = None
        self.LIMB = None
        self.FREC = None

    def initUI(self):
        pg.setConfigOption('background', 'k')  # Color de fondo oscuro para los gráficos
        pg.setConfigOption('foreground', 'w')  # Color de texto blanco para los gráficos
        # Estilo para los botones
        style = """
            QPushButton {
                background-color: #1E90FF;  /* Azul */
                color: white;  /* Texto en blanco */
                font-size: 18px;
                border: none;  /* Sin borde */
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #4682B4;  /* Azul más oscuro al pasar el mouse */
            }
            QPushButton:pressed {
                background-color: #4169E1;  /* Azul más claro al presionar el botón */
            }
        """
        self.setStyleSheet(style)

        # Obtiene el ancho y alto de la pantalla
        screen_width = QApplication.desktop().screenGeometry().width()
        screen_height = QApplication.desktop().screenGeometry().height()

        # Establecer las dimensiones de la ventana
        window_width = 0.7 * screen_width  # 90% del ancho de la pantalla
        window_height = 0.7 * screen_height  # 80% del alto de la pantalla

        self.setGeometry(100, 100, int(window_width), int(window_height))
        self.setWindowTitle("Markov Chain")
        self.icon_path = os.path.join(basedir, "img", "mc.png")
        self.setWindowIcon(QIcon(self.icon_path))
        self.create_widgets()
        
    def create_widgets(self):
        # Cargar los iconos utilizados
        self.Markov_img = Image.open(os.path.join(os.path.dirname(__file__), "img", "mc.png"))
        self.guardar_img = Image.open(os.path.join(os.path.dirname(__file__), "img", "gua.png"))
        self.goma_img = Image.open(os.path.join(os.path.dirname(__file__), "img", "gom.png"))
        self.lupa_img = Image.open(os.path.join(os.path.dirname(__file__), "img", "lup.png"))

        # Redimensionar los iconos si es necesario
        self.Markov_img = self.Markov_img.resize((30, 20))  # Ajusta el tamaño según tus necesidades
        self.goma_img = self.goma_img.resize((15, 15))
        self.lupa_img = self.lupa_img.resize((15, 15))

        # Convertir los iconos a un formato compatible con PyQt5
        self.Markov_icono = QIcon(self.convert_image_to_pixmap(self.Markov_img))
        self.goma_icono = QIcon(self.convert_image_to_pixmap(self.goma_img))
        self.lupa_icono = QIcon(self.convert_image_to_pixmap(self.lupa_img))

        # Crear el layout principal de la ventana y establecerlo como el layout central
        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Crear el primer frame y su layout
        self.frame1 = QWidget(self)
        frame1_layout = QVBoxLayout(self.frame1)
        main_layout.addWidget(self.frame1,3)

        # Alinear el contenido del layout en la parte superior izquierda
        frame1_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.limpiar_btn = QPushButton("Limpiar Gráfico", self.frame1)
        self.limpiar_btn.setIcon(self.goma_icono)
        self.limpiar_btn.setEnabled(False)
        self.limpiar_btn.clicked.connect(self.limpiar_grafico)
        frame1_layout.addWidget(self.limpiar_btn)

        self.label = QLabel("Seleccione un archivo:", self.frame1)
        frame1_layout.addWidget(self.label)

        self.filepath_entry = QLineEdit(self.frame1)
        self.filepath_entry.setFixedWidth(300)
        frame1_layout.addWidget(self.filepath_entry)

        self.browse_btn = QPushButton("Buscar", self.frame1)
        self.browse_btn.setIcon(self.lupa_icono)
        self.browse_btn.clicked.connect(self.browse_file)
        frame1_layout.addWidget(self.browse_btn)

        ###botones para pedir valores
        freq_widget = QWidget(self.frame1)
        freq_layout = QHBoxLayout(freq_widget)
        frame1_layout.addWidget(freq_widget)
        lima_widget = QWidget(self.frame1)
        lima_layout = QHBoxLayout(lima_widget)
        frame1_layout.addWidget(lima_widget)
        limb_widget = QWidget(self.frame1)
        limb_layout = QHBoxLayout(limb_widget)
        frame1_layout.addWidget(limb_widget)

        txtfreq = QLabel("Tamaño de ventana:")  # Texto frecuencia
        txtfreq.setStyleSheet("font-size: 18px")
        freq_layout.addWidget(txtfreq)
        txtlima = QLabel("Valor mínimo:")  
        txtlima.setStyleSheet("font-size: 18px")
        lima_layout.addWidget(txtlima)
        txtlimb = QLabel("Valor máximo:")  
        txtlimb.setStyleSheet("font-size: 18px")
        limb_layout.addWidget(txtlimb)   

        self.form_freq = QLineEdit()  # Línea para poner frecuencia
        freq_layout.addWidget(self.form_freq)
        self.form_lima = QLineEdit()  # Línea para poner limite inferior
        lima_layout.addWidget(self.form_lima)
        self.form_limb = QLineEdit()  # Línea para poner limite inferior
        limb_layout.addWidget(self.form_limb)

        def asignar_valores_lim():
            try:
                self.LIMA = float(self.form_lima.text())
                self.LIMB = float(self.form_limb.text())
                self.FREC = int(self.form_freq.text())
            except ValueError:
                QMessageBox.critical(self, "Error", "Por favor, ingrese valores numéricos válidos para FREC, LIMA y LIMB.")

        self.Markov_btn = QPushButton("Calcular probabilidades", self.frame1)
        self.Markov_btn.setIcon(self.Markov_icono)
        self.Markov_btn.setEnabled(False)
        frame1_layout.addWidget(self.Markov_btn)

        self.Est_btn = QPushButton("Comparar pacientes", self.frame1)
        self.Est_btn.clicked.connect(self.show_comparar_window)  # Conectar el evento clicked a la función show_comparar_window
        frame1_layout.addWidget(self.Est_btn)

        # Conectar la función al evento de clic del botón
        self.Markov_btn.clicked.connect(asignar_valores_lim)

        # Crear el segundo frame y su layout
        self.frame2 = QWidget(self)
        self.frame2_layout = QVBoxLayout(self.frame2)  # Agrega esta línea para crear frame2_layout
        main_layout.addWidget(self.frame2,97)
        
        #ojito
        # Crear el lienzo al inicio
        self.fig = plt.Figure(figsize=(0, 0), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.frame2_layout.addWidget(self.canvas)

        # Crear la barra de herramientas de navegación
        navigation_toolbar = NavigationToolbar2QT(self.canvas, self)
        self.frame2_layout.addWidget(navigation_toolbar)

        # Habilitar el zoom interactivo
        navigation_toolbar.zoom()

        self.Markov_btn.setEnabled(True)
        self.limpiar_btn.setEnabled(True)

        self.data = None

         # Modificar la conexión del botón para acceder a p y Y
        def on_triangulo_click():
            if self.data is not None:
                self.Markovprob(self)
                self.canvas.draw()
            else:
                QMessageBox.critical(self, "Error", "Por favor, genere una gráfica primero.")

        self.Markov_btn.clicked.connect(self.Markovprob)
        self.frame2_layout.addWidget(self.canvas)  # Agregar el canvas al layout después de crearlo

    def convert_image_to_pixmap(self, image):
        # Guardar la imagen de PIL en un búfer temporal
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")
        buffer.seek(0)

        # Cargar la imagen desde el búfer temporal con QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.data())

        return pixmap

    def browse_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Seleccione un archivo", "", "Archivo de texto (*.txt)")
        if filepath:
            self.filepath_entry.setText(filepath)  # Establecer la ruta del archivo seleccionado en el campo de texto
            self.data = pd.read_table(filepath, header=None)[0][:] # Almacenar los datos del archivo
            # Imprimir los primeros 10 registros de self.data
            print("Primeros 10 registros de self.data:") 
            print(self.data.head(10))
            self.generar_grafica()

    def clear_graph(self):
        if self.ax is not None:
            self.ax.clear()
            self.canvas.draw()

    def generar_grafica(self):
        filepath = self.filepath_entry.text()
        if filepath:
            try:  
                 # Habilitar los botones después de cargar los datos
                self.Markov_btn.setEnabled(True)
                self.limpiar_btn.setEnabled(True)

                self.canvas.draw()
                # Limpiar la gráfica anterior
                self.clear_graph()

            except Exception as e:
                print("Error al cargar el archivo:", e)
                QMessageBox.critical(self, "Error", "Error al cargar el archivo.")
        else:
            QMessageBox.critical(self, "Error", "Por favor, seleccione un archivo.")
   
    def Markovprob(self):
        if self.data is not None:
            # Limpiar el gráfico anterior
            self.ax.clear()

            # Obtener la ruta del archivo desde el campo de texto
            ruta_archivo = self.filepath_entry.text()

            # Cargar el DataFrame desde el archivo
            df = pd.read_table(ruta_archivo, header=None, names=['Intervalos'])

            # Extraer el nombre del archivo sin la extensión
            nombre = ruta_archivo.split("/")[-1].split(".")[0]

            # Crear un DataFrame para almacenar los resultados
            results_data = []

            # Obtener los valores de LIMA y LIMB
            LIMA = self.LIMA if self.LIMA is not None else 0
            LIMB = self.LIMB if self.LIMB is not None else 0
            FREC = self.FREC if self.FREC is not None else 0

             # Especificar el tamaño de la ventana

            # Iterar sobre el DataFrame en bloques de n filas
            for start_idx in range(0, len(df), FREC):
                end_idx = start_idx + FREC
                window_df = df.iloc[start_idx:end_idx]

                count_A_to_N = 0
                count_N_to_A = 0
                count_A_to_A = 0
                count_N_to_N = 0

                # Lista para almacenar las letras (A o N) correspondientes a cada intervalo RR en la ventana
                letter_labels = []

                # Asignar las letras (A o N) según el valor del intervalo RR y contar las transiciones
                for rr in window_df['Intervalos']:
                    if rr < LIMA or rr > LIMB:
                        letter_labels.append("A")
                    else:
                        letter_labels.append("N")

                # Contar las transiciones en esta ventana
                for i in range(1, len(letter_labels)):
                    if letter_labels[i - 1] == "A" and letter_labels[i] == "N":
                        count_A_to_N += 1
                    elif letter_labels[i - 1] == "N" and letter_labels[i] == "A":
                        count_N_to_A += 1
                    elif letter_labels[i - 1] == "A" and letter_labels[i] == "A":
                        count_A_to_A += 1
                    elif letter_labels[i - 1] == "N" and letter_labels[i] == "N":
                        count_N_to_N += 1

   # Calcular las probabilidades de transición
                total_A_transitions = count_A_to_N + count_A_to_A
                total_N_transitions = count_N_to_A + count_N_to_N
                if total_A_transitions == 0:
                    probability_A_to_N = 1
                    probability_A_to_A = 0
                else:
                    probability_A_to_N = count_A_to_N / total_A_transitions
                    probability_A_to_A = count_A_to_A / total_A_transitions

                if total_N_transitions == 0:
                    probability_N_to_A = 1
                    probability_N_to_N = 0
                else:
                    probability_N_to_A = count_N_to_A / total_N_transitions
                    probability_N_to_N = count_N_to_N / total_N_transitions

                results_data.append([nombre, probability_A_to_N, probability_A_to_A, probability_N_to_A, probability_N_to_N])

            # Crear un DataFrame a partir de results_data
            results_df = pd.DataFrame(results_data, columns=['ventana', 'A_to_N', 'A_to_A', 'N_to_A', 'N_to_N'])

            # Especificar la ruta del archivo Excel existente
            archivo_excel = os.path.join(os.path.dirname(ruta_archivo), f'{os.path.splitext(os.path.basename(ruta_archivo))[0]}_rs.xlsx')

            # Guardar el DataFrame actualizado en el archivo Excel
            results_df.to_excel(archivo_excel, index=False)

            num_bins = int(np.sqrt(len(df)))
            sns.histplot(df["Intervalos"], bins=num_bins, kde=True, color="darkblue")

            plt.title("Histograma de HRV")
            plt.xlabel("Intervalos RR")
            plt.ylabel("Frecuencia")
            # Mostrar el histograma
            plt.show()

             # Mostrar la gráfica original en el lienzo
            self.ax.plot(df.index, df['Intervalos'], linestyle='-', color='black', linewidth=.7)
            self.ax.set_title("Gráfica de Intervalos RR")
            self.ax.set_xlabel("Índice")
            self.ax.set_ylabel("Intervalos RR")

            # Actualizar el lienzo
            self.canvas.draw()

        else:
            QMessageBox.critical(self, "Error", "Por favor, seleccione un archivo antes de generar la gráfica.")

    def show_comparar_window(self):
        # Instanciar y mostrar la ventana Comparar
        self.comparar_window = Comparar()
        self.comparar_window.show()
            

    def limpiar_grafico(self):
        self.clear_graph()

    def run(self):
        self.root.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet('QMainWindow {background-color: #86aeb3;}')  
    root = QWidget()  
    Markov_app = Markov(root=root)
    Markov_app.show()
    sys.exit(app.exec_())