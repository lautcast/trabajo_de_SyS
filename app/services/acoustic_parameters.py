"""Servicio de calculo de parametros acusticos segun ISO 3382.

Milestone 3: Analisis de parametros acusticos.
"""

import numpy as np
from scipy.signal import hilbert

from app.services.filter import filtro_octava


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

        # Trabajamos con la energía, elevando al cuadrado la señal.

        energia = signal ** 2

        # Creamos el kernel para el promedio.

        kernel = np.ones(ventana) / ventana

        # Aplicamos la convolución para deslizar la ventana.
        # El mode='same' nos asegura que el arreglo de salida tenga el mismo tamaño que la entrada.

        senal_suavizada = np.convolve(energia, kernel, mode='same')

        return senal_suavizada

    # Segunda opción.

    elif ventana == 'hilbert':

        # Aplicamos la funcion signal.hilbert() de scipy para obtener la señal analítica
        # que es igual a la suma de la señal real con la transformada de Hilbert de la misma.

        # Agregamos np.asarray() para que Pylance entienda correctamente el tipo de dato
        analitica = np.asarray(hilbert(signal))

        # Para calcular la envolvente de la señal real, calculamos la magnitud de la señal analítica

        envolvente = np.abs(analitica)

        return envolvente

    else:
        raise ValueError("El parámetro 'ventana' debe ser 'hilbert' o un entero positivo.")


def integral_schroeder(ri: np.ndarray) -> np.ndarray:
    """Calcula la integral de Schroeder (Energy Decay Curve).

    Parameters
    ----------
    ri : np.ndarray --> Respuesta al impulso (array 1D).

    Returns
    -------
    np.ndarray --> Curva de decaimiento energetico (EDC), normalizada.

    References
    ----------
    .. [1] Schroeder, M. R. (1965). "New method of measuring reverberation
       time." The Journal of the Acoustical Society of America.
    """

    # Elevamos la señal al cuadrado para obtener la energía de cada muestra.

    energia = ri ** 2

    # Damos vuelta el arreglo para calcular la integral discreta.

    energia_inversa = energia[::-1]

    # Llevamos a cabo la integral discreta con la función np.cumsum().
    # El parámetro [::-1] al final lo vuelve a poner en el orden cronológico correcto.

    edc = np.cumsum(energia_inversa)[::-1]

    # Pasamos a la EDC a escala logarítmica, utilizando un valor muy cercano a cero al que llamnamos épsilon
    # para evitar la división por cero.

    epsilon = np.finfo(float).eps

    edc_db = 10 * np.log10(edc / edc[0] + epsilon)


    return edc_db


def regresion_lineal(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """
    Calcula la regresion lineal por minimos cuadrados implementando las fórmulas manualmente.

    Parameters
    ----------
    x : np.ndarray --> Variable independiente.
    
    y : np.ndarray --> Variable dependiente.

    Returns
    -------
    tuple[float, float, float]
        (pendiente, ordenada_al_origen, r_cuadrado)
        pendiente en dB/s, ordenada en dB, coeficiente de determinacion.
    """
    # Primero calculamos la cantidad total de muestras y la guardamos en N.

    N = len(x)

    # Ahora, calculamos las sumatorias que neceistamos para calcular la pendiente 'm' y la ordenada 'b'.
    # Utilizamos np.sum() para sumar todos los elementos del array.

    sum_x = np.sum(x)
    sum_y = np.sum(y)
    sum_xy = np.sum(x * y)
    sum_x2 = np.sum(x**2)

    # Luego aplicamos las fórmulas para la pendiente y la ordenada.

    m = (N * sum_xy - sum_x * sum_y) / (N * sum_x2 - (sum_x)**2)
    b = (sum_y - m * sum_x) / N

    # Ahora calculamos el coeficiente de determinación (R^2):

    # Primero obtenemos los valores predichos con la regresión lineal para cada x.

    y_pred = m * x + b

    # Después obtenemos el promedio de los valores de y.

    y_mean = np.mean(y)

    # Finalmente, aplicamos la ecuación para obtener R^2, calculando primero las sumatorias que la componen.

    # Suma de errores cuadráticos.

    ss_res = np.sum((y - y_pred)**2)

    # Suma total de cuadrados.

    ss_tot = np.sum((y - y_mean)**2)

    # Cálculo de R.

    r_cuadrado = 1 - (ss_res / ss_tot)

    # Pedimos que los valores de m y b sean del tipo float, como indica la firma.

    return float(m), float(b), float(r_cuadrado)


def calcular_parametros_acusticos(ri: np.ndarray, fs: int) -> dict:
    """Calcula los parametros acusticos de una sala a partir de su RI.

    Parameters
    ----------
    ri : np.ndarray --> Respuesta al impulso (array 1D).
    fs : int --> Frecuencia de muestreo en Hz.

    Returns
    -------
    dict --> Diccionario con los parametros acusticos por banda.

    References
    ----------
    .. [1] ISO 3382-1:2009. "Acoustics -- Measurement of room acoustic parameters -- Part 1: Performance spaces."
    """

    # Frecuencias centrales normalizadas según la norma IEC 61620

    frecuencias_centrales = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]

    # Creamos el diccionario con claves correspondientes a los parámetrosa acústicos y valores vacíos

    resultados = {'EDT': {}, 'T10': {}, 'T20': {}, 'T30': {}, 'D50': {}, 'C80': {}}

    # Hacemos un bucle principal por cada frecuencia.

    for f in frecuencias_centrales:

        # Filatramos la RI en la banda de la frecuencia central correspondiente.

        ri_banda = filtro_octava(ri, fc=f, fs=fs, orden = 4)

        # Calculamos la energía total a partir de la energía instantánea de cada muestra.

        ri_banda_cuadrado = ri_banda ** 2
        energia_total = np.sum(ri_banda_cuadrado)

        "-------------------------------------------------------------------------------------------------"

        # D50 (Definición): Es la relacion entre la energia en los primeros 50 ms y la energia total.

        # Multiplicamos los 50 ms por la frecuencia de muestreo para obtener
        # la cantidad de muestras en ese tiempo.

        N50 = int(0.050 * fs)

        # Calculamos la energía total en los primeros 50 ms.

        energia_50 = np.sum(ri_banda_cuadrado[:N50])

        # En la clave 'D50' del diccionario resultados colocamos el valor de este
        # parámetro para la freucencia central f.

        resultados['D50'][f] = (energia_50 / energia_total) * 100 if energia_total > 0 else 0.0

        "-------------------------------------------------------------------------------------------------"

        # C80 (Claridad): Es la relación entre la energía de los primeros 80 ms, y
        # el resto de la energía de la RI.

        # Primero calculamos la cantidad de muestras contenidas en 80 ms.

        N80 = int(0.080 * fs)

        # Luego, en 'energia_80' guardamos toda la energía de esos primeros 80 ms, mientras que
        # en 'energia_tardia_80' guardamos toda la energía del resto de la RI sin los primeros
        # 80 ms.

        energia_80 = np.sum(ri_banda_cuadrado[:N80])
        energia_tardia_80 = np.sum(ri_banda_cuadrado[N80:])

        # Finalmente, calculamos la relacion para hallar C80 y guardamos en resultados.
        # Prevenimos la división por cero teniendo en cuenta que la señal puede ser corta.

        if energia_80 > 0 and energia_tardia_80 > 0:
            resultados['C80'][f] = 10 * np.log10(energia_80 / energia_tardia_80)
        else:
            resultados['C80'][f] = None

        "-------------------------------------------------------------------------------------------------"

        # Ahora, calculamos el EDT y los Tiempos de Reverberación.

        # Primero usamos la función de integral_schroeder() que definimos anteriormente para
        # obtener la envolvente de la RI filtrada en la banda de la frecuencia f correspondiente.

        envolvente_ri_banda = integral_schroeder(ri_banda)

        # Creamos un vector de tiempo con el mismo tamaño que la RI.

        t = np.arange(len(ri_banda)) / fs

        "------------------------------"

        # Hacemos una función auxiliar para encontrar el índice (muestra) donde
        # la curva corta ciertos dB que nos interesan para hallar los parámetros mencionados.

        def buscar_indice(array, value) -> int:
            """
            Acciones
            --------
            La función devuelve el índice correspondiente al valor del array más cercano a value.

            """
            return (np.abs(array - value)).argmin()

        # Con la función buscar_indice(), encontramos los índices de la RI filtrada en
        # la banda con frecuencia central f donde el valor de dB es el que indica el parámetro
        # 'value' utilizado en cada uno de los llamados de la funcion.

        indice_0 = buscar_indice(envolvente_ri_banda, 0)
        indice_5 = buscar_indice(envolvente_ri_banda, -5)
        indice_10 = buscar_indice(envolvente_ri_banda, -10)
        indice_15 = buscar_indice(envolvente_ri_banda, -15)
        indice_25 = buscar_indice(envolvente_ri_banda, -25)
        indice_35 = buscar_indice(envolvente_ri_banda, -35)

        # Función para calcular la pendiente 'm' y extrapolar a -60 dB

        def calcular_tx(indice_inicio, indice_final):
            if indice_final <= indice_inicio or (indice_final - indice_inicio) < 2:
                return None # Previene errores si la curva cae muy de golpe (mala SNR)

            tramo_temporal = t[indice_inicio:indice_final]
            db = envolvente_ri_banda[indice_inicio:indice_final]

            m, b, R_2 = regresion_lineal(tramo_temporal, db)

            extrapolacion = (-60.0) / m if m != 0 else None

            return extrapolacion

        # Asignación final extrapolada a -60dB según la fórmula de tus apuntes

        resultados['EDT'][f] = calcular_tx(indice_0, indice_10)
        resultados['T10'][f] = calcular_tx(indice_5, indice_15)
        resultados['T20'][f] = calcular_tx(indice_5, indice_25)
        resultados['T30'][f] = calcular_tx(indice_5, indice_35)

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

    # 1. Definimos el tamaño de la ventana en muestras (ej. 10 ms)
    window_ms = 10
    ventana_muestras = int((window_ms / 1000) * fs)

    # Esto devuelve la energía suavizada de tamaño completo

    energia_suavizada_completa = suavizar_signal(ri, ventana=ventana_muestras)

    # 3. Submuestreo (Diezmado) para obtener bloques discretos
    # Tomamos un valor cada 'ventana_muestras' saltos

    energia_bloques = energia_suavizada_completa[::ventana_muestras]

    # 4. Pasamos a dB (igual que antes)

    db_bloques = 10 * np.log10(energia_bloques + eps)

    # Eje de tiempo en muestras para cada bloque

    n_blocks = len(db_bloques)
    tiempo_bloques = np.arange(n_blocks) * ventana_muestras + (ventana_muestras / 2)

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
        new_tail_start_block = new_tail_start_samples // ventana_muestras

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
