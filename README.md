# Subestaciones de alta velocidad y centros de datos

Este trabajo estudia la capacidad de acceso a la red de transporte que las subestaciones de tracción de alta
velocidad tienen concedida y no utilizan, y cuánta potencia de centros de proceso de datos (CPD) podría compartirla
sin afectar al servicio ferroviario. Analiza además la arquitectura de conexión de ese CPD, su respuesta ante la
pérdida de suministro y el encaje regulatorio de la propuesta. Se estudian dos líneas: Madrid–Zaragoza–Barcelona
(alta densidad de tráfico) y Madrid–Sevilla (baja densidad).

El repositorio sirve de base a un artículo conceptual y a una propuesta de investigación. Los resultados son
preliminares: varios parámetros relevantes (potencia de cada subestación, tramo alimentado y PK exactos, curva de
carga real) no son públicos y se han estimado (ver [`docs/limitaciones_y_datos.md`](docs/limitaciones_y_datos.md)).

## Guía de lectura

La vía de entrada recomendada es la **web del proyecto** ([`web/index.html`](web/index.html)), que reúne en una sola página la propuesta, los resultados, la arquitectura, la regulación y el acceso al panel, al esquema y al vídeo. Se publica en Vercel con [`vercel.json`](vercel.json), que genera la carpeta `public/` a partir de los ficheros del repositorio sin duplicarlos.

| Material | Contenido |
|---|---|
| [`video/trenes_y_centros_de_datos.mp4`](video/trenes_y_centros_de_datos.mp4) | Presentación divulgativa de la propuesta (55 s) |
| [`results/dashboard.html`](results/dashboard.html) | Panel interactivo con las conclusiones, las dos líneas, la operación diaria de un CPD, las baterías y las cifras financieras |
| [`docs/esquema_instalacion.html`](docs/esquema_instalacion.html) | Esquema unifilar interactivo del emplazamiento de Anchuelo en cuatro escenarios (operación normal, pico de tracción, pérdida de la subestación vecina y apagón) |
| Sección [Documentos](#documentos) | Arquitectura, respuesta ante caídas, encaje regulatorio, fuentes de datos y limitaciones |
| Sección [El modelo](#el-modelo) | Descripción de cada script e instrucciones de ejecución |

## Planteamiento

- Las subestaciones de tracción de alta velocidad están conectadas a la red de transporte a 220/400 kV y tienen
  concedidos entre 30 y 66 MW de acceso cada una. La carga ferroviaria media apenas alcanza el 6–10 % de ese valor,
  aunque sus picos de pocos minutos sí lo ocupan.
- En España, la falta de capacidad de acceso a la red es la principal barrera para la implantación de nuevos CPD.
- Un CPD con posición propia en el mismo nudo, transformación propia y almacenamiento en baterías podría utilizar la
  capacidad que el ferrocarril deja libre. **El servicio ferroviario mantiene siempre la prioridad**: la batería absorbe
  sus picos y la fracción flexible de la carga del CPD (entrenamiento de IA, cálculo por lotes) se reduce cuando es
  necesario.
- La regulación vigente no permite compartir el permiso de acceso de Adif. El trabajo cuantifica la capacidad
  bloqueada y propone una reforma: el "acceso compartido con prioridad".

## Resultados principales

Miércoles laborable con Renfe (GTFS), Iryo (horarios reales) y Ouigo (frecuencias anunciadas), pendientes
aproximadas y las subestaciones reales con el acceso que REE tiene concedido a cada una:

| | Madrid–Barcelona (alta densidad) | Madrid–Sevilla (baja densidad) |
|---|---|---|
| Trenes / tren-km al día | 210 / 98.602 | 280 / 63.976 |
| Energía del tren | 1.292 MWh/día (12,8 kWh/tren-km) | 723 MWh/día (10,9 kWh/tren-km) |
| Subestaciones / acceso concedido | 13 / 516 MW | 12 / 512 MW |
| **Hoy**: capacidad firme (resiste N-1) | 35 MW (49 con CPD flexible) | 174 MW (248 con CPD flexible) |
| **Con reforma**: sin batería / CPD flexible 30 % | 70 / 100 MW | 227 / 314 MW |
| **Con reforma** y batería óptima (limitada a 2C) | 385 MW (161 MWh, 103 M€) | 417 MW (99 MWh, 63 M€) |
| Acceso ampliado a los transformadores: firme / con batería | 595 / 1.056 MW | 292 / 549 MW |

Arquitectura y caídas ([`docs/arquitectura_y_caidas.md`](docs/arquitectura_y_caidas.md), tabla en
[`results/arquitectura.csv`](results/arquitectura.csv)):

- **La batería es de potencia.** Con la energía mínima se descargaría por completo en 12–15 min y haría 4–6 ciclos al día
  (vida útil de unos 3 años). El modelo la limita a 2C: unos 30 min de energía, ≈2,8 ciclos al día y unos 8 años de vida.
- **La resolución con la que se evalúa el límite es determinante.** Sin batería, la capacidad para el CPD en
  Madrid–Barcelona pasa de 70 a 234 MW si el límite se evalúa con medias de 15 min en lugar de 1 min.
- **Cuando cae una subestación vecina**, el CPD con batería debe reducir 71 de 385 MW en Madrid–Barcelona
  (≈21 % por emplazamiento) y 57 de 417 MW en Madrid–Sevilla. La reducción cabe en el 30 % de carga flexible supuesto.
- **La instalación eléctrica completa** (posición propia, dos transformadores, batería y grupos) cuesta unos 317 M€ en
  Madrid–Barcelona y 296 M€ en Madrid–Sevilla, ≈10 % de lo que cuesta el propio CPD. Prescindir de grupos en el bloque flexible
  ahorra 62–69 M€.
- **El CPD conserva su Tier III**, porque para Uptime la red no es la fuente fiable, sino los grupos del propio
  emplazamiento. Se propone un diseño en dos bloques: uno firme con SAI y grupos, y otro flexible sin grupos.
- **El desequilibrio introducido por la tracción monofásica** se sitúa entre un 0,2 y un 0,8 % en el nudo de alta tensión (Scc supuesta).

Proyecto de RD de centros de datos ([`docs/encaje_regulatorio.md`](docs/encaje_regulatorio.md#7-proyecto-de-rd-de-centros-de-datos-estado-a-19102026)):

- Exige que, en cada hora, el 80 % del consumo esté cubierto por renovable nueva. Con los perfiles horarios de REE de 2025,
  un CPD plano necesita unos 9,5 MW de eólica y FV por MW para cumplir en el 95 % de las horas. **Si el bloque flexible
  baja en las horas sin viento ni sol, bastan 6,75 MW y cuesta ≈10 €/MWh menos.** La misma flexibilidad que cede
  potencia al ferrocarril reduce el coste de cumplimiento del decreto.
- El modelo adopta el PUE de 1,15 que establece el proyecto.

## Documentos

| Documento | Qué contiene |
|---|---|
| [`docs/arquitectura_y_caidas.md`](docs/arquitectura_y_caidas.md) | Cómo se conecta el CPD (posición, transformadores, 30 kV, batería, solar, grupos, control) y qué pasa en cada tipo de caída, con tiempos y Tier III/IV |
| [`docs/esquema_instalacion.html`](docs/esquema_instalacion.html) | El mismo diseño dibujado, interactivo, con los números de Anchuelo |
| [`docs/encaje_regulatorio.md`](docs/encaje_regulatorio.md) | Qué permite hoy la normativa (acceso flexible Tipo 3, reducción voluntaria del permiso de Adif), qué reforma haría falta y efecto del proyecto de RD de centros de datos (80 % renovable horario, PUE ≤ 1,15) |
| [`docs/capacidad_acceso.md`](docs/capacidad_acceso.md) | Fuentes y método para el acceso de cada subestación (REE, CNMC, BOE) |
| [`docs/limitaciones_y_datos.md`](docs/limitaciones_y_datos.md) | Parámetros no públicos que se han estimado, su efecto sobre los resultados y el parámetro del modelo al que afectan |
| [`docs/estado_del_arte.md`](docs/estado_del_arte.md) | Trabajos relacionados y contribución de este estudio |
| [`data/README.md`](data/README.md) | Datos de entrada: GTFS de Renfe, Iryo y Ouigo, subestaciones y perfiles horarios de REE |
| [`video/guion.md`](video/guion.md) | Guion del vídeo y origen de cada cifra |

## El modelo

```
GTFS Renfe + Iryo/Ouigo ─► extract.py ─► sim.py ─► analysis.py ─► finance.py ─► export.py ─► dashboard.py
   (horarios)            (trenes por    (potencia   (capacidad     (cifras      (tablas      (panel HTML)
                          tramo y PK)    por SET     para el CPD    €)            results/)
                                         a 1 s)      por SET)    ├► arquitectura.py (batería, N-1, caídas)
                                                                 └► renovable_horaria.py (80 % horario, datos REE)
```

| Script | Qué hace |
|---|---|
| `src/lines.py` | Definición de las líneas: estaciones, perfil de cotas, subestaciones, Iryo y Ouigo |
| `src/extract.py` | 1. Lee el GTFS y saca los trenes que usan cada línea, como tramos sobre el PK |
| `src/sim.py` | 2. Simula cada tren segundo a segundo (con pendientes) y suma la potencia por subestación |
| `src/analysis.py` | 3. Capacidad para el CPD por subestación: firme, sin batería, flexible, batería óptima |
| `src/finance.py` | 4. Cifras financieras orientativas e inversión eléctrica (posición, transformadores, batería, grupos) |
| `src/arquitectura.py` | 4b. Uso de la batería (C-rate, ciclos), recorte si cae la vecina, ventana de medida, rampas y desequilibrio |
| `src/renovable_horaria.py` | 4c. Renovable nueva que necesita un CPD para el 80 % horario del proyecto de RD, con y sin flexibilidad y batería |
| `src/export.py` | 5. Exporta las tablas de `results/` |
| `src/dashboard.py` | 6. Genera el panel `results/dashboard.html` a partir de esas tablas |
| `run_all.py` | Ejecuta todo para las dos líneas |

Carpetas: `data/` (subestaciones y acceso de REE, perfiles horarios de REE de 2025; el GTFS no se versiona), `results/` (tablas CSV y panel),
`docs/` (documentos y esquema), `video/` (vídeo, guion y el código que lo genera).

### Cómo ejecutarlo

Requiere Python 3.10 o superior.

```bash
pip install -r requirements.txt
# descomprime google_transit.zip de Renfe en data/gtfs/  (ver data/README.md)
python run_all.py                     # usa data/gtfs y el 21/10/2026
python run_all.py data/gtfs 20261104  # otra fecha dentro del calendario del GTFS
python src/dashboard.py results       # rehace solo el panel, sin volver a simular
```

En Windows puede ser necesario usar `py` en lugar de `python`.

### Tablas de resultados

| Fichero | Contenido |
|---|---|
| `results/capacidad.csv` | Capacidad para el CPD por subestación, opción y escenario de acceso |
| `results/arquitectura.csv` | Batería (C-rate, ciclos, versión 2C), recorte en N-1, hueco con medias de 1 s / 1 min / 15 min, rampas y desequilibrio |
| `results/finanzas.csv` | Canon a Adif, inversión del CPD y de la instalación eléctrica, valor de no esperar a una conexión propia |
| `results/renovable_horaria.csv` | Cartera mínima de eólica, FV y batería por MW de CPD para el 80 % horario, y su coste |
| `results/curvas_bateria.csv` | Tamaño del CPD frente a la batería necesaria |
| `results/perfil_hora.csv`, `perfil_minuto_*.csv` | Carga del tren por subestación |
| `results/simulacion.csv`, `lineas.json` | Resumen de la simulación y de las líneas |
| `results/supuestos.csv`, `supuestos_financieros.csv` | Todos los supuestos, con su fuente |

## Supuestos principales

Están en [`results/supuestos.csv`](results/supuestos.csv), [`results/supuestos_financieros.csv`](results/supuestos_financieros.csv)
y en la cabecera de cada script. Los de mayor influencia son:

1. **Acceso real y zona de cada subestación.** El acceso concedido es público (REE), pero en 6 subestaciones no se ha
   identificado la posición y los PK son estimados (±10 km).
2. **Pendientes.** Perfil de cotas aproximado (±50 m) a partir de estaciones y puertos; no se dispone del perfil longitudinal oficial.
3. **Horas de Ouigo.** Solo se conocen sus frecuencias.
4. **Criterio N-1.** Si cae una subestación, cada vecina asume la mitad de su carga.
5. **CPD flexible.** Un 30 % de su carga puede reducirse durante los picos de tracción.
6. **Ventana del límite.** El modelo evalúa el límite con medias de 1 minuto; con 15 minutos la capacidad aumenta de forma notable.
7. **Potencia de cortocircuito de cada nudo** (para el desequilibrio): 12 GVA a 400 kV y 5 GVA a 220 kV, supuestos.
8. **PUE de 1,15**, el tope del proyecto de RD de centros de datos.
9. **Cifras financieras.** Canon a Adif de 40 €/kW·año (20–80), baterías a 0,20 M€/MW + 0,25 M€/MWh, 3 años de
   espera evitados. Son órdenes de magnitud, no una valoración.

## Estado y líneas futuras

- **Fase actual:** artículo conceptual que desarrolle la propuesta (arquitectura, modelo, regulación y riesgos),
  orientado a revistas Q1. Posteriormente, estudios de casos concretos.
- **Validación:** los parámetros no públicos con mayor efecto sobre los resultados se recogen, ordenados por su peso,
  en [`docs/limitaciones_y_datos.md`](docs/limitaciones_y_datos.md). Los más influyentes son la resolución temporal
  con la que se evalúa el límite de potencia y las curvas de carga reales de las subestaciones.
- **Modelo:** perfil longitudinal real, horarios reales de Ouigo, perfiles de plantas renovables concretas (el perfil
  peninsular es optimista para el 80 % horario) y trazas reales de carga de CPD de IA para calibrar la parte flexible.
