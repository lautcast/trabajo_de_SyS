# En este documento se guardarán los prompts utilizados en chats de IA, se agregarán sintesis de las respuesta obtenidas, y que reflexión hace el grupo respecto de su uso, los objetivos del mismo, y como atraviesa al proyecto en su totalidad.

## Prompt 1 (M0), sobre el armado de Ramas: 

Respecto al armado de ramas del proyecto que hemos estado hablando en conversaciones recientes, y teniendo en cuenta las condiciones que el profesor sugiere para la estrategia de ramas de este proyecto te hago una consulta; ¿se puede crear en vs code una branch dentro de una branch osea una rama dentro de otra rama?, porque nuestro porfue nos pide una rama por cada git issue, y surgió la idea de anidar la misma a los distintos Milestone que te mostré.

 *Respuesta dada por Gemini:*

Sí, totalmente. Se puede hacer sin ningún problema y, de hecho, es la forma ideal de trabajar cuando el profe les pide >aislar cada issue del proyecto. Aclaración: En Git no existe exactamente una rama "adentro" de otra como si fueran >carpetas. Lo que hacés es crear una rama nueva tomando como punto de partida el estado actual de otra rama. Ambas ramas >son independientes, pero comparten todo el historial hasta el momento en que las separaste.

Un tip clave para el trabajo en equipo: Antes de sacar una rama nueva para arrancar a codear, asegurate de hacer un git pull en la rama padre. Así te garantizás de tener los últimos commits que hayan subido tus compañeros al repositorio y te ahorrás el dolor de cabeza de resolver conflictos a la hora de hacer el merge.


## Prompt 2 (M0), sobre la sincornización de los cambios e instalación de despendencias:

Lo último a corregir sobre la sincronización en las dependencias del proyecto es que cuando aparece el pytest, pide "select a different interpeter", ¿cual debemos seleccionar, o hay alguna manera de solucionarlo?

 *Respuesta dada por Gemini:*

Cuando hicieron el git merge y resolviste los conflictos, te trajiste el archivo uv.lock actualizado de Lauti. Ese >archivo es como una "receta" que dice qué librerías necesita el proyecto. Pero Git solo te trae la receta, ¡no te >descarga los ingredientes automáticamente! Tu carpeta .venv local quedó desactualizada respecto a lo que dice el nuevo uv.>lock.

Escribí este comando y dale Enter:

>Bash
>uv sync

Ese comando va a leer el uv.lock, se va a dar cuenta de que te falta pytest, y lo va a instalar en un segundo.


## Prompt 3 (M2/M3), sobre la abstracción del Método de Lundeby:

Me está costando entender la lógica de iteración y convergencia en el método de Lundeby para buscar el punto de truncamiento. ¿Hay alguna manera de visualizar cómo se corrige a sí mismo o alguna analogía con sistemas de control?

 *Resúesta dada por Gemini:*

Propuso visualizar la Respuesta al Impulso como la ladera de una montaña que desciende hacia un mar de niebla (el ruido). Iterar significa medir la niebla a lo lejos, trazar una recta por la montaña, ver dónde cruza, y volver a medir la niebla exactamente en ese nuevo kilómetro de cruce. Además, trazó una analogía directa con un sistema de lazo cerrado (feedback loop): la señal es la planta, la medición del ruido en la cola es el sensor, el controlador es la regresión lineal que ajusta la pendiente, y el estado estacionario (convergencia) se alcanza cuando la diferencia entre mediciones cae por debajo de la tolerancia (0.1 dB).


## Prompt 4 (M2), sobre el aislamiento de tests unitarios y el manejo de rutas (Pytest):

Tengo un error de "variables no definidas" al intentar testear si la frecuencia final de un Sine Sweep es mayor a la inicial usando la FFT. Además, ¿cómo evitamos que los tests de generación de audio nos llenen el repositorio local de archivos .wav basura?

 *Respuesta dada por Gemini:*

Detectó un error de contexto (scope): estábamos intentando medir variables acústicas dentro de un bloque pytest.raises diseñado exclusivamente para capturar errores lógicos de duración, donde el código abortaba antes de calcular nada. Se reestructuró la aserción al test correcto. Respecto a los archivos, sugirió la implementación del fixture tmp_path nativo de Pytest para crear directorios temporales efímeros durante los tests.


## Prompt 5 (M3), sobre la precisión diferencial entre EDT y T30:

Al comparar los resultados de nuestra API contra REW usando la respuesta al impulso de un Mausoleo, el T30 nos da casi idéntico (perfecto), pero el EDT falla bastante en frecuencias graves. ¿Hay un error en cómo programamos Lundeby?

 *Respuesta dada por Gemini:*

Descartó tajantemente tocar Lundeby, argumentando desde la física acústica: Lundeby opera exclusivamente en el piso de ruido (al final del impulso), mientras que el EDT se calcula en los primeros 10 dB de la caída (al inicio del impulso). Diagnosticó que el problema radicaba en el "pre-ringing" del filtro de fase cero (sosfiltfilt), el cual desplazaba el tiempo cero de la señal. La solución fue forzar a la Integral de Schroeder a comenzar a integrar estrictamente desde el argmax (el verdadero impacto temporal).


## Prompt 6 (M2), sobre la robustez de los tests y el uso de semillas aleatorias:

Nuestros tests pasan bien con señales ideales, pero queremos poner a prueba el algoritmo con ruido real. ¿Cómo podemos mejorar los tests para asegurarnos de que la regresión no se rompa, sin que el test falle aleatoriamente cada vez que lo corremos?

 *Respuesta sintetizada de Gemini:*

Sugirió pasar de un "Happy Path Testing" a pruebas de resiliencia inyectando estática/ruido a la señal. Para evitar los "Flaky Tests" (tests que a veces pasan y a veces fallan por la aleatoriedad del ruido), recomendó usar `np.random.seed(42)`. Esto fija el generador de números aleatorios, garantizando que el ruido inyectado, aunque caótico, sea idéntico en cada ejecución del test. También sugirió usar aserciones con tolerancias (ej. `< 0.5`) en lugar de igualdades estrictas.


## Prompt 7 (M3), sobre la elección del filtrado y la función `sosfiltfilt`:

¿Por qué en el procesamiento de bandas de octava (Norma IEC 61260) es preferible usar `signal.sosfiltfilt` en lugar de un filtro estándar como `lfilter`, y qué impacto tiene en la señal acústica?

 *Respuesta sintetizada de Gemini:*

Explicó que `sosfiltfilt` aplica el filtro dos veces (hacia adelante y en reversa), lo que anula cualquier distorsión de fase (filtro de fase cero). Esto es vital en acústica para no desplazar temporalmente los picos de la Respuesta al Impulso. Además, al trabajar en secciones de segundo orden (SOS), evita inestabilidades numéricas comunes en filtros IIR de alto orden. La contrapartida es que atenúa el doble (-6 dB en vez de -3 dB) en las frecuencias de corte y genera un ligero "pre-ringing".


## Prompt 8 (M3), sobre el análisis espectral y la implementación del Método de Welch:

Para analizar el contenido frecuencial y el ruido de nuestras señales, ¿nos alcanza con usar una Transformada Rápida de Fourier (FFT) clásica o deberíamos implementar la función Welch, qué hace esta función?

 *Respuesta sintetizada de Gemini:*

Indicó que mientras la FFT es suficiente para señales estacionarias o puras (como un Sine Sweep ideal), para analizar señales con ruido el Método de Welch es superior. Welch divide la señal en ventanas superpuestas (overlapping), calcula el periodograma de cada una y las promedia. Esto reduce drásticamente la varianza de la estimación del espectro, entregando una curva de Densidad Espacial de Potencia (PSD) mucho más limpia y representativa del ruido de fondo real.


## Prompt 9 (M1/M2), sobre la escalabilidad, FastAPI y estandarización del código (Docstrings):

Tenemos todo el procesamiento acústico funcionando en scripts sueltos. Queremos unificarlo en una API REST y necesitamos que el código sea comprensible para cualquier desarrollador. ¿Qué buenas prácticas de documentación deberíamos aplicar?

 *Respuesta sintetizada de Gemini:*

Recomendó separar estrictamente la lógica acústica (el motor) de la lógica web (los endpoints). Hizo mucho énfasis en documentar todas las funciones matemáticas utilizando estándares como NumPy Docstrings, detallando explícitamente los parámetros, tipos de datos (Type Hinting) y retornos. Además, destacó que FastAPI lee automáticamente estos docstrings para autogenerar la documentación interactiva en Swagger UI.


## Prompt 10 (M3), sobre la sincronización de ramas cruzadas y actualización del entorno local:

Creé una rama desde main para trabajar en los endpoints (routers_endpoints), pero me di cuenta de que me faltan las funciones matemáticas que mi compañero recién fusionó a main desde su propia rama de parametros_acusticos. ¿Cómo hago para traerme esas funciones nuevas a mi rama actual sin romper el progreso que estoy haciendo?

 *Respuesta dada por Gemini:*

Explicó que este procedimiento estándar se llama "actualizar tu rama con main". Para hacerlo de forma segura y evitar errores de dependencias perdidas, detalló un flujo de 4 pasos:

-Hacer un commit en la rama actual para asegurar y guardar el progreso local.

-Cambiar a la rama main (git checkout main) y descargar los últimos cambios del remoto (git pull origin main).

-Volver a la rama de trabajo (git checkout routers_endpoints).

-Ejecutar la fusión (git merge main).

Además, aclaró que como estábamos trabajando en archivos lógicamente separados (un archivo para las rutas y otro para el procesamiento DSP), Git realizaría la fusión automáticamente sin generar conflictos.


## Prompt 11 (M3 - Demo e Integración), sobre la carga de archivos de audio reales en la API y Swagger UI:

Llegamos al "jefe final" del proyecto: la presentación en vivo. El profesor pide que demostremos cómo cargamos un audio real en la API y cómo esta hace su trabajo. El problema es que nuestro endpoint actual solo acepta un JSON gigante con números crudos. Aunque ya tenemos una función interna en Python que lee archivos WAV locales, ¿cómo adaptamos la API para poder subirle un archivo de audio directamente desde la interfaz y que nos devuelva el JSON con los parámetros?

 *Respuesta sintetizada de Gemini:*

Indicó que el endpoint debía actualizarse para utilizar el tipo de dato `UploadFile` nativo de FastAPI. Explicó que, al hacer esto, la interfaz gráfica de Swagger UI (`/docs`) genera automáticamente un botón de "Seleccionar archivo", permitiendo la subida desde el navegador. Detalló el flujo lógico necesario para el router: recibir el archivo, guardarlo en el disco de forma temporal, pasárselo a nuestra función de carga, procesar la acústica, devolver el JSON resultante y finalmente borrar el archivo temporal para no saturar el servidor. Además, proporcionó un "guion de demo" paso a paso, incluyendo cómo hacer la misma petición vía terminal usando `curl` para cumplir con las exigencias de la evaluación.


## Prompt 12 (M3), sobre calidad de código y linting:

El analizador de código estático (Ruff) bloqueaba la ejecución por la falta de un salto de línea final en los archivos y por la declaración de una variable de bucle iterativo (iteracion) que no se utilizaba en el cálculo de los parámetros acústicos de Lundeby.

 *Respuesta dada por Geimini:*

Sugirió utilizar el comando de corrección automática del linter para arreglar los saltos de línea y los espacios en blanco rápidamente (ruff check --fix). Para el bucle, recomendó renombrar manualmente la variable iteracion a _ (guion bajo), que es la convención estándar en Python para indicar que una variable es descartable y no será leída dentro del scope.


## Prompt 13 (M3), sobre Infracciones de nomenclatura (mixedCase vs snake_case):

Ruff identificó la variable nivel_ruido_dB como una infracción a la guía de estilo PEP 8, ya que la convención exige el uso estricto de minúsculas (snake_case). ¿Qué deberíamos hacer en este caso considerando la nomenclatura técnica?

 *Respuesta dada por Gemini:*

Planteó dos opciones:

1.Cambiar el nombre a nivel_ruido_db (recomendado para cumplir con PEP 8 a rajatabla).

2.Agregar una directiva de exclusión en esa línea específica (# noqa: N815) para forzar al linter a ignorar la regla, priorizando la claridad técnica de la unidad física (los decibeles se escriben "dB").


## Prompt 14 (M2), sobre Rutas no encontradas (Error 404 en Pytest):

Los tests automatizados fallaban (Error 404) al intentar enviar peticiones con archivos de audio a la API. El código de la prueba parecía estar bien estructurado, pero la conexión no se lograba.

 *Respuesta dada por Gemini:*

Diagnosticó que el cliente de pruebas (TestClient) estaba apuntando a un endpoint viejo que ya no existía en el enrutador refactorizado. Solucionó el problema actualizando el archivo de pruebas para que la URL base coincida estrictamente con la nueva arquitectura de endpoints de FastAPI (ej: /api/v1/analysis/impulse-response).

## Prompt 15 (M2), sobre Errores de estructura de datos en tests (KeyError):

Una vez superado el error 404, el test avanzó pero lanzó un KeyError al intentar acceder a la métrica de Claridad Acústica (C80), buscando dentro de una clave del JSON que ya no existía.

 *Respuesta dada por Gemini:*

Explicó que tras las actualizaciones en los modelos de Pydantic, la estructura del JSON devuelto había cambiado. Se ajustó la aserción dentro del archivo de pruebas (test_api_endpoints.py) para que la búsqueda del parámetro se hiciera directamente en la raíz de la respuesta JSON actualizada, sincronizando el test con el nuevo contrato de la API.


## Prompt 16 (M3), sobre Filtros IEC y extracción de envolventes (Hilbert/Schroeder)

Queríamos asegurarnos de que el filtro pasabanda de octava (Butterworth) y las tres funciones de suavizado acústico (Schroeder, Media Móvil e Hilbert) funcionaran correctamente sobre las señales reales. ¿Cómo validamos empíricamente esta matemática?

 *Respuesta sintetizada de Gemini:*

Desarrolló visualizaciones gráficas superpuestas para validar el código. Para los filtros, ajustó el ventaneo de análisis (`nperseg=8192`) para verificar visualmente que las frecuencias de corte cayeran exactamente a -3 dB. Para los suavizados, superpuso las tres curvas respetando estrictamente sus dominios físicos (energía vs. amplitud), validando cómo cada método extraía la envolvente del decaimiento.


## Prompt 17 (M2), sobre Simulación de Medición (Técnica de Farina) y Mínimos Cuadrados
**Contexto:** Para probar nuestra función de deconvolución (obtener la RI a partir de un Sine Sweep) y nuestra regresión lineal, necesitamos simular una medición real en una sala virtual, incluyendo ruido de fondo.

 *Respuesta sintetizada de Gemini:*

Programó un entorno de simulación usando convolución matemática para emular la sala. Graficó el proceso paso a paso: extrajo el impulso de Dirac compensado y recortó el "pre-ringing" mediante umbrales RMS. Por otro lado, generó una curva teórica de decaimiento, le inyectó ruido gaussiano, y graficó la recta ajustada para validar la robustez de nuestro cálculo de Mínimos Cuadrados y R².


## Prompt 18 (M0), sobre Gestión de entornos virtuales y VS Code tras un merge (uv sync)

Contexto: Luego de sincronizar y fusionar la rama de un compañero, VS Code dejó de reconocer a Pytest y nos arrojó el error "Select a different interpreter". ¿Cuál deberiamos seleccionar o cómo se solucionaba este desajuste?

 *Respuesta sintetizada de la IA:*

Diagnosticó que el error se debía a una desincronización del entorno virtual. Explicó que al hacer el merge, Git trajo el archivo uv.lock actualizado (la "receta" de dependencias del compañero), pero que Git no instala los paquetes automáticamente. La carpeta local .venv había quedado desactualizada. Sugirió correr el comando uv sync en la terminal para que el gestor leyera el nuevo .lock e instalara lo que faltaba, y luego seleccionar ese .venv como intérprete en VS Code.