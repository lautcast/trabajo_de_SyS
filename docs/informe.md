
1. INTRODUCCIÓN 

El objetivo de este proyecto es desarrollar un software modular para el cálculo de parámetros acústicos de acuerdo a la normativa ISO 3382 [1]. Esta normativa indica métodos de medición del tiempo de reverberación de un recinto cerrado. Para ello, utiliza respuestas al impulso. Este impulso puede generarse con una fuente impulsiva (disparo, globo) o con la generación de un barrido de frecuencias sinusoidal o sine sweep. A lo largo de este trabajo se desarrollan y analizan señales digitales para así caracterizar recintos a través de la obtención de parámetros acústicos del mismo. 

____________________________________________________________________________________________________________

2. MARCO TEÓRICO 

A continuación, se detalla el marco teórico de las funciones implementadas a lo largo de las milestones, 
explicaciones que son vitales para la comprensión de los resultados y conclusiones.

### 2.1. 

RUIDO ROSA 

El ruido rosa es un ruido que experimenta en cada octava de su espectro frecuencial una disminución en su nivel de 3 dB [2]. De este modo, su densidad espectral de potencia es proporcional a la inversa de la frecuencia; lo que resulta en un nivel constante por banda de tercio de octava. Esto lleva a que tenga más energía en frecuencias bajas y que refleje mejor la audición de tipo logarítmico del oído humano. Además, resulta más sencillo de producir que el ruido blanco. Por estas razones, es muy utilizado en mediciones acústicas para calibrar equipos: empleando este ruido, se ajusta el nivel de la fuente al menos a 45 dB por encima del piso de ruido, teniendo en cuenta el rango de frecuencias que se está analizando. 

### 2.2. 

SINE SWEEP LOGARÍTMICO Y FILTRO INVERSO 

La función tiene como objetivo crear dos señales de audio digitales: un barrido senoidal logarítmico (sine sweep) y su correspondiente filtro inverso.
El sine sweep es un tono de audio que comienza en una frecuencia grave y va aumentando gradualmente hasta una frecuencia alta a lo largo de un tiempo determinado. Al ser "logarítmico", el tono sube más lento en las frecuencias graves y más rápido en las agudas, lo cual se alinea con la forma en que el oído humano percibe el sonido.
En este trabajo, se utiliza principalmente para medir la Respuesta al Impulso de un sistema. La técnica de Angelo Farina (2000) [3] demostró que reproducir este "barrido" en una sala, grabarlo con un micrófono y luego procesarlo matemáticamente usando el filtro inverso, es el método más preciso para caracterizar acústicamente ese espacio y separar las distorsiones.


### 2.3. 

CARGAR AUDIO

### 2.4

SINTETIZAR RI

### 2.5

OBTENER RI DESDE SWEEP

Al excitar un sistema lineal e invariante en el tiempo con una señal x(t), se obtiene otra señal y(t) la cual será la respuesta o salida de este sistema a la señal de entrada insertad. Es posible pensar al sistema como un recinto, y a la señal y(t) como la grabación a través de un micrófono cuando sea lleva a cabo la reproducción de la señal x(t) en dicho recinto. 
Sin embargo, conociendo la respuesta al impulso de un recinto, es posible conocer y(t) sin necesidad de pasar a x(t) por el sistema. Esto se puede llevar a cabo mediante la convolución de x(t) con el impulso h(t):

y(t)=x(t)*h(t)   

Si quisiéramos conocer la respuesta al impulso del recinto, no podemos simplemente dividir y(t) con x(t), pero es posible hacer la convolución de la grabación y(t) con el filtro inverso de x(t):

y(t)*xinv(t)=[h(t)*x(t)]*xinv(t)

Por propiedades de la convolución, podemos reescribir esta última expresión como:

   y(t)*xinv(t)=[x(t)*xinv(t)]*h(t)(t)*h(t)

   y(t)*xinv(t)(t)*h(t)=h(t)

Es decir, al convolucionar x(t) con su filtro inverso, obtenemos aproximadamente la señal conocida como delta de dirac. Al hacer la convolución de la delta de dirac con cualquier otra señal, obtenemos dicha señal en sí misma.

### 2.6

A ESCALA LOG

### 2.7

FILTRO DE OCTAVA

### 2.8

SUAVIZAR SIGNAL

### 2.9

INTEGRAL DE SCHROEDER

### 2.10

REGRESIÓN LINEAL

### 2.11

CALCULAR PARÁMETROS ACÚSTICOS

### 2.12

MÉTODO LUNDEBY

___________________________________________________________________________________________________________

3. 

RESPUESTA AL IMPULSO 

La respuesta al impulso de un sistema es, como indica su nombre, la salida del sistema cuando se le inserta un impulso en la entrada. Debido a las características de un impulso (en teoría, su duración tiende a cero y su amplitud a infinito, lo que resulta en un espectro de frecuencias plano), permite caracterizar el sistema. Es decir, convolucionar una señal de entrada con la respuesta al impulso resulta en la señal de salida del sistema, o en este caso, del recinto. Por lo tanto, obtener la respuesta al impulso de un recinto nos permite calcular los parámetros acústicos del mismo. 

### 2.4. 

INTEGRAL DE SCHROEDER 

Mediante la integración regresiva propuesta por Schroeder, es posible calcular el tiempo de reverberación de un recinto. Para reducir errores, se suaviza la respuesta al impulso, antes de calcularla. A partir de esta integral, se obtiene una curva de decaimiento de la energía de la señal, la cual, tras aplicarle una regresión lineal se puede utilizar para calcular otros parámetros acústicos. 

### 2.5. 

PARÁMETROS ACÚSTICOS Y RT60 

La normativa ISO 3382 define el tiempo de reverberación como la duración requerida para que la energía promedio de la señal en un recinto cerrado decaiga 60 dB luego de que se haya dejado de emitir la misma [1]. Este parámetro es conocido como RT60 y se expresa en segundos. Sin embargo, en muchos casos no se tiene una diferencia señal-ruido de más de 60 dB, por lo que la normativa se basa en el cálculo de parámetros como el T20 (se calcula extrapolando el tiempo de decaimiento de -5 a -25 dB) o el T30 (-5 a -35 dB). 

3. DESARROLLO EXPERIMENTAL 

### 3.1. 

SINTETIZACIÓN DE RUIDO ROSA 

Para generar el ruido rosa se emplea el algoritmo de Voss y Clarke [3]. El mismo crea una matriz con fuentes de números aleatorios, los cuales varían a distintas velocidades. Sumando las filas, se consigue un vector de ruido rosa: más energía en bajas frecuencias debido a una menor variación de fuentes. La entrada de la función es el tiempo en segundos (resulta del cociente entre muestras y frecuencia de muestreo). Tiene como parámetros opcionales la frecuencia de muestreo (44100 Hz) y la cantidad de fuentes aleatorias (16). Devuelve un array normalizado, con valores entre 1 y -1. Una vez sintetizada la señal, se define una función que permite visualizar el dominio temporal de la misma. Por otro lado, se corrobora el dominio espectral de la misma con la herramienta de ploteo del software Audacity. Por último, se reproduce la señal mediante el uso de la librería sound device. 

### 3.2. 

GENERACIÓN DE SINE SWEEP LOGARÍTMICO + FILTRO INVERSO 

Para generar el sine sweep se utiliza la siguiente ecuación: 

$$f(x)=\sin[\theta(t)]=\sin[K(e^{\frac{t}{L}}-1)]$$

Donde $K=\frac{Tw_{1}}{R}$ y $L=\frac{T}{R}$ (1) T es el tiempo de duración del sine sweep en segundos y R el sweep rate $R=\ln(\frac{w_{2}}{w_{1}})$ donde $w_{1}$ es la frecuencia inferior y $w_{2}$ la superior del barrido. Por otro lado, la ecuación para generar el filtro inverso que ajuste el decaimiento del sine sweep es: 

$$k(t)=m(t)x(-t)$$

Donde $m(t)$ es la modulación dada por: 

$$m(t)=\frac{w_{1}}{2\pi w(t)}$$

$w(t)$ es la frecuencia instantánea, es decir, la derivada de la amplitud en función de la frecuencia: 

$$w(t)=\frac{d[\theta(t)]}{dt}=\frac{K}{L}e^{\frac{t}{L}}$$

A partir de estas ecuaciones, se definieron funciones para sintetizar un sine sweep y su filtro inverso. Ambas funciones tienen como parámetro de entrada la duración en segundos, y como parámetros opcionales la frecuencia de muestreo (44100 Hz), la frecuencia inferior (20 Hz) y la frecuencia superior (20000 Hz). Se reprodujeron las señales con sound device, y se visualizó su dominio espectral. 

### 3.3. 

FUNCIÓN ADQUISICIÓN Y REPRODUCCIÓN 

Se definió una función para la reproducción y adquisición de manera simultánea. Para ello se utilizó la función playrec de sound device. Su parámetro de entrada era la señal, con la frecuencia de muestreo como parámetro opcional (44100 Hz). La función definida reproduce y graba la señal, guardándola en un archivo wav. Asimismo, se desarrolló otra función para medir la latencia de playrec. Sus parámetros opcionales son la frecuencia de muestreo (44100 Hz) y la duración (1 segundo). Devuelve la latencia e imprime su valor en términos de muestras y de milisegundos. 

### 3.4. 

SINTETIZACIÓN DE RESPUESTA AL IMPULSO 

Desarrollamos una función que, a partir de un diccionario de frecuencias centrales, sus respectivos tiempos de reverberación T60 y amplitudes, sintetiza una respuesta al impulso. Para ello, primero determinamos la duración de la respuesta al impulso, siendo esta un 20% mayor al T60 más alto del diccionario, asegurándonos de esta manera que incluya toda la reverberación. La respuesta al impulso, se definió teniendo en cuenta la ecuación: 

$$y_{i}=A_{i}e^{-\tau_{i}t}\cos(2\pi f_{i}t)$$

Donde A es la amplitud de la banda, y $\tau$ define el decaimiento exponencial en función del tiempo de reverberación, ambas para la frecuencia $f_{i}$ con la que se esté trabajando. 

$$\tau_{i}=-\frac{\ln(10^{-3})}{T_{60_{i}}}$$

Luego, la sumatoria de las respuestas al impulso para cada frecuencia central, genera una aproximación a la respuesta al impulso total del recinto, siendo n la cantidad de frecuencias centrales del filtro. 

$$y=\sum_{y=1}^{n}y_{i}$$

Para finalizar, se normalizó el vector de la respuesta al impulso, de manera que se pueda guardar en un archivo de audio .wav. 

### 3.5. 

OBTENCIÓN DE LA RESPUESTA AL IMPULSO CON UN SINE SWEEP 

Partiendo de la base que, al excitar un recinto con un sineswep logarítmico $x(t)$, se obtiene la respuesta al impulso del mismo $h(t)$ captado por un micrófono $y(t)$: 

$$y(t)=x(t)*h(t)$$

Se puede deducir que: 

$$h(t)=F^{-1}[H(jw)]=F^{-1}[Y(jw)K(jw)]$$

Con $k(t)$ el filtro inverso y $K(jw)$ su respectiva transformada de Fourier. De esta manera, realizamos una función que obtiene la respuesta al impulso de un recinto a través de la multiplicación de espectros. Por último, normalizamos la respuesta al impulso con el objetivo de poder exportarla como un archivo de audio .wav. 

### 3.6. 

FILTRO DE OCTAVA Y TERCIO DE OCTAVA 

Para calcular los parámetros acústicos en función de sus frecuencias, realizamos una función que filtra todas las señales en octavas y tercios de octavas según la norma IEC 61260. Para ello, definimos una variable G para determinar el ancho de banda tanto para los filtros de octava como para los de tercio de octava y se realizaron dos listas con las frecuencias centrales de ambos filtros. Luego, se calcularon los límites de las bandas y, a través del módulo scipy, se realizó un filtro pasabandas. Finalmente, el código imprime qué banda se filtró, sus cortes y devuelve un diccionario que contiene la frecuencia central y la señal filtrada para esa banda. 

### 3.7. 

CONVERSIÓN A ESCALA LOGARÍTMICA 

A razón de visualizar la señal adecuadamente, es necesario convertirla a escala logarítmica. Realizamos entonces, una función que se encargue de ello a partir de la siguiente ecuación: 

$$R(t)=20\log_{10}\frac{A(t)}{A(t)_{max}}$$

Donde $A(t)$ es la señal que se quiere escalar. Además, se modificó levemente la ecuación al sumarle una magnitud despreciable, de modo que no influya en el resultado pero que se evite el error en caso de que el argumento sea 0. 

### 3.8. 

SUAVIZADO DE LA SEÑAL 

Para obtener una señal suavizada, se utilizó la transformada de Hilbert cuyo espectro de frecuencias es nulo para frecuencias negativas e igual a la señal original para frecuencias positivas. Esta transformada, permite obtener la envolvente de la señal. Para ello, primero se obtuvo la cantidad de muestras de la señal de entrada y se le aplicó la transformada rápida de Fourier, convirtiendo la misma al dominio de la frecuencia. Luego, se la multiplicó por un vector que elimina las frecuencias negativas de modo que quede una señal analítica. Por último, se aplicó la transformada inversa y se calculó el valor absoluto de este resultado. De esta manera, se obtuvo la envolvente, es decir una señal suavizada de la original. 

### 3.9. 

FILTRO PROMEDIO MÓVIL 

Se realizó un código capaz de obtener una función filtrada para cada muestra de una señal. Esto, sucede según la ecuación: 

$$y[i]=\frac{1}{L}\sum_{j=0}^{L-1}x[i-j]$$

Se creó un Kernel, es decir una ventana de L valores de $1/L$. Luego, se lo convolucionó con la señal y, de esta forma se obtuvo la señal suavizada. 

### 3.10. 

INTEGRAL DE SCHROEDER 

A partir de la respuesta al impulso de la señal, se realizó un vector de la energía instantánea de la misma. Esto se utilizó para calcular la integral de Schroeder con lo que es posible analizar el decaimiento de energía de la señal. Su ecuación se define como: 

$$E(t)=\int_{t}^{\infty}p^{2}(\tau)\partial\tau=\int_{0}^{\infty}p^{2}(\tau)\partial\tau-\int_{0}^{t}p^{2}(\tau)\partial\tau$$

Para calcularla, propusimos dos posibilidades, en primer lugar, se puede hacer implementando la función de Lundeby, que calcula los límites de la integral para evitar la influencia del ruido de fondo y solo calcular la curva de Schroeder hasta donde es útil. Por otro lado, en caso que no se especifique los límites por Lundeby, la función utiliza toda la señal. Para hacer esto posible, primero se calcula la energía total de la señal, es decir la integral desde cero hasta infinito. Luego, se realiza un vector de la energía total acumulada hasta cada punto. Por último, se restan ambas partes y se obtiene el resultado de la integral de Schroeder. 

### 3.11. 

REGRESIÓN LINEAL 

Para aproximar la tendencia de decaimiento de la señal a una recta, a partir de la integral de Schroeder, realizamos una función de regresión lineal por el método de cuadrados mínimos. Esta recta, minimiza la suma de los cuadrados de las diferencias entre los valores observados y los predichos por la línea que se define como: 

$$y=ax+b$$

con y la variable dependiente, x la variable independiente y donde a y b son: 

$$a=\frac{n\sum xy-\sum x\sum y}{n\sum x^{2}-\sum x^{2}}$$



$$b=\frac{\sum y-a\sum x}{n}$$

respectivamente. Donde n es la cantidad de muestras de la señal. 

### 3.12. 

PARÁMETROS ACÚSTICOS 

A partir de la regresión lineal obtenida luego de aplicar la integral de Schroeder a la respuesta al impulso, se calcularon el EDT, T10, T20, T30, D50 y C80. En primer lugar, se creó un vector con la energía instantánea de la respuesta al impulso y otro vector de tiempo para asociar cada muestra a su respectivo instante. Además, se normalizó la curva de modo que la misma empiece en 0 dB. Para calcular el EDT, se realizó una regresión lineal entre -1 y -11 dB. Esta, empieza desde -1 en vez de 0 dB para mejorar la estabilidad del cálculo, evitando posibles irregularidades causadas por el sistema. Luego, se extrapoló la recta generada a través del método de mínimos cuadrados, permitiendo de esta manera, estimar cuánto tarda la señal en caer 60 dB. Para el T10, T20 y T30 el desarrollo fue similar pero las regresiones lineales se generaron desde -5 hasta -15, -25 y -35 dB respectivamente. Con respecto al D50, para calcularlo se dividió el vector de la energía instantánea de la respuesta al impulso en muestras de hasta 50 ms, sin exceder la longitud de la señal. Luego, se dividió la magnitud de energía de la primera muestra por el resultado de la energía total de la señal. Al multiplicar este resultado por 100, se obtuvo el D50. Para el cálculo del C80, el procedimiento fue semejante al del D50, pero fraccionando la señal en muestras de 80 ms. Finalmente, el código devuelve un diccionario con todos los parámetros acústicos mencionados y sus respectivos resultados. 

4. RESULTADOS Y ANÁLISIS 

La figura 1 muestra el diagrama de flujo del software. Es decir, cómo se conectan todas las funciones desarrolladas para finalmente calcular los parámetros acústicos de un recinto. 

### 4.1. 

SINTETIZACIÓN DE RUIDO ROSA 

A partir del código realizado, pudimos obtener la señal de ruido rosa de 10 segundos que se observa en la figura 2. En la figura 3, se puede apreciar el espectro del ruido rosa, el cual decrece aproximadamente 3 dB por octava. 

### 4.2. 

SINE SWEEP LOGARÍTMICO Y FILTRO INVERSO 

Logramos obtener el sinesweep logarítmico asi como su filtro inverso, como se observa en la figura 4. En esta, se puede advertir el decaimiento en amplitud del filtro inverso debido a su característica inversamente exponencial. La figura 5, es un gráfico del filtro inverso teniendo en cuenta la amplitud en función de la frecuencia. Se puede observar como la amplitud aumenta a medida que la frecuencia se incrementa. La energía distribuida en el filtro se relaciona con la amplitud, por lo tanto, también tendrá un comportamiento ascendente respecto a la frecuencia. 

### 4.3. 

SINTETIZACIÓN DE LA RESPUESTA AL IMPULSO 

Partiendo del T60 de cada frecuencia central de cierto recinto, obtuvimos la respuesta al impulso del mismo, como se puede apreciar en la figura 6. La señal no es del todo limpia, ya que el método utilizado da como resultado una aproximación a la respuesta al impulso del recinto. A pesar de ser una buena aproximación, no deja de ser una modulación a partir de condiciones teóricas. Esto puede verse aún más en la figura 7, la cual muestra el dominio espectral de la respuesta al impulso sintetizada. Se puede observar cómo la respuesta fue generada a partir de valores otorgados a cada frecuencia octavada. 

### 4.4. 

OBTENCIÓN DE LA RESPUESTA AL IMPULSO CON UN SINE SWEEP 

A partir de un sine sweep grabado, y el filtro inverso, logramos obtener la respuesta al impulso en formato de señal de audio como se muestra en la figura 8. A diferencia de la respuesta al impulso sintetizada, esta respuesta obtenida a partir de una grabación resulta más fiel a la realidad, particularmente en la forma heterogénea de la cola reverberante. 

### 4.5. 

FILTRO DE OCTAVA Y TERCIO DE OCTAVA, Y FUNCIÓN DE CONVERSIÓN A ESCALA LOGARÍTMICA 

La figura 9 muestra el espectro de frecuencias de la respuesta al impulso sintetizada luego de haber sido filtrada por la función desarrollada según la norma IEC 61260. Particularmente muestra el resultado del filtro de orden 4, centrado en 125 Hz. Se observa una curva de decaimiento pronunciada (debido al orden del filtro) y se comprueba el correcto funcionamiento del código desarrollado, lo cual será útil para el desarrollo del algoritmo. Esta misma señal filtrada se pasó por la función de conversión a escala logarítmica. La figura 10 muestra la caída en decibeles a lo largo del tiempo, es decir, el gráfico del dominio temporal de la respuesta al impulso filtrada. 

### 4.6. 

OBTENCIÓN DE PARÁMETROS ACÚSTICOS 

A continuación se analizarán los resultados obtenidos a partir de la respuesta al impulso grabada desde un punto del Jack Lyons Concert Hall, siguiendo el resto del diagrama de bloque que aún no fue analizado. La figura 11 muestra su evolución en el dominio temporal, mientras que la figura 12 muestra su espectro en frecuencias. 

#### 4.6.1. 

SUAVIZADO DE LA SEÑAL Y FILTRO PROMEDIO MÓVIL 

La señal primero fue filtrada por bandas de octava con filtro de orden 4. A cada banda de octava se le aplicó la transformada de Hilbert y el filtro de promedio móvil. La envolvente de la respuesta al impulso resultante se muestra en la figura 13. Se observa el suavizado de la señal en comparación a la original. 

#### 4.6.2. 

INTEGRAL DE SCHROEDER Y REGRESIÓN LINEAL 

A la señal suavizada se le aplicó la integral de Schroeder. Esta integral se la convirtió a escala logarítmica y se aproximó la curva obtenida a una recta mediante cuadrados mínimos. El resultado se observa en la figura 14. Se puede ver el claro decaimiento de la señal en función del tiempo, hasta alcanzar el nivel de ruido determinado por el método de Lundeby. 

#### 4.6.3. 

PARÁMETROS ACÚSTICOS Y COMPARACIÓN CON SOFTWARE REW 

Finalmente, a partir de la integral de Schroeder y su aproximación lineal se obtuvieron los valores de parámetros acústicos por banda de octava de la Tabla 1. 

| Parámetro | 125 | 250 | 500 | 1000 | 2000 | 4000 | 8000 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EDT | 1.97 | 2.33 | 1.81 | 1.89 | 1.81 | 1.34 | 0.87 |
| T10 | 1.62 | 1.86 | 1.77 | 1.71 | 1.68 | 1.25 | 0.87 |
| T20 | 1.96 | 1.90 | 1.85 | 1.76 | 1.67 | 1.24 | 0.83 |
| T30 | 2.23 | 1.79 | 2.07 | 1.77 | 1.67 | 1.28 | 0.83 |
| C80 | 0.64 | 0.62 | 0.87 | -0.64 | 0.36 | 0.69 | 4.32 |
| D50 | 34.35 | 34.33 | 41.53 | 40.98 | 36.45 | 37.32 | 52.66 |

*Tabla 1: Parámetros acústicos obtenidos con el software desarrollado.* 

La Tabla 2 muestra los valores obtenidos al importar la misma respuesta al impulso al software REW. 

| Parámetro | 125 | 250 | 500 | 1000 | 2000 | 4000 | 8000 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EDT | 2.27 | 2.36 | 2.57 | 2.35 | 1.92 | 1.41 | 0.82 |
| T20 | 2.04 | 2.08 | 1.80 | 1.76 | 1.75 | 1.30 | 0.88 |
| T30 | 2.11 | 2.18 | 1.79 | 1.79 | 1.72 | 1.31 | 0.88 |
| C80 | -4.88 | -6.00 | -6.49 | -4.44 | -1.14 | 0.69 | 5.87 |
| D50 | 16.3 | 20.3 | 8.8 | 18.2 | 33.9 | 41.9 | 69.5 |

*Tabla 2: Parámetros acústicos obtenidos con el software REW.* 

Los valores de tiempo de reverberación (EDT, T20 Y T30) resultaron similares a los calculados por el REW, con mayor tiempo de decaimiento alrededor de los 250 y 500 Hz. Por otro lado, los valores de C80 y D50 son considerablemente distintos entre los dos softwares, especialmente en el rango de medias y bajas frecuencias. Esto puede ser debido a que estos parámetros no se calculan a partir de la regresión lineal, sino de la energía dada por la integral de Schroeder. 

5. CONCLUSIONES 

Se logró desarrollar un software que, a partir de la respuesta al impulso sintetizada u obtenida, calcule parámetros acústicos de una sala. Las funciones desarrolladas fueron eficientes a la hora de procesar las señales. Se tuvieron en cuenta posibles inconvenientes, como la aparición de logaritmos nulos o errores del usuario al cargar datos. Se verificó el óptimo funcionamiento de las mismas mediante gráficos de dominio temporal y espectral. Los valores EDT, T10, T20 y T30 obtenidos resultaron coherentes entre sí. Particularmente, los EDT, T10 y T20 fueron similares a los calculados con el software REW. Sin embargo, los parámetros C80 y D50 tienen diferencias considerables con respecto a los obtenidos con el REW. 

Referencias 

* [1] ISO 3382-2. Measurement of room acoustic parameters, 2008. 


* [2] Universidad Nacional de Tres de Febrero. Trabajo práctico: "desarrollo de software para el cálculo de parámetros acústicos iso 3382". Señales y Sistemas. 


* [3] Clarke J. Voss, R. F. "1/f noise in music: Music from 1/f noise". Journal of the Acoustical Society of America 63: 258-263, 63:258-263, 1978.