"Milestone 3: Endpoints de análisis"

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Union
import numpy as np
from scipy.signal import hilbert
from typing import List, Dict, Optional, Any
from app.services.acoustic_parameters import calcular_parametros_acusticos, integral_schroeder, regresion_lineal
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

class AcousticsBroadbandResponse(BaseModel):
    EDT: Optional[float] = Field(None, description="Early Decay Time global (segundos)")
    T10: Optional[float] = Field(None, description="T10 global (segundos)")
    T20: Optional[float] = Field(None, description="T20 global (segundos)")
    T30: Optional[float] = Field(None, description="T30 global (segundos)")
    D50: Optional[float] = Field(None, description="Definición global (%)")
    C80: Optional[float] = Field(None, description="Claridad global (dB)")

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

@router.post("/parameters", response_model=AcousticsBroadbandResponse, summary="Calcular Parámetros Globales (Broadband)")
def calcular_parametros_global_endpoint(request: AcousticsRequest):
    """
    Parámetros Acústicos Globales:
    Calcula los parámetros para la señal completa sin aplicar filtrado por bandas de octava.
    """
    ri = np.array(request.ri, dtype=np.float64)
    fs = request.fs
    
    try:
        # 1. Cálculos de Energía (Sin filtros)
        ri_cuadrado = ri ** 2
        energia_total = np.sum(ri_cuadrado)

        # D50 Global
        N50 = int(0.050 * fs)
        energia_50 = np.sum(ri_cuadrado[:N50])
        d50 = float((energia_50 / energia_total) * 100) if energia_total > 0 else 0.0

        # C80 Global
        N80 = int(0.080 * fs)
        energia_80 = np.sum(ri_cuadrado[:N80])
        energia_tardia_80 = np.sum(ri_cuadrado[N80:])
        if energia_80 > 0 and energia_tardia_80 > 0:
            c80 = float(10 * np.log10(energia_80 / energia_tardia_80))
        else:
            c80 = None

        # 2. Tiempos de Reverberación Globales
        envolvente = integral_schroeder(ri)
        t = np.arange(len(ri)) / fs

        def buscar_indice(array, value) -> int:
            return int((np.abs(array - value)).argmin())

        indice_0 = buscar_indice(envolvente, 0)
        indice_5 = buscar_indice(envolvente, -5)
        indice_10 = buscar_indice(envolvente, -10)
        indice_15 = buscar_indice(envolvente, -15)
        indice_25 = buscar_indice(envolvente, -25)
        indice_35 = buscar_indice(envolvente, -35)

        def calcular_tx(indice_inicio, indice_final):
            if indice_final <= indice_inicio or (indice_final - indice_inicio) < 2:
                return None 
            tramo_temporal = t[indice_inicio:indice_final]
            db = envolvente[indice_inicio:indice_final]
            m, b, R_2 = regresion_lineal(tramo_temporal, db)
            return float((-60.0) / m) if m != 0 else None

        edt = calcular_tx(indice_0, indice_10)
        t10 = calcular_tx(indice_5, indice_15)
        t20 = calcular_tx(indice_5, indice_25)
        t30 = calcular_tx(indice_5, indice_35)

        # 3. Retornamos el modelo con los resultados
        return AcousticsBroadbandResponse(
            EDT=edt,
            T10=t10,
            T20=t20,
            T30=t30,
            D50=d50,
            C80=c80
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando parámetros globales: {str(e)}")