"""Tests para los servicios de analisis de parametros acusticos (Milestone 3)."""


import numpy as np

from app.services.acoustic_parameters import calcular_parametros_acusticos, integral_schroeder, regresion_lineal, suavizar_signal


class TestRegresionLineal:
    """Tests para la funcion regresion_lineal."""

    def test_regresion_lineal_exacta(self):
        """Para datos perfectamente lineales, R^2 debe ser 1.0 y coincidir la pendiente."""

        #Datos conocidos (y = 2x + 1)
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        y_verdadera = 2.0 * x + 1.0

        #Ejecución de la función
        m, b = regresion_lineal(x, y_verdadera)

        #Reconstrucción y cálculo manual del R^2 (Requisito mínimo para la función)
        y_predicha = m * x + b
        ss_res = np.sum((y_verdadera - y_predicha) ** 2)
        ss_tot = np.sum((y_verdadera - np.mean(y_verdadera)) ** 2)
        r_cuadrado = 1.0 - (ss_res / ss_tot)

        #Aduitoría con Asserts: R^2 debe ser 1.0, pendiente m debe ser 2.0 y ordenada b debe ser 1.0
        assert np.isclose(r_cuadrado, 1.0), f"Fallo: R^2 fue {r_cuadrado}, se esperaba 1.0"
        assert abs(m - 2.0) < 1e-10, "Fallo: La pendiente no coincide con la esperada."
        assert abs(b - 1.0) < 1e-10, "Fallo: La ordenada no coincide con la esperada."

    def test_regresion_lineal_con_ruido(self):
        """Verifica que la regresion se aproxima a la recta con datos ruidosos."""
        np.random.seed(42) #Usamos la misma semilla para que el test sea siempre igual
        x = np.linspace(0, 10, 100)
        #Recta modelo: y = 3x + 5 ensuciada con ruido normal,  desviación estándar de 0.1 para que el ruido sea pequeño pero presente
        y = 3.0 * x + 5.0 + np.random.normal(0, 0.1, 100)

        m, b = regresion_lineal(x, y)

        #Tolerancias más amplias (0.5 y 1.0) porque el ruido desvía levemente el ajuste
        assert abs(m - 3.0) < 0.5, "Fallo: La pendiente se desvió demasiado por el ruido."
        assert abs(b - 5.0) < 1.0, "Fallo: La ordenada se desvió demasiado por el ruido."

    def test_regresion_lineal_pendiente(self):
        """Verificar pendiente con datos conocidos simulando la curva de Schroeder."""
        x = np.array([0.0, 1.0, 2.0, 3.0])
        y_conocida = -15.0 * x + 0.0  #Simulación de caída de 15 dB

        m, b = regresion_lineal(x, y_conocida)

        #Precisión absoluta para la pendiente negativa
        assert np.isclose(m, -15.0), f"Fallo: Calculó pendiente de {m:.2f}, era -15.0"


class TestIntegralSchroeder:
    """Tests para la funcion integral_schroeder."""

    def test_integral_schroeder_forma_y_decreciente(self):
        """Verifica que la integral de Schroeder produzca una curva decreciente y con inicio en 0 dB."""

    #Señal de prueba (Una RI ruidosa)
    fs = 44100
    duracion = 1.0
    t = np.linspace(0, duracion, int(fs * duracion), endpoint=False)

    #Se simula sala real: Ruido aleatorio cayendo exponencialmente
    ruido = np.random.randn(len(t))
    ri_prueba = ruido * np.exp(-6 * t)

    #Se ejecuta la integral de Schroeder sobre la señal de prueba
    curva_db = integral_schroeder(ri_prueba)

    #Asserts que verifican las propiedades de la curva de Schroeder (Las 3 auditorías innegociables)

    #Assert A: La Longitud de la curva de Schroeder debe ser igual a la longitud de la RI original
    assert len(curva_db) == len(ri_prueba), \
        "Fallo: La curva de Schroeder no tiene la misma cantidad de muestras que la RI original."

    #Assert B: El Inicio a 0 dB
    #Se utiliza np.isclose porque en Python 0.0 a veces se calcula como 0.00000000001
    assert np.isclose(curva_db[0], 0.0, atol=1e-5), \
        f"Fallo: La curva arranca en {curva_db[0]:.3f} dB en lugar de 0 dB."

    #Assert C: La curva debe ser estrictamente decreciente (no puede subir nunca)
    # np.diff calcula los "escalones" entre cada muestra y la siguiente, verificando que sea descreciente.
    escalones = np.diff(curva_db)

    #Le damos un margen minúsculo (1e-10) por los errores de redondeo de punto flotante de Python
    #Si alguna resta es mayor a 1e-10, significa que la curva subió en algún punto, lanza un fallo.
    assert np.all(escalones <= 1e-10), \
        "Fallo: La curva de Schroeder tiene subidas de energía, no es estrictamente decreciente."

class TestSuavizarSignal:
    """Tests para la funcion suavizar_signal."""

    def test_suavizar_hilbert_envolvente(self):
        """La envolvente debe ser no negativa y suave."""

    #Se fabrica una señal modelo de prueba
    fs = 44100
    duracion = 1.0
    t = np.linspace(0, duracion, int(fs * duracion), endpoint=False)

    frecuencia_portadora = 1000  # Una onda de 1 kHz

    #Esta es la "silueta" real perfecta que tu función debería recuperar.
    envolvente_ideal = np.exp(-3 * t)

    #Multiplicamos la silueta por la onda  para generar nuestra RI simulada
    ri_simulada = envolvente_ideal * np.sin(2 * np.pi * frecuencia_portadora * t)

    #Se pone a prueba la función suavizar_signal con la opción de ventana 'hilbert'
    envolvente_calculada = suavizar_signal(ri_simulada, ventana='hilbert')

    #Se verifica que la envolvente calculada cumpla con ciertos criterios de validez y suavidad a traves de los asserts.
    #Si alguno de estos asserts falla, se lanzara un AssertionError con un mensaje descriptivo.

    #Primero: control de dimensiones (previene que se rompa el eje de tiempo)
    assert len(envolvente_calculada) == len(ri_simulada), \
        "Fallo: La función modificó la cantidad de muestras de la señal original."

    #Segundo: control físico (La energía NO puede ser negativa)
    assert np.all(envolvente_calculada >= 0), \
        "Fallo: La envolvente obtenida contiene valores por debajo de cero."

    #Tercero: control de suavidad (el núcleo del test)
    #Se calculan los "saltos" (la derivada discreta) entre una muestra y la siguiente.
    #Una señal oscilatoria tiene saltos enormes a diferencia de una señal suave, que tiene saltos minúsculos.
    saltos_original = np.max(np.abs(np.diff(ri_simulada)))
    saltos_envolvente = np.max(np.abs(np.diff(envolvente_calculada)))

    #Se verifica que los saltos de la envolvente suavizada sean significativamente menores que los de la señal original.
    assert saltos_envolvente < (saltos_original * 0.1), \
        "Fallo: La envolvente sigue siendo demasiado ruidosa/oscilatoria, no se suavizó correctamente."

class TestParametrosAcusticos:
    """Tests para los parámetros acústicos ISO 3382 (T60, D50, C80)."""

    def test_parametros_ri_sintetizada(self):
        """Sintetizar una RI con T60 = 2.0 s, calcular parametros 
        y verificar que T30 está dentro del +-10% del valor conocido."""

        fs = 44100
        #Necesitamos al menos 3 segundos de grabación para poder medir un T60 de 2.0s de manera holgada
        duracion = 3.0
        t = np.linspace(0, duracion, int(fs * duracion), endpoint=False)

        #Sintetizamos un decaimiento perfecto de 2.0 segundos
        t60_objetivo = 2.0
        #Multiplicamos ruido blanco por una envolvente exponencial de ejemplo
        ri_sintetica = np.random.randn(len(t)) * (10 ** (-3.0 * t / t60_objetivo))

        #Ejecutamos la función (Sabemos que devuelve un dict por bandas)
        parametros = calcular_parametros_acusticos(ri_sintetica, fs)

        #T30 es el parámetro solicitado por la norma ISO 3382
        #Revisamos que todas las bandas de octava hayan dado aprox 2.0s (+- 10%)
        for frecuencia, t30_calculado in parametros['T30'].items():
            error_maximo = t60_objetivo * 0.10
            assert abs(t30_calculado - t60_objetivo) <= error_maximo, \
                f"Fallo en banda {frecuencia}Hz: T30 dio {t30_calculado:.2f}s, se esperaba ~2.0s"

    def test_d50_rango(self):
        """D50 debe estar entre 0% y 100%."""
        fs = 44100
        duracion = 1.0
        t = np.linspace(0, duracion, int(fs * duracion), endpoint=False)

        #Generamos una RI genérica (ruido con decaimiento rápido)
        ri_generica = np.random.randn(len(t)) * np.exp(-10 * t)
        parametros = calcular_parametros_acusticos(ri_generica, fs)

        #Auditamos que la definición (inteligibilidad) cumpla la física de porcentajes
        for frecuencia, d50_calculado in parametros['D50'].items():
            assert 0.0 <= d50_calculado <= 100.0, \
                f"Fallo en banda {frecuencia}Hz: D50 dio {d50_calculado}%, fuera de rango."

    def test_c80_consistencia(self):
        """Para una RI con mucha energía temprana, C80 debe ser positivo."""
        fs = 44100
        #Fabricamos una sala "seca": todo el sonido muere en los primeros 50ms
        muestras_50ms = int(0.050 * fs)
        ri_seca = np.zeros(fs) # 1 segundo de silencio
        #Se llenan solo los primeros 50ms con alto impacto de energía (ruido blanco)
        ri_seca[:muestras_50ms] = np.random.randn(muestras_50ms) * np.linspace(1, 0, muestras_50ms)

        parametros = calcular_parametros_acusticos(ri_seca, fs)

        #Asserts que la claridad sea altamente positiva
        for frecuencia, c80_calculado in parametros['C80'].items():
            assert c80_calculado > 0.0, \
                f"Fallo en banda {frecuencia}Hz: C80 dio {c80_calculado} dB, debía ser positivo."
