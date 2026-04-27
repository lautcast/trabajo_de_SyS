# En este documento se guardarán los prompts utilizados en chats de IA, se agregarán sintesis de las respuesta obtenidas, y que reflexión hace el grupo respecto de su uso, los objetivos del mismo, y como atraviesa al proyecto en su totalidad.

## Prompt 1 (M0), sobre el armado de Ramas: 

Respecto al armado de ramas del proyecto que hemos estado hablando en conversaciones recientes, y teniendo en cuenta las condiciones que el profesor sugiere para la estrategia de ramas de este proyecto te hago una consulta; ¿se puede crear en vs code una branch dentro de una branch osea una rama dentro de otra rama?, porque nuestro porfue nos pide una rama por cada git issue, y surgió la idea de anidar la misma a los distintos Milestone que te mostré.

> **Respuesta dada por Gemini:**

>Sí, totalmente. Se puede hacer sin ningún problema y, de hecho, es la forma ideal de trabajar cuando el profe les pide >aislar cada issue del proyecto. Aclaración: En Git no existe exactamente una rama "adentro" de otra como si fueran >carpetas. Lo que hacés es crear una rama nueva tomando como punto de partida el estado actual de otra rama. Ambas ramas >son independientes, pero comparten todo el historial hasta el momento en que las separaste.

Un tip clave para el trabajo en equipo: Antes de sacar una rama nueva para arrancar a codear, asegurate de hacer un git pull en la rama padre. Así te garantizás de tener los últimos commits que hayan subido tus compañeros al repositorio y te ahorrás el dolor de cabeza de resolver conflictos a la hora de hacer el merge.



## Prompt 2 (M0), sobre la sincornización de los cambios e instalación de despendencias:

Lo último a corregir sobre la sincronización en las dependencias del proyecto es que cuando aparece el pytest, pide "select a different interpeter", ¿cual debemos seleccionar, o hay alguna manera de solucionarlo?

> **Respuesta dada por Gemini:**

>Cuando hicieron el git merge y resolviste los conflictos, te trajiste el archivo uv.lock actualizado de Lauti. Ese >archivo es como una "receta" que dice qué librerías necesita el proyecto. Pero Git solo te trae la receta, ¡no te >descarga los ingredientes automáticamente! Tu carpeta .venv local quedó desactualizada respecto a lo que dice el nuevo uv.>lock.
>
>Escribí este comando y dale Enter:
>
>Bash
>uv sync
>
>Ese comando va a leer el uv.lock, se va a dar cuenta de que te falta pytest, y lo va a instalar en un segundo.



## Prompt 3 (M0), 