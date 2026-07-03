"Milestone 2 a 3: Endpoints de Filtrado"

import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.filter import filtro_octava


class FilterBandRequest(BaseModel):
    # Field(...) permite agregar documentación que se verá en el Swagger UI
    signal_in: list[float] = Field(..., description="Arreglo de la señal de audio cruda")
    fc: float = Field(..., description="Frecuencia central de la banda de octava (Hz)")
    fs: int = Field(..., description="Frecuencia de muestreo (Hz)")
    orden: int = Field(4, description="Orden del filtro Butterworth")


class FilterBandResponse(BaseModel):
    signal_out: list[float] = Field(..., description="Arreglo de la señal de audio filtrada")


router = APIRouter()


@router.get("/frequencies")
def lista_de_frecuencias_centrales():
    """
    Lista frecuencias centrales:
    Devuelve las frecuencias centrales normalizadas según la norma IEC 61260.
    """
    frec_cent_normalizadas = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
    return {"frecuencias_centrales_hz": frec_cent_normalizadas}


@router.post("/band", response_model=FilterBandResponse)
def filtrar_audio_por_banda(request: FilterBandRequest):
    """
    Filtra audio por bandas de octava:
    Recibe una señal cruda en formato JSON, le aplica un filtro IIR Butterworth
    centrado en 'fc' y devuelve la señal procesada.
    """
    # 1. Transformar JSON web (List) a matemática pura (NumPy Array)
    senal_numpy = np.array(request.signal_in, dtype=np.float64)

    try:
        # 2. Llamar a tu función
        senal_filtrada = filtro_octava(
            signal_in=senal_numpy, fc=request.fc, fs=request.fs, orden=request.orden
        )

        # 3. Transformar matemática pura (NumPy Array) de vuelta a JSON (List)
        return FilterBandResponse(signal_out=senal_filtrada.tolist())

    except ValueError as e:
        # Si el usuario mandó una frecuencia inválida, atrapamos TU error y devolvemos un Bad Request (400)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Cualquier otro error matemático inesperado
        raise HTTPException(status_code=500, detail=f"Error interno en el filtrado: {str(e)}")
