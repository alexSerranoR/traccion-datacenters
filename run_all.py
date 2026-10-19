"""Ejecuta todo el modelo de principio a fin para las dos lineas (Madrid-Barcelona y Madrid-Sevilla).
Uso:  python run_all.py [carpeta_gtfs] [fecha YYYYMMDD]
Por defecto: data/gtfs y 20261021 (miercoles laborable). Resultados en results/,
incluido el panel results/dashboard.html (se abre con doble clic, sin servidor).
"""
import sys, subprocess, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
GTFS = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "gtfs"
DATE = sys.argv[2] if len(sys.argv) > 2 else "20261021"
WORK = ROOT / "build"; RES = ROOT / "results"
LINES = ["MZB", "MS"]
for d in [RES] + [WORK / l for l in LINES] + [WORK / f"{l}_renfe" for l in LINES]: d.mkdir(parents=True, exist_ok=True)
if not (GTFS / "stop_times.txt").exists():
    sys.exit(f"No encuentro el GTFS en {GTFS}. Descomprime google_transit.zip de Renfe ahi (ver data/README.md).")

def run(script, *args):
    print(f"\n> {script} {' '.join(map(str, args))}")
    subprocess.run([sys.executable, str(ROOT / "src" / script), *map(str, args)], check=True)

for l in LINES:
    run("extract.py", GTFS, DATE, l, WORK / f"tramos_{l}.csv")
    run("sim.py", WORK / f"tramos_{l}.csv", l, WORK / f"{l}_renfe", "--sin-otros")
    run("sim.py", WORK / f"tramos_{l}.csv", l, WORK / l)
    run("analysis.py", WORK / l, l, WORK / f"res_{l}.json")
run("finance.py", WORK, RES)
run("arquitectura.py", WORK, RES)
run("export.py", WORK, RES)
run("dashboard.py", RES)
print(f"\nAbre {RES / 'dashboard.html'} con doble clic para ver los resultados.")
