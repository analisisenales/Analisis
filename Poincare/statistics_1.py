import sys
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import shapiro, ttest_ind, wilcoxon
from statsmodels.stats.multitest import multipletests
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pyqtgraph as pg  
import csv
import os

# Ruta absoluta a la carpeta del script
base_path = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(base_path, 'img')

class Statistics(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.file1_path = None
        self.file2_path = None
        self.file3_path = None

        self.label = QLabel("Ventana de estadísticas", self.central_widget)
        self.layout.addWidget(self.label)

        self.setWindowTitle("Statistics of Normotension and Hypertension")


        # Set window icon
        self.setWindowIcon(QIcon(os.path.join(img_path, "staisticss.png")))

        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

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
        window_width = 0.7 * screen_width  # 70% del ancho de la pantalla
        window_height = 0.7 * screen_height  # 70% del alto de la pantalla

        self.setGeometry(100, 100, int(window_width), int(window_height))

        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        # Left panel for file selectors and buttons
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        # File selectors and buttons
        self.file1_label = QLabel("No file selected")
        left_layout.addWidget(self.file1_label)
        self.file1_button = QPushButton("Select File for Angles")
        self.file1_button.setIcon(QIcon(os.path.join(img_path, "lup.png")))
        self.file1_button.clicked.connect(self.select_file1)
        left_layout.addWidget(self.file1_button)

        self.button1 = QPushButton("Angles")
        self.button1.setIcon(QIcon(os.path.join(img_path, "staisticss.png")))
        self.button1.clicked.connect(self.plotangles)
        left_layout.addWidget(self.button1)

        self.file2_label = QLabel("No file selected")
        left_layout.addWidget(self.file2_label)
        self.file2_button = QPushButton("Select File for Loop")
        self.file2_button.setIcon(QIcon(os.path.join(img_path, "lup.png")))
        self.file2_button.clicked.connect(self.select_file2)
        left_layout.addWidget(self.file2_button)

        self.button2 = QPushButton("Loop")
        self.button2.setIcon(QIcon(os.path.join(img_path, "staisticss.png")))
        self.button2.clicked.connect(self.plotloop)
        left_layout.addWidget(self.button2)

        self.file3_label = QLabel("No file selected")
        left_layout.addWidget(self.file3_label)
        self.file3_button = QPushButton("Select File for SumSingedAngles")
        self.file3_button.setIcon(QIcon(os.path.join(img_path, "lup.png")))
        self.file3_button.clicked.connect(self.select_file3)
        left_layout.addWidget(self.file3_button)

        self.button3 = QPushButton("SumSingedAngles")
        self.button3.setIcon(QIcon(os.path.join(img_path, "staisticss.png")))
        self.button3.clicked.connect(self.plotsumsinged)
        left_layout.addWidget(self.button3)

        # Save plot button
        self.save_button = QPushButton("Save Plot")
        self.save_button.setIcon(QIcon(os.path.join(img_path, "gua.png")))
        self.save_button.clicked.connect(self.save_plot)
        left_layout.addWidget(self.save_button)

        layout.addWidget(left_panel)

        # Right panel for matplotlib plot
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

    def select_file1(self):
        self.file1_path, _ = QFileDialog.getOpenFileName(self, "Select File for Angles", "", "CSV Files (*.csv)")
        if self.file1_path:
            file1_name = os.path.basename(self.file1_path)
            self.file1_label.setText(file1_name)

    def select_file2(self):
        self.file2_path, _ = QFileDialog.getOpenFileName(self, "Select File for Loop", "", "CSV Files (*.csv)")
        if self.file2_path:
            file2_name = os.path.basename(self.file2_path)
            self.file2_label.setText(file2_name)

    def select_file3(self):
        self.file3_path, _ = QFileDialog.getOpenFileName(self, "Select File for SumSingedAngles", "", "CSV Files (*.csv)")
        if self.file3_path:
            file3_name = os.path.basename(self.file3_path)
            self.file3_label.setText(file3_name)

    def plotangles(self):
        self.ax.clear()
        if not self.file1_path:
            QMessageBox.warning(self, "Warning", "Please select a file first.")
            return
        if self.file1_path:
            df = pd.read_csv(self.file1_path)
            df['Group'] = df['Group'].astype('category')

            summary_stats = df.groupby('Group')['Angle'].agg(['mean', 'std', 'count'])

            # Ruta al archivo Angles.csv
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            angles_path = os.path.join(desktop, "Angles.csv")

            # Verificar si ya existe el archivo
            if os.path.isfile(angles_path):
                # Leer el archivo existente
                existing_df = pd.read_csv(angles_path)
            else:
                # Crear un DataFrame vacío si no existe
                existing_df = pd.DataFrame()

            # Formatear las estadísticas resumidas como un DataFrame
            formatted_stats = summary_stats.reset_index()
            formatted_stats.columns = ["Group", "mean", "std", "count"]

            # Crear un DataFrame para alinear las estadísticas en la columna E
            # Esto asume que las primeras columnas son "ID", "Group", y "Angle"
            empty_data = pd.DataFrame(index=range(max(len(existing_df), len(formatted_stats))))
            empty_data["ID"] = existing_df["ID"] if "ID" in existing_df else None
            empty_data["Group"] = existing_df["Group"] if "Group" in existing_df else None
            empty_data["Angle"] = existing_df["Angle"] if "Angle" in existing_df else None

            # Añadir las estadísticas a partir de la columna E
            empty_data = pd.concat([empty_data, formatted_stats], axis=1)

            # Guardar el archivo CSV actualizado
            empty_data.to_csv(angles_path, index=False)

            # Continuar con el resto del código de la función
            shapiro_results = df.groupby('Group').apply(lambda x: shapiro(x['Angle'])[1]).reset_index()
            shapiro_results.columns = ['Group', 'p-value']
            print(shapiro_results)

            hypertensive_angles = df[df['Group'] == 'Hypertensive']['Angle']
            normotensive_angles = df[df['Group'] == 'Normotensive']['Angle']

            p_value1 = shapiro_results['p-value'][0]
            p_value2 = shapiro_results['p-value'][1]

            if p_value1 >= 0.05 and p_value2 >= 0.05:
                t_test_result = ttest_ind(hypertensive_angles, normotensive_angles)
                print(f"t-test: statistic={t_test_result.statistic}, p-value={t_test_result.pvalue}")
            else:
                wilcoxon_result = wilcoxon(hypertensive_angles, normotensive_angles)
                print(f"Wilcoxon: statistic={wilcoxon_result.statistic}, p-value={wilcoxon_result.pvalue}")

            sns.boxplot(x='Group', y='Angle', data=df, palette={"Hypertensive": "red", "Normotensive": "blue"}, ax=self.ax)
            self.ax.set_title('Boxplot of Angles by Group')
            self.ax.set_ylabel('Angle')
            self.ax.set_xlabel('')

            x1, x2 = 0, 1
            y, h, col = df['Angle'].max() + 0.1, 0.1, 'k'
            self.ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c=col)
            p_value = t_test_result.pvalue
            self.ax.text((x1 + x2) * .5, y + h, f"p = {p_value:.3f}", ha='center', va='bottom', color=col)

            self.canvas.draw()

    def plotloop(self):
        self.ax.clear()
        if not self.file2_path:
            QMessageBox.warning(self, "Warning", "Please select a file first.")
            return
        if self.file2_path:
            df = pd.read_csv(self.file2_path)
            df['Group'] = df['Group'].astype('category')
            df['Loop'] = 'Loops'

            summary_stats = df.groupby(['Group', 'Loop']).agg(n=('Loops', 'size'), mean=('Loops', 'mean'), sd=('Loops', 'std')).reset_index()
            print(summary_stats)

            shapiro_results = df.groupby(['Group', 'Loop'])['Loops'].apply(lambda x: shapiro(x)).reset_index()
            shapiro_results[['statistic', 'p_value']] = pd.DataFrame(shapiro_results['Loops'].tolist(), index=shapiro_results.index)
            shapiro_results = shapiro_results.drop(columns=['Loops'])
            print(shapiro_results)

            p_value1=shapiro_results['p_value'][0]
            p_value2=shapiro_results['p_value'][1]

            if p_value1 and p_value2 >= 0.05:
                grouped = df.groupby('Group')['Loops']
                t_stat, p_value_final = ttest_ind(grouped.get_group('Hypertensive'), grouped.get_group('Normotensive'))
                print(f"t-test: statistic={t_stat}, p-value={p_value_final}")
            else:
                w_stat, p_value_final = wilcoxon(grouped.get_group('Hypertensive'), grouped.get_group('Normotensive'))
                print(f"Wilcoxon test: statistic={w_stat}, p-value={p_value_final}")
            

            sns.boxplot(x='Loop', y='Loops', hue='Group', data=df, palette={"Hypertensive": "red", "Normotensive": "blue"}, ax=self.ax)
            self.ax.set_title('Number of loops by Group')
            self.ax.set_ylabel('Number of loops')
            self.ax.set_xlabel('')
            self.ax.legend(title='Group', loc='lower right')

            x1, x2 = 0, 1
            y, h, col = df['Loops'].max() + 0.1, 0.1, 'k'
            self.ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c=col)
            self.ax.text((x1+x2)*.5, y+h, f"p = {p_value_final:.3f}", ha='center', va='bottom', color=col)
            
            self.canvas.draw()

    def plotsumsinged(self):
        self.ax.clear()
        if not self.file3_path:
            QMessageBox.warning(self, "Warning", "Please select a file first.")
            return
        if self.file3_path:
            df = pd.read_csv(self.file3_path)
            df1 = pd.melt(df, id_vars=["ID", "Group"], value_vars=["Sum"], var_name="Angle", value_name="angle")
            df1["Group"] = df1["Group"].astype("category")
            df1["Angle"] = df1["Angle"].astype("category")

            summary_stats = df1.groupby(['Group', 'Angle']).agg({'angle': ['mean', 'std']})
            print(summary_stats)

            shapiro_results = df1.groupby(["Group", "Angle"]).apply(lambda x: shapiro(x["angle"])[1]).reset_index()
            shapiro_results.columns = ["Group", "Angle", "p-value"]
            print(shapiro_results)
            p_value1=shapiro_results["p-value"][0]
            p_value2=shapiro_results["p-value"][1]
            if p_value1 and p_value2 >= 0.05:
                t_test_results = df1.groupby("Angle").apply(lambda x: ttest_ind(x[x["Group"] == "Hypertensive"]["angle"], x[x["Group"] == "Normotensive"]["angle"])[1]).reset_index()
                t_test_results.columns = ["Angle", "p-value"]
                print(t_test_results)
            else:
                wilcoxon_test_results = df1.groupby("Angle").apply(lambda x: wilcoxon(x[x["Group"] == "Hypertensive"]["angle"], x[x["Group"] == "Normotensive"]["angle"])[1]).reset_index()
                wilcoxon_test_results.columns = ["Angle", "p-value"]
                print(wilcoxon_test_results)

            sns.set(style="whitegrid")
            sns.boxplot(x="Angle", y="angle", hue="Group", data=df1, palette={"Hypertensive": "red", "Normotensive": "blue"}, ax=self.ax)
            self.ax.set_title("Sum of signed angles")
            self.ax.set_xlabel("Angle")
            self.ax.set_ylabel("Sum of signed angles")
            self.ax.legend(title='Group', loc='upper left')

            x1, x2 = 0, 1
            y, h, col = df1['angle'].max() + 0.1, 0.1, 'k'
            self.ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c=col)
            self.ax.text((x1+x2)*.5, y+h, f"p = {t_test_results['p-value'][0]:.3f}", ha='center', va='bottom', color=col)

            self.canvas.draw()

    def save_plot(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Plot", "", "JPEG files (*.jpg);;All Files (*)")
        if filename:
            self.fig.savefig(filename)
            QMessageBox.information(self, "Success", "Plot saved successfully!")

    def run(self):
        self.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    style = """
        QMainWindow {
            background-color: #86aeb3;
        }
    """
    app.setStyleSheet(style)
    mainWin = Statistics()
    mainWin.run()
