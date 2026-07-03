"Milestone 3: Endpoints de análisis"

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Union
import numpy as np
from scipy.signal import hilbert
from typing import List, Dict, Optional, Any
from app.services.acoustic_parameters import suavizar_signal, integral_schroeder, regresion_lineal, calcular_parametros_acusticos
from app.services.filter import filtro_octava

router = APIRouter()


class SmoothingRequest(BaseModel):
    signal_in: list[float] = Field(..., description="Arreglo de la señal de entrada (array 1D)")
    ventana: int | str = Field(
        "hilbert", description="Tamaño de la ventana (entero positivo) o 'hilbert'"
    )
class SmoothingResponse(BaseModel):
    signal_out: list[float] = Field(..., description="Arreglo de la señal suavizada")


class SchroederRequest(BaseModel):
    ri: List[float] = Field(..., description="Arreglo de la Respuesta al Impulso (array 1D)")

class SchroederResponse(BaseModel):
    edc_db: List[float] = Field(..., description="Curva de decaimiento energético en dB (EDC)")

@router.post("/smoothing", response_model=SmoothingResponse, summary="Suavizar Señal")
def procesar_suavizado(request: SmoothingRequest):
    """
    Suavizado de Señal:
    Aplica un suavizado por media móvil (indicando una ventana entera positiva)
    o extrae la envolvente analítica utilizando la transformada de Hilbert.
    """
    # 1. Transformamos JSON a NumPy
    senal_numpy = np.array(request.signal_in, dtype=np.float64)

    try:
        # 2. Ejecutamos tu función matemática
        senal_suavizada = suavizar_signal(signal=senal_numpy, ventana=request.ventana)

        # 3. Devolvemos la respuesta
        return SmoothingResponse(signal_out=senal_suavizada.tolist())

    except ValueError as e:
        # Este except agarra exactamente el ValueError que escribiste al final de tu función
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Para cualquier otro error matemático no previsto
        raise HTTPException(status_code=500, detail=f"Error inesperado en el suavizado: {str(e)}")

@router.post("/schroeder", response_model=SchroederResponse, summary="Calcular Integral de Schroeder")
def procesar_schroeder(request: SchroederRequest):
    """
    Integral de Schroeder:
    Calcula la curva de decaimiento de energía (EDC) a partir de una 
    respuesta al impulso. Devuelve la curva ya normalizada y en escala 
    logarítmica (dB).
    """
    # 1. Transformamos JSON a NumPy
    senal_numpy = np.array(request.ri, dtype=np.float64)
    
    try:
        # 2. Ejecutamos tu función
        edc_resultado = integral_schroeder(ri=senal_numpy)
        
        # 3. Devolvemos la respuesta
        return SchroederResponse(edc_db=edc_resultado.tolist())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular la integral de Schroeder: {str(e)}")
    
    from fastapi import APIRouter, HTTPException

class AcousticsRequest(BaseModel):
    ri: List[float] = Field(..., description="Arreglo de la Respuesta al Impulso (array 1D)")
    fs: int = Field(48000, description="Frecuencia de muestreo en Hz")

class AcousticsByBandsResponse(BaseModel):
    # Dict[str, float] permite devolver un objeto JSON como: {"1000.0": 1.5, "2000.0": 1.2}
    EDT: Dict[str, Optional[float]]
    T10: Dict[str, Optional[float]]
    T20: Dict[str, Optional[float]]
    T30: Dict[str, Optional[float]]
    D50: Dict[str, Optional[float]]
    C80: Dict[str, Optional[float]]


@router.post("/parameters/by-bands", response_model=AcousticsByBandsResponse, summary="Calcular Parámetros por Bandas")
def calcular_parametros_bandas_endpoint(request: AcousticsRequest):
    """
    Parámetros Acústicos por Bandas de Octava:
    Toma una Respuesta al Impulso, la filtra iterativamente en las bandas de octava 
    normalizadas (IEC 61260) y devuelve los parámetros D50, C80, EDT, T10, T20 y T30 
    para cada frecuencia central.
    """
    senal_numpy = np.array(request.ri, dtype=np.float64)
    
    try:
        # Llamamos a tu super-función
        diccionario_resultados = calcular_parametros_acusticos(ri=senal_numpy, fs=request.fs)
        return diccionario_resultados
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando parámetros acústicos: {str(e)}")

@router.post("/parameters", summary="Calcular Parámetros Globales (Broadband)")
def calcular_parametros_global_endpoint(request: AcousticsRequest):
    """
    Parámetros Acústicos Globales:
    Este endpoint calcula los parámetros para la señal completa sin aplicar 
    filtrado por bandas de octava.
    """
    # Aquí iría una versión de tu función que no itera sobre el arreglo de frecuencias,
    # sino que aplica el cálculo directamente sobre el request.ri
    # Para mantener el código limpio, puedes derivarla fácilmente de tu función principal.
    return {"mensaje": "Endpoint global disponible. Implementación broadband en curso."}
