"""Tests para los servicios de procesamiento de senales (Milestone 2)."""

from signal import signal

import numpy as np
import pytest as pytest
from app.services.signal_utils import a_escala_log, cargar_audio
from scipy.io import wavfile
from scipy.signal import butter, filtfilt
from app.services.signal_utils import sintetizar_ri, obtener_ri_desde_sweep
from app.routers.signals import generar_sine_sweep
from scipy.signal import fftconvolve
from app.services.signal_utils import a_escala_log
from scipy.signal import freqz
from app.services.filter import filtro_octava

class TestCargarAudio:
    """Tests para la funcion cargar_audio."""

    def test_cargar_audio_no_existe(self):
        """Verifica que se lanza FileNotFoundError si el archivo no existe."""

        #Si se carga un archivo que no existe, la función lanza un error de tipo FileNotFoundError, lo cual es el comportamiento esperado.
        with pytest.raises(FileNotFoundError):
            cargar_audio("archivo_que_no_existe.wav")

    def test_cargar_audio_wav(self, tmp_path):
        """Verificar carga correcta de archivo WAV."""

        #Se crea la ruta temporta para el archivo de prueba, 
        
        ruta_dummy = tmp_path / "prueba.wav"
        fs_esperada = 44100
        
        #Se genera una señal dummy con valores aleatorios
        senal_dummy = np.random.randint(-32768, 32767, fs_esperada, dtype=np.int16)
        wavfile.write(ruta_dummy, fs_esperada, senal_dummy)

        #Ejecutamos la función
        signal, fs = cargar_audio(str(ruta_dummy))

        #Verificamos que cargó bien la info
        assert fs == fs_esperada
        assert isinstance(signal, np.ndarray)
        assert len(signal) == len(senal_dummy)

    def test_cargar_audio_formato_invalido(self, tmp_path):
        """Verificar que lanza error con formato no soportado."""

        #A partir de la ruta temporal, se crea un archivo de texto que indica que no es un audio válido.
        ruta_invalida = tmp_path / "falso_audio.txt"
        ruta_invalida.write_text("Esto es texto, no es un archivo de audio.")

        #Al intentar cargar este archivo con la función cargar_audio, indicamos que el formato no es soportado.
        with pytest.raises(ValueError): 
            cargar_audio(str(ruta_invalida))

    def test_cargar_audio_normalizacion(self, tmp_path):
        """Verificar que la salida esta normalizada entre -1 y 1."""

        #Se crea la ruta temporta para el archivo de prueba, 
        #Se genera una señal con valores extremos para asegurarnos de que la función de normalización se active.
        ruta_dummy = tmp_path / "prueba_norm.wav"
        fs_esperada = 44100

        #Se genera una señal con valores extremos (máximo positivo, máximo negativo y un valor intermedio) para probar la normalización
        #Se adjunta la ruta del archivo temporal, la frecuencia de muestreo esperada y la señal con valores extremos
        senal_extrema = np.array([32767, 0, -32768, 15000], dtype=np.int16)
        wavfile.write(ruta_dummy, fs_esperada, senal_extrema)

        signal, _ = cargar_audio(str(ruta_dummy))

        #calculamos el máximo de la señal con la función np.max(np.abs(signal)) para obtener la amplitud máxima absoluta de la señal cargada
        max_amplitud = np.max(np.abs(signal))
        assert max_amplitud <= 1.0

        assert max_amplitud > 0.0


class TestAEscalaLog:
    """Tests para la funcion a_escala_log."""
    def test_a_escala_log_salida_ndarray(self):

        """Verifica que retorna un np.ndarray."""

        #Se crea un array de prueba con valores positivos para evitar problemas con el logaritmo.
        #al proponer valores de 1.0 y 0.5, se espera que el resultado en dB sea 0 dB para el valor 1.0 (Full Scale) y aproximadamente -6 dB para el valor 0.5
        #Al definir el parámetro db a escala logarítmica, se espera que la función a_escala_log convierta los valores lineales a decibelios, y que el resultado sea un array de tipo np.ndarray.
        x = np.array([1.0, 0.5])
        db = a_escala_log(x)
        assert isinstance(db, np.ndarray)

    def test_a_escala_log_maximo_cero(self):
        """Verifica que el valor maximo de la salida (Full Scale) es 0 dB."""
        #Se utiliza una señal con valores aleatorios positivos y negativos
        np.random.seed(42) #Con la semilla nos aseguramos que el test sea reproducible
        x = np.random.uniform(-0.8, 0.8, 100) 

        #Se indica un pico máximo artificial conocido
        x[50] = 1.0 

        db = a_escala_log(x)

        #El máximo absoluto en lineal (1.0), le debe corresponder 0.0 dB
        assert np.isclose(np.max(db), 0.0, atol=1e-10)

    def test_a_escala_log_relacion(self):
        """Verifica que una senal con amplitud mitad da aproximadamente -6 dB."""
        #Comparamos el valor máximo (1.0) con su mitad exacta (0.5)
        x = np.array([1.0, 0.5])
        db = a_escala_log(x)

        #En audio (presión/voltaje), 20 * log10(0.5 / 1.0) = -6.02059... dB
        #Usamos np.isclose con tolerancia porque -6 es una aproximación teórica
        assert np.isclose(db[1], -6.0206, atol=1e-4)

    def test_a_escala_log_cero_absoluto(self):
        """
        Verifica que la funcion maneje correctamente muestras con valor 0.0
        para evitar el error matematico de log10(0) = -Infinito.
        """
        #Se crea un Array trampa para probar la funcion: tiene un cero en el medio
        x = np.array([1.0, 0.0, 0.5])

        #Si la función no tiene protección, esto lanzará un RuntimeWarning o crasheará
        db = a_escala_log(x)

        #El cero lineal debe convertirse en un valor dB negativo muy grande (el piso de ruido), pero NUNCA en un -Inf o NaN (Not a Number) que rompan cálculos posteriores.
        assert not np.isinf(db[1]), "La función devolvió -Inf. Debe sumar un epsilon antes del log."
        assert not np.isnan(db[1]), "La función devolvió NaN."
        # Asumimos un piso de ruido típico de -120dB para el cero
        assert db[1] == -120.0

class TestSintesizarRI:
    """Tests para la síntesis de Respuestas al Impulso (RI)."""

    def test_sintetizar_ri_duracion(self):
        """Verificar que la RI tiene la duracion correcta."""

        #Se definen los parámetros para la síntesis de la RI
        fs = 44100
        duracion_esperada = 3.0

        #Llamamos a la función (se asume que recibe duración, fs y bandas/T60)
        #Se ajustan los parámetros habiendo definido una banda de 1000 Hz con un T60 de 2.0 segundos
        ri = sintetizar_ri(duracion=duracion_esperada, fs=fs, t60_por_banda={1000: 2.0})

        #Definimos primero las muestras esperadas
        #Se verifica con los asserts que la cantidad de muestras corresponde a la duración multiplicada por la fs, y que el resultado es un array de numpy.
        muestras_esperadas = int(duracion_esperada * fs)
        assert len(ri) == muestras_esperadas
        assert isinstance(ri, np.ndarray)

    def test_sintetizar_ri_decaimiento(self):
        """Verificar que el decaimiento por banda corresponde aproximadamente al T60 especificado."""
        #Se definen los parámetros para la síntesis de la RI
        fs = 44100
        duracion = 3.0
        f_central = 1000.0
        t60_objetivo = 2.0

        #Definimos la función para sintetizar Sintetizar una RI con T60 = 2.0 s en la banda de 1000 Hz
        ri = sintetizar_ri(duracion=duracion, fs=fs, t60_por_banda={f_central: t60_objetivo})

        #Filtrar la RI sintetizada en la banda de 1000 Hz (Filtro pasabanda de octava)
        #Calculamos frecuencias de corte para la banda de octava centrada en 1000 Hz
        f_low = f_central / np.sqrt(2)
        f_high = f_central * np.sqrt(2)

        #Se aplica un filtro Butterworth de orden 4
        b, a = butter(4, [f_low, f_high], btype='bandpass', fs=fs)  # type: ignore
        ri_filtrada = filtfilt(b, a, ri)

        #Se calcula la curva de decaimiento en dB (Integral de Schroeder)
        #Elevamos al cuadrado la RI filtrada
        energia = ri_filtrada ** 2
        #Integramos alreves (Schroeder)
        edc = np.cumsum(energia[::-1])[::-1]
        #Pasamos a dB normalizando respecto al máximo (evitamos log(0) sumando un epsilon)
        edc_db = 10 * np.log10((edc + 1e-12) / np.max(edc))

        #Se mide el tiempo en que la curva cruza -60 dB
        #Buscamos el primer índice donde la curva cae por debajo de -60 dB, importa el índice, no el nivel
        indices_cruce = np.where(edc_db <= -60)[0]

        #Si la señal nunca llega a -60dB, el test falla automáticamente
        assert len(indices_cruce) > 0, "La señal no decayó hasta -60 dB dentro de la duración dada."

        indice_t60 = indices_cruce[0]
        t60_medido = indice_t60 / fs

        #Se Verifica que el T60 medido está dentro del 10% del valor especificado, osea la tolerancia es de 0.2s para un T60 objetivo de 2.0s
        margen_error = t60_objetivo * 0.10  
        assert np.isclose(t60_medido, t60_objetivo, atol=margen_error), \
            f"Fallo: T60 medido = {t60_medido:.2f}s, se esperaba = {t60_objetivo}s"

class TestDeconvolución:

    def test_obtener_ri_pico(self):
        """Verificar que la RI obtenida por deconvolucion tiene
        un pico principal claramente identificable y coincide con la original."""

    fs = 44100

    #Generamos sweep y filtro inverso (usamos uno cortito de 1 seg para que el test vuele)
    #Reemplazamos esto por la llamada a la función de M1 con sus respectivos parámetros
    sweep, filtro_inverso = generar_sine_sweep(f1=20, f2=20000, duracion=2.0, fs=fs)

    #Sintetizamos una RI conocida (Simulamos la acústica de la sala)
    #Fabricamos un array donde el pico máximo esté en el índice 15 para alinearse perfectamente con el recorte (indice_max - 15) que hace tu función.
    ri_ideal = np.zeros(2000)
    ri_ideal[15] = 1.0  #Pico máximo
    #Le sumamos un decaimiento exponencial suave simulando reverberación
    ri_ideal[16:] = np.exp(-np.linspace(0, 10, len(ri_ideal)-16)) * 0.4

    #Simulamos la grabación física, la modificación de la sala del sweep, aplicando la convolución entre el sweep y la RI ideal
    grabacion_simulada = fftconvolve(sweep, ri_ideal, mode='full')

    #Hacemos la deconvolución para recuperar la RI a partir del sweep grabado y el filtro inverso
    ri_recuperada = obtener_ri_desde_sweep(grabacion_simulada, filtro_inverso)

    #Verificamos que la RI recuperada se parece a la RI ideal (correlacion cruzada > 0.8)
    #Recortamos las señales a la misma longitud para evitar problemas de correlación por diferencias de tamaño
    longitud_min = min(len(ri_ideal), len(ri_recuperada))
    ri_ideal_recortada = ri_ideal[:longitud_min]
    ri_rec_recortada = ri_recuperada[:longitud_min]

    #np.corrcoef devuelve una matriz de correlación 2x2. 
    #El valor en la posición [0, 1] es el coeficiente de Pearson cruzado entre ambas señales.
    correlacion = np.corrcoef(ri_ideal_recortada, ri_rec_recortada)[0, 1]

    #Comprobamos la similitud (1.0 sería matemáticamente idéntico)
    assert correlacion > 0.8, f"Fallo: La correlación fue de {correlacion:.3f}, se esperaba > 0.8"

    #verificamos que el pico efectivamente haya quedado normalizado a 1.0 como dice tu código
    assert np.isclose(np.max(np.abs(ri_recuperada)), 1.0), "Fallo: El pico máximo de la RI recuperada no está normalizado a 1.0"