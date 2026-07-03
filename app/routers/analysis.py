from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import numpy as np

from app.services.acoustic_parameters import calcular_parametros_acusticos

class AnalysisRequest(BaseModel):
    ri: List[float] = Field(..., description="Arreglo de la Respuesta al Impulso (array 1D) completa")
    fs: int = Field(48000, description="Frecuencia de muestreo en Hz")
    # Acá en el futuro podrías agregar metadatos si el profe lo pide
    # nombre_sala: str = Field(None, description="Nombre del recinto")

class AnalysisResponse(BaseModel):
    mensaje: str = Field(..., description="Estado del análisis")
    frecuencia_muestreo: int
    parametros_por_banda: Dict[str, Dict[str, Optional[float]]]

router = APIRouter()

@router.post("/impulse-response", response_model=AnalysisResponse, summary="Análisis Completo de Respuesta al Impulso")
def analyze_impulse_response(request: AnalysisRequest):
    """
    Endpoint Orquestador Maestro:
    Recibe una Respuesta al Impulso (RI) cruda. Internamente se encarga de 
    ejecutar todo el pipeline de DSP (Filtrado por bandas -> Integración de 
    Schroeder -> Regresión Lineal) y devuelve un reporte estructurado con 
    todos los parámetros acústicos calculados según la norma ISO 3382.
    """
    # 1. Pasamos los datos de internet a NumPy
    senal_numpy = np.array(request.ri, dtype=np.float64)
    
    try:
        # 2. Llamamos a TU función maestra (el motor matemático)
        resultados_acusticos = calcular_parametros_acusticos(ri=senal_numpy, fs=request.fs)
        
        # ---> NUEVO: Convertimos las claves (frecuencias) a strings para que el JSON sea válido
        resultados_formateados = {}
        for parametro, valores in resultados_acusticos.items():
            resultados_formateados[parametro] = {str(frecuencia): valor for frecuencia, valor in valores.items()}
        
        # 3. Empaquetamos todo en una respuesta bonita
        return AnalysisResponse(
            mensaje="Análisis acústico completado con éxito según ISO 3382.",
            frecuencia_muestreo=request.fs,
            parametros_por_banda=resultados_formateados
        )
        
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallo catastrófico en el motor de análisis: {str(e)}")