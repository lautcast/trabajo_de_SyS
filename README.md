# RIR-API

API REST para procesamiento y analisis de respuestas al impulso segun la norma ISO 3382.

<!-- Badges -->
![CI](../../actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Descripcion

RIR-API es un proyecto educativo que implementa una API REST (FastAPI) con una cadena
completa de procesamiento acustico: generacion de senales de excitacion, procesamiento
de respuestas al impulso por bandas de octava y calculo de parametros acusticos
(EDT, T20, T30) segun la norma ISO 3382-1.

> **API de referencia**: Explorar la [documentacion interactiva de la API de la catedra](https://rir-api.onrender.com/docs) para entender la estructura de endpoints, schemas y respuestas esperadas.

## Requisitos previos

- Python 3.12 o superior
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes y entornos virtuales)

## Instalacion

```bash
# Clonar el repositorio
git clone https://github.com/lautcast/trabajo_de_SyS.git
cd trabajo_de_SyS
```

Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
source venv/bin/activate
```

### Instalar dependencias
```bash
uv sync
```

## Ejecucion

```bash
# Iniciar la API con hot-reload
uvicorn app.main:app --reload

# O usando el modulo directamente
python -m app.main
```

La API estara disponible en `http://localhost:8000`. Documentacion interactiva en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Estructura del proyecto

```
rir-api/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Punto de entrada FastAPI
│   ├── routers/
│   │   ├── health.py              # GET /health
│   │   ├── signals.py             # Endpoints de generacion (M1 → M3)
│   │   ├── filters.py             # Endpoints de filtrado (M2 → M3)
│   │   ├── acoustics.py           # Endpoints de analisis (M3)
│   │   └── utils.py               # Endpoints de utilidades (M3)
│   ├── schemas/
│   │   └── ...                    # Modelos Pydantic de request/response
│   └── services/
│       ├── pink_noise.py          # Generacion de ruido rosa (M1)
│       ├── sine_sweep.py          # Generacion de sine sweep (M1)
│       ├── signal_utils.py        # Utilidades de procesamiento (M2)
│       ├── filter.py              # Filtros de banda de octava (M2)
│       └── acoustic_parameters.py # Parametros acusticos ISO 3382 (M3)
├── tests/
│   ├── test_generacion.py         # Tests de generacion (M1)
│   ├── test_procesamiento.py      # Tests de procesamiento (M2)
│   ├── test_analisis.py           # Tests de analisis (M3)
│   └── test_api.py                # Tests de endpoints (M3)
├── docs/                          # Documentacion
├── .github/workflows/ci.yml       # Integracion continua
├── pyproject.toml                 # Configuracion del proyecto
└── README.md
```