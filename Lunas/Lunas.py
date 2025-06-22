import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
from PIL import Image, ImageTk
from load2mne4 import Participant, Visualize
import panel as pn
from tkinter import ttk


# Datos de prueba
all_participantsl = ["AE", "CL", "EM", "FG", "GH", "GU", "JALO", "JANA", "JG", "LI", "MG", "MJ", "MMA", "PCM", "RANA", "RL", "RR", "VCR"]
selected_participantsl = []
selected_alll = False

# Variables globales para entry_path, output_path y selected_participants
entry_pathl = None
output_pathl = None

to_all = None
to_selected = None

base_path = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(base_path, "img")

class Lunas(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Lunas")
        self.geometry("425x300")

        self.entry_pathl_var = tk.StringVar()
        self.output_pathl_var = tk.StringVar()

        self.icon_path = os.path.join(img_path, "lunaico.png")
        self.iconphoto(True, tk.PhotoImage(file=self.icon_path))

        self.cargar1 = Image.open(os.path.join(img_path, "carpeta.png")).resize((40, 30))
        self.cargar1 = ImageTk.PhotoImage(self.cargar1)
        self.cargar2 = Image.open(os.path.join(img_path, "carpeta.png")).resize((40, 30))
        self.cargar2 = ImageTk.PhotoImage(self.cargar2)
        self.send1 = Image.open(os.path.join(img_path, "send.png")).resize((40, 30))
        self.send1 = ImageTk.PhotoImage(self.send1)
        self.check1 = Image.open(os.path.join(img_path, "check.png")).resize((40, 30))
        self.check1 = ImageTk.PhotoImage(self.check1)
        self.cleanlist = Image.open(os.path.join(img_path, "gom.png")).resize((40, 30))
        self.cleanlist = ImageTk.PhotoImage(self.cleanlist)
        self.moonylist = Image.open(os.path.join(img_path, "lunaico.png")).resize((40, 30))
        self.moonylist = ImageTk.PhotoImage(self.moonylist)

        entry_pathl_label = tk.Label(self, text="Entry Path:", bg="#011A27", fg="white")
        entry_pathl_label.grid(row=0, column=0)
        entry_pathl_entry = tk.Entry(self, textvariable=self.entry_pathl_var, width=40)
        entry_pathl_entry.grid(row=0, column=1)
        entry_pathl_button = tk.Button(self, text="Entrada",image=self.cargar1,compound=tk.LEFT, command=self.select_entry_pathl, bg="#bf8a3d", relief="groove")
        entry_pathl_button.grid(row=0, column=2)

        output_pathl_label = tk.Label(self, text="Output Path:", bg="#011A27", fg="white")
        output_pathl_label.grid(row=1, column=0)
        output_pathl_entry = tk.Entry(self, textvariable=self.output_pathl_var, width=40)
        output_pathl_entry.grid(row=1, column=1)
        output_pathl_button = tk.Button(self, text="Salida", image=self.cargar2,compound=tk.LEFT, command=self.select_output_pathl, bg="#bf8a3d", relief="groove")
        output_pathl_button.grid(row=1, column=2)
        
        save_button = tk.Button(self, text="Enviar", command=self.save_paths, image=self.send1, compound=tk.LEFT, bg="#bf8a3d", relief="groove")
        save_button.grid(row=2, column=1)
        
        self.config(bg="#011A27")

    def select_entry_pathl(self):
        global entry_pathl
        entry_pathl = str(filedialog.askdirectory())
        self.entry_pathl_var.set(entry_pathl)

    def select_output_pathl(self):
        global output_pathl
        output_pathl = str(filedialog.askdirectory())
        self.output_pathl_var.set(output_pathl)

    def save_paths(self):
        global entry_pathl, output_pathl

        entry_pathl = self.entry_pathl_var.get()
        output_pathl = self.output_pathl_var.get()

        if not entry_pathl or not output_pathl:
            messagebox.showwarning("Error", "No valid path")
            return

        # Check if the entry path exists
        if not os.path.exists(entry_pathl):
            messagebox.showwarning("Error", "Entry path does not exist")
            return

        # Check if the output path exists
        if not os.path.exists(output_pathl):
            messagebox.showwarning("Error", "Output path does not exist")
            return

        print("Entry Path:", entry_pathl)
        print("Output Path:", output_pathl)

        self.participants_screen = ParticipantsScreen(self, all_participantsl)
        self.participants_screen.lift()
        self.withdraw()  # Oculta la ventana actual (MainScreen)

    def control_and_pacient():
        print("aqui van los tipos de pacientes")
    
    def run(self):
        self.mainloop()

class ParticipantsScreen(tk.Toplevel):
    def __init__(self, parent, participants):
        super().__init__(parent)

        self.title("Participants")
        self.geometry("600x600")

        self.check1 = Image.open(os.path.join(img_path, "check.png")).resize((40, 30))
        self.check1 = ImageTk.PhotoImage(self.check1)
        self.cleanlist = Image.open(os.path.join(img_path, "gom.png")).resize((40, 30))
        self.cleanlist = ImageTk.PhotoImage(self.cleanlist)
        self.moonylist = Image.open(os.path.join(img_path, "lunaico.png")).resize((40, 30))
        self.moonylist = ImageTk.PhotoImage(self.moonylist)


        self.parent = parent  # Guarda una referencia a la ventana principal
        self.checkbox_vars = {}
        for i, participant in enumerate(participants):
            var = tk.BooleanVar()
            self.checkbox_vars[participant] = var
            checkbox = ttk.Checkbutton(self, style="Black.TCheckbutton", text=participant, variable=var, onvalue=True, offvalue=False, command=lambda participant=participant: self.on_checkbox_toggle(participant))
            checkbox.grid(row=i, column=0, sticky="W")

        # Estilo personalizado para el Checkbutton
        style = ttk.Style()
        style.configure("Black.TCheckbutton", background="#011A27", foreground="white", focuscolor="white", bordercolor="#011A27")

        select_all_button = tk.Button(self, text="Select All", command=self.on_select_all_button_press, image=self.check1, compound=tk.LEFT, bg="#bf8a3d", relief="groove")
        select_all_button.grid(row=len(participants), column=0, sticky="w")

        remove_button = tk.Button(self, text="Remove Selected", command=self.on_remove_button_press, image=self.cleanlist, compound=tk.LEFT, bg="#bf8a3d", relief="groove")
        remove_button.grid(row=len(participants) , column=1, sticky="w")

        self.visualize_button= tk.Button(self, text="Visualize moons", command=self.visualize_moony, image=self.moonylist, compound=tk.LEFT, bg="#bf8a3d", relief="groove")
        self.visualize_button.grid(row=len(participants), column=3, sticky="e")        
        
        self.config(bg="#011A27")

    def on_checkbox_toggle(self, participant):
        if self.checkbox_vars[participant].get():
            selected_participantsl.append(participant)
            print(f"{participant} seleccionado.")
        else:
            selected_participantsl.remove(participant)
            print(f"{participant} deseleccionado.")

    def on_select_all_button_press(self):
        global selected_alll
        selected_alll = not selected_alll
        for participant in all_participantsl:
            self.checkbox_vars[participant].set(selected_alll)
            if selected_alll and participant not in selected_participantsl:
                selected_participantsl.append(participant)
            elif not selected_alll and participant in selected_participantsl:
                selected_participantsl.remove(participant)

        if selected_alll:
            print("Todos los participantes seleccionados.")
        else:
            print("Todos los participantes deseleccionados.")

    def on_remove_button_press(self):
        for participant in selected_participantsl.copy():
            all_participantsl.remove(participant)
            self.checkbox_vars[participant].set(False)
        selected_participantsl.clear()

    def expensive_process(self):
        # Simulate an expensive process
        import time
        time.sleep(5)

        # Get the selected participants as a list and pass it to the other program
        selected_participants_list = selected_participantsl.copy()
        print("Participantes seleccionados:", selected_participants_list)  # Agrega esta línea para imprimir la lista
    
    def visualize_moony(self):
        if not entry_pathl or not output_pathl:
            messagebox.showwarning("Error", "La ruta de entrada y/o salida no está configurada.")
            return

        participants = selected_participantsl or selected_alll
        exclude_patterns = ["ojos"]
        v = Visualize(Participant(participants=participants, input_path=entry_pathl, output_path=output_pathl, exclude_patterns=exclude_patterns), to_all=to_all, to_selected=to_selected)

        # Función para iniciar el servidor en un hilo aparte
        def lanzar_bokeh():
            print("Iniciando servidor Bokeh...")
            bokeh_server = pn.Row(v.moony()).show(port=0)
            bokeh_server.stop()  # Este se ejecuta cuando se cierre la ventana del navegador

        # Inicia el hilo del servidor
        threading.Thread(target=lanzar_bokeh, daemon=True).start()

        print("Servidor lanzado, ventana principal sigue activa.")

if __name__ == "__main__":
    entry_pathl = None
    output_pathl = None
    app = Lunas()
    app.run()