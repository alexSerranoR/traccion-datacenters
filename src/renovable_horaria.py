"""Paso 4c: cuanta renovable nueva necesita un CPD para cumplir la correlacion horaria del proyecto de RD de centros
de datos (en cada hora, al menos el 80 % del consumo cubierto por renovable de esa misma hora; ver
docs/encaje_regulatorio.md, seccion 7).
Uso: python renovable_horaria.py <data/ree_horario_2025.csv> <dir_results>

Perfiles: la forma horaria de la eolica y la FV peninsular de 2025 (REE, tiempo real), escalada a un factor de
capacidad SUPUESTO por MW contratado. Es el perfil agregado de toda la peninsula: mas suave que el de unas pocas
plantas concretas, asi que el resultado es OPTIMISTA (hara falta algo mas).
CPD: 1 MW de consumo plano. Se prueban carteras de eolica (W) y FV (S) por MW de CPD, con o sin bateria de
desplazamiento de horas (distinta de la bateria de potencia del tren) y con o sin bloque flexible:
 - bateria: se carga con el excedente renovable y se descarga hasta llegar al 80 % en las horas que no llegan
 - flexible: en las horas que aun no llegan, el CPD baja hasta un 30 % (FLEX) lo justo para llegar al 80 %
Para cada combinacion se busca la cartera de menor coste anual (sin contar la venta de excedentes) que deja como mucho el 5 % o el 20 % de horas sin
cumplir (el 20 % es el umbral de perdida del permiso; por debajo del 5 % el recargo es el minimo).
"""
import sys
import numpy as np, pandas as pd

SRC, OUT = sys.argv[1], sys.argv[2]

TARGET = 0.80                    # cobertura horaria exigida
FLEX = 0.30                      # igual que analysis.py
CF_W, CF_S = 0.26, 0.21          # SUPUESTO: factor de capacidad de eolica nueva y FV nueva en el interior peninsular
ETA = 0.88                       # rendimiento ida y vuelta de la bateria de desplazamiento
# coste anual equivalente (M EUR/año por MW o MWh), SUPUESTO: inversion x factor de recuperacion (7 %)
COST_W = 1.25 * 0.086            # eolica 1,25 M EUR/MW, 25 años
COST_S = 0.55 * 0.086            # FV 0,55 M EUR/MWp, 25 años
COST_B = 0.25 * 0.110            # bateria 0,25 M EUR/MWh (4 h, la potencia incluida), 15 años
P_EXC = 30                       # SUPUESTO: EUR/MWh a los que se vende el excedente (precio capturado bajo por la FV)
GRID = np.round(np.arange(0, 8.01, 0.25), 2)
HOURS_B = [0, 2, 4, 8]

d = pd.read_csv(SRC)
w = d["eolica_MWh"].to_numpy(float); s = d["solar_fv_MWh"].to_numpy(float)
w = w / w.mean() * CF_W; s = np.clip(s, 0, None) / s.mean() * CF_S        # MWh/h por MW contratado
N = len(w)


def run(W, S, hb, flex):
    """Horas que no llegan al 80 %, energia renovable que cubre el consumo y energia recortada al CPD."""
    g = W * w + S * s
    if hb == 0 and not flex:
        cov = np.minimum(g, 1.0)
        return float((cov < TARGET - 1e-9).mean()), float(cov.mean()), 0.0, float(np.clip(g - 1, 0, None).mean())
    soc, E = 0.0, float(hb)
    fail = cub = cut = exc = 0.0
    for t in range(N):
        load = 1.0; gt = g[t]
        if gt >= load:
            ch = min((E - soc) / ETA, gt - load); soc += ch * ETA; exc += gt - load - ch; cov = load
        else:
            need = max(0.0, TARGET * load - gt)
            dis = min(soc, need); soc -= dis; cov = gt + dis
            if cov < TARGET * load - 1e-9 and flex:
                red = min(FLEX, 1 - cov / TARGET)       # bajar el consumo lo justo para llegar al 80 %
                load = 1 - red; cut += red
            if cov < TARGET * load - 1e-9: fail += 1
        cub += min(cov, load)
    return fail / N, cub / N, cut / N, exc / N


rows = []
for hb in HOURS_B:
    for flex in (False, True):
        for W in GRID:
            for S in GRID:
                f, c, k, x = run(W, S, hb, flex)
                rows.append(dict(bateria_h=hb, flexible=flex, eolica_MW=W, fv_MW=S, horas_fallo_pct=round(100 * f, 1),
                                 cobertura_pct=round(100 * c, 1), recorte_pct=round(100 * k, 2),
                                 renovable_sobre_consumo=round(float((W * w + S * s).mean()) / (1 - k), 2),
                                 coste_MEUR_año=round(W * COST_W + S * COST_S + hb * COST_B, 3),
                                 excedente_MEUR_año=round(x * 8760 * P_EXC / 1e6, 3)))
df = pd.DataFrame(rows)

best = []
for lim in (5, 20):
    ok = df[df.horas_fallo_pct <= lim]
    for (hb, flex), g in ok.groupby(["bateria_h", "flexible"]):
        r = g.sort_values("coste_MEUR_año").iloc[0].to_dict()
        r["limite_horas_fallo_pct"] = lim
        cons = 8760 * (1 - r["recorte_pct"] / 100)
        r["coste_EUR_MWh_cpd"] = round(r["coste_MEUR_año"] * 1e6 / cons, 1)
        r["coste_neto_EUR_MWh_cpd"] = round((r["coste_MEUR_año"] - r["excedente_MEUR_año"]) * 1e6 / cons, 1)
        best.append(r)
b = pd.DataFrame(best)[["limite_horas_fallo_pct", "bateria_h", "flexible", "eolica_MW", "fv_MW", "horas_fallo_pct",
                        "cobertura_pct", "recorte_pct", "renovable_sobre_consumo", "coste_MEUR_año",
                        "coste_EUR_MWh_cpd", "coste_neto_EUR_MWh_cpd"]]
b.to_csv(f"{OUT}/renovable_horaria.csv", index=False)
print(f"Perfil REE 2025: {N} h, FC eolica {w.mean():.2f}, FC FV {s.mean():.2f}")
print("Mejor cartera por MW de CPD (coste = inversion anualizada; neto = descontando la venta del excedente):")
print(b.to_string(index=False))
