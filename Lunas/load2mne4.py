import os
import re
import mne
from types import SimpleNamespace
import numpy as np
import matplotlib.pyplot as plt
from ifsoac_3 import Ifsoac
from numba import jit
from datashader import transfer_functions as tf
import datashader as ds
import pandas as pd
from datashader.mpl_ext import dsshow, alpha_colormap
from datashader.colors import inferno, viridis, Hot
from colorcet import palette
palette["viridis"] = viridis
palette["inferno"] = inferno
palette["Hot"] = Hot
from holoviews.operation.datashader import datashade, rasterize
from holoviews import opts
import holoviews as hv
import holoviews.operation.datashader as hd
import warnings
warnings.filterwarnings('ignore')
import panel as pn

all_channels = {"Fp1": "eeg", "Fp2": "eeg", "F7": "eeg", "F3": "eeg", "Fz": "eeg", "F4": "eeg", "F8": "eeg", "T3": "eeg", "C3": "eeg", 
                "Cz": "eeg", "C4": "eeg", "T4": "eeg", "T5": "eeg", "P3": "eeg", "Pz": "eeg", "P4": "eeg", "T6": "eeg", "O1": "eeg", 
                "O2": "eeg", "LOG": "eog", "ROG": "eog", "EKG": "ecg", "EMG": "emg"}

all_participants = ["AE", "CL", "EM", "FG", "GH", "GU", "JALO", "JANA", "JG", "LI", "MG", "MJ", "MMA", "PCM", "RANA", "RL", "RR", "VCR"]

default_path = ""
def_out_path = ""
            
class Verbose:
    active = True

    def chat(s="", continued=False):
        if Verbose.active:
            if continued:
                print(s, end=" ")
            else:
                print(s)

    def endl():
        Verbose.chat()

    def activate():
        Verbose.active = True
        mne.set_log_level('INFO')
        
    def deactivate():
        Verbose.active = False
        mne.set_log_level('CRITICAL')
                
def fix_lengths(mat, min_length=None):
    "Cut every row to the shortest row length."
    if min_length is None:
        min_length = min(len(row) for row in mat)
    nmat = [row[:min_length] for row in mat]
    return nmat

def regenerate_out(in_file, out_file):
    "Regenerate (returns True) out_file if not existent or older than in_file."
    if not os.path.exists(out_file):
        return True
        
    in_modified = os.path.getmtime(in_file)
    out_modified = os.path.getmtime(out_file)

    if in_modified > out_modified:
        return True

    return False

def get_files_in_path(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list
            
class Participant:
    def __init__(self, participants=all_participants, default_freq=200., input_path=default_path, output_path=def_out_path, exclude_patterns=None,
                txt_files=True):
        self.prefixes = participants
        self.default_freq = default_freq
        self.path = input_path
        self.out_path = output_path
        # Check for exclude patterns, that is, texts you don't want in the string file/path to load
        if exclude_patterns is None:
            self.exclude_patterns = []
        else:
            self.exclude_patterns = exclude_patterns
        self.txt_files = txt_files  # test for new txt files

    def _paths_with_files_starting_at(self, path):
        "Trayectorias con al menos 3 archivos .txt de canales a partir de path."
        trayectorias = dict()

        # Recorre los directorios y archivos en el path dado
        for directorio_actual, _, archivos in os.walk(path):
            contador = 0
            sufijos_encontrados = []
            archivos_encontrados = []
            for sufijo in all_channels:
                # Verifica si el nombre del archivo contiene alguna de las cadenas de 'suffix'
                for archivo in archivos:
                    if sufijo.upper() in archivo and archivo.endswith(".txt"):
                        sufijos_encontrados.append(sufijo)
                        archivos_encontrados.append(archivo)
                        contador += 1
                        break

            if contador >= 3:
                trayectoria_completa = directorio_actual  #os.path.join(directorio_actual, archivo)
                trayectorias.update({trayectoria_completa:[sufijos_encontrados, archivos_encontrados]})

        return trayectorias


    def _path_with_prefix(self):
        paths = []

        # Recorre los directorios y archivos en el path dado
        for cur_dir in os.listdir(self.path):
            full_dir = os.path.join(self.path, cur_dir)

            # Verifica si el nombre del directorio empieza con alguno de los prefijos
            for prefix in self.prefixes:
                if cur_dir.startswith(prefix) and os.path.isdir(full_dir):
                    paths.append((prefix, full_dir))
                    break

        return paths
        
    def _get_files(self):
        paths_found = self._path_with_prefix()
        
        res = {prefix:self._paths_with_files_starting_at(path) for prefix, path in paths_found}
        return res  # {prefix:{path_found: [list_of_available_channels, list_of_found_files], ...}, ...}

    def _get_freq(self, fn, default_freq=None):
        "Detect freq from fn name (data within the last '_' and the string ' Hz')"
        
        match = re.search(r"_([^_]+) Hz", fn)
        if match:
            return float(match.group(1))
        else:
            return self.default_freq if default_freq is None else default_freq

    def _exclude(self, path):
        "Returns True iff any of excluded_patters is in string."
        for _p in self.exclude_patterns:
            if _p in path:
                Verbose.chat(f'Path or file "{path}" excluded!')
                return True
        return False
        
    
    def load_raw(self, return_prefixes=False):
        "Returns list of MNE's raws and participant_paths found"
        raws, participant_paths = [], []
        gf = self._get_files()

        if not gf:  # search for fifs if no txt files found
            participant_paths = get_files_in_path(self.out_path)
            return [mne.io.read_raw_fif(out_file, preload=True) for out_file in participant_paths], participant_paths
        
        for prefix, paths in gf.items():
            for path,(chs, files) in paths.items():
                if self._exclude(path): continue
                data, loaded_channels, min_length = [], [], 1e100
                freq = self._get_freq(path)  # gets freq from filename
                Verbose.chat(f"Freq. detected:{freq}\nChannels found:{chs}\nProcessing:{path}")
    
                # check if new files or inexistent fif
                basename = os.path.basename(os.path.normpath(path))
                out_file = os.path.join(self.out_path, prefix) + "_" + basename + "_raw.fif.gz"

                any_new = False
                if self.txt_files:
                    for file in files:
                        if regenerate_out(os.path.join(path, file), out_file):
                            any_new = True
                            break
                
                if not any_new:
                    raws.append(mne.io.read_raw_fif(out_file, preload=True))  #pick_types(include=include_ch).
                    participant_paths.append(out_file)
                    continue

                # load files into list
                for ch, file in zip(chs,files):
                    file_path = os.path.join(path, file)
                    Verbose.chat(file, continued=True)
                    if self._exclude(file_path): continue
                    # Load file
                    Verbose.endl()
                    try:
                        #with warnings.catch_warnings():
                        #    warnings.simplefilter("ignore")
                            channel_data = np.loadtxt(file_path, dtype=float)
                            if channel_data.shape[0] > 0:  # discard empty files
                                if channel_data.shape[0] < min_length:
                                    min_length = channel_data.shape[0]  # to fix_length of ragged data
                                data.append(channel_data)
                                loaded_channels.append(ch)
                    except:
                        Verbose.chat(f'Loading failed for channel {ch}, file {file}!!!')
                chs = loaded_channels  # por si alguno no se cargó
                
                # Crear la matriz de datos EEG y especificar las etiquetas de los canales
                if chs != []: # not all channels excluded/inexistent?
                    try:
                        #np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
                        data = np.array(fix_lengths(data, min_length))
                        Verbose.chat(data.shape)
                        # Crear el objeto RawArray de MNE
                        info = mne.create_info(chs, freq, ch_types=[all_channels[c] for c in chs])
                        raw = mne.io.RawArray(data, info)
                        raw.set_montage("standard_1020")  # sensors positions
                        raws.append(raw)
                        participant_paths.append(path)
                    except: 
                        Verbose.chat(f'Create raw object failed for path "{path}"!!!...')
                    
                    #save fif
                    try: 
                        os.mkdir(self.out_path) 
                    except OSError as error: 
                        pass
                    # TODO: guardar fif
                    raw.save(out_file)
                    Verbose.chat(f'Saved file "{out_file}".')
        return raws, participant_paths


hd.shade.cmap=["lightblue", "darkblue"]
#hv.extension("bokeh", "matplotlib") 

class Preprocessable:
    def __init__(self, participants, to_selected=None, to_all=None, channel_types="eeg"):
        self.parti = participants
        self.to_selected = to_selected
        self.to_all = to_all

    def iterate_cropped_and_filtered(self, to_selected=None, to_all=None, include_ch=["eeg"]):
        if to_selected is None: to_selected = self.to_selected # defaults to init's
        if to_all is None: to_all = self.to_all # defaults to init's
        
        raws, paths = self.parti.load_raw()
        fnames = map(os.path.basename, paths)
        exts = "_raw.fif.gz"
        for raw, file in zip(raws, fnames):
            file = file.rstrip(exts)
            if to_selected is not None:
                s = to_selected.get(file, None)
                if s is not None:
                    to_crop = s.get("crop", None)
                    if to_crop is not None:
                        raw.crop(*to_crop)
                    filter_parms = s.get("filter", None)
                    if filter_parms is not None:
                        raw.filter(*filter_parms)
                    notch_filter_parms = s.get("notch_filter", None)
                    if notch_filter_parms is not None:
                        raw.notch_filter(*notch_filter_parms)
            if to_all is not None:
                to_crop = to_all.get("crop", None)
                if to_crop is not None:
                    raw.crop(*to_crop)
                filter_parms = to_all.get("filter", None)
                if filter_parms is not None:
                    raw.filter(*filter_parms)
                notch_filter_parms = to_all.get("notch_filter", None)
                if notch_filter_parms is not None:
                    raw.notch_filter(*notch_filter_parms)
            yield raw, file

def sensor_pos(raw, shift=100):
    sp = raw.info['chs']  # ch info
    to_plot = raw.ch_names
    for i in range(len(to_plot)):
        yield sp[i]['loc'][:2] * shift
            
class Visualize(Preprocessable):
    
    def head_plot(self, plot_func, **op):
        "Grafica la función plot_func(data, times, file, sp, **op) en una cabeza."
        hv.output(backend="bokeh")
        heads = []
        for raw, file in self.iterate_cropped_and_filtered():
            raw.pick(*self.channel_types)  # Graficar solo canales de EEG
            to_plot = raw.ch_names  # Nombres de los canales
            data, times = raw.get_data(return_times=True)
            sp = sensor_pos(raw)
            img = plot_func(data, times, file, sp, **op)
            label_set = hv.Labels({('x', 'y'): sp, 'text': to_plot}, ['x', 'y'], 'text')
            head = (img * label_set).opts(
                opts.Labels(backend="bokeh", text_color='text', cmap='Category20', padding=0.2),
                opts.Labels(backend="matplotlib", color='text', cmap='Category20', padding=0.2)
            )
            heads.append(head)

        # Decide qué opciones aplicar según el backend
        if hv.output.info().backend == 'matplotlib':
            layout_opts = {'width': 800}
        else:
            layout_opts = {'height': 800, 'width': 800}

        return hv.Layout(heads).cols(4).opts(
            opts.Layout(**layout_opts)
        )

    
    def channel_series(self, select=None, filters=None):
        "Plot channel series, selec can be a dict of crop duples (start, stop) indexed by filenames."
        colors = plt.cm.bwr(np.linspace(0,1,19))
        for raw, file in self.iterate_cropped_and_filtered(select, filters):
            to_plot = raw.ch_names[:19]
            data, times = raw.get_data(picks=to_plot, return_times=True)
            fig, ax = plt.subplots(figsize=(4.5, 3))
            for i, d in enumerate(data):
                ax.set_title(file)
                ax.plot(times, d+3*i, color=colors[i], lw=.1)
                #ax.plot(times, np.mean(data, axis=0))
            plt.show()
                  
    def spectral(self, select=None, filters=None, average=False):
        for raw, file in self.iterate_cropped_and_filtered(select, filters):
            image = raw.compute_psd().plot(average=average)  #average=True, picks="data")
            ax = image.get_axes()
            ax[0].set_title(file)
        plt.show()
 
    def hplot_series(self, **op):
        op_defaults = {'fk':0.005, 'width':5, 'height':0.7, 'linewidth':0.1, 'vscale':1, 
                       'my_filter':None, 'my_notch':None, 'select':None}
        """locals().update(op_defaults)
        locals().update(op)"""
        op_defaults.update(op)
        op = SimpleNamespace(**op_defaults)
        raws, participant_paths = self.parti.load_raw()
        
        for raw, part in zip(raws, participant_paths):
            # Obtener las coordenadas de los sensores
            sensor_pos = raw.info['chs'][0:19]  # Obtén las primeras 20 posiciones de los sensores
            if op.my_filter is not None:
                raw.filter(*op.my_filter)
            if op.my_notch is not None:
                raw.notch_filter(op.my_notch)
            if op.select is not None:
                data = raw.get_data(start=op.select[0], stop=op.select[1])
            else:
                data = raw.get_data()
            # Crear una figura para situar los gráficos en la posición de los sensores
            fig = plt.figure(figsize=(8, 8))
            #ax = fig.add_subplot(111, projection='3d')  # Utilizar proyección 3D para mostrar las coordenadas
            ax = fig.add_subplot(111)

            # Iterar sobre cada sensor y situar el gráfico en su posición correspondiente
            for i, sensor in enumerate(sensor_pos):
                try:
                    # Aquí puedes personalizar el gráfico según tus necesidades
                    title = sensor['ch_name']  # Configura el título del gráfico como el nombre del sensor
                    sl=sensor['loc'][:2]
                    ax.set(xlim=(-0.15, 0.15), ylim=(-0.1, 0.15))
                    ax.text(sl[0], sl[1] * op.vscale, title)
                    ax.plot(np.linspace(0, op.fk, len(data[i])) * op.width + sl[0], 
                                data[i] * op.fk * op.height + sl[1] * op.vscale, 
                                linewidth=op.linewidth)  # Traza los datos del sensor
                except:
                    Verbose.chat(f'Plot failed for sensor {i}!!!')
            plt.box(None)
            plt.axis(False)
            ax.set_title(part)
            plt.show()

    # *********************************************
    def ifs(self, select=None, filters=None, nsides=4):
        "IFS."  
        hv.output(backend="bokeh")#, size=800)  # Set the size here
        heads = []
        for raw, file in self.iterate_cropped_and_filtered(select, filters):
            raw.pick_types(eeg=True)  # plot only eeg channels
            to_plot = raw.ch_names  # ch names
            data, times = raw.get_data(return_times=True)
            dfs = Ifsoac(data, nsides=nsides, rotate=np.pi/4).to_dataframes()
            # dfs = [df + sensor_pos[i]['loc'][:2]*sloc for i, df in enumerate(dfs)]
            dfs = [df + sp for df, sp in zip(dfs, sensor_pos(raw))]
            length = len(dfs[0])
            df = pd.concat(dfs, ignore_index=True)
            points = hv.Points(df)
            img = datashade(points, cmap=palette["bmw"]).opts(bgcolor="black", title=file)
            label_set =  hv.Labels({('x', 'y'): list(sensor_pos(raw)), 'text': to_plot}, ['x', 'y'], 'text')
            head = (img * label_set).opts(opts.Labels(text_color='text', cmap='Category20', padding=0.2))
            heads.append(head)
        return hv.Layout(heads).cols(4)

    def aladdin(self, select=None, filters=None, nsides=4):
        "IFS on a carpet."  
        return self.ifs(select, filters, nsides=4)
    
    
    def moony(self, select=None, filters=None, nsides=500):
        "IFS on a circle."
        # Set the HoloViews backend to Bokeh
        hv.extension("bokeh")
        # Llamar a la función ifs con los mismos argumentos
        layout = self.ifs(select, filters, nsides=nsides)
        # Combine the plots into a single plot using .cols(1)
        combined_plot = layout.cols(1)
        return combined_plot


# Cargar participantes
participants = ["AE", "CL", "EM", "FG"]
exclude_patterns = ["ojos"]
input_path = r"C:/Users/Toshiba/Desktop/Lunas4/SNI CONGRESO"
output_path = r"C:/Users/Toshiba/Desktop/Lunas4/FIF"

p = Participant(participants=participants, input_path=input_path, output_path=output_path, exclude_patterns=exclude_patterns, txt_files=False)

def crop(left=0):
    return {"crop":(left, 5*60+left)}

# Configurar opciones para visualización
to_selected = {
    "FG_Datos": crop(20),
    "FG_Datos-reducidos": {"crop": (15, 5 * 60 - 0.01)},
    "RL_Datos reducidos": crop(),
    "EM_Segmentos": crop(20),
    "MG_Datos reducidos": crop(20),
    "GU_Datos": crop(),
    "RR_Datos": crop(),
    "JG_Datos reducidos": crop(25),
    "JANA_Frecuencia reducida": crop(25),
    "MMA_Datos reducidos": crop(20),
    "PCM_Datos reducidos": crop(10),
    "JALO_Frecuencia reducida": crop(150),
    "AE_Datos reducidos": crop(),
    "CL_Datos reducidos": crop(50),
    "MJ_Frecuencia-Reducida": crop(50),
}

to_all = {"filter": (0.5, 40), "notch_filter": (60,)}

# Crear objeto Visualize
v = Visualize(p, to_selected=to_selected, to_all=to_all)

# Configurar el backend de HoloViews para que utilice Matplotlib
hv.extension("bokeh")
