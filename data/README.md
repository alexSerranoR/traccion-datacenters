# Datos de entrada

## Horarios de Renfe (GTFS, no se versiona)

El modelo usa los horarios de Renfe en formato GTFS (datos abiertos). No se suben al repositorio
porque pesan unos 45 MB y caducan: Renfe los actualiza a diario.

1. Descarga `google_transit.zip` de alta velocidad, larga y media distancia desde el portal de
   datos abiertos de Renfe (https://data.renfe.com).
2. Descomprímelo en `data/gtfs/` (deben quedar `stops.txt`, `stop_times.txt`, `trips.txt`...).
3. Elige una fecha que esté dentro del calendario del fichero al ejecutar `run_all.py`.

Los resultados de `results/` se calcularon con el GTFS descargado el 12 de octubre de 2026
y el día simulado 21 de octubre de 2026 (miércoles).

## Iryo y Ouigo (en `src/lines.py`)

El GTFS de Renfe no incluye a los otros operadores:

- **Iryo**: horarios reales de lunes a viernes de octubre de 2026 (blablacar.es/train/iryo, consultado el
  12/10/2026): 14 por sentido Madrid–Barcelona, 7/6 Madrid–Sevilla y 4 por sentido Madrid–Málaga.
- **Ouigo**: frecuencias anunciadas desde el 14/12/2025 (Hosteltur): 6 por sentido Madrid–Barcelona, 4 Madrid–Sevilla
  y 3 Madrid–Málaga. Las horas se reparten entre las 7 y las 20 h. Ouigo publica su GTFS en el Punto de Acceso
  Nacional (nap.transportes.gob.es; copia en mobilitydatabase.org, feed mdb-2785): si se descarga a mano, se pueden
  sustituir por las horas reales.

## Subestaciones de tracción (`subestaciones_traccion.csv`)

Una fila por subestación (13 en Madrid–Barcelona, 12 en Madrid–Sevilla) con municipio, PK estimado (±10 km),
nudo y posición de REE, acceso concedido y escenarios de acceso. Fuentes: REE, «Capacidad de acceso de demanda
ocupada por posición» (01/10/2026); dossier de Adif de la LAV Madrid–Barcelona–Frontera; elEconomista (07/2025)
para Madrid–Sevilla; informes de la CNMC y BOE para los nudos. Detalle en la columna `fuente_set`.

- `acceso_escenario_bajo_MW`: acceso concedido hoy por REE (35–40 MW donde no se conoce).
- `acceso_escenario_alto_MW`: lo que admitirían los transformadores de tracción (~100 MW con 2×60 MVA en 2×25 kV,
  ~55 MW con 2×30 MVA en 1×25 kV).

## Perfiles horarios de REE (`ree_horario_2025.csv`)

Generación por tecnología, intercambios y demanda del sistema peninsular, hora a hora, de todo 2025 (8760 filas). Sale del
servicio de demanda en tiempo real de REE (demanda.ree.es, curva DEMANDAAU), que da potencia cada 5 minutos, promediada
por hora (MWh/h). Son datos de tiempo real y no el cierre definitivo, así que pueden diferir algo de las estadísticas
oficiales. La API REData (apidatos.ree.es) no da la generación por tecnología con resolución horaria.

- `datetime`: hora local con su desfase (los cambios de hora están resueltos).
- `eolica_MWh`, `solar_fv_MWh`, `solar_termica_MWh`, `hidraulica_MWh`, `demanda_MWh` y el resto de tecnologías con el
  nombre original de REE (`nuc`, `cc`, `cogenResto`...). Exportaciones y consumo de bombeo y baterías salen en negativo.
- Totales de 2025: eólica 55,6 TWh, FV 49,2 TWh, demanda 238,5 TWh. Las horas del apagón del 28/4/2025 están sin corregir.

Lo usa `src/renovable_horaria.py` para el 80 % renovable horario del proyecto de RD de centros de datos.
