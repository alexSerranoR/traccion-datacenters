"""Paso 6: genera un panel HTML autocontenido con los resultados (results/dashboard.html).
Uso: python dashboard.py <dir_results>
Lee solo las tablas de results/, asi que puede rehacerse sin volver a simular.
El HTML no necesita servidor ni internet: se abre con doble clic y se puede enviar por correo.
"""
import sys, json, pathlib
import pandas as pd

RES = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent / "results"
TEMPLATE = pathlib.Path(__file__).resolve().parent / "dashboard_template.html"

geo = json.loads((RES / "lineas.json").read_text(encoding="utf-8"))
cap = pd.read_csv(RES / "capacidad.csv", dtype={"acceso": str})
fin = pd.read_csv(RES / "finanzas.csv", dtype={"acceso": str})
sim = pd.read_csv(RES / "simulacion.csv")
hora = pd.read_csv(RES / "perfil_hora.csv")
cur = pd.read_csv(RES / "curvas_bateria.csv", dtype={"acceso": str})
sup = pd.read_csv(RES / "supuestos.csv").fillna("")
supf = pd.read_csv(RES / "supuestos_financieros.csv").fillna("")
LINES = list(geo)


def night(m):
    """Tramo continuo mas largo con <1 MW en toda la linea (el dia es ciclico)."""
    idle = (m.iloc[:, 1:].sum(axis=1) < 1.0).tolist()
    best, start = (0, 0), None
    for i in range(2 * len(idle)):
        if idle[i % len(idle)]:
            start = i if start is None else start
            if i - start + 1 > best[0] and i - start + 1 <= len(idle): best = (i - start + 1, start)
        else:
            start = None
    return dict(inicio=best[1] % len(idle), minutos=best[0])


minuto, noche = {}, {}
for l in LINES:
    m = pd.read_csv(RES / f"perfil_minuto_{l}.csv")
    minuto[l] = {se: m[se].round(2).tolist() for se in m.columns[1:]}
    noche[l] = night(m)


# ------------------------------- conclusiones (escenario central) -------------------------------
def n(v, d=0):
    s = f"{v:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def tot(line, acc, f, col):
    r = cap[(cap.linea == line) & (cap.acceso == acc) & (cap.carga_x == f)]
    return r[col].sum()


def fn(line, acc, opt, col, f=1.0):
    r = fin[(fin.linea == line) & (fin.acceso == acc) & (fin.carga_x == f) & (fin.opcion == opt)]
    return float(r[col].iloc[0])


A0, AX = "REE", "trafo"      # escenario central: acceso concedido hoy por REE; ampliacion hasta los transformadores
s = {l: sim[(sim.linea == l) & sim.escenario.str.contains("Iryo")].iloc[0] for l in LINES}
c = {l: cap[(cap.linea == l) & (cap.acceso == A0) & (cap.carga_x == 1.0)] for l in LINES}
nm = {l: geo[l]["corto"] for l in LINES}
H, B = "MZB", "MS"
T = lambda l, col, a=A0, f=1.0: tot(l, a, f, col)
uso = {l: c[l].media.sum() / c[l].acceso_MW.sum() * 100 for l in LINES}
over = {l: c[l][c[l].pico_N1 > 0.9 * c[l].acceso_MW] for l in LINES}
tight = {l: c[l][c[l].pico_min > 0.9 * c[l].acceso_MW] for l in LINES}
peak = {l: c[l].loc[c[l].pico_min.idxmax()] for l in LINES}
rec = max(cap[(cap.acceso == A0) & (cap.carga_x == 1.0)].flex_recorte_pct)
cotas = {l: max(z for _, z in geo[l]["cotas"]) for l in LINES}
acc = {l: c[l].acceso_MW.sum() for l in LINES}
bh = {l: T(l, "batopt_MWh") / max(T(l, "batopt_MW"), 1) * 60 for l in LINES}
concl = [
    ("Los trenes usan poca energía, pero sus picos llenan el acceso",
     f"Con el acceso que REE tiene concedido hoy a cada subestación ({n(acc[H])} MW en {nm[H]}, {n(acc[B])} MW en "
     f"{nm[B]}), el tren usa de media solo el {n(uso[H], 1)} % y el {n(uso[B], 1)} %. Pero sus picos de 1 minuto "
     f"llegan a {n(peak[H].pico_min)} MW ({peak[H].se}): en {len(over[H])} de {len(c[H])} subestaciones de {nm[H]} "
     f"y {len(over[B])} de {len(c[B])} de {nm[B]} el pico con una vecina caída ya supera el 90 % del acceso concedido."),
    ("Hoy, la capacidad firme es pequeña",
     f"La capacidad que Adif no usa nunca, ni con una vecina caída, y que podría liberar para que un CPD la pida en "
     f"el mismo nudo, suma {n(T(H, 'firme'))} MW en {nm[H]} y {n(T(B, 'firme'))} MW en {nm[B]}. "
     f"La línea de baja densidad ofrece {n(T(B, 'firme') / max(T(H, 'firme'), 1), 0)} veces más, porque al sur de "
     f"Madrid pasan muchos menos trenes. Con un 30 % de carga flexible sube a {n(T(H, 'firme_flex'))} y "
     f"{n(T(B, 'firme_flex'))} MW."),
    ("Con un acceso compartido, el CPD flexible casi triplica lo firme",
     f"Si la regulación permitiera compartir el acceso con prioridad del tren, cabrían {n(T(H, 'flexible'))} MW en "
     f"{nm[H]} y {n(T(B, 'flexible'))} MW en {nm[B]} con un 30 % de carga recortable (entrenamiento de IA, lotes), "
     f"recortando como mucho el {n(rec, 1)} % de su energía."),
    ("La batería es de potencia, no de energía",
     f"Una batería dimensionada para cada subestación lleva el CPD a {n(T(H, 'bateria_opt'))} MW en {nm[H]} "
     f"({n(T(H, 'batopt_MW'))} MW / {n(T(H, 'batopt_MWh'))} MWh, {n(T(H, 'batopt_MEUR'))} M€) y a "
     f"{n(T(B, 'bateria_opt'))} MW en {nm[B]} ({n(T(B, 'batopt_MW'))} MW / {n(T(B, 'batopt_MWh'))} MWh, "
     f"{n(T(B, 'batopt_MEUR'))} M€). Son baterías de unos {n(bh[H])} minutos: cubren picos, no desplazan energía."),
    ("Ampliar el acceso cambia la escala",
     f"Si se ampliara el acceso hasta lo que admiten los transformadores de tracción (~100 MW por subestación en "
     f"{nm[H]}, ~55 MW en {nm[B]}), la capacidad firme pasaría a {n(T(H, 'firme', AX))} MW en {nm[H]} y "
     f"{n(T(B, 'firme', AX))} MW en {nm[B]}, y con batería a {n(T(H, 'bateria_opt', AX))} y "
     f"{n(T(B, 'bateria_opt', AX))} MW. La alta densidad gana más porque sus transformadores son el doble de grandes."),
    ("Las pendientes y el tráfico futuro pesan",
     f"Con el perfil de cotas (hasta {n(cotas[H])} m en {nm[H]}) el consumo sale a {n(s[H].kWh_tren_km, 1)} "
     f"kWh/tren-km en {nm[H]} y {n(s[B].kWh_tren_km, 1)} en {nm[B]}, y los picos se van a las rampas. Si la carga "
     f"del tren fuera un 50 % mayor, la firme con el acceso actual caería a {n(T(H, 'firme', A0, 1.5))} MW en "
     f"{nm[H]} y {n(T(B, 'firme', A0, 1.5))} MW en {nm[B]}. Cada noche hay {n(noche[H]['minutos'] / 60, 1)} h "
     f"sin trenes, pero es la ventana de mantenimiento, no capacidad firme."),
    ("Orden de magnitud económico",
     f"Con un canon de 40 €/kW·año, la capacidad firme de hoy daría a Adif "
     f"{n(fn(H, A0, 'firme', 'ingreso_adif_MEUR_año'), 1)} M€/año en {nm[H]} y "
     f"{n(fn(B, A0, 'firme', 'ingreso_adif_MEUR_año'), 1)} M€/año en {nm[B]}; con reforma y batería, "
     f"{n(fn(H, A0, 'bateria_opt', 'ingreso_adif_MEUR_año'), 1)} y {n(fn(B, A0, 'bateria_opt', 'ingreso_adif_MEUR_año'), 1)} "
     f"M€/año. Para el promotor, no esperar 3 años a una conexión propia vale unos "
     f"{n(fn(H, A0, 'bateria_opt', 'valor_adelanto_MEUR'))} M€ en {nm[H]}, frente a "
     f"{n(fn(H, A0, 'bateria_opt', 'inversion_bateria_MEUR'))} M€ de batería."),
]
if len(tight[H]) + len(tight[B]):
    concl.append(("Un dato a revisar",
        "En " + ", ".join(tight[H].se.tolist() + tight[B].se.tolist()) + " el pico simulado del tren en operación normal "
        "ya supera el 90 % del acceso concedido. Encaja con que Adif pidiera a REE justo lo que necesitan sus picos, "
        "pero también puede ser que el acceso publicado no corresponda a esa subestación (posición pendiente, "
        "alimentación desde distribución) o que la zona que alimenta sea distinta de la supuesta. Es lo primero que "
        "contrastar con Adif."))

data = dict(
    lineas=geo, capacidad=cap.to_dict(orient="records"), finanzas=fin.to_dict(orient="records"),
    simulacion=json.loads(sim.to_json(orient="records")),
    minuto=minuto, noche=noche,
    hora_media={l: {se: hora[(hora.linea == l) & (hora.subestacion == se)].sort_values("hora").media_MW.round(2).tolist()
                    for se in minuto[l]} for l in LINES},
    curvas={l: {a: {se: g[["cpd_MW", "bateria_MW", "bateria_MWh"]].values.tolist()
                    for se, g in cur[(cur.linea == l) & (cur.acceso == a)].groupby("subestacion")}
                for a in cur[cur.linea == l].acceso.unique()} for l in LINES},
    supuestos=sup.to_dict(orient="records"), supuestos_fin=supf.to_dict(orient="records"),
    conclusiones=[dict(t=t, x=x) for t, x in concl],
)
html = TEMPLATE.read_text(encoding="utf-8").replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
out = RES / "dashboard.html"
out.write_text(html, encoding="utf-8")
print("Panel escrito en", out, f"({len(html) // 1024} KB, abrelo con doble clic)")
for t, x in concl: print("-", t + ":", x)
