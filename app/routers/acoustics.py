"Milestone 3: Endpoints de análisis"

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Union
import numpy as np
from scipy.signal import hilbert
from typing import List, Dict, Optional, Any
from app.services.acoustic_parameters import calcular_parametros_acusticos
from app.services.filter import filtro_octava

router = APIRouter()


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
