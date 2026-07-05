"""Tests para los servicios de generacion de senales (Milestone 1)."""

import numpy as np
import pytest
from scipy.signal import welch
from unittest.mock import patch
from app.services.pink_noise import generar_ruido_rosa
from app.services.sine_sweep import generar_sine_sweep
from app.services.audio.py import reproducir_y_grabar

"""----------------------------------------------------------------------------------------------------------------------------------------------------------------------"""

class TestGenerarRuidoRosa:
    """Tests para la funcion generar_ruido_rosa."""

    def test_ruido_rosa_duracion(self):
        """Verifica que la longitud de la senal corresponda a duracion * fs."""

        # Usamos la funcion generar_ruido_rosa con parametros genericos.

        duracion = 2.0
        fs = 44100
        ruido = generar_ruido_rosa(duracion, fs)

        # Definimos una variable que exiba la cantidad de muestras esperada en la senal.

        expected_length = int(duracion * fs)

        assert len(ruido) == expected_length        # Verificamos que la cantidad de muestras del ruido rosa es igual a la variable.


    def test_ruido_rosa_tipo(self):
        """Verifica que la funcion retorna un np.ndarray."""

        # Usamos la funcion generar_ruido_rosa con parametros genericos

        ruido = generar_ruido_rosa(1.0, 44100)

        assert isinstance(ruido, np.ndarray)        # Verificamos que el elemento devuelto por la funcion sea un array.


    def test_ruido_rosa_normalizado(self):
        """Verifica que la senal esta normalizada entre -1 y 1."""

        # Usamos la funcion generar_ruido_rosa con parametros genericos

        ruido = generar_ruido_rosa(1.0, 44100)
        assert np.max(np.abs(ruido)) <= 1.0

        assert np.max(np.abs(ruido)) <= 1.0          # Verificamos que el máximo valor absoluto es menor o igual que 1.


    def test_distribucion_espectral_ruido_rosa(self):
        """Verifica que la densidad espectral caiga a razon de 1/f (pendiente ~ -1 en log-log)."""

        # Usamos la funcion generar_ruido_rosa con parametros genericos

        fs = 44100
        duracion = 5.0
        ruido = generar_ruido_rosa(duracion, fs)

        #Calculamos la densidad espectral de potencia (PSD)
        frecuencias, psd = welch(ruido, fs, nperseg=8192)

        #Filtramos el rango de frecuencias util (evitamos f=0 y altas frecuencias)
        # Calculamos la densidad espectral de potencia (PSD)

        frecuencias, psd = welch(ruido, fs, nperseg=8192)

        # Filtramos el rango de frecuencias util (evitamos f=0 y altas frecuencias)

        idx_validos = (frecuencias > 20) & (frecuencias < 10000)
        f_util = frecuencias[idx_validos]
        psd_util = psd[idx_validos]

        #Pasamos a escala logaritmica (base 10)
        log_f = np.log10(f_util)
        log_psd = np.log10(psd_util)

        #Ajuste lineal para encontrar la pendiente
        coeficientes = np.polyfit(log_f, log_psd, 1)
        pendiente = coeficientes[0]

        #Verificamos que la pendiente este cerca de -1.0
        # Pasamos a escala logaritmica (base 10)

        log_f = np.log10(f_util)
        log_psd = np.log10(psd_util)

        # Ajuste lineal para encontrar la pendiente
        coeficientes = np.polyfit(log_f, log_psd, 1)
        pendiente = coeficientes[0]

        # Verificamos que la pendiente este cerca de -1.0
        assert np.isclose(pendiente, -1.0, atol=0.2), f"Fallo: Pendiente fue {pendiente:.2f}, se esperaba ~ -1.0"


"""----------------------------------------------------------------------------------------------------------------------------------------------------------------------"""


class TestGenerarSineSweep:
    """Tests para la funcion generar_sine_sweep."""

    def test_sine_sweep_retorna_tupla(self):
        """Verifica que retorna una tupla con dos arrays."""

        # Usamos la funcion generar_sine_sweep con parametros genericos

        resultado = generar_sine_sweep(20, 20000, 1.0, 44100)

        #Auditamodos que el resultado sea una tupla de dos elementos, ambos np.ndarray
        assert isinstance(resultado, tuple)
        assert len(resultado) == 2
        assert isinstance(resultado[0], np.ndarray)
        assert isinstance(resultado[1], np.ndarray)
        assert isinstance(resultado, tuple)             # Verifica que el resultado de utilizar la funcion es una tupla.
        assert len(resultado) == 2                      # Verifica que la tupla tiene dos elementos dentro.
        assert isinstance(resultado[0], np.ndarray)     # Verifica que el primer elemento que contiene la tupla sea un array.
        assert isinstance(resultado[1], np.ndarray)     # Verifica que el segundo elemento que contiene la tupla sea un array.


    def test_sine_sweep_duracion(self):
        """Verifica que ambas senales tienen la longitud correcta."""

        # Usamos la funcion de generar_sine_sweep con parametros genericos.

        duracion = 3.0
        fs = 44100

        #Generamos un sweep de 20 Hz a 20000 Hz
        sweep, filtro_inv = generar_sine_sweep(20, 20000, duracion, fs)

        # Definimos una variable la cual contiene al numero de muestras del sine sweep segun nuestros parametros genericos.

        expected_length = int(duracion * fs)

        #Auditamos que ambas senales tengan la longitud correcta
        assert len(sweep) == expected_length
        assert len(filtro_inv) == expected_length
        assert len(sweep) == expected_length        # Verifica que la cantidad de muestras del sine sweep es igual a la variable.
        assert len(filtro_inv) == expected_length   # Verifica que la cantidad de muestras del filtro inverso es igual a la variable, y por tanto, a las muestras del sine sweep


    def test_sine_sweep_progresion_frecuencias(self):
        """Verifica que la frecuencia de la señal aumente con el tiempo."""

        # Usamos la funcion de generar_sine_sweep con parametros genericos.

        fs = 44100
        duracion = 2.0
        #Generamos un sweep de 20 Hz a 20000 Hz
        sweep, _ = generar_sine_sweep(20, 20000, duracion, fs)

        #Tomamos una ventana pequeña de muestras al inicio y al final (ej: 0.1 segundos)
        muestras_ventana = int(0.1 * fs)
        fragmento_inicio = sweep[:muestras_ventana]
        fragmento_fin = sweep[-muestras_ventana:]

        #Función auxiliar para encontrar la frecuencia con más energía usando FFT
        def obtener_frecuencia_dominante(senal_fragmento):

            #Calculamos el espectro de frecuencias del fragmento
        sweep, _ = generar_sine_sweep(20, 20000, duracion, fs)

        # Tomamos una ventana pequeña de muestras al inicio y al final (ej: 0.1 segundos)

        muestras_ventana = int(0.1 * fs)                # En este caso, tomamos 4410 muestras
        fragmento_inicio = sweep[:muestras_ventana]     # Las primeras 4410 muestras.
        fragmento_fin = sweep[-muestras_ventana:]       # Las ultimas 4410 muestras.

        # Definimos una función auxiliar para encontrar la frecuencia con más energía usando FFT
        def obtener_frecuencia_dominante(senal_fragmento):

            # Calculamos el espectro de frecuencias del fragmento

            espectro = np.abs(np.fft.rfft(senal_fragmento))
            frecuencias = np.fft.rfftfreq(len(senal_fragmento), 1/fs)

            # Buscamos el índice donde el espectro tiene su pico máximo

            indice_pico = np.argmax(espectro)

            return frecuencias[indice_pico]

        #Calculamos las frecuencias dominantes
        frec_inicio = obtener_frecuencia_dominante(fragmento_inicio)
        frec_fin = obtener_frecuencia_dominante(fragmento_fin)

        #Verificamos con Asserts que la frecuencia del final sea estrictamente mayor que la del inicio
        assert frec_fin > frec_inicio, "Fallo: La frecuencia no aumenta con el tiempo"

        #Opcional: Comprobamos que arranca en bajas frecuencias y termina en altas
        assert frec_inicio < 1000, f"Fallo: Arranca con frecuencia muy alta ({frec_inicio} Hz)"
        assert frec_fin > 10000, f"Fallo: Termina con frecuencia muy baja ({frec_fin} Hz)"

class TestReproducirYGrabar:
    def test_reproducir_y_grabar_padding_y_dimensiones():
        """Verifica que la señal de salida se ensamble correctamente con pre-roll y silencios."""
    fs = 1000  #Frecuencia baja para agilizar el procesamiento del test
    duracion_grabacion = 3.0  # 3 segundos = 3000 muestras
    pre_roll = 0.5           # 0.5 segundos = 500 muestras
    
    #Generamos 1 segundo de señal activa llena de unos
    signal_entrada = np.ones(1000)

    #Simulamos el comportamiento de sounddevice sin tocar el hardware real
    with patch('sounddevice.playrec') as mock_playrec:
        #Simulamos que el micrófono grabó 3000 muestras en un arreglo 2D
        mock_playrec.return_value = np.zeros((3000, 1), dtype=np.float32)

        resultado = reproducir_y_grabar(signal_entrada, fs, duracion_grabacion, pre_roll=pre_roll)

        #Auditamos que el resultado final sea un vector 1D correcto
        assert isinstance(resultado, np.ndarray)
        assert resultado.ndim == 1
        assert len(resultado) == 3000

        #Auditamos los argumentos con los que fue invocado sd.playrec
        mock_playrec.assert_called_once()
        args, kwargs = mock_playrec.call_args
        vector_enviado_a_hardware = args[0]

        #Se verifica que el vector enviado mide exactamente lo solicitado
        assert len(vector_enviado_a_hardware) == 3000
        
        #Chequeamos el bloque de Pre-roll (deben ser puros ceros)
        assert np.all(vector_enviado_a_hardware[:500] == 0)
        
        #Chequeamos la inyección de la señal (deben ser los unos de nuestra señal)
        assert np.all(vector_enviado_a_hardware[500:1500] == 1)
        
        #Chequeamos la cola de reverberación (el resto vuelve a ser cero)
        assert np.all(vector_enviado_a_hardware[1500:] == 0)


def test_reproducir_y_grabar_error_duracion_insuficiente():
    """Comprueba que la función rechaza ejecuciones donde la grabación no cubre el estímulo."""
    fs = 1000
    signal_larga = np.ones(2000) #2 segundos de señal
    
    #Se procura meter 0.5s de pre-roll + 2s de señal en una grabación de 1.5s, debe lanzar ValueError
    with pytest.raises(ValueError):
        reproducir_y_grabar(signal_larga, fs, duracion_grabacion=1.5, pre_roll=0.5)
        # Calculamos las frecuencias dominantes

        frec_inicio = obtener_frecuencia_dominante(fragmento_inicio)
        frec_fin = obtener_frecuencia_dominante(fragmento_fin)

        # Verificamos

        assert frec_fin > frec_inicio, "Fallo: La frecuencia no aumenta con el tiempo"
        assert frec_inicio < 1000, f"Fallo: Arranca con frecuencia muy alta ({frec_inicio} Hz)"


"""----------------------------------------------------------------------------------------------------------------------------------------------------------------------"""


