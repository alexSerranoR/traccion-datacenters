"""Paso 3: capacidad que podria compartirse con un centro de datos conectado en el embarrado de AT
de cada subestacion. Uso: python -I analysis.py <dir_escenario> <salida.json>

Supuestos (todos parametrizables):
 - El centro de datos (CPD) se conecta al embarrado de alta tension de la subestacion con su propio
   transformador trifasico; comparte la CAPACIDAD DE ACCESO C de ese punto, no los transformadores
   de traccion. El tren tiene siempre prioridad.
 - Margen de seguridad: solo se usa el 90 % de C.
 - N-1: si cae una subestacion vecina, esta asume la mitad de la carga de la vecina mas cargada.
 - 'Firme' = cabe incluso en N-1 y en el peor minuto del dia, sin bateria.
 - 'Con bateria' = cabe en operacion normal usando una bateria que cubre los picos del tren.
"""
import sys, json
import numpy as np

D, OUT = sys.argv[1], sys.argv[2]
P = np.clip(np.load(f"{D}/Pse_1s.npy").astype(float), 0, None)
NSE = P.shape[0]
L = P.reshape(NSE, 1440, 60).mean(axis=2)                 # MW, medias de 1 minuto
SE_PK = [15, 70, 130, 190, 250, 305, 365, 425, 485, 545, 605]

def n1(L):
    out = L.copy()
    for k in range(NSE):
        nb = [L[j] for j in (k - 1, k + 1) if 0 <= j < NSE]
        out[k] = L[k] + 0.5 * np.max(nb, axis=0)
    return out

def battery_need(H, D):
    """Bateria (MW, MWh) para mantener un CPD constante de D MW con techo de red H(t) (1 min)."""
    s = (H - D) / 60.0                                      # MWh por minuto (+ sobra, - falta)
    e, emin = 0.0, 0.0
    for _ in range(2):                                      # dos vueltas: el dia es ciclico
        for v in s:
            e = min(0.0, e + v); emin = min(emin, e)
    return max(0.0, float((D - H).max())), -emin

def max_D(H, Pb, Eb):
    lo, hi = 0.0, float(H.max())
    for _ in range(40):
        m = (lo + hi) / 2
        pb, eb = battery_need(H, m)
        (lo, hi) = (m, hi) if (pb <= Pb and eb <= Eb) else (lo, m)
    return lo

res = {"escenarios": []}
for C in (30, 60, 120):
    for f in (1.0, 1.5):           # f = 1.5: carga del tren +50 % (pendientes, crecimiento de trafico...)
        Lf = L * f; LN1 = n1(Lf); cap = 0.9 * C
        rows = []
        for k in range(NSE):
            H = cap - Lf[k]
            firm = max(0.0, cap - LN1[k].max())
            nobat = max(0.0, float(H.min()))
            bat = max_D(np.clip(H, 0, None), Pb=20, Eb=20)
            pb, eb = battery_need(np.clip(H, 0, None), bat)
            rows.append(dict(se=f"SE{k+1}", pk=SE_PK[k], firme=round(firm, 1), sin_bateria=round(nobat, 1),
                             con_bateria=round(bat, 1), bat_MW=round(pb, 1), bat_MWh=round(eb, 1),
                             uso_medio_pct=round(100 * Lf[k].mean() / C, 1),
                             pico_N1=round(float(LN1[k].max()), 1)))
        res["escenarios"].append(dict(C=C, f=f, filas=rows,
            total_firme=round(sum(r["firme"] for r in rows)), total_sin_bat=round(sum(r["sin_bateria"] for r in rows)),
            total_con_bat=round(sum(r["con_bateria"] for r in rows))))

# perfiles horarios para graficas: carga media y maxima por hora de cada subestacion
res["perfil_min"] = {f"SE{k+1}": [round(float(v), 2) for v in L[k]] for k in range(NSE)}
res["hora_media"] = {f"SE{k+1}": [round(float(v), 2) for v in L[k].reshape(24, 60).mean(axis=1)] for k in range(NSE)}
res["hora_max"] = {f"SE{k+1}": [round(float(v), 2) for v in L[k].reshape(24, 60).max(axis=1)] for k in range(NSE)}
res["linea_hora_media"] = [round(float(v), 1) for v in L.sum(axis=0).reshape(24, 60).mean(axis=1)]
# franja nocturna sin trenes
tot = L.sum(axis=0)
idle = tot < 0.5 * len(L) * 0.0 + 1.0
res["minutos_sin_trenes"] = int((tot < 1.0).sum())
json.dump(res, open(OUT, "w"), ensure_ascii=False)
for e in res["escenarios"]:
    print(f"C={e['C']:>3} MW  carga x{e['f']}:  firme {e['total_firme']:>5} MW | sin bateria {e['total_sin_bat']:>5} MW | "
          f"con bateria 20MW/20MWh {e['total_con_bat']:>5} MW")
print("minutos/dia con <1 MW en toda la linea:", res["minutos_sin_trenes"])
e = [x for x in res["escenarios"] if x["C"] == 60 and x["f"] == 1.0][0]
for r in e["filas"]: print(r)
