"""Paso 5: genera un panel HTML autocontenido con los resultados (results/dashboard.html).
Uso: python dashboard.py <dir_results>
Lee solo las tablas CSV de results/, asi que puede rehacerse sin volver a simular.
El HTML no necesita servidor ni internet: se abre con doble clic y se puede enviar por correo.
"""
import sys, json, pathlib
import pandas as pd

RES = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent / "results"
TEMPLATE = pathlib.Path(__file__).resolve().parent / "dashboard_template.html"

cap = pd.read_csv(RES / "capacidad.csv")
minuto = pd.read_csv(RES / "perfil_minuto.csv")
hora = pd.read_csv(RES / "perfil_hora.csv")
sim = pd.read_csv(RES / "simulacion.csv")
sup = pd.read_csv(RES / "supuestos.csv").fillna("")
ses = [c for c in minuto.columns if c != "minuto"]

# franja nocturna: tramo continuo mas largo con <1 MW en toda la linea (el dia es ciclico)
idle = (minuto[ses].sum(axis=1) < 1.0).tolist()
best, start = (0, 0), None
for i in range(2 * len(idle)):
    if idle[i % len(idle)]:
        start = i if start is None else start
        if i - start + 1 > best[0] and i - start + 1 <= len(idle): best = (i - start + 1, start)
    else:
        start = None
noche = dict(inicio=best[1] % len(idle), minutos=best[0])

data = dict(
    subestaciones=ses,
    capacidad=cap.to_dict(orient="records"),
    minuto={se: minuto[se].round(2).tolist() for se in ses},
    hora_media={se: hora[hora.subestacion == se].sort_values("hora").media_MW.round(2).tolist() for se in ses},
    simulacion=sim.to_dict(orient="records"),
    supuestos=sup.to_dict(orient="records"),
    noche=noche,
)
html = TEMPLATE.read_text(encoding="utf-8").replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
out = RES / "dashboard.html"
out.write_text(html, encoding="utf-8")
print("Panel escrito en", out, "(abrelo con doble clic)")
