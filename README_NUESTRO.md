# SyS_2026
Trabajo para la materia señales y sistemas.

# RIR-API

API REST desarrollada en Python utilizando FastAPI para el cálculo de parámetros acústicos a partir de respuestas al impulso (RIR), siguiendo la norma ISO 3382.

El sistema permite generar señales de excitación, procesar respuestas al impulso y calcular parámetros como RT60, C50 y EDT. La API está diseñada para ser consumida por clientes externos como aplicaciones web, scripts o herramientas de análisis.

---

## 🎯 Objetivo técnico

Procesar respuestas al impulso (RIR) y calcular parámetros acústicos según la norma ISO 3382.

---

## 👥 Integrantes

- Pellegrino Salvador - Legajo: 75978 - Rol: Backend / API
- Castrillo Lautaro - Legajo: 70558 - Rol: Procesamiento de señales
- Maiolo Ivan - Legajo: 76593 - Rol: Testing / Documentación

---

## 🛠️ Tecnologías

- FastAPI
- NumPy
- SciPy
- Pydantic
- Uvicorn
- Matplotlib
- Soundfile
- Sounddevice
- Python-multipart

---

## ⚙️ Instalación

### Clonar el repositorio

```bash
git clone https://github.com/salvipellegrino/SyS_2026.git
cd SyS_2026
```


### Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate
```


### Instalar dependencias
```bash
pip install -r requirements.txt
```


### Ejecutar la api:
```bash
uvicorn app.main:app --reload
```


### 🌐 Acceso a la API
Una vez ejecutada:
Documentación interactiva: http://127.0.0.1:8000/docs
Estado del servidor: http://127.0.0.1:8000/health


### Estructura del proyecto
```bash
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


### Estrategia de ramas

**Main** -> rama protegida

#Ramas de desarrollo de los git-issues divididas por cada Milestone:

# ==============================================================
# 🚀 GUÍA RÁPIDA DE RAMAS PARA NUESTRO PROYECTO RIR-API 
# ==============================================================


# --- M1: Generación ---

**feature/sine-sweep**                                  # Issue #1
**feature/ruido-rosa**                                  # Issue #2
**feature/test-distribucion**                           # Issue #3

# --- M2: Procesamiento ---

**feature/filtro-butterworth**                          # Issue #4
**docs/rango-fc**                                       # Issue #5 (Etiqueta docs)
**docs/test-senales-conocidas**                         # Issue #6 (Etiqueta docs)
**feature/cargar-audio**                                # Issue #7
**feature/sintesis-rir**                                # Issue #8
**feature/deconvolucion**                               # Issue #9
**feature/escala-logaritmica**                          # Issue #10

# --- M3: Producto Final ---

**feature/suavizado-media-movil**                       # Issue #11
**feature/integral-schroeder**                          # Issue #12
**feature/regresion-lineal**                            # Issue #13
**feature/parametros-iso3382**                          # Issue #14
**feature/lundeby-RI**                                  # Issue #15

# --------------------------------------------------------------
# GUARDAR Y SUBIR MODIFICACIONES (EL ABC)
# --------------------------------------------------------------

git add .
git commit -m "...(#Nro de issue)"
git push 



### Convencion de commits
- **feat**: nueva funcionalidad
- **fix**: corrección de errores
- **test**: pruebas

---