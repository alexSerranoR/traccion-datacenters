"""Paso 2: simula segundo a segundo la potencia que cada tren pide a la catenaria y la reparte
entre las subestaciones de traccion de la LAV Madrid-Zaragoza-Barcelona.
Uso: python -I sim.py <tramos.csv> <dir_salida> [--competencia N]
  --competencia N : anade N trenes por sentido de otros operadores (Iryo/Ouigo), clonando
                    patrones de Renfe Madrid-Barcelona desplazados 20 min (supuesto).
"""
import sys, json
import numpy as np, pandas as pd

TR, OUT = sys.argv[1], sys.argv[2]
NCOMP = int(sys.argv[sys.argv.index("--competencia") + 1]) if "--competencia" in sys.argv else 0

# ---------------- parametros de material rodante (supuestos, a refinar) ----------------
# m: masa (t) | P: potencia max. en llanta (MW) | F: esfuerzo max. arranque (kN) | vmax (km/h)
# Davis R(v) = A + B v + C v^2  [N, v en m/s]
TRAINS = {
    "AVE":   dict(m=425, P=8.8, F=283, vmax=300, A=4000, B=50, C=6.5, aux=0.45),  # S-103/S-112/Iryo/Ouigo
    "ALVIA": dict(m=320, P=4.8, F=200, vmax=250, A=3000, B=40, C=5.0, aux=0.20),  # S-130/S-730/S-120
    "AVANT": dict(m=290, P=4.4, F=180, vmax=250, A=3000, B=40, C=5.0, aux=0.20),  # S-121/S-114
}
ETA_T, ETA_R = 0.85, 0.80     # rendimiento pantografo->llanta (traccion) y llanta->pantografo (regeneracion)
BRAKE = 0.50                  # deceleracion de servicio (m/s2)
MARGIN = 0.08                 # margen de regularidad del horario: el tren marcha un 8 % mas rapido
                              # que el horario y gasta el margen parado (hipotesis habitual)
ROT = 1.06                    # factor de masas rotativas

# Subestaciones (supuesto: cada ~60 km; posiciones reales en IDEADIF de Adif)
SE_PK = np.array([15, 70, 130, 190, 250, 305, 365, 425, 485, 545, 605])
BOUND = (SE_PK[:-1] + SE_PK[1:]) / 2      # zonas neutras a mitad de camino
DAY = 86400

def tables(p):
    """Curvas de aceleracion y frenado a 1 s: tiempo, velocidad, distancia, potencia electrica (MW)."""
    m = p["m"] * 1000 * ROT; vmax = p["vmax"] / 3.6
    R = lambda v: p["A"] + p["B"] * v + p["C"] * v * v
    v, x, acc = 0.0, 0.0, []
    while v < vmax - 1e-6:
        F = min(p["F"] * 1e3, p["P"] * 1e6 / max(v, 0.1))
        a = (F - R(v)) / m
        if a < 0.02: break
        acc.append((v, x, F * v / 1e6 / ETA_T + p["aux"]))
        x += v + a / 2; v = min(v + a, vmax)
    acc.append((v, x, 0)); acc = np.array(acc)
    # frenado desde vmax hasta 0 a deceleracion constante; recupera hasta P max en llanta
    v, br = vmax, []
    while v > 0:
        Fb = max(p["m"] * 1000 * ROT * BRAKE - R(v), 0)
        Pw = min(Fb * v, p["P"] * 1e6)
        br.append((v, -Pw / 1e6 * ETA_R + p["aux"]))
        v -= BRAKE
    br = np.array(br)
    return dict(acc=acc, br=br, vmax=acc[-1, 0], R=R)

TAB = {k: tables(p) for k, p in TRAINS.items()}

def profile(tipo, d, T, stop0, stop1):
    """Perfil 1 s (posicion relativa en m, potencia MW) de un tramo de longitud d (m) en T (s)."""
    tb, p = TAB[tipo], TRAINS[tipo]
    acc, br = tb["acc"], tb["br"]
    def parts(vc):
        ia = np.searchsorted(acc[:, 0], vc) if stop0 else 0
        ib = np.searchsorted(-br[:, 0], -vc) if stop1 else len(br)
        da = acc[ia, 1] if stop0 else 0.0
        bseg = br[ib:]; db = bseg[:, 0].sum() if stop1 else 0.0
        return ia, ib, da, db
    def runtime(vc):
        ia, ib, da, db = parts(vc)
        dc = d - da - db
        return np.inf if dc < 0 else ia + (len(br) - ib if stop1 else 0) + dc / vc
    lo, hi = 1.0, tb["vmax"]
    if runtime(hi) > T:                         # el horario exige mas que vmax: se va a vmax
        while runtime(hi) == np.inf: hi *= 0.98
        vc = hi
    else:
        for _ in range(40):
            mid = (lo + hi) / 2
            (lo, hi) = (mid, hi) if runtime(mid) > T else (lo, mid)
        vc = hi
    ia, ib, da, db = parts(vc)
    dc = d - da - db; tc = int(round(dc / vc))
    Pc = tb["R"](vc) * vc / 1e6 / ETA_T + p["aux"]
    x, P = [], []
    if stop0: x += list(acc[:ia, 1]); P += list(acc[:ia, 2])
    x0 = da
    x += list(x0 + vc * np.arange(tc)); P += [Pc] * tc
    if stop1:
        xb = d - db + np.concatenate([[0], np.cumsum(br[ib:, 0])[:-1]])
        x += list(xb); P += list(br[ib:, 1])
    return np.array(x), np.array(P), vc

seg = pd.read_csv(TR)

if NCOMP:  # trenes de otros operadores: clonar patrones Renfe Madrid<->Barcelona
    g = seg.assign(a=seg[["pk0", "pk1"]].min(axis=1), b=seg[["pk0", "pk1"]].max(axis=1)).groupby("trip").agg(
        lo=("a", "min"), hi=("b", "max"), tipo=("tipo", "first"))
    full = seg[seg.trip.isin(g[(g.lo == 0) & (g.hi == 621) & (g.tipo == "AVE")].index)]
    extra = []
    for direction in (1, -1):
        trips = [t for t, s in full.groupby("trip") if np.sign(s.pk1.iloc[0] - s.pk0.iloc[0]) == direction]
        trips = sorted(trips, key=lambda t: full[full.trip == t].t0.min())
        pick = [trips[int(i)] for i in np.linspace(0, len(trips) - 1, NCOMP)]
        for j, t in enumerate(pick):
            s = full[full.trip == t].copy()
            s["trip"] = f"COMP{direction}_{j}"; s[["t0", "t1"]] += 20 * 60
            extra.append(s)
    seg = pd.concat([seg] + extra, ignore_index=True)

NSE = len(SE_PK)
Pse = np.zeros((NSE, DAY))      # potencia neta por subestacion (MW), resolucion 1 s
Pdem = np.zeros((NSE, DAY))     # solo consumo (trenes traccionando)
Preg = np.zeros((NSE, DAY))     # solo regeneracion (valor positivo)
late, energy_tr = 0, 0.0
trainkm = 0.0
for tid, s in seg.sort_values("t0").groupby("trip"):
    s = s.sort_values("t0")
    prev = None
    for r in s.itertuples():
        if prev is not None and r.t0 > prev.t1:            # parada en estacion: solo auxiliares
            tt = np.arange(int(prev.t1), int(r.t0)) % DAY
            k = np.searchsorted(BOUND, prev.pk1)
            np.add.at(Pse[k], tt, TRAINS[r.tipo]["aux"]); np.add.at(Pdem[k], tt, TRAINS[r.tipo]["aux"])
        d = abs(r.pk1 - r.pk0) * 1000; T = (r.t1 - r.t0) * (1 - MARGIN)
        x, P, vc = profile(r.tipo, d, T, r.para0 == 1, r.para1 == 1)
        if len(x) > T + 30: late += 1
        pk = r.pk0 + np.sign(r.pk1 - r.pk0) * x / 1000
        k = np.searchsorted(BOUND, pk)
        tt = (int(r.t0) + np.arange(len(P))) % DAY
        np.add.at(Pse, (k, tt), P)
        np.add.at(Pdem, (k, tt), np.clip(P, 0, None))
        np.add.at(Preg, (k, tt), np.clip(-P, 0, None))
        trainkm += d / 1000
        prev = r

# ---------------- salidas ----------------
pos = np.clip(Pse, 0, None)
minute = pos.reshape(NSE, 1440, 60).mean(axis=2)
q15 = pos.reshape(NSE, 96, 900).mean(axis=2)
pd.DataFrame(minute.T, columns=[f"SE{i+1}" for i in range(NSE)]).to_csv(f"{OUT}/carga_minuto.csv", index_label="minuto")
np.save(f"{OUT}/Pse_1s.npy", Pse.astype(np.float32))
E_dem = Pdem.sum() / 3600; E_reg = Preg.sum() / 3600
E_net_grid = pos.sum() / 3600; E_back = np.clip(-Pse, 0, None).sum() / 3600
summary = dict(
    trenes=int(seg.trip.nunique()), tren_km=round(trainkm), tramos_mas_lentos_que_horario=late,
    energia_consumo_MWh=round(E_dem, 1), energia_regenerada_MWh=round(E_reg, 1),
    energia_red_MWh=round(E_net_grid, 1), energia_devuelta_red_MWh=round(E_back, 1),
    kWh_por_tren_km=round((E_net_grid - E_back) * 1000 / trainkm, 1),
    se=[dict(se=f"SE{i+1}", pk=int(SE_PK[i]), E_MWh=round(pos[i].sum() / 3600, 1),
             media_MW=round(pos[i].mean(), 2), pico_1s_MW=round(pos[i].max(), 1),
             pico_1min_MW=round(minute[i].max(), 1), pico_15min_MW=round(q15[i].max(), 1),
             devuelta_MWh=round(np.clip(-Pse[i], 0, None).sum() / 3600, 1))
        for i in range(NSE)])
json.dump(summary, open(f"{OUT}/resumen.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in summary.items() if k != "se"}, ensure_ascii=False))
print(pd.DataFrame(summary["se"]).to_string(index=False))
