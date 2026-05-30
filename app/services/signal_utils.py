"""Utilidades de procesamiento de senales.

Milestone 2: Procesamiento de la respuesta al impulso.
"""

import numpy as np
import soundfile as sf
from pathlib import Path
from scipy import signal

def cargar_audio(ruta: str) -> tuple[np.ndarray, int]:
    """Carga un archivo de audio y retorna la senal y la frecuencia de muestreo.

    Parameters
    ----------
    ruta : str
        Ruta al archivo de audio a cargar.

    Returns
    -------
    tuple[np.ndarray, int]
        Tupla con (senal, frecuencia_de_muestreo).
        La senal se devuelve como float64 normalizada entre -1 y 1.
        Nota sobre canales: Si el audio es mono, devuelve un arreglo 1D (muestras,).
        Si el audio es multicanal (ej. estéreo), devuelve un arreglo 2D 
        con forma (muestras, canales), donde las filas son el tiempo y las columnas los canales.

    Raises
    ------
    FileNotFoundError
        Si el archivo no existe en la ruta especificada.
    ValueError
        Si el formato del archivo no es soportado (no es .wav ni .flac).
    """
    # 1. Convertimos la ruta a un objeto Path para manejarla de forma segura
    ruta_obj = Path(ruta)
    
    # 2. Verificamos que el archivo realmente exista
    if not ruta_obj.is_file():
        raise FileNotFoundError(f"El archivo no existe en la ruta especificada: {ruta_obj.absolute()}")
    
    # 3. Verificamos la extension (aceptamos .wav y .flac ignorando mayúsculas)
    extension = ruta_obj.suffix.lower()
    if extension not in ['.wav', '.flac']:
        raise ValueError(f"Formato no soportado: '{extension}'. Solo se admiten archivos .wav y .flac.")
    
    # 4. Leemos el archivo. 
    # always_2d=False permite que los archivos mono sean 1D (más fácil de procesar después).
    # dtype='float64' garantiza la normalización automática entre -1 y 1.
    try:
        senal, fs = sf.read(file=str(ruta_obj), dtype='float64', always_2d=False)
    except Exception as e:
        # Capturamos cualquier error interno de la librería (ej. archivo corrupto)
        raise ValueError(f"Error al intentar leer el archivo de audio: {e}")
        
    return senal, fs


def sintetizar_ri(
    t60_por_banda: dict[float, float], fs: int, duracion: float
) -> np.ndarray:
    """Sintetiza una respuesta al impulso artificial a partir de valores T60 por banda.

    Parameters
    ----------
    t60_por_banda : dict[float, float]
        Diccionario {frecuencia_central_Hz: T60_segundos}.
    fs : int
        Frecuencia de muestreo en Hz.
    duracion : float
        Duracion de la respuesta al impulso en segundos.

    Returns
    -------
    np.ndarray
        Respuesta al impulso sintetizada (array 1D).
    """
    raise NotImplementedError("Implementar en Milestone 2")


def obtener_ri_desde_sweep(grabacion: np.ndarray, filtro_inverso: np.ndarray) -> np.ndarray:
    """
    Acciones
    ----------
    La funcion obtener_ri_desde_sweep obtiene la respuesta al impulso mediante deconvolucion de un sine sweep.

    Parameters
    ----------
    grabacion: np.ndarray --> Senal grabada que contiene la respuesta de la sala al sweep.
    
    filtro_inverso: np.ndarray --> Filtro inverso del sweep utilizado.

    Returns
    -------
    np.ndarray
        Respuesta al impulso estimada, normalizada.
    """

    # Realizamos la convolución entre el filtro inverso del sine sweep y la grabacion del sine sweep en el recinto.

    impulso = signal.fftconvolve(grabacion, filtro_inverso, mode='full')
    
    # Buscamos el índice donde ocurre el valor máximo absoluto.

    imp_max = np.argmax(np.abs(impulso))
    
    # Comenzamos en el pico, o ligeramente antes.

    inicio = max(0, imp_max - 15)
    h_recortada = impulso[inicio:]
    
    # 4. Post-procesamiento: Normalizar respecto al pico
    # Dividimos todo el array por el valor máximo absoluto para que quede entre -1 y 1
    pico_maximo = np.max(np.abs(h_recortada))
    
    # Prevenir división por cero en caso de que la señal sea nula
    if pico_maximo > 0:
        h_norm = h_recortada / pico_maximo
    else:
        h_norm = h_recortada


    raise NotImplementedError("Implementar en Milestone 2")


def a_escala_log(signal: np.ndarray) -> np.ndarray:
    """Convierte una senal a escala logaritmica (dB) normalizada.

    Parameters
    ----------
    signal : np.ndarray
        Senal de entrada (array 1D).

    Returns
    -------
    np.ndarray
        Senal en escala logaritmica (dB), normalizada a 0 dB en el maximo.
    """
    raise NotImplementedError("Implementar en Milestone 2")
