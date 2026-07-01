"""Servicio de calculo de parametros acusticos segun ISO 3382.

Milestone 3: Analisis de parametros acusticos.
"""

import numpy as np
from scipy.signal import hilbert

def suavizar_signal(signal: np.ndarray, ventana: int|str = 'hilbert') -> np.ndarray:
    """Aplica un suavizado por media movil a la senal.

    Parameters
    ----------
    signal : np.ndarray --> Senal de entrada (array 1D).
    
    ventana : int --> Tamaño de la ventana de suavizado en muestras.

    Returns
    -------
    np.ndarray --> Senal suavizada, de la misma longitud que ``signal``.
    """
    
    # Dependiendo la ventana escogida por el usuario, se tienen dos opciones.

    # Primera opción.   

    if isinstance(ventana, int) and ventana > 0:
        
        # Trabajamos con la energía.
        
        energia = signal ** 2
        
        # Creamos el kernel para el promedio.

        kernel = np.ones(ventana) / ventana
        
        # Aplicamos la convolución para deslizar la ventana rápidamente.
        # El mode='same' nos asegura que el arreglo de salida tenga el mismo tamaño que la entrada.

        senal_suavizada = np.convolve(energia, kernel, mode='same')
        
        return senal_suavizada

    # Segunda opción.

    elif ventana == 'hilbert':
        
        analitica = hilbert(signal)
        envolvente = np.abs(analitica)
        
        # Nota: Hilbert devuelve amplitud. Si los pasos posteriores requieren 
        # estrictamente energía, puedes devolver envolvente**2
        return envolvente
        
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

    # Frecuencias centrales normalizadas según la norma IEC 61620
    
    frecuencias_centrales = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
    
    # Creamos el diccionario valores vacíos y claves correspondientes a los parámetrosa acústicos.

    resultados = {'EDT': {}, 'T10': {}, 'T20': {}, 'T30': {}, 'D50': {}, 'C80': {}}

    # Hacemos un bucle principal por cada frecuencia.

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
    ri : np.ndarray --> Respuesta al impulso (array 1D).
    
    fs : int --> Frecuencia de muestreo en Hz.

    Returns
    -------
    int --> Indice de la muestra donde se estima el punto de truncamiento.

    Notes
    -----
    El punto de truncamiento se usa para corregir la integral de Schroeder. Las muestras 
    despues del punto de truncamiento se reemplazan por la extrapolacion de la recta de 
    regresion antes de integrar.

    References
    ----------
    [1] Lundeby, A. et al. (1995). "Uncertainties of measurements in room acoustics." Acta Acustica.
    """

    # Prevención: evitar ceros absolutos para el cálculo de logaritmos
    eps = np.finfo(float).eps
    
    # Primer Inciso --> Calcular la curva de decaimiento promediada en intervalos.

    # Pasamos la RI a energía (cuadrado)
    energia = ri ** 2
    
    window_ms = 10
    window_samples = int((window_ms / 1000) * fs)
    
    # Agrupamos en bloques y promediamos
    n_blocks = len(energia) // window_samples
    if n_blocks == 0:
        return len(ri), 0.0 # Fallback si la RI es anormalmente corta
        
    energia_truncada = energia[:n_blocks * window_samples]
    energia_bloques = energia_truncada.reshape(n_blocks, window_samples).mean(axis=1)
    
    # Convertimos a dB
    db_bloques = 10 * np.log10(energia_bloques + eps)
    
    # Eje de tiempo en muestras para cada bloque (tomamos el centro del bloque)
    tiempo_bloques = np.arange(n_blocks) * window_samples + (window_samples / 2)
    
    # Encontramos el pico máximo para no incluir la subida inicial en la regresión
    peak_idx = np.argmax(db_bloques)

    # Segundo Inciso --> Estimar el nivel de ruido de fondo (últimos 10%).

    tail_start_idx = int(n_blocks * 0.9)
    if tail_start_idx <= peak_idx:
        tail_start_idx = n_blocks - 1 # Fallback de seguridad
        
    noise_level = np.mean(db_bloques[tail_start_idx:])
    
    # Parámetros de iteración
    max_iter = 10
    tolerance_db = 0.1
    slope = 0
    intercept = 0

    # Quinto Inciso --> Iterar: recalcular el nivel de ruido, el punto de cruce y la regresion hasta convergencia.

    for iteracion in range(max_iter):
       
        # Tercer Inciso --> Punto de cruce preliminar (ruido + 10 dB).
        threshold = noise_level + 10
        
        # Buscar el primer bloque que cruza el umbral después del pico
        cross_idx = peak_idx
        for j in range(peak_idx, n_blocks):
            if db_bloques[j] < threshold:
                cross_idx = j
                break
                
        # Si no hay suficiente caída, abortamos la iteración
        if cross_idx == peak_idx or cross_idx - peak_idx < 3:
            break
            
        # Cuarto Inciso --> Realizar regresión lineal desde el pico hasta el punto de cruce preliminar
        x_reg = tiempo_bloques[peak_idx:cross_idx]
        y_reg = db_bloques[peak_idx:cross_idx]
        
        # Ajuste polinómico de grado 1 (recta: y = mx + b)
        slope, intercept = np.polyfit(x_reg, y_reg, 1)
        
        # Si la pendiente es positiva, algo falló (no es un decaimiento)
        if slope >= 0:
            break
            
        # Encontrar dónde la nueva recta cruza el ruido actual (en muestras)
        cross_x_samples = (noise_level - intercept) / slope
        
        # Recalcular el nivel de ruido usando un margen de seguridad después del cruce
        # (ej. 10% de la longitud restante o un valor fijo, aquí usamos el 10% del total como margen)
        margin_samples = int(0.1 * len(ri))
        new_tail_start_samples = int(cross_x_samples + margin_samples)
        new_tail_start_block = new_tail_start_samples // window_samples
        
        # Asegurar que no nos pasamos de los límites del arreglo
        if new_tail_start_block >= n_blocks:
            new_tail_start_block = int(n_blocks * 0.9)
            
        new_noise_level = np.mean(db_bloques[new_tail_start_block:])
        
        # Verificar convergencia
        if abs(new_noise_level - noise_level) < tolerance_db:
            noise_level = new_noise_level
            break
            
        noise_level = new_noise_level

    # Sexto Inciso --> El punto de truncamiento final.

    if slope < 0:
        trunc_sample = int((noise_level - intercept) / slope)
    else:
        # Fallback si no hubo un decaimiento claro (señal con bajísimo SNR)
        trunc_sample = len(ri)
        
    # Clamping: Asegurarnos de que el índice devuelto sea válido para el array original
    trunc_sample = max(0, min(trunc_sample, len(ri) - 1))
    
    return trunc_sample, float(noise_level)