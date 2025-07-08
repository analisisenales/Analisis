import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QVBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt5.QtGui import QIcon
from scipy.stats import mannwhitneyu
import pandas as pd

basedir = os.path.dirname(__file__)

class Comparar(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comparar pacientes")
        self.icon_path = os.path.join(basedir, "img", "mc.ico")
        self.setWindowIcon(QIcon(self.icon_path))
        self.setStyleSheet("background-color: #86aeb3")  # Cambiar el color de fondo de la ventana
        self.resize(600, 400)  # Cambiar el tamaño de la ventana
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.group1_label = QLabel("Grupo Tratamiento:")
        self.group1_label.setStyleSheet("font-size: 18px")
        layout.addWidget(self.group1_label)
        self.group1_button = QPushButton("Seleccionar archivos")
        self.group1_button.clicked.connect(self.select_group1_files)
        self.group1_button.setStyleSheet("""
            QPushButton {
                background-color: #1E90FF;
                color: white;
                padding: 10px 24px;
                font-size: 16px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #4682B4;
            }
            QPushButton:pressed {
                background-color: #4169E1;  /* Azul más claro al presionar el botón */
            }
        """) 
        layout.addWidget(self.group1_button)

        self.group2_label = QLabel("Grupo Control:")
        self.group2_label.setStyleSheet("font-size: 18px")
        layout.addWidget(self.group2_label)
        self.group2_button = QPushButton("Seleccionar archivos")
        self.group2_button.clicked.connect(self.select_group2_files)
        self.group2_button.setStyleSheet("""
            QPushButton {
                background-color: #1E90FF;
                color: white;
                padding: 10px 24px;
                font-size: 16px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #4682B4;
            }
            QPushButton:pressed {
                background-color: #4169E1;  /* Azul más claro al presionar el botón */
            }
        """)        
        layout.addWidget(self.group2_button)

        self.calculate_button = QPushButton("Prueba de Mann-Whitney U")
        self.calculate_button.clicked.connect(self.calculate_mannwhitneyu)
        self.calculate_button.setStyleSheet("""
            QPushButton {
                background-color: #1E90FF;
                color: white;
                padding: 10px 24px;
                font-size: 16px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #4682B4;
            }
            QPushButton:pressed {
                background-color: #4169E1;  /* Azul más claro al presionar el botón */
            }
        """)        
        layout.addWidget(self.calculate_button)

        self.group1_files = []
        self.group2_files = []

    def select_group1_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar archivos para Grupo Trat", "", "Archivos Excel (*.xlsx *.xls)", options=options)
        self.group1_files = files
        self.show_selected_files(files, self.group1_label)

    def select_group2_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar archivos para Grupo Control", "", "Archivos Excel (*.xlsx *.xls)", options=options)
        self.group2_files = files
        self.show_selected_files(files, self.group2_label)

    def show_selected_files(self, files, label):
        if files:
            file_names = ", ".join(file.split('/')[-1] for file in files)
            label.setText("Archivos " + label.text().split()[1] + ": " + file_names)
        else:
            label.setText("Archivos " + label.text().split()[1] + ": (ninguno)")

    def calculate_mannwhitneyu(self):
        if self.group1_files and self.group2_files:
            group1_data = pd.concat((pd.read_excel(file) for file in self.group1_files))
            group2_data = pd.concat((pd.read_excel(file) for file in self.group2_files))

            results = {}
            for column in group1_data.select_dtypes(include='number'):
                if column not in results:
                    results[column] = {}
                results[column]['Grupo 1'] = group1_data[column]
                results[column]['Grupo 2'] = group2_data[column]

            results_df = pd.DataFrame(columns=['Columna', 'Est. de prueba', 'p-valor', 'Resultado'])
            for column, groups in results.items():
                if 'Grupo 1' in groups and 'Grupo 2' in groups:
                    stat, p = mannwhitneyu(groups['Grupo 1'], groups['Grupo 2'], alternative='two-sided')
                    if p < 0.05:
                        resultado = "Rechazar H0"
                    else:
                        resultado = "No rechazar H0"
                    results_df = results_df._append({'Columna': column, 'Est. de prueba': stat, 'p-valor': p, 'Resultado': resultado}, ignore_index=True)

            # Calcular promedios
            group1_means = group1_data.select_dtypes(include='number').mean()
            group2_means = group2_data.select_dtypes(include='number').mean()
            
            # Crear DataFrames para los promedios
            group1_means_df = pd.DataFrame({'Columna': group1_means.index, 'Promedio Trat Data': group1_means.values})
            group2_means_df = pd.DataFrame({'Columna': group2_means.index, 'Promedio Control Data': group2_means.values})

            file_path, _ = QFileDialog.getSaveFileName(self, "Guardar resultados", "", "Archivos Excel (*.xlsx)")
            if file_path:
                with pd.ExcelWriter(file_path) as writer:
                    results_df.to_excel(writer, index=False, sheet_name='Resultados')
                    group1_data.to_excel(writer, index=False, sheet_name='Grupo Trat Data')
                    group2_data.to_excel(writer, index=False, sheet_name='Grupo Control Data')
                    
                    # Escribir los promedios en una nueva hoja
                    group1_means_df.to_excel(writer, index=False, sheet_name='Promedio Trat Data')
                    group2_means_df.to_excel(writer, index=False, sheet_name='Promedio Control Data')
        else:
            QMessageBox.critical(self, "Error", "Por favor, seleccione los archivos.")


def main():
    app = QApplication(sys.argv)
    selector = Comparar()
    selector.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
