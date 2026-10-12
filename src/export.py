"""Paso 4: exporta los resultados de la simulacion a tablas CSV legibles.
Uso: python export.py <dir_trabajo> <dir_results>
<dir_trabajo> debe contener renfe/, todos/, res_renfe.json y res_todos.json (los crea run_all.py).
"""
import sys, json
import pandas as pd

W, OUT = sys.argv[1], sys.argv[2]
r = json.load(open(f"{W}/res_todos.json"))
rows = []
for e in r["escenarios"]:
    for f in e["filas"]:
        rows.append(dict(acceso_MW=e["C"], carga_x=e["f"], subestacion=f["se"], pk_km=f["pk"], firme_MW=f["firme"],
                         sin_bateria_MW=f["sin_bateria"], con_bateria_MW=f["con_bateria"], bateria_MW=f["bat_MW"],
                         bateria_MWh=f["bat_MWh"], uso_medio_pct=f["uso_medio_pct"], pico_N1_MW=f["pico_N1"]))
pd.DataFrame(rows).to_csv(f"{OUT}/capacidad.csv", index=False)
h = [dict(hora=i, subestacion=se, media_MW=m, max_MW=x)
     for se in r["hora_media"] for i, (m, x) in enumerate(zip(r["hora_media"][se], r["hora_max"][se]))]
pd.DataFrame(h).to_csv(f"{OUT}/perfil_hora.csv", index=False)
pd.read_csv(f"{W}/todos/carga_minuto.csv").round(2).to_csv(f"{OUT}/perfil_minuto.csv", index=False)
sim = []
for name, d in [("Solo Renfe (GTFS)", "renfe"), ("Renfe + Iryo y Ouigo estimados", "todos")]:
    j = json.load(open(f"{W}/{d}/resumen.json")); rr = json.load(open(f"{W}/res_{d}.json"))
    sim.append(dict(escenario=name, trenes=j["trenes"], tren_km=j["tren_km"], energia_red_MWh=j["energia_red_MWh"],
                    devuelta_red_MWh=j["energia_devuelta_red_MWh"], kWh_tren_km=j["kWh_por_tren_km"],
                    potencia_media_linea_MW=round(j["energia_red_MWh"] / 24, 1), minutos_sin_trenes=rr["minutos_sin_trenes"]))
pd.DataFrame(sim).to_csv(f"{OUT}/simulacion.csv", index=False)
print("Tablas escritas en", OUT)
