# Subestaciones de alta velocidad y centros de datos

¿Cuánta capacidad de conexión a la red tienen sin usar las subestaciones de tracción de la LAV
Madrid–Zaragoza–Barcelona, y cuántos MW de centros de datos podrían compartirla sin afectar al
servicio ferroviario?

Prueba de concepto para una propuesta de investigación. Los resultados son preliminares: varios
parámetros clave (potencia de cada subestación, su ubicación exacta, su curva de carga real) no
son públicos y se han supuesto.

## Idea

- Las subestaciones de tracción de alta velocidad están conectadas a la red de transporte a
  220/400 kV y se dimensionan para los picos de tráfico, así que de media están casi vacías.
- En España, la falta de acceso a la red es el principal freno para nuevos centros de datos.
- Un centro de datos conectado al lado de alta tensión de la subestación, con su propio
  transformador, podría usar la capacidad que el tren deja libre. El tren tiene siempre prioridad,
  y una batería cubre sus picos.

## Resultados preliminares

Miércoles laborable, 199 trenes (Renfe según su GTFS y estimación de Iryo y Ouigo), 11
subestaciones supuestas cada ~60 km:

| Acceso por subestación | Firme (resiste el fallo de una vecina) | Sin batería | Con batería de 20 MW / 20 MWh |
|---|---|---|---|
| 30 MW  | 0 MW   | 23 MW  | 226 MW  |
| 60 MW  | 150 MW | 250 MW | 453 MW  |
| 120 MW | 742 MW | 844 MW | 1.047 MW |

- Con 60 MW de acceso, los trenes usan de media solo el 5–8 % de la capacidad.
- Casi 6 horas cada noche sin trenes en toda la línea.
- Los picos del tren duran minutos: la batería necesaria es de mucha potencia y poca energía
  (normalmente menos de 5 MWh).
- El frenado regenerativo que vuelve a la red es poco (~27 MWh/día, menos del 3 %), porque en
  alterna ya lo aprovechan otros trenes.

Las tablas completas están en [`results/`](results/).

## Estructura

```
src/extract.py    1. Lee el GTFS y saca los trenes que usan la LAV, como tramos sobre el PK
src/sim.py        2. Simula cada tren segundo a segundo y suma la potencia por subestación
src/analysis.py   3. Calcula la capacidad compartible (firme, normal, con batería) por escenario
src/export.py     4. Exporta las tablas de results/
run_all.py        Ejecuta los cuatro pasos
data/             Instrucciones para descargar el GTFS de Renfe (no se versiona)
results/          Tablas de resultados (CSV)
docs/             Estado del arte y motivación
```

## Cómo ejecutarlo

Requiere Python 3.10 o superior.

```bash
pip install -r requirements.txt
# descomprime google_transit.zip de Renfe en data/gtfs/  (ver data/README.md)
python run_all.py                     # usa data/gtfs y el 21/10/2026
python run_all.py data/gtfs 20261104  # otra fecha dentro del calendario del GTFS
```

En Windows, usa `py` en lugar de `python` si hace falta.

## Supuestos principales (a contrastar con Adif)

Están todos en [`results/supuestos.csv`](results/supuestos.csv) y en la cabecera de cada script.
Los que más pesan:

1. **Capacidad de acceso de cada subestación.** Se prueban 30, 60 y 120 MW. Es el dato que más
   cambia el resultado.
2. **Ubicación de las subestaciones.** Repartidas cada ~60 km. Las reales están en IDEADIF (Adif).
3. **Trenes de Iryo y Ouigo.** No están en el GTFS de Renfe; se añaden 22 por sentido.
4. **Pendientes.** No se modelan, así que el consumo sale bajo (~11 kWh/tren-km). El escenario
   de carga ×1,5 lo cubre.
5. **Criterio N-1.** Si cae una subestación, cada vecina asume la mitad de su carga.

## Siguientes pasos

- Pedir a Adif potencias y curvas de carga reales de las subestaciones (convenio o Portal de
  Transparencia).
- Añadir perfil de pendientes y posiciones reales de las subestaciones.
- Modelar la carga del centro de datos con trazas reales y su parte desplazable.
- Repetir para Madrid–Sevilla como caso de baja densidad.
