"""Paso 2: simula segundo a segundo la potencia que cada tren pide a la catenaria y la reparte entre
las subestaciones de traccion de la linea (ver lines.py).
Uso: python sim.py <tramos.csv> <linea MZB|MS> <dir_salida> [--sin-otros]
  --sin-otros : solo trenes de Renfe (GTFS). Por defecto se anaden Iryo y Ouigo (lines.py).

Novedades respecto a la v1: pendientes (perfil de cotas aproximado), material de Iryo y Ouigo,
horarios reales de Iryo, subestaciones por linea y limites de potencia en traccion y freno.
"""
import sys, json
import numpy as np, pandas as pd
from lines import LINES, OTHER_OPERATORS

TR, LINE, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
OTHERS = "--sin-otros" not in sys.argv
CFG = LINES[LINE]

# ---------------- material rodante (supuestos, a refinar) ----------------
# m: masa en carga (t) | P: potencia max. en llanta (MW) | F: esfuerzo max. de arranque (kN) | vmax (km/h)
# Davis R(v) = A + B v + C v^2  [N, v en m/s] | aux: servicios auxiliares (MW)
TRAINS = {
    "AVE":   dict(m=425, P=8.8, F=283, vmax=300, A=4000, B=50, C=6.5, aux=0.45),  # S-103/S-112 (Renfe)
    "IRYO":  dict(m=500, P=9.8, F=370, vmax=300, A=4500, B=55, C=6.8, aux=0.50),  # Frecciarossa 1000
    "OUIGO": dict(m=430, P=9.3, F=220, vmax=300, A=4200, B=50, C=7.0, aux=0.50),  # TGV Euroduplex
    "ALVIA": dict(m=320, P=4.8, F=200, vmax=250, A=3000, B=40, C=5.0, aux=0.20),  # S-130/S-730/S-120
    "AVANT": dict(m=290, P=4.4, F=180, vmax=250, A=3000, B=40, C=5.0, aux=0.20),  # S-121/S-114
}
ETA_T, ETA_R = 0.85, 0.80     # rendimiento pantografo->llanta (traccion) y llanta->pantografo (regeneracion)
BRAKE = 0.50                  # deceleracion de servicio (m/s2)
MARGIN = 0.08                 # margen de regularidad: el tren marcha un 8 % mas rapido que el horario
ROT = 1.06                    # factor de masas rotativas
G = 9.81

SE_NAMES = [s for s, _ in CFG["subestaciones"]]
SE_PK = np.array([p for _, p in CFG["subestaciones"]], dtype=float)
BOUND = (SE_PK[:-1] + SE_PK[1:]) / 2      # zonas neutras a mitad de camino
DAY = 86400

# perfil de cotas -> pendiente (milesimas) por km, suavizada a 2 km
_c = np.array(CFG["cotas"], dtype=float)
_km = np.arange(0, CFG["L"] + 1.0, 0.1)
_z = np.interp(_km, _c[:, 0], _c[:, 1])
_slope = np.gradient(_z, _km * 1000)                       # m/m, positiva = sube hacia el PK creciente
_slope = np.convolve(_slope, np.ones(21) / 21, mode="same")


def slope_at(pk):
    return np.interp(pk, _km, _slope)


def tables(p):
    """Curva de aceleracion a 1 s en llano: velocidad, distancia y aceleracion; y la de frenado."""
    m = p["m"] * 1000 * ROT; vmax = p["vmax"] / 3.6
    R = lambda v: p["A"] + p["B"] * v + p["C"] * v * v
    v, x, acc = 0.0, 0.0, []
    while v < vmax - 1e-6:
        F = min(p["F"] * 1e3, p["P"] * 1e6 / max(v, 0.1))
        a = (F - R(v)) / m
        if a < 0.02: break
        acc.append((v, x, a))
        x += v + a / 2; v = min(v + a, vmax)
    acc.append((v, x, 0.0)); acc = np.array(acc)
    vb = np.arange(vmax, 0, -BRAKE)                          # frenado a deceleracion constante
    return dict(acc=acc, br=vb, vmax=acc[-1, 0], R=R)


TAB = {k: tables(p) for k, p in TRAINS.items()}


def profile(tipo, d, T, stop0, stop1):
    """Marcha a 1 s de un tramo de d metros en T segundos: posicion (m), velocidad (m/s), acel. (m/s2)."""
    tb = TAB[tipo]; acc, br = tb["acc"], tb["br"]
    def parts(vc):
        ia = np.searchsorted(acc[:, 0], vc) if stop0 else 0
        ib = np.searchsorted(-br, -vc) if stop1 else len(br)
        da = acc[ia, 1] if stop0 else 0.0
        db = br[ib:].sum() if stop1 else 0.0
        return ia, ib, da, db
    def runtime(vc):
        ia, ib, da, db = parts(vc)
        dc = d - da - db
        return np.inf if dc < 0 else ia + (len(br) - ib if stop1 else 0) + dc / vc
    lo, hi = 1.0, tb["vmax"]
    late = False
    if runtime(hi) > T:                         # el horario exige mas que vmax: se va a vmax
        late = True
        while runtime(hi) == np.inf: hi *= 0.98
        vc = hi
    else:
        for _ in range(40):
            mid = (lo + hi) / 2
            (lo, hi) = (mid, hi) if runtime(mid) > T else (lo, mid)
        vc = hi
    ia, ib, da, db = parts(vc)
    tc = int(round((d - da - db) / vc))
    x, v, a = [], [], []
    if stop0: x += list(acc[:ia, 1]); v += list(acc[:ia, 0]); a += list(acc[:ia, 2])
    x += list(da + vc * np.arange(tc)); v += [vc] * tc; a += [0.0] * tc
    if stop1:
        vb = br[ib:]
        x += list(d - db + np.concatenate([[0], np.cumsum(vb)[:-1]])); v += list(vb); a += [-BRAKE] * len(vb)
    return np.array(x), np.array(v), np.array(a), late


def power(tipo, v, a, slope_dir):
    """Potencia electrica en pantografo (MW, negativa = devuelve a la catenaria)."""
    p = TRAINS[tipo]; m = p["m"] * 1000
    W = (m * ROT * a + TAB[tipo]["R"](v) + m * G * slope_dir) * v       # potencia en llanta (W)
    W = np.clip(W, -p["P"] * 1e6, p["P"] * 1e6)                          # limites de traccion y freno electrico
    return np.where(W > 0, W / ETA_T, W * ETA_R) / 1e6 + p["aux"]


def hhmm(s):
    h, m = map(int, s.split(":")); return h * 3600 + m * 60


def add_other_operators(seg):
    """Clona trenes de Renfe para construir los de Iryo y Ouigo (ver lines.py)."""
    seg = seg.copy()
    span = seg.groupby("trip").agg(first=("pk0", "first"), last=("pk1", "last"), tipo=("tipo", "first"),
                                   sal=("sal_tren", "first"), lleg=("lleg_tren", "first"))
    extra = []
    for op, tipo, a, b, times in OTHER_OPERATORS[LINE]:
        cand = span[(span["first"] == a) & (span["last"] == b) & (span.tipo == "AVE")]
        if cand.empty: cand = span[(span["first"] == a) & (span["last"] == b)]
        if cand.empty:
            print(f"  aviso: no hay tren de Renfe {a}->{b} para clonar ({op})"); continue
        dur = cand.lleg - cand.sal
        if isinstance(times, int):   # solo se conoce la frecuencia: salidas repartidas de 7 a 20 h
            dep = np.linspace(7 * 3600, 20 * 3600, times) + 10 * 60
            sched = [(int(t), int(t + dur.median())) for t in dep]
            src = "frecuencia anunciada; horas supuestas"
        else:
            sched = [(hhmm(d), hhmm(r)) for d, r in times]
            src = "horario real oct-2026"
        for j, (d0, d1) in enumerate(sched):
            tpl = (dur - (d1 - d0)).abs().idxmin()
            s = seg[seg.trip == tpl].copy()
            k = (d1 - d0) / (span.loc[tpl, "lleg"] - span.loc[tpl, "sal"])
            for c in ("t0", "t1"):
                s[c] = d0 + (s[c] - span.loc[tpl, "sal"]) * k
            s["trip"] = f"{op}_{a}_{b}_{j}"; s["tipo"] = tipo; s["operador"] = op
            s["sal_tren"], s["lleg_tren"] = d0, d1; s["fuente"] = src
            extra.append(s)
    return pd.concat([seg.assign(fuente="GTFS Renfe")] + extra, ignore_index=True)


seg = pd.read_csv(TR)
seg = add_other_operators(seg) if OTHERS else seg.assign(fuente="GTFS Renfe")

NSE = len(SE_PK)
Pse = np.zeros((NSE, DAY))      # potencia neta por subestacion (MW), resolucion 1 s
Pdem = np.zeros((NSE, DAY))     # solo consumo
Preg = np.zeros((NSE, DAY))     # solo regeneracion (valor positivo)
late, trainkm = 0, 0.0
E_tipo, km_tipo = {}, {}
for tid, s in seg.sort_values("t0").groupby("trip"):
    s = s.sort_values("t0")
    prev = None
    for r in s.itertuples():
        aux = TRAINS[r.tipo]["aux"]
        if prev is not None and r.t0 > prev.t1:            # parada en estacion: solo auxiliares
            tt = np.arange(int(prev.t1), int(r.t0)) % DAY
            k = np.searchsorted(BOUND, prev.pk1)
            np.add.at(Pse[k], tt, aux); np.add.at(Pdem[k], tt, aux)
        d = abs(r.pk1 - r.pk0) * 1000; T = (r.t1 - r.t0) * (1 - MARGIN)
        x, v, a, lt = profile(r.tipo, d, T, r.para0 == 1, r.para1 == 1)
        late += lt
        sign = np.sign(r.pk1 - r.pk0)
        pk = r.pk0 + sign * x / 1000
        P = power(r.tipo, v, a, sign * slope_at(pk))
        k = np.searchsorted(BOUND, pk)
        tt = (int(r.t0) + np.arange(len(P))) % DAY
        np.add.at(Pse, (k, tt), P)
        np.add.at(Pdem, (k, tt), np.clip(P, 0, None))
        np.add.at(Preg, (k, tt), np.clip(-P, 0, None))
        trainkm += d / 1000
        E_tipo[r.tipo] = E_tipo.get(r.tipo, 0) + P.sum() / 3600
        km_tipo[r.tipo] = km_tipo.get(r.tipo, 0) + d / 1000
        prev = r

# ---------------- salidas ----------------
pos = np.clip(Pse, 0, None)
minute = pos.reshape(NSE, 1440, 60).mean(axis=2)
q15 = pos.reshape(NSE, 96, 900).mean(axis=2)
pd.DataFrame(minute.T, columns=SE_NAMES).to_csv(f"{OUT}/carga_minuto.csv", index_label="minuto")
np.save(f"{OUT}/Pse_1s.npy", Pse.astype(np.float32))
E_net_grid = pos.sum() / 3600; E_back = np.clip(-Pse, 0, None).sum() / 3600
ops = seg.groupby("trip").agg(op=("operador", "first"), fuente=("fuente", "first"))
summary = dict(
    linea=LINE, trenes=int(seg.trip.nunique()), tren_km=round(trainkm), tramos_mas_lentos_que_horario=int(late),
    trenes_por_operador=ops.op.value_counts().to_dict(),
    trenes_por_fuente=ops.fuente.value_counts().to_dict(),
    energia_consumo_MWh=round(Pdem.sum() / 3600, 1), energia_regenerada_MWh=round(Preg.sum() / 3600, 1),
    energia_red_MWh=round(E_net_grid, 1), energia_devuelta_red_MWh=round(E_back, 1),
    kWh_por_tren_km=round((E_net_grid - E_back) * 1000 / trainkm, 1),
    kWh_tren_km_por_tipo={t: round(E_tipo[t] * 1000 / km_tipo[t], 1) for t in E_tipo},
    se=[dict(se=SE_NAMES[i], pk=float(SE_PK[i]), E_MWh=round(pos[i].sum() / 3600, 1),
             media_MW=round(pos[i].mean(), 2), pico_1s_MW=round(pos[i].max(), 1),
             pico_1min_MW=round(minute[i].max(), 1), pico_15min_MW=round(q15[i].max(), 1),
             devuelta_MWh=round(np.clip(-Pse[i], 0, None).sum() / 3600, 1))
        for i in range(NSE)])
json.dump(summary, open(f"{OUT}/resumen.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in summary.items() if k != "se"}, ensure_ascii=False))
print(pd.DataFrame(summary["se"]).to_string(index=False))
