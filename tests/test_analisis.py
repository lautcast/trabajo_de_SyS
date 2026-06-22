"""Tests para los servicios de analisis de parametros acusticos (Milestone 3)."""

import numpy as np

from app.services.acoustic_parameters import integral_schroeder, regresion_lineal, calcular_parametros_acusticos, suavizar_signal


class TestRegresionLineal:
    """Tests para la funcion regresion_lineal."""

    def test_regresion_lineal_conocida(self):
        """Verifica con una recta conocida y = 2x + 1."""
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        y = 2.0 * x + 1.0
        pendiente, ordenada = regresion_lineal(x, y)
        assert abs(pendiente - 2.0) < 1e-10
        assert abs(ordenada - 1.0) < 1e-10

    def test_regresion_lineal_con_ruido(self):
        """Verifica que la regresion se aproxima a la recta con datos ruidosos."""
        np.random.seed(42)
        x = np.linspace(0, 10, 100)
        y = 3.0 * x + 5.0 + np.random.normal(0, 0.1, 100)
        pendiente, ordenada = regresion_lineal(x, y)
        assert abs(pendiente - 3.0) < 0.5
        assert abs(ordenada - 5.0) < 1.0


class TestIntegralSchroeder:
    """Tests para la funcion integral_schroeder."""

    def test_integral_schroeder_forma(self):
        """Verifica que la EDC tiene la misma longitud que la entrada."""
        ri = np.random.randn(1000)
        edc = integral_schroeder(ri)
        assert len(edc) == len(ri)

    def test_integral_schroeder_decreciente(self):
        """Verifica que la EDC es monotonamente decreciente."""
        ri = np.random.randn(1000)
        edc = integral_schroeder(ri)
        assert np.all(np.diff(edc) <= 0)

class TestSuavizarSignal:
    """Tests para la funcion suavizar_signal."""

def test_suavizar_hilbert_envolvente():
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
    #Una señal oscilatoria tiene saltos enormesa diferencia de una señal suave, que tiene saltos minúsculos.
    saltos_original = np.max(np.abs(np.diff(ri_simulada)))
    saltos_envolvente = np.max(np.abs(np.diff(envolvente_calculada)))

    #Se verifica que los saltos de la envolvente suavizada sean significativamente menores que los de la señal original.
    assert saltos_envolvente < (saltos_original * 0.1), \
        "Fallo: La envolvente sigue siendo demasiado ruidosa/oscilatoria, no se suavizó correctamente."