# Subestaciones de alta velocidad y centros de datos

¿Cuánta capacidad de conexión a la red tienen sin usar las subestaciones de tracción de alta velocidad,
y cuántos MW de centros de datos (CPD) podrían compartirla sin afectar al servicio ferroviario? ¿Cómo
se conectaría ese CPD y qué le pasa si se cae la subestación? Se estudian dos líneas: Madrid–Zaragoza–Barcelona
(alta densidad) y Madrid–Sevilla (baja densidad).

Es la base de un paper conceptual y de una propuesta de investigación. Los resultados son preliminares: varios
datos clave (potencia de cada subestación, su zona y PK exactos, su curva de carga real) no son públicos y se han
estimado.

## Por dónde empezar

| Si tienes... | Abre | Qué vas a ver |
|---|---|---|
| 1 minuto | [`video/trenes_y_centros_de_datos.mp4`](video/trenes_y_centros_de_datos.mp4) | La idea en 55 s, para público no técnico |
| 5 minutos | [`results/dashboard.html`](results/dashboard.html) (doble clic) | Panel interactivo con las conclusiones, las dos líneas, el día de un CPD, las baterías y las cifras financieras |
| Ganas de entender la instalación | [`docs/esquema_instalacion.html`](docs/esquema_instalacion.html) (doble clic) | Esquema unifilar interactivo de Anchuelo: red, transformadores, batería, solar, grupos y servidores en 4 escenarios (día normal, pico del tren, cae la vecina, apagón) |
| Que escribir el paper | La sección [Documentos](#documentos) | Arquitectura, respuesta ante caídas, encaje regulatorio, fuentes de datos |
| Que tocar el modelo | La sección [El modelo](#el-modelo) | Qué hace cada script y cómo ejecutarlo |

## La idea

- Las subestaciones de tracción de alta velocidad están conectadas a la red de transporte de REE a 220/400 kV y
  tienen concedidos 30–66 MW de acceso cada una. El tren solo usa de media el 6–10 %, pero sus picos de minutos
  llenan ese acceso.
- En España, la falta de acceso a la red es el principal freno para nuevos centros de datos.
- Un CPD con su propia posición en el mismo nudo, su propio transformador y una batería podría usar la capacidad
  que el tren deja libre. **El tren tiene siempre prioridad**: la batería se come sus picos y la parte flexible del
  CPD (entrenamiento de IA, cálculo por lotes) cede potencia cuando hace falta.
- Hoy la regulación no permite compartir el acceso de Adif. El paper cuantifica cuánta capacidad está bloqueada y
  propone la reforma: un "acceso compartido con prioridad".

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
| **Con reforma** y batería óptima | 380 MW (89 MWh, 84 M€) | 412 MW (36 MWh, 46 M€) |
| Acceso ampliado a los transformadores: firme / con batería | 595 / 1.046 MW | 292 / 544 MW |

Arquitectura y caídas ([`docs/arquitectura_y_caidas.md`](docs/arquitectura_y_caidas.md), tabla en
[`results/arquitectura.csv`](results/arquitectura.csv)):

- **La batería es de potencia y trabaja mucho.** Se descarga entera en 12–15 min y hace 5–6 ciclos al día. Si se
  limita a 2C (101 M€ en Madrid–Barcelona, 60 M€ en Madrid–Sevilla), baja a 2,5–3 ciclos y dura unos 8 años.
- **Cómo se mida el límite lo cambia todo.** Sin batería, el CPD pasa de 70 a 234 MW en Madrid–Barcelona si el
  límite se vigila con medias de 15 min en vez de 1 min.
- **Cuando cae una subestación vecina**, el CPD con batería tiene que recortar 86 de 380 MW en Madrid–Barcelona
  (≈25 % por emplazamiento) y 62 de 412 MW en Madrid–Sevilla. Cuadra con el 30 % de carga flexible supuesto.
- **El CPD conserva su Tier III**, porque para Uptime la red no es la fuente fiable, sino los grupos del propio
  emplazamiento. Se propone un diseño en dos bloques: uno firme con SAI y grupos, y otro flexible sin grupos.
- **El desequilibrio del tren monofásico** sale entre un 0,2 y un 0,8 % en el nudo de alta tensión (Scc supuesta).

## Documentos

| Documento | Qué contiene |
|---|---|
| [`docs/arquitectura_y_caidas.md`](docs/arquitectura_y_caidas.md) | Cómo se conecta el CPD (posición, transformadores, 30 kV, batería, solar, grupos, control) y qué pasa en cada tipo de caída, con tiempos y Tier III/IV |
| [`docs/esquema_instalacion.html`](docs/esquema_instalacion.html) | El mismo diseño dibujado, interactivo, con los números de Anchuelo |
| [`docs/encaje_regulatorio.md`](docs/encaje_regulatorio.md) | Qué permite hoy la normativa (acceso flexible Tipo 3, reducción voluntaria del permiso de Adif) y qué reforma haría falta |
| [`docs/capacidad_acceso.md`](docs/capacidad_acceso.md) | De dónde sale el acceso de cada subestación (REE, CNMC, BOE) y qué falta |
| [`docs/solicitud_transparencia_adif.md`](docs/solicitud_transparencia_adif.md) | Texto para pedir a Adif los datos reales de sus subestaciones |
| [`docs/estado_del_arte.md`](docs/estado_del_arte.md) | Trabajos cercanos y hueco que cubre este estudio |
| [`data/README.md`](data/README.md) | Datos de entrada: GTFS de Renfe, Iryo y Ouigo, subestaciones |
| [`video/guion.md`](video/guion.md) | Guion del vídeo y origen de cada cifra |

## El modelo

```
GTFS Renfe + Iryo/Ouigo ─► extract.py ─► sim.py ─► analysis.py ─► finance.py ─► export.py ─► dashboard.py
   (horarios)            (trenes por    (potencia   (capacidad     (cifras      (tablas      (panel HTML)
                          tramo y PK)    por SET     para el CPD    €)            results/)
                                         a 1 s)      por SET)    └► arquitectura.py (batería, N-1, caídas)
```

| Script | Qué hace |
|---|---|
| `src/lines.py` | Definición de las líneas: estaciones, perfil de cotas, subestaciones, Iryo y Ouigo |
| `src/extract.py` | 1. Lee el GTFS y saca los trenes que usan cada línea, como tramos sobre el PK |
| `src/sim.py` | 2. Simula cada tren segundo a segundo (con pendientes) y suma la potencia por subestación |
| `src/analysis.py` | 3. Capacidad para el CPD por subestación: firme, sin batería, flexible, batería óptima |
| `src/finance.py` | 4. Cifras financieras orientativas |
| `src/arquitectura.py` | 4b. Uso de la batería (C-rate, ciclos), recorte si cae la vecina, ventana de medida, rampas y desequilibrio |
| `src/export.py` | 5. Exporta las tablas de `results/` |
| `src/dashboard.py` | 6. Genera el panel `results/dashboard.html` a partir de esas tablas |
| `run_all.py` | Ejecuta todo para las dos líneas |

Carpetas: `data/` (subestaciones y acceso de REE; el GTFS no se versiona), `results/` (tablas CSV y panel),
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

En Windows, usa `py` en lugar de `python` si hace falta.

### Tablas de resultados

| Fichero | Contenido |
|---|---|
| `results/capacidad.csv` | Capacidad para el CPD por subestación, opción y escenario de acceso |
| `results/arquitectura.csv` | Batería (C-rate, ciclos, versión 2C), recorte en N-1, hueco con medias de 1 s / 1 min / 15 min, rampas y desequilibrio |
| `results/finanzas.csv` | Canon a Adif, inversión, valor de no esperar a una conexión propia |
| `results/curvas_bateria.csv` | Tamaño del CPD frente a la batería necesaria |
| `results/perfil_hora.csv`, `perfil_minuto_*.csv` | Carga del tren por subestación |
| `results/simulacion.csv`, `lineas.json` | Resumen de la simulación y de las líneas |
| `results/supuestos.csv`, `supuestos_financieros.csv` | Todos los supuestos, con su fuente |

## Supuestos principales (a contrastar con Adif)

Están en [`results/supuestos.csv`](results/supuestos.csv), [`results/supuestos_financieros.csv`](results/supuestos_financieros.csv)
y en la cabecera de cada script. Los que más pesan:

1. **Acceso real y zona de cada subestación.** El acceso concedido es público (REE), pero en 6 subestaciones no se ha
   identificado la posición y los PK son estimados (±10 km).
2. **Pendientes.** Perfil de cotas aproximado (±50 m) a partir de estaciones y puertos; falta el perfil de Adif.
3. **Horas de Ouigo.** Solo se conocen sus frecuencias.
4. **Criterio N-1.** Si cae una subestación, cada vecina asume la mitad de su carga.
5. **CPD flexible.** Un 30 % de su carga se puede recortar en los picos del tren.
6. **Ventana del límite.** El modelo vigila el límite con medias de 1 minuto; con 15 minutos la capacidad sube mucho.
7. **Potencia de cortocircuito de cada nudo** (para el desequilibrio): 12 GVA a 400 kV y 5 GVA a 220 kV, supuestos.
8. **Cifras financieras.** Canon a Adif de 40 €/kW·año (20–80), baterías a 0,20 M€/MW + 0,25 M€/MWh, 3 años de
   espera evitados. Son órdenes de magnitud, no una valoración.

## Estado y siguientes pasos

- **Ahora:** paper conceptual que desarrolle bien la idea (arquitectura, modelo, regulación y riesgos), orientado a
  revistas Q1. Después, papers sobre casos concretos.
- **Datos de Adif:** potencias, zonas y curvas de carga reales de las subestaciones; tiempo de reconfiguración de la
  catenaria cuando cae una; con qué resolución se vigilaría un acceso compartido.
- **Datos de REE:** margen de capacidad y potencia de cortocircuito de cada nudo.
- **Modelo:** usar la batería limitada a 2C y su degradación en el dimensionado, perfil longitudinal real, horarios
  reales de Ouigo y trazas reales de carga de CPD de IA para calibrar la parte flexible.
