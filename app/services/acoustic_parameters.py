"""Servicio de calculo de parametros acusticos segun ISO 3382.

Milestone 3: Analisis de parametros acusticos.
"""

import numpy as np
from scipy.signal import hilbert

def suavizar_signal(signal: np.ndarray, ventana: int|str = 'hilbert') -> np.ndarray:
    """Aplica un suavizado por media movil a la senal.

    Parameters
    ----------
    signal : np.ndarray
        Senal de entrada (array 1D).
    ventana : int
        Tamano de la ventana de suavizado en muestras.

    Returns
    -------
    np.ndarray
        Senal suavizada, de la misma longitud que ``signal``.
    """
    if ventana == 'hilbert':
        # --- Opción B: Envolvente de Hilbert ---
        analitica = hilbert(signal)
        envolvente = np.abs(analitica)
        
        # Nota: Hilbert devuelve amplitud. Si los pasos posteriores requieren 
        # estrictamente energía, puedes devolver envolvente**2
        return envolvente
        
    elif isinstance(ventana, int) and ventana > 0:
        # --- Opción A: Media Móvil ---
        # 1. Trabajamos con la energía (amplitud al cuadrado)
        energia = signal ** 2
        
        # 2. Creamos el kernel para el promedio
        kernel = np.ones(ventana) / ventana
        
        # 3. Aplicamos la convolución para deslizar la ventana rápidamente
        # mode='same' asegura que el arreglo de salida tenga el mismo tamaño que la entrada
        senal_suavizada = np.convolve(energia, kernel, mode='same')
        
        return senal_suavizada
        
    else:
        raise ValueError("El parámetro 'ventana' debe ser 'hilbert' o un entero positivo.")


def integral_schroeder(ri: np.ndarray) -> np.ndarray:
    """Calcula la integral de Schroeder (Energy Decay Curve).

    Parameters
    ----------
    ri : np.ndarray
        Respuesta al impulso (array 1D).

    Returns
    -------
    np.ndarray
        Curva de decaimiento energetico (EDC), normalizada.

    References
    ----------
    .. [1] Schroeder, M. R. (1965). "New method of measuring reverberation
       time." The Journal of the Acoustical Society of America.
    """
    
    # 1. Elevamos la señal al cuadrado para obtener la energía de cada muestra.
    energia = ri ** 2
    
    # 2. Aplicamos la integral hacia atrás. 
    # energia[::-1] da vuelta el arreglo.
    # np.cumsum() hace la suma acumulativa (la integral discreta).
    # [::-1] al final lo vuelve a poner en el orden cronológico correcto.
    edc = np.cumsum(energia[::-1])[::-1]
    
    # 3. Normalizamos la curva. 
    # Como es una suma que va bajando, el valor máximo siempre está en el índice 0.
    # Al dividir todo por ese máximo, la curva arrancará exactamente en 1.0.
    edc_normalizada = edc / np.max(edc)
    
    return edc_normalizada


def regresion_lineal(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Calcula la regresion lineal por minimos cuadrados.

    Parameters
    ----------
    x : np.ndarray
        Variable independiente (array 1D).
    y : np.ndarray
        Variable dependiente (array 1D).

    Returns
    -------
    pendiente : float
        Pendiente de la recta ajustada (m).
    ordenada : float
        Ordenada al origen de la recta ajustada (b).
    """
    # Utilizamos np.polyfit de NumPy.
    # El '1' indica que queremos ajustar un polinomio de grado 1 (una línea recta: y = mx + b).
    # Esta función aplica automáticamente el método de mínimos cuadrados.
    coeficientes = np.polyfit(x, y, 1)
    
    # polyfit devuelve un arreglo con los coeficientes de mayor a menor grado.
    # El índice 0 es 'm' (la pendiente) y el índice 1 es 'b' (la ordenada al origen).
    # Los forzamos a tipo float nativo de Python para cumplir exactamente con el Type Hint de la firma.
    pendiente = float(coeficientes[0])
    ordenada = float(coeficientes[1])
    
    return pendiente, ordenada


def calcular_parametros_acusticos(ri: np.ndarray, fs: int) -> dict:
    """Calcula los parametros acusticos de una sala a partir de su RI.

    Parameters
    ----------
    ri : np.ndarray
        Respuesta al impulso (array 1D).
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    dict
        Diccionario con los parametros acusticos por banda.

    References
    ----------
    .. [1] ISO 3382-1:2009. "Acoustics -- Measurement of room acoustic
       parameters -- Part 1: Performance spaces."
    """

    # Frecuencias centrales típicas de bandas de octava (en Hz)
    frecuencias_centrales = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
    
    # Estructura del diccionario de salida tal como requiere la firma
    resultados = {
        'EDT': {}, 'T10': {}, 'T20': {}, 'T30': {}, 'D50': {}, 'C80': {}
    }

    # Bucle principal por cada banda de frecuencia
    for fc in frecuencias_centrales:
        # --- 0. Filtrado ---
        # Aquí aplicarías tu banco de filtros (ej. scipy.signal.sosfiltfilt)
        # ri_banda = aplicar_filtro_octava(ri, fs, fc) 
        
        # Para mantener el ejemplo enfocado en la matemática de la imagen, 
        # asignamos 'ri' directo. En tu versión final, usá 'ri_banda'.
        ri_banda = ri 
        
        # --- 1. Cálculos de Energía Temprana y Tardía ---
        ri_sq = ri_banda ** 2
        energia_total = np.sum(ri_sq)
        
        # D50 (Definición): Primeros 50 ms
        N50 = int(0.050 * fs)
        energia_50 = np.sum(ri_sq[:N50])
        resultados['D50'][fc] = (energia_50 / energia_total) * 100 if energia_total > 0 else 0.0
        
        # C80 (Claridad): Primeros 80 ms vs el resto
        N80 = int(0.080 * fs)
        energia_80 = np.sum(ri_sq[:N80])
        energia_tardia_80 = np.sum(ri_sq[N80:])
        
        if energia_80 > 0 and energia_tardia_80 > 0:
            resultados['C80'][fc] = 10 * np.log10(energia_80 / energia_tardia_80)
        else:
            resultados['C80'][fc] = None # Manejo seguro por si la señal es muy corta

        # --- 2. Curva de Schroeder ---
        # Integración hacia atrás: suma acumulada del arreglo invertido y lo volvemos a invertir
        schroeder = np.cumsum(ri_sq[::-1])[::-1]
        
        # Reemplazamos los ceros por un valor minúsculo (eps) para que el log10 no tire error
        schroeder = np.where(schroeder == 0, np.finfo(float).eps, schroeder)
        schroeder_db = 10 * np.log10(schroeder / np.max(schroeder))
        
        # Vector de tiempo
        t = np.arange(len(ri_banda)) / fs
        
        # --- 3. Decaimientos y Regresiones Lineales ---
        # Función auxiliar para encontrar el índice (muestra) donde la curva corta ciertos dB
        def find_idx(array, value):
            return (np.abs(array - value)).argmin()
            
        # Puntos de corte exigidos por la teoría
        idx_0 = find_idx(schroeder_db, 0)
        idx_m5 = find_idx(schroeder_db, -5)
        idx_m10 = find_idx(schroeder_db, -10)
        idx_m15 = find_idx(schroeder_db, -15)
        idx_m25 = find_idx(schroeder_db, -25)
        idx_m35 = find_idx(schroeder_db, -35)
        
        # Función para calcular la pendiente 'm' y extrapolar a -60 dB
        def calcular_tx(idx_start, idx_end):
            if idx_end <= idx_start or (idx_end - idx_start) < 2:
                return None # Previene errores si la curva cae muy de golpe (mala SNR)
            
            t_slice = t[idx_start:idx_end]
            db_slice = schroeder_db[idx_start:idx_end]
            
            # np.polyfit(x, y, grado) devuelve [pendiente, ordenada_al_origen]
            m, _ = np.polyfit(t_slice, db_slice, 1)
            
            return -60.0 / m if m != 0 else None

        # Asignación final extrapolada a -60dB según la fórmula de tus apuntes
        resultados['EDT'][fc] = calcular_tx(idx_0, idx_m10)
        resultados['T10'][fc] = calcular_tx(idx_m5, idx_m15)
        resultados['T20'][fc] = calcular_tx(idx_m5, idx_m25)
        resultados['T30'][fc] = calcular_tx(idx_m5, idx_m35)

    return resultados


def metodo_lundeby(ri: np.ndarray, fs: int) -> int:
    """Estima el punto de truncamiento de la RI (metodo de Lundeby).

    Parameters
    ----------
    ri : np.ndarray
        Respuesta al impulso (array 1D).
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    int
        Indice de la muestra donde se estima el punto de truncamiento.

    Notes
    -----
    Esta funcion es **opcional** (extra credit).

    References
    ----------
    .. [1] Lundeby, A. et al. (1995). "Uncertainties of measurements in
       room acoustics." Acta Acustica.
    """
    raise NotImplementedError("Implementar en Milestone 3 (opcional)")

#prueba