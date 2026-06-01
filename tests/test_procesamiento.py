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


class TestCargarAudio:
    """Tests para la funcion cargar_audio."""

    def test_cargar_audio_no_existe(self):
        """Verifica que se lanza FileNotFoundError si el archivo no existe."""
        with pytest.raises(FileNotFoundError):
            cargar_audio("archivo_que_no_existe.wav")

    def test_cargar_audio_wav(self, tmp_path):
        """Verificar carga correcta de archivo WAV."""
        # 1. Creamos un archivo WAV temporal de prueba
        ruta_dummy = tmp_path / "prueba.wav"
        fs_esperada = 44100
        # Señal de prueba (ruido aleatorio convertido a formato de audio estándar de 16 bits)
        senal_dummy = np.random.randint(-32768, 32767, fs_esperada, dtype=np.int16)
        wavfile.write(ruta_dummy, fs_esperada, senal_dummy)

        # 2. Ejecutamos la función
        signal, fs = cargar_audio(str(ruta_dummy))

        # 3. Verificamos que cargó bien la info
        assert fs == fs_esperada
        assert isinstance(signal, np.ndarray)
        assert len(signal) == len(senal_dummy)

    def test_cargar_audio_formato_invalido(self, tmp_path):
        """Verificar que lanza error con formato no soportado."""
        # 1. Creamos un archivo temporal que no es un audio (un txt disfrazado)
        ruta_invalida = tmp_path / "falso_audio.txt"
        ruta_invalida.write_text("Esto es texto, no es un archivo de audio.")

        # 2. Verificamos que la función ataje el error al intentar leerlo
        # (Dependiendo de cómo programen cargar_audio, puede ser ValueError o Exception)
        with pytest.raises(ValueError): 
            cargar_audio(str(ruta_invalida))

    def test_cargar_audio_normalizacion(self, tmp_path):
        """Verificar que la salida esta normalizada entre -1 y 1."""
        # 1. Creamos un WAV temporal forzando picos máximos del formato digital
        ruta_dummy = tmp_path / "prueba_norm.wav"
        fs_esperada = 44100
        # Forzamos los valores límite de 16 bits: 32767 y -32768
        senal_extrema = np.array([32767, 0, -32768, 15000], dtype=np.int16)
        wavfile.write(ruta_dummy, fs_esperada, senal_extrema)

        # 2. Ejecutamos la función
        signal, _ = cargar_audio(str(ruta_dummy))

        # 3. Verificamos matemáticamente que el valor absoluto máximo no supere 1.0
        max_amplitud = np.max(np.abs(signal))
        assert max_amplitud <= 1.0

        # Opcional pero recomendado: asegurar que no haya devuelto un arreglo de puros ceros
        assert max_amplitud > 0.0


class TestAEscalaLog:
    """Tests para la funcion a_escala_log."""

    def test_a_escala_log_valores(self):
        """Verifica que el maximo de la senal corresponde a 0 dB."""
        x = np.array([1.0, 0.5, 0.25, 0.1])
        db = a_escala_log(x)
        assert abs(db[0] - 0.0) < 1e-10

    def test_a_escala_log_tipo(self):
        """Verifica que retorna un np.ndarray."""
        x = np.array([1.0, 0.5])
        db = a_escala_log(x)
        assert isinstance(db, np.ndarray)


class TestSintesizarRI:
    """Tests para la síntesis de Respuestas al Impulso (RI)."""

    def test_sintetizar_ri_duracion(self):
        """Verificar que la RI tiene la duracion correcta."""
        fs = 44100
        duracion_esperada = 3.0

        # Llamamos a la función (asumiendo que recibe duración, fs y bandas/T60)
        # Ajustá los parámetros según cómo hayan definido la función ustedes
        ri = sintetizar_ri(duracion=duracion_esperada, fs=fs, t60_por_banda={1000: 2.0})

        muestras_esperadas = int(duracion_esperada * fs)
        assert len(ri) == muestras_esperadas
        assert isinstance(ri, np.ndarray)
    def test_sintetizar_ri_decaimiento(self):
        """Verificar que el decaimiento por banda corresponde aproximadamente al T60 especificado."""
        fs = 44100
        duracion = 3.0
        f_central = 1000.0
        t60_objetivo = 2.0

        # 1. Sintetizar una RI con T60 = 2.0 s en la banda de 1000 Hz
        ri = sintetizar_ri(duracion=duracion, fs=fs, t60_por_banda={f_central: t60_objetivo})

        # 2. Filtrar la RI sintetizada en la banda de 1000 Hz (Filtro pasabanda de octava)
        # Calculamos frecuencias de corte: f_low = f_c / sqrt(2), f_high = f_c * sqrt(2)
        f_low = f_central / np.sqrt(2)
        f_high = f_central * np.sqrt(2)

        # Diseñamos un filtro Butterworth de orden 4
        b, a = butter(4, [f_low, f_high], btype='bandpass', fs=fs)  # type: ignore
        ri_filtrada = filtfilt(b, a, ri)

        # 3. Calcular la curva de decaimiento en dB (Integral de Schroeder)
        # Elevamos al cuadrado la RI filtrada
        energia = ri_filtrada ** 2
        # Integramos en reversa (Schroeder)
        edc = np.cumsum(energia[::-1])[::-1]
        # Pasamos a dB normalizando respecto al máximo (evitamos log(0) sumando un epsilon)
        edc_db = 10 * np.log10((edc + 1e-12) / np.max(edc))

        # 4. Medir el tiempo en que la curva cruza -60 dB
        # Buscamos el primer índice donde la curva cae por debajo de -60 dB
        indices_cruce = np.where(edc_db <= -60)[0]

        # Si la señal nunca llega a -60dB, el test falla automáticamente
        assert len(indices_cruce) > 0, "La señal no decayó hasta -60 dB dentro de la duración dada."

        indice_t60 = indices_cruce[0]
        t60_medido = indice_t60 / fs

        # 5. Verificar que el T60 medido está dentro del 10% del valor especificado
        margen_error = t60_objetivo * 0.10  # 10% de tolerancia
        assert np.isclose(t60_medido, t60_objetivo, atol=margen_error), \
            f"Fallo: T60 medido = {t60_medido:.2f}s, se esperaba = {t60_objetivo}s"

def test_obtener_ri_pico():
    """
    Verificar que la RI obtenida por deconvolucion tiene 
    un pico principal claramente identificable y coincide con la original.
    """
    fs = 44100
    
    # 1. Generar sweep y filtro inverso (usamos uno cortito de 1 seg para que el test vuele)
    # Reemplazá esto por la llamada a la función que armaron en el Milestone 1
    sweep, filtro_inverso = generar_sine_sweep(f1=20, f2=20000, duracion=1.0, fs=fs)
    
    # 2. Sintetizar una RI conocida (Simulamos la acústica de la sala)
    # Fabricamos un array donde el pico máximo esté en el índice 15 para alinearse 
    # perfectamente con el recorte (indice_max - 15) que hace tu función.
    ri_ideal = np.zeros(2000)
    ri_ideal[15] = 1.0  # El sonido directo (pico máximo)
    # Le sumamos un decaimiento exponencial suave simulando reverberación
    ri_ideal[16:] = np.exp(-np.linspace(0, 10, len(ri_ideal)-16)) * 0.4
    
    # Simulamos la grabación física, la sala modifica el sweep
    grabacion_simulada = fftconvolve(sweep, ri_ideal, mode='full')
    
    # 3. Aplicar tu función de deconvolución
    ri_recuperada = obtener_ri_desde_sweep(grabacion_simulada, filtro_inverso)
    
    # 4. Verificar que la RI recuperada se parece a la RI original (correlacion cruzada > 0.9)
    # Recortamos la señal recuperada a la misma longitud que la ideal para compararlas 1 a 1
    longitud_min = min(len(ri_ideal), len(ri_recuperada))
    ri_ideal_recortada = ri_ideal[:longitud_min]
    ri_rec_recortada = ri_recuperada[:longitud_min]
    
    # np.corrcoef devuelve una matriz de correlación 2x2. 
    # El valor en la posición [0, 1] es el coeficiente de Pearson cruzado entre ambas señales.
    correlacion = np.corrcoef(ri_ideal_recortada, ri_rec_recortada)[0, 1]
    
    # Comprobamos la similitud (1.0 sería matemáticamente idéntico)
    assert correlacion > 0.9, f"Fallo: La correlación fue de {correlacion:.3f}, se esperaba > 0.9"
    
    # Extra: verificamos que el pico efectivamente haya quedado normalizado a 1.0 como dice tu código
    assert np.isclose(np.max(np.abs(ri_recuperada)), 1.0)