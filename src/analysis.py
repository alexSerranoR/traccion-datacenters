"""Paso 3: capacidad que podria usar un centro de datos (CPD) conectado en el embarrado de AT de cada
subestacion, para varias opciones tecnicas y escenarios de acceso.
Uso: python analysis.py <dir_simulacion> <linea MZB|MS> <salida.json>

Opciones (todas con margen de seguridad del 10 % sobre el acceso C y el tren siempre con prioridad):
 - firme        : cabe incluso si cae la subestacion vecina (N-1) en el peor minuto, sin bateria.
                  Es la capacidad que Adif nunca usa: la unica que encaja con la regulacion actual
                  (Adif reduce su permiso y el CPD pide acceso propio en el mismo nudo).
 - sin_bateria  : cabe en operacion normal en el peor minuto del dia.
 - flexible     : el CPD tiene una parte flexible (FLEX, p. ej. entrenamiento de IA) que se recorta
                  cuando el tren la necesita. D * (1 - FLEX) <= hueco minimo.
 - firme_flex   : como 'firme' pero con la parte flexible recortable en N-1.
 - bateria_20   : bateria fija de 20 MW / 20 MWh (referencia de la v1).
 - bateria_opt  : bateria dimensionada para cada subestacion: se amplia el CPD mientras cada MW
                  adicional cueste menos de VAL_MW en bateria.
Escenarios de acceso por subestacion:
 - REE   : capacidad de acceso concedida hoy por REE a cada posicion de Adif (data/subestaciones_traccion.csv;
           donde no se conoce, 35-40 MW).
 - trafo : lo que admitirian los transformadores de traccion si se ampliara el acceso (~100 MW en 2x25 kV con
           2x60 MVA; ~55 MW en 1x25 kV con 2x30 MVA).
 - 30/60/120 : el mismo acceso en todas las subestaciones (sensibilidad).
"""
import sys, json
import numpy as np, pandas as pd
from lines import LINES, SE_DATA

D_, LINE, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
CFG = LINES[LINE]
SE_NAMES = [s for s, _ in CFG["subestaciones"]]; SE_PK = [p for _, p in CFG["subestaciones"]]

SAFETY = 0.90          # se usa el 90 % del acceso
FLEX = 0.30            # SUPUESTO: 30 % de la carga del CPD es flexible (entrenamiento IA, lotes)
N1_SHARE = 0.5         # SUPUESTO: si cae una vecina, esta subestacion asume la mitad de su carga
BAT_P_COST = 0.20      # M EUR por MW de bateria (SUPUESTO, ver finance.py)
BAT_E_COST = 0.25      # M EUR por MWh de bateria
VAL_MW = 1.0           # M EUR: lo maximo que se paga en bateria por cada MW adicional de CPD (SUPUESTO)
BAT_C_MAX = 2.0        # C-rate maximo: E >= P/2. Con 2C la bateria hace ~2,5-3 ciclos/dia y dura ~8 anos;
                       # con la energia minima haria 5-6 ciclos/dia y duraria ~3 (ver arquitectura.py)
ACCESS = [30, 60, 120]
LOADS = [1.0, 1.5]     # 1,5 = carga del tren +50 % (crecimiento de trafico, incertidumbre de consumo)

P = np.clip(np.load(f"{D_}/Pse_1s.npy").astype(float), 0, None)
NSE = P.shape[0]
L = P.reshape(NSE, 1440, 60).mean(axis=2)                 # MW, medias de 1 minuto


def n1(L):
    out = L.copy()
    for k in range(NSE):
        nb = [L[j] for j in (k - 1, k + 1) if 0 <= j < NSE]
        out[k] = L[k] + N1_SHARE * np.max(nb, axis=0)
    return out


def battery_need(H, D):
    """Bateria (MW, MWh) para mantener un CPD constante de D MW con techo H(t) (1 min, dia ciclico).
    La energia necesaria es la maxima caida de la suma acumulada (recurrencia de Lindley)."""
    s = np.tile((H - D) / 60.0, 2)
    S = np.cumsum(s)
    dd = np.maximum.accumulate(np.maximum(S, 0)) - S
    return max(0.0, float((D - H).max())), float(dd.max())


def bat_cost(pb, eb):
    return BAT_P_COST * pb + BAT_E_COST * eb


def max_D(H, Pb, Eb):
    lo, hi = 0.0, float(H.max())
    for _ in range(30):
        m = (lo + hi) / 2
        pb, eb = battery_need(H, m)
        (lo, hi) = (m, hi) if (pb <= Pb and eb <= Eb) else (lo, m)
    return lo


def battery_curve(H, step=1.0):
    """CPD (MW) frente a bateria necesaria, desde 'sin bateria' hasta el maximo fisico.
    La energia se sube a P/BAT_C_MAX si la necesaria es menor, para no degradar la bateria."""
    D0 = max(0.0, float(H.min())); pts = []
    for D in np.arange(np.floor(D0), float(H.mean()), step):
        D = max(D, D0); pb, eb = battery_need(H, D); eb = max(eb, pb / BAT_C_MAX)
        pts.append((round(float(D), 1), round(pb, 1), round(eb, 2)))
    return pts


def optimal_battery(curve):
    best = curve[0] if curve else (0.0, 0.0, 0.0)
    for a, b in zip(curve[:-1], curve[1:]):
        dD = b[0] - a[0]
        if dD <= 0: continue
        if (bat_cost(b[1], b[2]) - bat_cost(a[1], a[2])) / dD > VAL_MW: break
        best = b
    return best


def curtailed(H, D):
    if D <= 0: return 0.0
    return float(np.clip(D - H, 0, None).sum() / (D * len(H)) * 100)


by = {r["subestacion"]: r for r in SE_DATA[LINE]}
scen = [(k, np.array([float(by[s][col]) for s in SE_NAMES])) for k, col in
        (("REE", "acceso_escenario_bajo_MW"), ("trafo", "acceso_escenario_alto_MW"))]
scen += [(str(C), np.full(NSE, float(C))) for C in ACCESS]

res = {"linea": LINE, "nombre": CFG["nombre"], "escenarios": [], "curvas_bateria": {},
       "parametros": dict(margen=SAFETY, flex=FLEX, n1=N1_SHARE, val_MW=VAL_MW,
                          bat_P_coste=BAT_P_COST, bat_E_coste=BAT_E_COST, bat_C_max=BAT_C_MAX)}
for name, Cv in scen:
    for f in LOADS:
        Lf = L * f; LN1 = n1(Lf)
        rows = []
        for k in range(NSE):
            cap = SAFETY * Cv[k]; H = np.clip(cap - Lf[k], 0, None)
            firm = max(0.0, cap - float(LN1[k].max()))
            nobat = float(H.min())
            flex = min(nobat / (1 - FLEX), cap)
            curve = battery_curve(H)
            Dopt, pb_o, eb_o = optimal_battery(curve)
            b20 = max_D(H, 20, 20); pb20, eb20 = battery_need(H, b20)
            if f == 1.0: res["curvas_bateria"].setdefault(name, {})[SE_NAMES[k]] = curve
            rows.append(dict(
                se=SE_NAMES[k], pk=SE_PK[k], acceso_MW=round(float(Cv[k]), 1),
                firme=round(firm, 1), firme_flex=round(min(firm / (1 - FLEX), cap), 1),
                sin_bateria=round(nobat, 1), flexible=round(flex, 1),
                flex_recorte_pct=round(curtailed(H, flex), 2),
                bateria_20=round(b20, 1), bat20_MW=round(pb20, 1), bat20_MWh=round(eb20, 1),
                bateria_opt=round(Dopt, 1), batopt_MW=round(pb_o, 1), batopt_MWh=round(eb_o, 1),
                batopt_MEUR=round(bat_cost(pb_o, eb_o), 1),
                uso_medio_pct=round(100 * float(Lf[k].mean()) / Cv[k], 1),
                pico_min=round(float(Lf[k].max()), 1), pico_N1=round(float(LN1[k].max()), 1),
                media=round(float(Lf[k].mean()), 2)))
        tot = {c: round(sum(r[c] for r in rows), 1) for c in
               ("firme", "firme_flex", "sin_bateria", "flexible", "bateria_20", "bateria_opt",
                "batopt_MW", "batopt_MWh", "batopt_MEUR")}
        res["escenarios"].append(dict(acceso=name, f=f, filas=rows, total=tot))

tot = L.sum(axis=0)
res["minutos_sin_trenes"] = int((tot < 1.0).sum())
json.dump(res, open(OUT, "w"), ensure_ascii=False)
for e in res["escenarios"]:
    t = e["total"]
    print(f"{LINE} acceso={e['acceso']:>8} carga x{e['f']}: firme {t['firme']:>6} | firme+flex {t['firme_flex']:>6} | "
          f"sin bat {t['sin_bateria']:>6} | flex {t['flexible']:>6} | bat20 {t['bateria_20']:>6} | "
          f"bat opt {t['bateria_opt']:>6} ({t['batopt_MWh']} MWh, {t['batopt_MEUR']} MEUR)")
print("minutos/dia con <1 MW en toda la linea:", res["minutos_sin_trenes"])
