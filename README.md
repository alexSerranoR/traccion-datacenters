# Subestaciones de alta velocidad y centros de datos

¿Cuánta capacidad de conexión a la red tienen sin usar las subestaciones de tracción de alta velocidad,
y cuántos MW de centros de datos podrían compartirla sin afectar al servicio ferroviario? Se estudian
dos líneas: Madrid–Zaragoza–Barcelona (alta densidad) y Madrid–Sevilla (baja densidad).

Prueba de concepto para una propuesta de investigación. Los resultados son preliminares: varios
parámetros clave (potencia de cada subestación, su zona y PK exactos, su curva de carga real) no
son públicos y se han estimado.

## Idea

- Las subestaciones de tracción de alta velocidad están conectadas a la red de transporte a
  220/400 kV y se dimensionan para los picos de tráfico, así que de media están casi vacías.
- En España, la falta de acceso a la red es el principal freno para nuevos centros de datos.
- Un centro de datos conectado al lado de alta tensión de la subestación, con su propio
  transformador, podría usar la capacidad que el tren deja libre. El tren tiene siempre prioridad,
  y una batería cubre sus picos.

## Resultados preliminares (v2)

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

- El tren usa de media el 6–10 % del acceso, pero sus picos de un minuto (30–45 MW) se acercan al acceso
  concedido: Adif parece haber pedido a REE justo lo que necesitan sus picos.
- Hoy el permiso de Adif no se puede ceder; lo que encaja es que Adif reduzca su permiso y el CPD pida acceso
  propio en el mismo nudo. Eso solo libera la capacidad firme. Compartir el acceso con prioridad del tren
  necesitaría una reforma.
- La batería necesaria es de potencia y poca energía (unos 15 minutos).
- Cifras financieras orientativas en `results/finanzas.csv` (canon a Adif, inversión, valor de no esperar a una
  conexión propia), con los supuestos en `results/supuestos_financieros.csv`.

Para consultarlo de forma visual, abre [`results/dashboard.html`](results/dashboard.html) con doble clic: panel
interactivo sin servidor con conclusiones, comparación de líneas, perfil de la línea, perfil de un día de centro de
datos (firme, flexible, con batería), dimensionado de baterías y cifras financieras.

## Estructura

```
src/lines.py      Definición de las líneas: estaciones, perfil de cotas, subestaciones, Iryo y Ouigo
src/extract.py    1. Lee el GTFS y saca los trenes que usan cada línea, como tramos sobre el PK
src/sim.py        2. Simula cada tren segundo a segundo (con pendientes) y suma la potencia por subestación
src/analysis.py   3. Capacidad para CPD por subestación: firme, sin batería, flexible, batería óptima
src/finance.py    4. Cifras financieras orientativas
src/export.py     5. Exporta las tablas de results/
src/dashboard.py  6. Genera el panel results/dashboard.html a partir de esas tablas
run_all.py        Ejecuta todo para las dos líneas
data/             Subestaciones y acceso de REE; instrucciones para el GTFS de Renfe (no se versiona)
results/          Tablas de resultados (CSV) y panel
docs/             Estado del arte y motivación
```

## Cómo ejecutarlo

Requiere Python 3.10 o superior.

```bash
pip install -r requirements.txt
# descomprime google_transit.zip de Renfe en data/gtfs/  (ver data/README.md)
python run_all.py                     # usa data/gtfs y el 21/10/2026
python run_all.py data/gtfs 20261104  # otra fecha dentro del calendario del GTFS
python src/dashboard.py results       # rehace solo el panel, sin volver a simular
```

En Windows, usa `py` en lugar de `python` si hace falta.

## Supuestos principales (a contrastar con Adif)

Están en [`results/supuestos.csv`](results/supuestos.csv), [`results/supuestos_financieros.csv`](results/supuestos_financieros.csv)
y en la cabecera de cada script. Los que más pesan:

1. **Acceso real y zona de cada subestación.** El acceso concedido es público (REE), pero en 6 subestaciones no se ha
   identificado la posición y los PK son estimados (±10 km).
2. **Pendientes.** Perfil de cotas aproximado (±50 m) a partir de estaciones y puertos; falta el perfil de Adif.
3. **Horas de Ouigo.** Solo se conocen sus frecuencias.
4. **Criterio N-1.** Si cae una subestación, cada vecina asume la mitad de su carga.
5. **CPD flexible.** Un 30 % de su carga se puede recortar en los picos del tren.
6. **Cifras financieras.** Canon a Adif de 40 €/kW·año (20–80), baterías a 0,20 M€/MW + 0,25 M€/MWh, 3 años de
   espera evitados. Son órdenes de magnitud, no una valoración.

## Siguientes pasos

- Pedir a Adif potencias, zonas y curvas de carga reales de las subestaciones (solicitud de transparencia).
- Perfil longitudinal real y horarios reales de Ouigo (GTFS del Punto de Acceso Nacional).
- Margen de capacidad de cada nudo de REE para el escenario de ampliación.
- Trazas reales de carga de centros de datos de IA para calibrar la parte flexible.
