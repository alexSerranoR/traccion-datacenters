"""Paso 1: extrae del GTFS de Renfe los trenes que circulan por una LAV (ver lines.py) en un dia
laborable y los convierte en tramos (segmentos) sobre el PK de la linea.
Uso: python extract.py <dir_gtfs> <fecha YYYYMMDD> <linea MZB|MS> <salida.csv>
"""
import sys, math
import pandas as pd
from lines import LINES, entry_pk as _entry

GTFS, DATE, LINE, OUT = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
CFG = LINES[LINE]

def load(name):
    df = pd.read_csv(f"{GTFS}/{name}", dtype=str, skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    return df.apply(lambda s: s.str.strip())

# --- servicios activos en la fecha
cal, cd = load("calendar.txt"), load("calendar_dates.txt")
wd = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"][pd.Timestamp(DATE).weekday()]
active = set(cal[(cal.start_date <= DATE) & (cal.end_date >= DATE) & (cal[wd] == "1")].service_id)
ex = cd[cd.date == DATE]
active |= set(ex[ex.exception_type == "1"].service_id)
active -= set(ex[ex.exception_type == "2"].service_id)

routes, trips = load("routes.txt"), load("trips.txt")
HS = {"AVE": "AVE", "AVLO": "AVE", "AVE INT": "AVE", "ALVIA": "ALVIA", "Intercity": "ALVIA",
      "AVANT": "AVANT", "AVANT EXP": "AVANT", "EUROMED": "AVE"}
trips = trips[trips.service_id.isin(active)].merge(routes[["route_id", "route_short_name"]], on="route_id")
trips = trips[trips.route_short_name.isin(HS)]
st = load("stop_times.txt")
st = st[st.trip_id.isin(trips.trip_id)].copy()
stops = load("stops.txt").set_index("stop_id")

PK, L_END = CFG["pk"], CFG["L"]

def secs(t):
    h, m, s = map(int, t.split(":")); return h * 3600 + m * 60 + s

def hav(a, b):
    la1, lo1 = map(float, (stops.loc[a, "stop_lat"], stops.loc[a, "stop_lon"]))
    la2, lo2 = map(float, (stops.loc[b, "stop_lat"], stops.loc[b, "stop_lon"]))
    p = math.pi / 180
    h = math.sin((la2-la1)*p/2)**2 + math.cos(la1*p)*math.cos(la2*p)*math.sin((lo2-lo1)*p/2)**2
    return 2 * 6371 * math.asin(math.sqrt(h))

def entry_pk(off_stop):
    """Punto por el que un tren procedente/con destino fuera de la linea entra o sale de ella."""
    return _entry(LINE, float(stops.loc[off_stop, "stop_lat"]), float(stops.loc[off_stop, "stop_lon"]))

rows = []
tt = trips.set_index("trip_id")
for tid, g in st.assign(seq=st.stop_sequence.astype(int)).sort_values("seq").groupby("trip_id"):
    typ = HS[tt.loc[tid, "route_short_name"]]
    g = g.to_dict("records")
    dep0, arr1 = secs(g[0]["departure_time"]), secs(g[-1]["arrival_time"])   # horario completo del tren
    n0 = len(rows)
    for a, b in zip(g[:-1], g[1:]):
        pa, pb = PK.get(a["stop_id"]), PK.get(b["stop_id"])
        t0, t1 = secs(a["departure_time"]), secs(b["arrival_time"])
        if pa is None and pb is None:
            continue
        if pa is not None and pb is not None:
            if pa == pb: continue
            rows.append((tid, typ, pa, pb, t0, t1, a["stop_id"], b["stop_id"], 1, 1)); continue
        # tramo que entra o sale del corredor: se recorta la parte dentro de la LAV
        on, off = (b, a) if pa is None else (a, b)
        p_on, p_e = PK[on["stop_id"]], entry_pk(off["stop_id"])
        if p_on == p_e: continue
        d_in = abs(p_on - p_e)
        d_tot = max(hav(a["stop_id"], b["stop_id"]) * 1.15, d_in + 1)
        T_in = (t1 - t0) * d_in / d_tot
        if pa is None:   # entra: llega a 'on' en t1
            rows.append((tid, typ, p_e, p_on, t1 - T_in, t1, "ENTRADA", on["stop_id"], 0, 1))
        else:            # sale: parte de 'on' en t0
            rows.append((tid, typ, p_on, p_e, t0, t0 + T_in, on["stop_id"], "SALIDA", 1, 0))
    rows[n0:] = [r + (dep0, arr1, "Renfe") for r in rows[n0:]]

seg = pd.DataFrame(rows, columns=["trip", "tipo", "pk0", "pk1", "t0", "t1", "de", "a", "para0", "para1",
                                  "sal_tren", "lleg_tren", "operador"])
seg.to_csv(OUT, index=False)
print("servicios activos:", len(active), "| trenes AV del dia:", len(trips))
print("trenes en el corredor:", seg.trip.nunique(), "| tramos:", len(seg))
print(seg.groupby("tipo").trip.nunique())
seg["km"] = (seg.pk1 - seg.pk0).abs()
seg["vmed"] = seg.km / ((seg.t1 - seg.t0) / 3600)
print(seg.vmed.describe().round(1))
print("tren-km en el corredor:", round(seg.km.sum()))
