"""Paso 5: exporta los resultados de la simulacion a tablas legibles en results/.
Uso: python export.py <dir_trabajo> <dir_results>
<dir_trabajo> debe contener <LINEA>/, <LINEA>_renfe/ y res_<LINEA>.json (los crea run_all.py).
"""
import sys, json
import numpy as np, pandas as pd
from lines import LINES

W, OUT = sys.argv[1], sys.argv[2]
cap, hora, sim, curvas, geo = [], [], [], [], {}
for line, cfg in LINES.items():
    r = json.load(open(f"{W}/res_{line}.json"))
    for e in r["escenarios"]:
        for f in e["filas"]:
            cap.append(dict(linea=line, acceso=e["acceso"], carga_x=e["f"], **f))
    for acc, d in r["curvas_bateria"].items():
        for se, pts in d.items():
            curvas += [dict(linea=line, acceso=acc, subestacion=se, cpd_MW=a, bateria_MW=b, bateria_MWh=c)
                       for a, b, c in pts]
    m = pd.read_csv(f"{W}/{line}/carga_minuto.csv")
    m.round(2).to_csv(f"{OUT}/perfil_minuto_{line}.csv", index=False)
    for se in m.columns[1:]:
        v = m[se].to_numpy().reshape(24, 60)
        hora += [dict(linea=line, hora=h, subestacion=se, media_MW=round(v[h].mean(), 2), max_MW=round(v[h].max(), 2))
                 for h in range(24)]
    for name, d in [("Solo Renfe (GTFS)", f"{line}_renfe"), ("Renfe + Iryo + Ouigo", line)]:
        j = json.load(open(f"{W}/{d}/resumen.json"))
        tot = m.iloc[:, 1:].sum(axis=1) if d == line else None
        sim.append(dict(linea=line, escenario=name, trenes=j["trenes"], tren_km=j["tren_km"],
                        energia_red_MWh=j["energia_red_MWh"], devuelta_red_MWh=j["energia_devuelta_red_MWh"],
                        regenerada_MWh=j["energia_regenerada_MWh"], kWh_tren_km=j["kWh_por_tren_km"],
                        potencia_media_linea_MW=round(j["energia_red_MWh"] / 24, 1),
                        pico_linea_MW=round(float(tot.max()), 1) if tot is not None else None,
                        minutos_sin_trenes=r["minutos_sin_trenes"] if d == line else None,
                        trenes_Renfe=j["trenes_por_operador"].get("Renfe", 0),
                        trenes_Iryo=j["trenes_por_operador"].get("Iryo", 0),
                        trenes_Ouigo=j["trenes_por_operador"].get("Ouigo", 0),
                        kWh_tren_km_tipo=json.dumps(j["kWh_tren_km_por_tipo"])))
    se_res = json.load(open(f"{W}/{line}/resumen.json"))["se"]
    km = np.arange(0, cfg["L"] + 1, 5)
    c = np.array(cfg["cotas"])
    geo[line] = dict(nombre=cfg["nombre"], corto=cfg["corto"], densidad=cfg["densidad"], sistema=cfg["sistema"],
                     L=cfg["L"], estaciones=cfg["estaciones"], pos_subestaciones=cfg["pos_subestaciones"],
                     subestaciones=[dict(s, nombre=s["se"]) for s in se_res],
                     cotas=[[int(k), round(float(z))] for k, z in zip(km, np.interp(km, c[:, 0], c[:, 1]))])

pd.DataFrame(cap).to_csv(f"{OUT}/capacidad.csv", index=False)
pd.DataFrame(hora).to_csv(f"{OUT}/perfil_hora.csv", index=False)
pd.DataFrame(sim).to_csv(f"{OUT}/simulacion.csv", index=False)
pd.DataFrame(curvas).to_csv(f"{OUT}/curvas_bateria.csv", index=False)
json.dump(geo, open(f"{OUT}/lineas.json", "w"), ensure_ascii=False, indent=1)

SUP = [
    ("Día simulado", "miércoles 21 oct 2026", "", "GTFS de Renfe descargado el 12/10/2026 (datos abiertos)"),
    ("Líneas", "Madrid–Barcelona (621 km) y Madrid–Sevilla (471 km)", "", "Alta y baja densidad de tráfico"),
    ("Trenes de Iryo", "horarios reales", "", "Horarios de lunes a viernes de octubre de 2026 (blablacar.es)"),
    ("Trenes de Ouigo", "6/sentido Madrid–Barcelona; 4 Madrid–Sevilla; 3 Madrid–Málaga", "",
     "Frecuencias anunciadas (Hosteltur, dic. 2025). Horas supuestas entre las 7 y las 20 h"),
    ("Tramos compartidos", "Levante (25 km), Toledo (53 km), Málaga (358 km)", "",
     "Trenes de otras líneas que usan parte de Madrid–Sevilla"),
    ("Subestaciones", "13 en Madrid–Barcelona y 12 en Madrid–Sevilla (reales)", "",
     "Dossier de Adif, elEconomista 07/2025, nudos de REE; PK estimados ±10 km (data/subestaciones_traccion.csv)"),
    ("Acceso a la red", "concedido por REE (12–66 MW); ampliado: ~100 MW (2×25 kV) y ~55 MW (1×25 kV)", "",
     "REE, capacidad de acceso de demanda por posición (01/10/2026); 35–40 MW donde no se conoce"),
    ("Pendientes", "perfil de cotas aproximado (±50 m)", "", "Supuesto: a sustituir por el perfil longitudinal de Adif"),
    ("Material", "AVE 425 t / 8,8 MW; Iryo 500 t / 9,8 MW; Ouigo 430 t / 9,3 MW", "",
     "Fichas S-103/S-112, Frecciarossa 1000 y TGV Euroduplex (masa en carga estimada)"),
    ("Alvia / Avant", "4,8 / 4,4", "MW", "Fichas S-130 y S-121"),
    ("Margen de regularidad del horario", 8, "%", "El tren marcha más rápido y gasta el margen parado"),
    ("Rendimiento tracción / regeneración", "85 / 80", "%", "Supuesto"),
    ("Conexión del centro de datos", "embarrado de AT (220/400 kV)", "",
     "Transformador propio; comparte la capacidad de acceso, no los transformadores de tracción"),
    ("Margen de seguridad sobre el acceso", 10, "%", "Supuesto"),
    ("Contingencia N-1", "+50 % de la carga de la vecina más cargada", "", "Supuesto simplificado"),
    ("Parte flexible del CPD", 30, "%", "Supuesto: entrenamiento de IA y cargas por lotes que se pueden recortar"),
    ("Batería óptima", "se amplía mientras cada MW extra de CPD cueste < 1 M€ en batería", "",
     "0,20 M€/MW + 0,25 M€/MWh (supuesto)"),
    ("Encaje regulatorio", "«hoy» = solo capacidad firme; «con reforma» = acceso compartido con prioridad del tren", "",
     "Hilo «Encaje regulatorio»: el permiso de Adif no se puede ceder hoy"),
]
pd.DataFrame(SUP, columns=["parametro", "valor", "unidad", "fuente"]).to_csv(f"{OUT}/supuestos.csv", index=False)
print("Tablas escritas en", OUT)
