"Milestone 3: Endpoints de análisis"


import numpy as np
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
import os

# Importamos las funciones principales desde servicios. 
# Ya no necesitamos importar integral_schroeder ni regresion_lineal acá.
from app.services.acoustic_parameters import calcular_parametros_acusticos, calcular_parametros_globales
from app.routers.analysis import procesar_audio_subido

router = APIRouter()


class AcousticsRequest(BaseModel):
    ri: list[float] = Field(..., description="Arreglo de la Respuesta al Impulso (array 1D)")
    fs: int = Field(48000, description="Frecuencia de muestreo en Hz")

class AcousticsByBandsResponse(BaseModel):
    EDT: dict[str, float | None]
    T10: dict[str, float | None]
    T20: dict[str, float | None]
    T30: dict[str, float | None]
    D50: dict[str, float | None]
    C80: dict[str, float | None]

class AcousticsBroadbandResponse(BaseModel):
    EDT: float | None = Field(None, description="Early Decay Time global (segundos)")
    T10: float | None = Field(None, description="T10 global (segundos)")
    T20: float | None = Field(None, description="T20 global (segundos)")
    T30: float | None = Field(None, description="T30 global (segundos)")
    D50: float | None = Field(None, description="Definición global (%)")
    C80: float | None = Field(None, description="Claridad global (dB)")


@router.post("/parameters/by-bands", response_model=AcousticsByBandsResponse, summary="Calcular Parámetros por Bandas (Sube WAV)")
async def calcular_parametros_bandas_endpoint(file: UploadFile = File(...)):
    """
    Sube un archivo de audio (.wav o .flac).
    La API lo filtra en bandas de octava y devuelve los parámetros (EDT, T20, etc.) por frecuencia.
    """
    senal_numpy, fs, ruta_temporal = await procesar_audio_subido(file)

    try:
        # 1. Calculamos la matemática
        resultados_acusticos = calcular_parametros_acusticos(ri=senal_numpy, fs=fs)
        
        # 2. Convertimos las frecuencias (números) a texto (strings) para que el JSON no explote
        resultados_formateados = {}
        for parametro, valores in resultados_acusticos.items():
            resultados_formateados[parametro] = {str(frec): val for frec, val in valores.items()}

        # 3. Devolvemos el diccionario ya formateado
        return resultados_formateados
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando parámetros acústicos: {str(e)}") from e
    finally:
        if os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)


@router.post("/parameters", response_model=AcousticsBroadbandResponse, summary="Calcular Parámetros Globales (Broadband)")
def calcular_parametros_global_endpoint(request: AcousticsRequest):
    """
    Parámetros Acústicos Globales:
    Calcula los parámetros para la señal completa sin aplicar filtrado por bandas de octava.
    """
    ri = np.array(request.ri, dtype=np.float64)
    fs = request.fs

    try:
        # Llamamos al servicio, que nos devuelve un diccionario listo para usar
        resultados_globales = calcular_parametros_globales(ri=ri, fs=fs)
        
        # Desempaquetamos el diccionario (**) directamente en el modelo de Pydantic
        return AcousticsBroadbandResponse(**resultados_globales)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando parámetros globales: {str(e)}") from e
    
