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
    # Convertimos la ruta o direccion del archivo a un objeto Path para manejarlo de forma segura
    
    ruta_obj = Path(ruta)
    
    # Verificamos que el archivo realmente exista. Caso contrario, devolvemos un error.

    if not ruta_obj.is_file():
        raise FileNotFoundError(f"El archivo no existe en la ruta especificada: {ruta_obj.absolute()}")
    
    # Verificamos la extension (aceptamos .wav y .flac ignorando mayúsculas)

    extension = ruta_obj.suffix.lower()

    if extension not in ['.wav', '.flac']:
        raise ValueError(f"Formato no soportado: '{extension}'. Solo se admiten archivos .wav y .flac.")
    
    # Leemos el archivo. 
    # always_2d=False permite que los archivos mono sean 1D (más fácil de procesar después).
    # dtype='float64' garantiza la normalización automática entre -1 y 1.
    
    try:
        senal, fs = sf.read(file=str(ruta_obj), dtype='float64', always_2d=False)
    except Exception as e:

        # Capturamos cualquier error interno de la librería.

        raise ValueError(f"Error al intentar leer el archivo de audio: {e}")
    
    # Creamos un diccionario que guarde las variables que debe devolver la funcion.

    diccionario = {senal, fs}

    return diccionario


from app.services.filter import filtro_octava

def sintetizar_ri(t60_por_banda: dict[float, float], fs: int, duracion: float) -> np.ndarray:
    """
    Sintetiza una respuesta al impulso con valores de T60 conocidos por banda.

    Parameters
    ----------
    t60_por_banda : dict[float, float] --> Diccionario {frecuencia_central_Hz: T60_segundos}. Ejemplo: {125: 2.0, 250: 1.8, 500: 1.5, 1000: 1.2, 2000: 1.0, 4000: 0.8}
    fs : int --> Frecuencia de muestreo en Hz.
    duracion : float --> Duracion total de la RI sintetizada en segundos.

    Returns
    -------
    np.ndarray --> Respuesta al impulso sintetizada y normalizada.
    """
    # Calculamos la cantidad total de muestras y creamos el vector de tiempo (t)

    total_muestras = int(fs * duracion)
    t = np.arange(total_muestras) / fs
    
    # Inicializamos un arreglo vacío de ceros donde iremos sumando cada banda

    ri_total = np.zeros(total_muestras)
    
    # Fabricamos un bucle que 

    for freq_central, t60 in t60_por_banda.items():

        # Generamos un ruido blanco con la funcion np.random.randn
        
        ruido_blanco = np.random.randn(total_muestras)
        
        # Filtramos con filtro pasa-banda centrado en la frecuencia central
   
        ruido_filtrado = filtro_octava(ruido_blanco, freq_central, fs)
        
        # Aplicar la envolvente exponencial
        # Matemáticamente, para que la energía caiga 60 dB en t = T60, el coeficiente de atenuación alpha de la amplitud es ln(1000) / T60
        
        alpha = np.log(1000) / t60
        envolvente = np.exp(-alpha * t)
        
        # Multiplicamos el ruido filtrado por la curva de decaimiento

        componente_banda = ruido_filtrado * envolvente
        
        # Sumamos todas las componentes filtradas en el arreglo hecho anteriormente

        ri_total += componente_banda
        
    # Normalizamos la senal resultante, buscando el pico máximo absoluto y dividiendo todo por ese valor
    
    valor_maximo = np.max(np.abs(ri_total))
    if valor_maximo > 0:
        ri_total = ri_total / valor_maximo
        
    return ri_total


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
    np.ndarray -- > Respuesta al impulso estimada, normalizada.
    """

    # Realizamos la convolución entre el filtro inverso del sine sweep y la grabacion del sine sweep en el recinto.

    ri = signal.fftconvolve(grabacion, filtro_inverso, mode='full')
    
    # Buscamos el índice donde ocurre el valor máximo absoluto.

    indice_max = np.argmax(np.abs(ri))
    
    # Comenzamos en el pico, o ligeramente antes.

    inicio = max(0, indice_max - 15)
    ri_recortado = ri[inicio:]
    
    # Dividimos todo el array por el valor máximo absoluto para que quede entre -1 y 1
    pico_maximo = np.max(np.abs(ri_recortado))
    
    # Prevenir división por cero en caso de que la señal sea nula
    if pico_maximo > 0:
        h_norm = ri_recortado / pico_maximo
    else:
        h_norm = ri_recortado

    return h_norm


def a_escala_log(signal: np.ndarray) -> np.ndarray:
    """Convierte una senal a escala logaritmica (dB) normalizada.

    Parameters
    ----------
    signal : np.ndarray --> Senal de entrada (array 1D).

    Returns
    -------
    np.ndarray --> Senal en escala logaritmica (dB), normalizada a 0 dB en el maximo.
    """

    # Calculamos la amplitud de la senal

    amplitud = np.abs(signal)

    # Calculamos el maximo de amplitud de la senal

    amp_max = np.max(amplitud)

    # Evitamos la division por cero

    if amp_max == 0.0:
        return np.full_like(signal, -120.00 , dtype=float)
    else:
        pass

    # Normalizamos la senal

    signal_normalizada = amplitud/amp_max

    # Evitamos el logaritmo de cero

    epsilon = np.finfo(float).eps
    signal_final = np.maximum(signal_normalizada, epsilon)

    # Finalmente, pasamos la senal a escala logaritmica

    signal_db = 20 * np.log(signal_final)

    # Definimos el piso de ruido para que no hayan niveles extremadamente negativos

    signal_db = np.maximum(signal_db, -120.00)

    return signal_db