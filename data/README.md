# Datos de entrada

El modelo usa los horarios de Renfe en formato GTFS (datos abiertos). No se suben al repositorio
porque pesan unos 45 MB y caducan: Renfe los actualiza a diario.

1. Descarga `google_transit.zip` de alta velocidad, larga y media distancia desde el portal de
   datos abiertos de Renfe (https://data.renfe.com).
2. Descomprímelo en `data/gtfs/` (deben quedar `stops.txt`, `stop_times.txt`, `trips.txt`...).
3. Elige una fecha que esté dentro del calendario del fichero al ejecutar `run_all.py`.

Los resultados de `results/` se calcularon con el GTFS descargado el 12 de octubre de 2026
y el día simulado 21 de octubre de 2026 (miércoles).

El GTFS de Renfe no incluye los trenes de Iryo ni de Ouigo: el modelo los estima (ver supuestos).
