"""Paso 4b: indicadores de arquitectura y de respuesta ante caidas, por subestacion (ver docs/arquitectura_y_caidas.md).
Uso: python arquitectura.py <dir_trabajo> <dir_results>

Parte de la simulacion a 1 s (build/<linea>/Pse_1s.npy) y de la bateria optima de analysis.py (acceso REE, carga x1,0):
 - bateria: relacion P/E (C-rate) y ciclos equivalentes al dia de la bateria del modelo (limitada a 2C en analysis.py)
   frente a la de energia minima, que duraria mucho menos
 - N-1 de la vecina: CPD que se sostiene con la misma bateria si cae una subestacion vecina, y cuanto hay que recortar
 - ventana de medida: hueco minimo libre para el CPD si el limite se vigila con medias de 1 s, 1 min o 15 min
 - rampas: mayor salto de la carga del tren en 1 s y en 10 s (la velocidad que debe tener el control)
 - desequilibrio: VUF ~ S_tren / Scc con el pico de 1 s y una Scc SUPUESTA por tension (central y nudo debil)
"""
import sys, json
import numpy as np, pandas as pd
from lines import LINES, SE_DATA

W, OUT = sys.argv[1], sys.argv[2]

SAFETY = 0.90          # igual que analysis.py
N1_SHARE = 0.5         # igual que analysis.py
FLEX = 0.30            # igual que analysis.py
SCC = {400: (12000, 6000), 220: (5000, 2500)}   # MVA, SUPUESTO (central, nudo debil): pedir a REE la Scc real


def battery_need(H, D, dt):
    """Igual que analysis.py, para un paso de dt segundos."""
    s = np.tile((H - D) * dt / 3600, 2)
    S = np.cumsum(s)
    dd = np.maximum.accumulate(np.maximum(S, 0)) - S
    return max(0.0, float((D - H).max())), float(dd.max())


def max_D(H, Pb, Eb, dt):
    lo, hi = 0.0, float(H.max())
    for _ in range(30):
        m = (lo + hi) / 2
        pb, eb = battery_need(H, m, dt)
        (lo, hi) = (m, hi) if (pb <= Pb + 1e-6 and eb <= Eb + 1e-6) else (lo, m)
    return lo


rows = []
for line in ("MZB", "MS"):
    names = [s for s, _ in LINES[line]["subestaciones"]]
    by = {r["subestacion"]: r for r in SE_DATA[line]}
    P = np.clip(np.load(f"{W}/{line}/Pse_1s.npy").astype(float), 0, None)
    n = P.shape[0]
    L1 = P.reshape(n, 1440, 60).mean(axis=2)
    L15 = P.reshape(n, 96, 900).mean(axis=2)
    res = json.load(open(f"{W}/res_{line}.json"))
    esc = next(e for e in res["escenarios"] if e["acceso"] == "REE" and e["f"] == 1.0)
    for k, se in enumerate(names):
        r = esc["filas"][k]
        cap = SAFETY * float(by[se]["acceso_escenario_bajo_MW"])
        H = np.clip(cap - L1[k], 0, None)
        nb = [L1[j] for j in (k - 1, k + 1) if 0 <= j < n]
        HN1 = np.clip(cap - (L1[k] + N1_SHARE * np.max(nb, axis=0)), 0, None)
        D, pb, eb = r["bateria_opt"], r["batopt_MW"], r["batopt_MWh"]
        descarga = np.clip(D - H, 0, None).sum() / 60                       # MWh/dia que da la bateria
        eb_min = battery_need(H, D, 60)[1] if D > 0 else 0.0                # energia minima, sin limite de C-rate
        D_n1 = max_D(HN1, pb, eb, 60) if D > 0 else 0.0
        kv = int(by[se]["tension_kV"]); scc, scc_debil = SCC[kv]
        rows.append(dict(
            linea=line, se=se, tension_kV=kv, limite_MW=round(cap, 1),
            cpd_bateria_MW=D, bat_MW=pb, bat_MWh=eb,
            bat_C=round(pb / eb, 1) if eb else None,
            bat_ciclos_dia=round(descarga / eb, 1) if eb else None,
            bat_MWh_minima=round(eb_min, 1),
            bat_ciclos_dia_minima=round(descarga / eb_min, 1) if eb_min else None,
            cpd_N1_vecina_MW=round(D_n1, 1), recorte_N1_MW=round(D - D_n1, 1),
            recorte_N1_pct=round(100 * (D - D_n1) / D) if D else None,
            cpd_flexible_MW=r["flexible"],
            recorte_N1_flexible_MW=round(max(0.0, r["flexible"] * (1 - FLEX) - float(HN1.min())), 1),
            hueco_min_1s_MW=round(float(np.clip(cap - P[k], 0, None).min()), 1),
            hueco_min_1min_MW=round(float(H.min()), 1),
            hueco_min_15min_MW=round(float(np.clip(cap - L15[k], 0, None).min()), 1),
            pico_tren_1s_MW=round(float(P[k].max()), 1),
            rampa_1s_MW=round(float(np.abs(np.diff(P[k])).max()), 1),
            rampa_10s_MW=round(float(np.abs(P[k][10:] - P[k][:-10]).max()), 1),
            desequilibrio_pct=round(100 * float(P[k].max()) / scc, 2),
            desequilibrio_nudo_debil_pct=round(100 * float(P[k].max()) / scc_debil, 2)))

df = pd.DataFrame(rows)
df.to_csv(f"{OUT}/arquitectura.csv", index=False)
tot = df.groupby("linea")[["cpd_bateria_MW", "bat_MW", "bat_MWh", "bat_MWh_minima", "cpd_N1_vecina_MW",
                           "recorte_N1_MW", "hueco_min_1s_MW", "hueco_min_1min_MW", "hueco_min_15min_MW"]].sum().round(1)
print(tot.T.to_string())
print(df.groupby("linea")[["bat_C", "bat_ciclos_dia", "bat_ciclos_dia_minima", "recorte_N1_pct", "rampa_10s_MW",
                           "desequilibrio_pct"]].median().T.to_string())
