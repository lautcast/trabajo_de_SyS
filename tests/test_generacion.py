"""Tests para los servicios de generacion de senales (Milestone 1)."""

import numpy as np
from scipy.signal import welch

from app.services.pink_noise import generar_ruido_rosa
from app.services.sine_sweep import generar_sine_sweep


class TestGenerarRuidoRosa:
    """Tests para la funcion generar_ruido_rosa."""

    def test_ruido_rosa_duracion(self):
        """Verifica que la longitud de la senal corresponda a duracion * fs."""
        duracion = 2.0
        fs = 44100
        ruido = generar_ruido_rosa(duracion, fs)
        expected_length = int(duracion * fs)
        assert len(ruido) == expected_length

    def test_ruido_rosa_tipo(self):
        """Verifica que la funcion retorna un np.ndarray."""
        ruido = generar_ruido_rosa(1.0, 44100)
        assert isinstance(ruido, np.ndarray)

    def test_ruido_rosa_normalizado(self):
        """Verifica que la senal esta normalizada entre -1 y 1."""
        ruido = generar_ruido_rosa(1.0, 44100)
        assert np.max(np.abs(ruido)) <= 1.0
    def test_distribucion_espectral_ruido_rosa(self):
        """Verifica que la densidad espectral caiga a razon de 1/f (pendiente ~ -1 en log-log)."""
        fs = 44100
        duracion = 5.0
        ruido = generar_ruido_rosa(duracion, fs)

        # 1. Calculamos la densidad espectral de potencia (PSD)
        frecuencias, psd = welch(ruido, fs, nperseg=8192)

        # 2. Filtramos el rango de frecuencias util (evitamos f=0 y altas frecuencias)
        idx_validos = (frecuencias > 20) & (frecuencias < 10000)
        f_util = frecuencias[idx_validos]
        psd_util = psd[idx_validos]

        # 3. Pasamos a escala logaritmica (base 10)
        log_f = np.log10(f_util)
        log_psd = np.log10(psd_util)

        # 4. Ajuste lineal para encontrar la pendiente
        coeficientes = np.polyfit(log_f, log_psd, 1)
        pendiente = coeficientes[0]

        # 5. Verificamos que la pendiente este cerca de -1.0
        assert np.isclose(pendiente, -1.0, atol=0.2), f"Fallo: Pendiente fue {pendiente:.2f}, se esperaba ~ -1.0"

class TestGenerarSineSweep:
    """Tests para la funcion generar_sine_sweep."""

    def test_sine_sweep_retorna_tupla(self):
        """Verifica que retorna una tupla con dos arrays."""
        resultado = generar_sine_sweep(20, 20000, 1.0, 44100)
        assert isinstance(resultado, tuple)
        assert len(resultado) == 2
        assert isinstance(resultado[0], np.ndarray)
        assert isinstance(resultado[1], np.ndarray)

    def test_sine_sweep_duracion(self):
        """Verifica que ambas senales tienen la longitud correcta."""
        duracion = 3.0
        fs = 44100
        sweep, filtro_inv = generar_sine_sweep(20, 20000, duracion, fs)
        expected_length = int(duracion * fs)
        assert len(sweep) == expected_length
        assert len(filtro_inv) == expected_length

    def test_sine_sweep_progresion_frecuencias(self):
        """Verifica que la frecuencia de la señal aumente con el tiempo."""
        fs = 44100
        duracion = 2.0
        # Generamos un sweep de 20 Hz a 20000 Hz
        sweep, _ = generar_sine_sweep(20, 20000, duracion, fs)

        # 1. Tomamos una ventana pequeña de muestras al inicio y al final (ej: 0.1 segundos)
        muestras_ventana = int(0.1 * fs)
        fragmento_inicio = sweep[:muestras_ventana]
        fragmento_fin = sweep[-muestras_ventana:]

        # 2. Función auxiliar para encontrar la frecuencia con más energía usando FFT
        def obtener_frecuencia_dominante(senal_fragmento):

            # Calculamos el espectro de frecuencias del fragmento
            espectro = np.abs(np.fft.rfft(senal_fragmento))
            frecuencias = np.fft.rfftfreq(len(senal_fragmento), 1/fs)
            # Buscamos el índice donde el espectro tiene su pico máximo
            indice_pico = np.argmax(espectro)
            return frecuencias[indice_pico]

        # 3. Calculamos las frecuencias dominantes
        frec_inicio = obtener_frecuencia_dominante(fragmento_inicio)
        frec_fin = obtener_frecuencia_dominante(fragmento_fin)

        # 4. Verificamos (Asserts)
        # Comprobamos que la frecuencia del final sea estrictamente mayor que la del inicio
        assert frec_fin > frec_inicio, "Fallo: La frecuencia no aumenta con el tiempo"

        # Opcional: Comprobamos que arranca en bajas frecuencias y termina en altas
        assert frec_inicio < 1000, f"Fallo: Arranca con frecuencia muy alta ({frec_inicio} Hz)"
        assert frec_fin > 10000, f"Fallo: Termina con frecuencia muy baja ({frec_fin} Hz)"
