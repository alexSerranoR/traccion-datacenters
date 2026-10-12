"""Ejecuta todo el modelo de principio a fin.
Uso:  python run_all.py [carpeta_gtfs] [fecha YYYYMMDD]
Por defecto: data/gtfs y 20261021 (miercoles laborable). Resultados en results/,
incluido el panel results/dashboard.html (se abre con doble clic, sin servidor).
"""
import sys, subprocess, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
GTFS = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "gtfs"
DATE = sys.argv[2] if len(sys.argv) > 2 else "20261021"
WORK = ROOT / "build"; RES = ROOT / "results"
for d in (WORK / "renfe", WORK / "todos", RES): d.mkdir(parents=True, exist_ok=True)
if not (GTFS / "stop_times.txt").exists():
    sys.exit(f"No encuentro el GTFS en {GTFS}. Descomprime google_transit.zip de Renfe ahi (ver data/README.md).")

def run(script, *args):
    print(f"\n> {script} {' '.join(map(str, args))}")
    subprocess.run([sys.executable, str(ROOT / "src" / script), *map(str, args)], check=True)

run("extract.py", GTFS, DATE, WORK / "tramos.csv")
run("sim.py", WORK / "tramos.csv", WORK / "renfe")
run("sim.py", WORK / "tramos.csv", WORK / "todos", "--competencia", 22)
run("analysis.py", WORK / "renfe", WORK / "res_renfe.json")
run("analysis.py", WORK / "todos", WORK / "res_todos.json")
run("export.py", WORK, RES)
run("dashboard.py", RES)
print(f"\nAbre {RES / 'dashboard.html'} con doble clic para ver los resultados.")
