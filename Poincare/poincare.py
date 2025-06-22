import sys
import os
from PyQt5.QtWidgets import QToolBar, QStatusBar, QMenuBar, QAction, QMainWindow, QApplication, QWidget, QFileDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
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
import traceback
import math
from statistics_1 import Statistics
import csv

# Defines the basedir variable that refers to the current directory
basedir = os.path.dirname(__file__)

base_path = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(base_path, 'img')

#The Poincare class is created
class Poincare(QMainWindow):

    def __init__(self, root=None):
        super().__init__()
        self.root = root
        self.initUI()
        self.p = None
        self.Y = None
        self.sd1 = None
        self.sd2 = None

    def Statistics_boton(self):
        try:
            self.statistics_window = Statistics(self)  # Pass self as the parent widget
            self.statistics_window.show()
            self.StatisticsWindow.exec_()
        except Exception as e:
            print(f"Error opening statistics window: {e}")

    def initUI(self):
        self.barra_estado = QStatusBar()
        self.setStatusBar(self.barra_estado)
        
        barra_herr = QToolBar("Toolbar")
        self.addToolBar(barra_herr)
        
        barra_menu = QMenuBar()
        self.setMenuBar(barra_menu)
        
        Statistics_action = QAction(QIcon(os.path.join(img_path, "staisticss.png")), 'Stadistics', self)
        Statistics_action.setToolTip('Stadistics')
        Statistics_action.setStatusTip('Stadistics') 
        Statistics_action.triggered.connect(self.Statistics_boton)
        barra_herr.addAction(Statistics_action)
        
        pg.setConfigOption('background', 'k')  # Dark background color for charts
        pg.setConfigOption('foreground', 'w')  # White text color for graphics
        
        # Style for buttons
        style = """
            QPushButton {
                background-color: #1E90FF;  /* Blue */
                color: white;  /* Blank text */
                font-size: 18px;
                border: none;  /* Without border */
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #4682B4;  /* Darker blue on hover */
            }
            QPushButton:pressed {
                background-color: #4169E1;  /* Lighter blue when pressing the button */
            }
        """
        self.setStyleSheet(style)

        # Gets the width and height of the screen
        screen_width = QApplication.desktop().screenGeometry().width()
        screen_height = QApplication.desktop().screenGeometry().height()

        # Set window dimensions
        window_width = 0.7 * screen_width  # 70% of screen width
        window_height = 0.7 * screen_height  # 70% of screen height

        self.setGeometry(100, 100, int(window_width), int(window_height))
        self.setWindowTitle("Poincare")
        self.setWindowIcon(QIcon(os.path.join(img_path, "pcr.png")))
        
        if self.root:
            self.setCentralWidget(self.root)

        self.create_widgets()

    def calculate_sd_axes(self, segment_data):
        delay = 1
        x = segment_data[:-delay]
        y = segment_data[delay:]
        self.sd1 = np.std(np.diff(y), ddof=1)
        self.sd2 = np.std(np.diff(x), ddof=1)
        
    def create_widgets(self):
        # Load used icons
        self.Poincaremap_img = Image.open(os.path.join(os.path.dirname(__file__), "img", "pcr.png"))
        self.guardar_img = Image.open(os.path.join(os.path.dirname(__file__), "img", "gua.png"))
        self.goma_img = Image.open(os.path.join(os.path.dirname(__file__), "img", "gom.png"))
        self.lupa_img = Image.open(os.path.join(os.path.dirname(__file__), "img", "lup.png"))
        self.topolo_img=Image.open(os.path.join(os.path.dirname(__file__), "img", "topo.png"))
        self.statistics=Image.open(os.path.join(os.path.dirname(__file__), "img", "staisticss.png"))
        self.descriptorsimg=Image.open(os.path.join(os.path.dirname(__file__), "img", "elipse.png"))
        self.openimg=Image.open(os.path.join(os.path.dirname(__file__), "img", "open.png"))
        
        # Resize icons if necessary
        self.Poincaremap_img = self.Poincaremap_img.resize((30, 30))  # Adjust the size according to your needs
        self.guardar_img = self.guardar_img.resize((30, 30))
        self.goma_img = self.goma_img.resize((15, 15))
        self.lupa_img = self.lupa_img.resize((15, 15))
        self.topolo_img = self.topolo_img.resize((15, 15))
        self.statistics = self.statistics.resize((15, 15))
        self.descriptorsimg = self.descriptorsimg.resize((15, 15))
        self.openimg = self.openimg.resize((40, 40))

        # Convert icons to a PyQt5 compatible format
        self.Poincaremap_icono = QIcon(self.convert_image_to_pixmap(self.Poincaremap_img))
        self.guardar_icono = QIcon(self.convert_image_to_pixmap(self.guardar_img))
        self.goma_icono = QIcon(self.convert_image_to_pixmap(self.goma_img))
        self.lupa_icono = QIcon(self.convert_image_to_pixmap(self.lupa_img))
        self.topolo_icono= QIcon(self.convert_image_to_pixmap(self.topolo_img))
        self.statistics= QIcon(self.convert_image_to_pixmap(self.statistics))
        self.descriptorsimg= QIcon(self.convert_image_to_pixmap(self.descriptorsimg))
        self.openimg= QIcon(self.convert_image_to_pixmap(self.openimg))

        # Create the main window layout and set it as the central layout
        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Create the first frame and its layout
        self.frame1 = QWidget(self)
        frame1_layout = QVBoxLayout(self.frame1)
        main_layout.addWidget(self.frame1,3)

        # Align layout content to the top left
        frame1_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.limpiar_btn = QPushButton("Clear Chart", self.frame1)
        self.limpiar_btn.setIcon(self.goma_icono)
        self.limpiar_btn.setEnabled(False)
        self.limpiar_btn.clicked.connect(self.limpiar_grafico)
        frame1_layout.addWidget(self.limpiar_btn)

        self.label = QLabel("Select a file:", self.frame1)
        frame1_layout.addWidget(self.label)

        self.filepath_entry = QLineEdit(self.frame1)
        self.filepath_entry.setFixedWidth(300)
        frame1_layout.addWidget(self.filepath_entry)

        self.browse_btn = QPushButton("Search", self.frame1)
        self.browse_btn.setIcon(self.lupa_icono)
        self.browse_btn.clicked.connect(self.browse_file)
        frame1_layout.addWidget(self.browse_btn)

        self.guardar_btn = QPushButton("Save Map", self.frame1)
        self.guardar_btn.setIcon(self.guardar_icono)
        self.guardar_btn.clicked.connect(self.save_fractal)
        frame1_layout.addWidget(self.guardar_btn)


        self.Poincaremap_btn = QPushButton("Poincaré map", self.frame1)
        self.Poincaremap_btn.setIcon(self.Poincaremap_icono)
        self.Poincaremap_btn.setEnabled(False)
        frame1_layout.addWidget(self.Poincaremap_btn)


        self.PoincaremapTopo_btn = QPushButton("Complex Correlation Measure", self.frame1)
        self.PoincaremapTopo_btn.setIcon( self.topolo_icono)
        self.PoincaremapTopo_btn.setEnabled(False)
        frame1_layout.addWidget(self.PoincaremapTopo_btn)

        self.Descriptors_btn = QPushButton("Descriptors", self.frame1) # icono tipo elipse como semi eje
        self.Descriptors_btn.setIcon(self.descriptorsimg)
        self.Descriptors_btn.clicked.connect(self.descriptors_btn)
        self.Descriptors_btn.setEnabled(False)
        frame1_layout.addWidget(self.Descriptors_btn)

        self.label = QLabel("Loops and Statistics", self.frame1)
        frame1_layout.addWidget(self.label)

        self.Graph_theory_btn = QPushButton("Graph Theory", self.frame1)
        self.Graph_theory_btn.setIcon(self.statistics)
        self.Graph_theory_btn.setEnabled(True)
        self.Graph_theory_btn.clicked.connect(self.graph_theory)
        frame1_layout.addWidget(self.Graph_theory_btn)
        
        # Añadir el nuevo Textbox y botón debajo de "Graph Theory"
        self.new_number_input = QLineEdit(self.frame1)  # Textbox para ingresar el número
        self.new_number_input.setPlaceholderText("Ingrese un número")
        frame1_layout.addWidget(self.new_number_input)

        self.save_number_btn = QPushButton("Guardar Número", self.frame1)  # Botón para guardar
        self.save_number_btn.setIcon(self.guardar_icono)
        self.save_number_btn.clicked.connect(self.save_number)
        frame1_layout.addWidget(self.save_number_btn)

        self.create_files_btn = QPushButton("Create files", self.frame1)  # Botón para guardar
        self.create_files_btn.setIcon(self.openimg)
        self.create_files_btn.clicked.connect(self.files_statitistics)
        frame1_layout.addWidget(self.create_files_btn)

        # Create the second frame and its layout
        self.frame2 = QWidget(self)
        self.frame2_layout = QVBoxLayout(self.frame2)  # Add this line to create frame2_layout
        main_layout.addWidget(self.frame2,97)
        
        # Create the canvas at the beginning
        self.fig = plt.Figure(figsize=(0, 0), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.frame2_layout.addWidget(self.canvas)


        self.Poincaremap_btn.setEnabled(True)
        self.limpiar_btn.setEnabled(True)
        self.PoincaremapTopo_btn.setEnabled(True)
        self.Descriptors_btn.setEnabled(True)

        self.data = None

         # Modify button connection to access p and Y
        def on_triangulo_click():
            if self.data is not None:
                self.Poincaremap(self)
                self.PoincaremapTopo(self)
                self.canvas.draw()
            else:
                QMessageBox.critical(self, "Error", "Please generate a graph first.")


        self.Poincaremap_btn.clicked.connect(self.Poincaremap)
        self.frame2_layout.addWidget(self.canvas) 
        self.PoincaremapTopo_btn.clicked.connect(self.Poincaremaptopo)
        self.frame2_layout.addWidget(self.canvas)        

    def angle_between_points(self, x1, y1, x2, y2, x3, y3):
        # Calcular vectores AC y BC
        vector_AC = (x1 - x3, y1 - y3)
        vector_BC = (x3 - x2, y3 - y2)

        # Calcular producto punto de AC y BC
        dot_product = vector_AC[0] * vector_BC[0] + vector_AC[1] * vector_BC[1]

        # Calcular magnitudes de AC y BC
        magnitude_AC = math.sqrt(vector_AC[0] ** 2 + vector_AC[1] ** 2)
        magnitude_BC = math.sqrt(vector_BC[0] ** 2 + vector_BC[1] ** 2)

        # Calcular el coseno del ángulo entre AC y BC
        cosine_theta = dot_product / (magnitude_AC * magnitude_BC)

        # Asegurarse de que el valor del coseno esté dentro del rango válido [-1, 1]
        cosine_theta = max(-1.0, min(1.0, cosine_theta))

        # Calcular el ángulo en radianes
        angle_rad = math.acos(cosine_theta)

        # Determinar el signo del ángulo usando el producto cruzado
        cross_product = vector_AC[0] * vector_BC[1] - vector_AC[1] * vector_BC[0]
        if cross_product < 0:
            angle_rad = -angle_rad

        return angle_rad

    def calculate_angles(self, x, y):
        angles = []
        radian_values = []  # Lista para almacenar los valores de angle_rad
        total_angle = 0.0
        loop_count = 0

        for i in range(len(x) - 2):
            x1, y1 = x[i], y[i]
            x3, y3 = x[i + 1], y[i + 1]
            x2, y2 = x[i + 2], y[i + 2]

            angle_rad = self.angle_between_points(x1, y1, x2, y2, x3, y3)


             # Convertir ángulos negativos a positivos (en radianes y grados)
            angle_rad = abs(angle_rad)
            radian_values.append(angle_rad)  # Almacenar el valor de angle_rad
            angle_deg = math.degrees(angle_rad)  # Convertir el ángulo a grados
            total_angle += angle_deg  # Sumar el ángulo en grados
            angles.append(angle_deg)  # Agregar el ángulo en grados a la lista

        # Calcular el número de vueltas
        loop_count = total_angle / 360

        return angles, radian_values, loop_count  # Devolver la lista radian_values

    def plot_first_six_angles(self, angles):
        # Limitar la cantidad de ángulos a 6 para graficar
        first_six_angles = angles[:6]

        plt.figure(figsize=(8, 4))
        plt.plot(range(1, len(first_six_angles) + 1), first_six_angles, marker='o')

        # Añadir anotaciones para mostrar el tamaño de los ángulos
        for i, angle in enumerate(first_six_angles):
            plt.text(i + 1, angle, f'{angle:.2f}°', ha='center', va='bottom')

        plt.title("Primeros 6 Ángulos Calculados")
        plt.xlabel("Índice del Ángulo")
        plt.ylabel("Valor del Ángulo (grados)")
        plt.grid(True)
        plt.show()

    def graph_theory(self):
        if hasattr(self, 'data') and self.data is not None:
            try:
                # Convertir datos a coordenadas x, y
                segment_data = self.data.values
                x = segment_data[:-1]
                y = segment_data[1:]

                # Calcular los ángulos y loops
                angles, radian_values, num_loops = self.calculate_angles(x, y)
                total_angle = sum(angles)
                sum_radian_values = 0.0  # Inicializar la suma de los valores en radianes
                loop_count_radians = 0  # Inicializar el contador de loops basado en radianes

                for radian_value in radian_values:
                    sum_radian_values += radian_value

                # Calcular las vueltas basadas en radianes
                loop_count_radians = sum_radian_values / (2 * math.pi)

                # Graficar los primeros 6 ángulos
                self.plot_first_six_angles(angles)

                # Guardar datos en un archivo CSV
                self.save_angles_to_csv(angles, num_loops, total_angle, sum_radian_values, loop_count_radians, radian_values)

                QMessageBox.information(self, "Graph Theory", f"Datos guardados:\nÁngulo Total: {total_angle}\nVueltas: {num_loops}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Se produjo un error: {e}")
        else:
            QMessageBox.critical(self, "Error", "Seleccione un archivo antes de realizar operaciones de Teoría de Grafos.")

    # Declarar el contador global al inicio
    save_count = 0  # Inicializamos el contador en 0

    def save_angles_to_csv(self, angles, num_loops, total_angle, sum_radian_values, loop_count_radians, radian_values):
        filepath, _ = QFileDialog.getSaveFileName(self, "Guardar datos de ángulos", "", "Archivos CSV (*.csv);;Todos los archivos (*)")
        if filepath:
            with open(filepath, 'w', newline='') as file:
                writer = csv.writer(file)
                
                # Incrementar el contador cada vez que se guarda el archivo
                self.save_count += 1
                
                # Contador de celdas/filas ocupadas por los ángulos
                angle_data_count = len(angles)  # Número de ángulos que se guardan en el CSV
                
                writer.writerow(["Ángulos (grados)", "Valores en radianes"])  # Escribir los encabezados de las columnas
                for angle, radian in zip(angles, radian_values):
                    writer.writerow([angle, radian])  # Escribir los valores de ángulos y radianes en cada fila
                
                writer.writerow([])  # Línea vacía para separar los datos
                writer.writerow(["Ángulo Total", total_angle])
                writer.writerow(["Suma de Radianes", sum_radian_values])
                writer.writerow(["Vueltas (Radianes)", loop_count_radians])
                writer.writerow(["Vueltas", num_loops])
                
                # Escribir el número de celdas ocupadas por los ángulos
                writer.writerow([])
                writer.writerow(["Cantidad de celdas usadas para ángulos", angle_data_count])
            
            QMessageBox.information(self, "Guardado exitoso", f"Los datos se han guardado exitosamente en el archivo CSV.\nNúmero de ángulos guardados: {angle_data_count}")
        else:
            QMessageBox.information(self, "Guardado cancelado", "El guardado de datos en el archivo CSV ha sido cancelado.")
                
    def save_number(self):
        try:
            number = int(self.new_number_input.text())
            self.saved_number = number
            QMessageBox.information(self, "Número Guardado", f"El número {self.saved_number} ha sido guardado.")
        except ValueError:
            QMessageBox.critical(self, "Error", "Por favor, ingrese un número válido.")
    
    def convert_image_to_pixmap(self, image):
        # Save the PIL image to a temporary buffer
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")
        buffer.seek(0)

        # Load image from temporary buffer with QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.data())

        return pixmap

    def browse_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select a file", "", "Text file (*.txt)")
        if filepath:
            self.filepath_entry.setText(filepath)  # Set the path of the selected file in the text field
            self.selected_filename = os.path.basename(filepath)  # Almacenar el nombre del archivo (sin la ruta completa)
            self.data = pd.read_table(filepath, header=None)[0][:2530]  # Store file data
            # Print the first records of self.data
            print("First self.data records:")
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
                data = pd.read_table(filepath, header=None)[:2530]
                self.p = len(data)
                x = range(self.p)
                z = np.zeros((self.p,))
                self.Y = np.column_stack((x, data, z))
                
                
                 # Enable buttons after loading data
                self.Poincaremap_btn.setEnabled(True)
                self.limpiar_btn.setEnabled(True)
                self.PoincaremapTopo_btn.setEnabled(True)
                self.Descriptors_btn.setEnabled(True)

                self.canvas.draw()
                # Clear the previous graph
                self.clear_graph()

            except Exception as e:
                print("Error loading file:", e)
                QMessageBox.critical(self, "Error", "Error loading file.")
        else:
            QMessageBox.critical(self, "Error", "Please select a file before generating the graph.")
    
    # Define a function to create the Poincaré map
    def create_poincare_map(self,segment_data):
        delay = 1
        x = segment_data[:-delay]
        y = segment_data[delay:]
        return x, y

    def Poincaremap(self):

        print(self.data.head(215))
        if self.data is not None:
            # Clear the previous graph
            self.ax.clear()

            print(1)#ok1
            
            # Define the marker as an asterisk
            marker = '.'  # Switch to your desired marker

            # Define color as Dark Blue in hexadecimal
            color = '#212F3C'


            # Plot the Poincaré map for the data series
            x, y = self.create_poincare_map(self.data)

            self.ax.scatter(x, y, s=4, c=color, edgecolors='black', linewidths=0.5, marker=marker)
            results_data = []
            

            
            print(2)#ok2

            # Calculate the covariance matrix
            cov_matrix = np.cov(x, y)

            print(3)#ok

            # Calculate the eigenvalues ​​and eigenvectors of the covariance matrix
            eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)

            print(4)#ok4

            # Select the largest eigenvalue and its corresponding eigenvector
            max_eigenvalue_index = np.argmax(eigenvalues)
            max_eigenvector = eigenvectors[:, max_eigenvalue_index]

            # Calculate the semi-axes of the ellipse based on the eigenvalues ​​and the expansion factor
            expansion_factor = 2.0# Adjust the expansion factor as needed
            sd_major = np.sqrt(eigenvalues[max_eigenvalue_index]) * expansion_factor
            sd_minor = np.sqrt(eigenvalues[1 - max_eigenvalue_index]) * expansion_factor
            results_data.append([sd_minor, sd_major])
            self.results_df1 = pd.DataFrame(results_data, columns=['sd_minor','sd_major'])
            self.sd_minor = sd_minor
            self.sd_major = sd_major
            

            print(8)

            # Calculate the angle of rotation of the ellipse
            angle = np.degrees(np.arctan(max_eigenvector[1] / max_eigenvector[0]))

            # Calculate extreme coordinates of the ellipse after rotation
            t = np.linspace(0, 2 * np.pi, 100)
            ellipse_x = np.mean(x) + sd_major * np.cos(t) * np.cos(np.radians(angle)) - sd_minor * np.sin(t) * np.sin(np.radians(angle))
            ellipse_y = np.mean(y) + sd_major * np.cos(t) * np.sin(np.radians(angle)) + sd_minor * np.sin(t) * np.cos(np.radians(angle))

            # Add the ellipse fitted to the points
            ellipse = Ellipse(xy=(np.mean(x), np.mean(y)), width=2*sd_major, height=2*sd_minor,
                            angle=angle, edgecolor='r', fc='None', lw=2)
            self.ax.add_patch(ellipse)

            # Add the lines that pass through the axes of the ellipse in blue
            self.ax.plot([np.mean(x) - 2*sd_major*np.cos(np.radians(angle)), np.mean(x) + 2*sd_major*np.cos(np.radians(angle))],
                    [np.mean(y) - 2*sd_major*np.sin(np.radians(angle)), np.mean(y) + 2*sd_major*np.sin(np.radians(angle))],
                    color='blue', linestyle='--', alpha=0.7)

            self.ax.plot([np.mean(x) - 2*sd_minor*np.sin(np.radians(angle)), np.mean(x) + 2*sd_minor*np.sin(np.radians(angle))],
                    [np.mean(y) + 2*sd_minor*np.cos(np.radians(angle)), np.mean(y) - 2*sd_minor*np.cos(np.radians(angle))],
                    color='green', linestyle='--', alpha=0.7)

            # Add text annotations for SD1, SD2, and SD1/SD2 measures
            self.ax.text(0.05, 0.95, f'SD1: {sd_minor:.2f}', transform=self.ax.transAxes, fontsize=10,
                    color='green', verticalalignment='top', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

            self.ax.text(0.05, 0.88, f'SD2: {sd_major:.2f}', transform=self.ax.transAxes, fontsize=10,
                    color='blue', verticalalignment='top', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

            self.ax.text(0.05, 0.81, f'SD1/SD2: {sd_minor/sd_major:.2f}', transform=self.ax.transAxes, fontsize=10,
                    color='black', verticalalignment='top', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

            self.ax.set_xlabel('n')
            self.ax.set_ylabel('n+1')
            self.ax.set_title('Map of Poincaré')

            # Get the axis limits without taking into account the ellipse
            x_min, x_max = min(x), max(x)
            y_min, y_max = min(y), max(y)

            # Adjusting axis limits
            self.ax.set_xlim([x_min, x_max])
            self.ax.set_ylim([y_min, y_max])
            

            # Refresh the canvas
            self.canvas.draw()
            return self.results_df1
        else:
            QMessageBox.critical(self, "Error", "Please select a file before generating the graph.")

    def Poincaremaptopo(self):
        if self.data is not None:
            # Clear the previous graph
            self.ax.clear()

            # Define marker and color Charleston Green
            marker = '.'  
            color = '#212F3C'

            # Plot the Poincaré map for the data series
            lag=self.find_optimal_lag(self.data, maxtau=1000)
            x_data, y_data = self.create_poincare_mapv1(self.data,lag)
            print(lag)
            
            results_data=[]
            areas=[]
            if len(x_data)>=3:
                for i in range(len(x_data)-2):
                    a1,b1=x_data.iloc[i],y_data.iloc[i]
                    a2,b2=x_data.iloc[i+1], y_data.iloc[i+1]
                    a3,b3=x_data.iloc[i+2], y_data.iloc[i+2]
                    area=self.areatri(a1, b1, a2, b2, a3, b3)
                    areas.append(area)
                suma_areas=sum(areas)
                print(f"The total area is: {suma_areas}")
                #results_data.append(['Suma', suma_areas])
                #results_df = pd.DataFrame(results_data, columns=['Columna','Suma'])
                #aligned_df = self.results_df1.copy()
                #aligned_df['sd_minor'] = self.results_df1['Suma']
                #aligned_df.to_excel('alineado1.xlsx', index=False)
                print('okay')
                self.resultado_ccm = self.CCM_c(self.sd_minor, self.sd_major, suma_areas)
                print("CCM_c result:", self.resultado_ccm)

                self.ax.text(0.05, 0.95, f'Lag: {lag}', transform=self.ax.transAxes, fontsize=10,
                    color='green', verticalalignment='top', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

                self.ax.text(0.05, 0.88, f'Area: {suma_areas:.2f}', transform=self.ax.transAxes, fontsize=10,
                    color='blue', verticalalignment='top', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
                self.ax.text(0.05, 0.80, f'CCM: {self.resultado_ccm:.2f}', transform=self.ax.transAxes, fontsize=10,
                    color='red', verticalalignment='top', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

    


         # Plotear el mapa de Poincaré
                self.ax.plot(x_data[:20], y_data[:20], markersize=4, c=color, marker=marker)
                self.ax.set_xlabel('n')
                self.ax.set_ylabel(f'n+ {lag}')
                #self.ax.set_ylim(-5, 10)
                #self.ax.set_xlim(-5, 10)
                self.ax.set_title(f'Temporal Dynamics Plot')

            # Actualizar el lienzo
                self.canvas.draw()
        else:
         QMessageBox.critical(self, "Error", "Please, select a file before generating the graph.")

    def mi(self,x, y, bins=64):
        p_x = np.histogram(x, bins)[0]
        p_y = np.histogram(y, bins)[0]
        p_xy = np.histogram2d(x, y, bins)[0].flatten()
        # Convert frequencies into probabilities.  Also, in the limit
    # p -> 0, p*log(p) is 0.  We need to take out those.
        p_x = p_x[p_x > 0] / np.sum(p_x)
        p_y = p_y[p_y > 0] / np.sum(p_y)
        p_xy = p_xy[p_xy > 0] / np.sum(p_xy)
        # Calculate the corresponding Shannon entropies.
        h_x = np.sum(p_x * np.log2(p_x))
        h_y = np.sum(p_y * np.log2(p_y))
        h_xy = np.sum(p_xy * np.log2(p_xy))
        return h_xy - h_x - h_y
    
    def dmi(self,x, maxtau=1000, bins=64):
        N = len(x)
        maxtau = min(N, maxtau)
        ii = np.empty(maxtau)
        ii[0] = self.mi(x, x, bins)
        for tau in range(1, maxtau):
            ii[tau] = self.mi(x[:-tau], x[tau:], bins)
        return ii

    def find_optimal_lag(self,x, maxtau=1000):
        N = len(x)
        maxtau = min(N, maxtau)
        mi = self.dmi(x, maxtau=maxtau)
        diffmi = np.diff(mi)
        try:
         index = np.where(diffmi > 0)[0][0]   
         return index
        except IndexError:
             print("Error: No optimal lag found. Try with a larger maxtau value.")
        return None  # or any other value to indicate failure
    
    def create_poincare_mapv1(self, segment_data1,lag):
        
        x_1 = segment_data1[:-lag]
        y_1 = segment_data1[lag:]
        return x_1, y_1

    def areatri(self, a1, b1, a2, b2, a3, b3):
        matriz = np.array([
            [a1, b1, 1],
            [a2, b2, 1],
            [a3, b3, 1]])
        det = np.linalg.det(matriz)
        area = abs(0.5 * det)
        return area
    
    def CCM_c (self,sd_minor,sd_major,suma_areas):
        ccm = 1/(math.pi*sd_minor*sd_major)*suma_areas
        return ccm

    def save_fractal(self):
        global canvas
        
        # Check if there is a generated chart on the canvas
        if self.canvas is not None:
            # Open a dialog box to save the image
            self.filepath, _ = QFileDialog.getSaveFileName(self, "Guardar Imagen", "", "Imagen JPG (*.jpg);;Todos los archivos (*)")
            if self.filepath:
                # Get the image from the canvas and save it to the specified file
                self.canvas.figure.savefig(self.filepath)
                QMessageBox.information(self, "Save", "The image has been saved successfully.")
            else:
                QMessageBox.information(self,"Cancelled", "Image saving has been cancelled.")
        else:
            QMessageBox.showerror("Error", "No graph generated.")

    def descriptors_btn(self):
        
        if self.data is not None:
            try:
                # Generate Poincaré data points for sd1 and sd2
                segment_data = self.data
                self.calculate_sd_axes(segment_data)
                
                # Assume CCM is already calculated as self.resultado_ccm
                results = {
                    "SD1": [self.sd_minor],
                    "SD2": [self.sd_major],
                    "SD1/SD2": [self.sd_minor / self.sd_major],
                    "CCM": [self.resultado_ccm]
                }
                
                # Convert results to DataFrame
                results_df = pd.DataFrame(results)
                
                # Get the current filename
                current_file = self.filepath_entry.text()
                
                # Extract filename without extension
                filename = os.path.splitext(os.path.basename(current_file))[0]
                
                # Add ID column with filename
                results_df.insert(0, 'Id', filename)
                
                # Get the desktop path
                desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
                
                # Define the CSV file path
                csv_file = os.path.join(desktop_path, 'descriptors.csv')
                
                if os.path.exists(csv_file):
                    # Check if the CSV file already exists and load it
                    existing_df = pd.read_csv(csv_file)
                    
                    # Check if the current file is already in the CSV
                    if filename in existing_df['Id'].values:
                        # Overwrite the existing entry
                        existing_df = existing_df[existing_df['Id'] != filename]
                    
                    # Append the new data
                    updated_df = pd.concat([existing_df, results_df], ignore_index=True)
                    updated_df.to_csv(csv_file, index=False)
                else:
                    # Create or overwrite CSV file with the results
                    results_df.to_csv(csv_file, index=False)
                
                # Display message
                QMessageBox.information(self, "Descriptors", "Descriptors have been saved successfully.")
            except Exception as e:
                print(f"Error calculating descriptors: {e}")
                QMessageBox.critical(self, "Error", f"There was an error calculating descriptors: {e}")
        else:
            QMessageBox.critical(self, "Error", "Please select a file before generating descriptors.")

    def limpiar_grafico(self):
        self.clear_graph()

    def files_statitistics(self):
        # Obtener el nombre del archivo seleccionado en browse_file
        filepath = self.filepath_entry.text()
        file_name = os.path.basename(filepath)
        
        # Determinar el grupo según el nombre del archivo
        if 'hip' in file_name:
            group = 'Hypertensive'
        elif 'norm' in file_name:
            group = 'Normotensive'
        else:
            group = 'Unknown'

        # ID basado en el nombre del archivo
        file_id = file_name.split('.')[0]

        # Crear rutas para guardar los archivos CSV en el escritorio
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        angles_path = os.path.join(desktop, "Angles.csv")
        loops_path = os.path.join(desktop, "Loops.csv")
        sum_of_angles_path = os.path.join(desktop, "SumOfAngles.csv")

        # Convertir datos a coordenadas x, y
        segment_data = self.data.values
        x = segment_data[:-1]
        y = segment_data[1:]

        # Calcular los ángulos y loops usando la función calculate_angles
        angles, radian_values, num_loops = self.calculate_angles(x, y)
        total_angle = sum(angles)

        # Usar angle_data_count para definir cuántos ángulos se promedian
        angle_data_count = self.saved_number 

        # Asegurarse de que angle_data_count no exceda la longitud de angles
        if angle_data_count > len(angles):
            angle_data_count = len(angles)

        # Seleccionar los primeros angle_data_count ángulos para calcular el promedio
        selected_angles = angles[:angle_data_count]
        average_angle = sum(selected_angles) / len(selected_angles)

        # Función para comprobar y escribir en el archivo
        def check_and_write(file_path, header, row):
            try:
                # Comprobar si el archivo ya existe y si tiene la cabecera
                file_exists = os.path.isfile(file_path)
                header_exists = False
                
                if file_exists:
                    with open(file_path, 'r', newline='') as file:
                        reader = csv.reader(file)
                        first_row = next(reader, None)
                        if first_row == header:
                            header_exists = True

                # Escribir en el archivo
                with open(file_path, 'a', newline='') as file:
                    writer = csv.writer(file)
                    if not header_exists:
                        writer.writerow(header)
                    writer.writerow(row)
            except PermissionError:
                QMessageBox.critical(self, "Error", f"No se puede acceder a {file_path}. Asegúrate de que el archivo no esté abierto y de tener permisos adecuados.")
                return

        # Guardar los datos en los archivos correspondientes
        check_and_write(angles_path, ["ID", "Group", "Angle"], [file_id, group, average_angle])
        check_and_write(loops_path, ["ID", "Group", "Loops"], [file_id, group, num_loops])
        check_and_write(sum_of_angles_path, ["ID", "Group", "Sum"], [file_id, group, total_angle])

        QMessageBox.information(self, "Archivos creados", "Los archivos CSV se han guardado en el escritorio.")

    def run(self):
        self.root.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet('QMainWindow {background-color: #86aeb3;}')  
    root = QWidget()  
    Poincare_app = Poincare(root=root)
    Poincare_app.show()
    sys.exit(app.exec_())