"""Definicion de las dos lineas estudiadas: estaciones (PK), enlaces con otras lineas, perfil de cotas,
subestaciones de traccion y horarios de los operadores que no estan en el GTFS de Renfe.

Todo lo que no es dato publico verificado esta marcado como SUPUESTO en el comentario.
PK = punto kilometrico aproximado desde Madrid-Puerta de Atocha.
"""
import csv, pathlib

# Subestaciones reales (nombre, PK estimado, nudo de REE y capacidad de acceso concedida), recopiladas en el hilo
# "Capacidad de acceso de subestaciones": REE "Capacidad de acceso de demanda ocupada por posicion" (01/10/2026),
# dossier de Adif de la LAV Madrid-Barcelona, elEconomista 07/2025. Ver data/README.md.
SE_CSV = pathlib.Path(__file__).resolve().parent.parent / "data" / "subestaciones_traccion.csv"
SE_DATA = {}
for r in csv.DictReader(open(SE_CSV, encoding="utf-8")):
    SE_DATA.setdefault(r["linea"], []).append(r)


def _se(line):
    return [(r["subestacion"], float(r["pk_est_km"])) for r in sorted(SE_DATA[line], key=lambda r: int(r["orden"]))]


LINES = {
    # ------------------------------------------------------------------------------------------
    "MZB": dict(
        nombre="Madrid–Zaragoza–Barcelona",
        corto="Madrid–Barcelona",
        densidad="alta",
        sistema="2x25 kV, 50 Hz",
        L=621,
        # stop_id GTFS -> PK
        pk={"60000": 0, "17000": 0, "04007": 56, "70600": 221, "04040": 306,
            "78400": 442, "04104": 521, "71801": 621},
        estaciones=[("Madrid", 0), ("Guadalajara", 56), ("Calatayud", 221), ("Zaragoza", 306),
                    ("Lleida", 442), ("Camp de Tarragona", 521), ("Barcelona", 621)],
        # SUPUESTO: perfil de cotas aproximado (m) a partir de la altitud de estaciones y puertos
        # (Alcarria, Sierra Ministra, valle del Jalon, Monegros, Garrigues). Precision +-50 m.
        # Debe sustituirse por el perfil longitudinal de Adif.
        cotas=[(0, 650), (20, 620), (40, 800), (56, 925), (80, 850), (110, 950), (135, 1050),
               (150, 1180), (165, 1060), (185, 850), (205, 640), (221, 530), (245, 430), (265, 560),
               (285, 420), (306, 210), (330, 300), (360, 380), (390, 330), (420, 250), (442, 160),
               (465, 330), (485, 500), (505, 300), (521, 110), (545, 200), (565, 250), (590, 120),
               (621, 30)],
        subestaciones=_se("MZB"),
        pos_subestaciones="13 reales (dossier de Adif, nudos de REE); PK estimados ±10 km",
    ),
    # ------------------------------------------------------------------------------------------
    "MS": dict(
        nombre="Madrid–Córdoba–Sevilla",
        corto="Madrid–Sevilla",
        densidad="baja",
        sistema="1x25 kV, 50 Hz",
        L=471,
        pk={"60000": 0, "17000": 0, "37200": 171, "37300": 209, "37704": 285, "50500": 344,
            "51003": 471},
        estaciones=[("Madrid", 0), ("Ciudad Real", 171), ("Puertollano", 209),
                    ("Villanueva de Córdoba", 285), ("Córdoba", 344), ("Sevilla", 471)],
        # SUPUESTO: perfil aproximado (meseta, Montes de Toledo, Campo de Calatrava, Sierra Morena con
        # bajada a Cordoba en rampas de hasta 12,5 milesimas, valle del Guadalquivir). +-50 m.
        cotas=[(0, 650), (30, 520), (53, 530), (80, 700), (105, 820), (130, 680), (171, 630),
               (209, 700), (235, 730), (255, 790), (285, 720), (305, 600), (325, 350), (344, 120),
               (380, 80), (420, 40), (471, 10)],
        subestaciones=_se("MS"),
        pos_subestaciones="12 reales (prensa y nudos de REE); PK estimados ±10 km",
    ),
}


def entry_pk(line, lat, lon):
    """PK por el que un tren que viene de (o va a) una estacion fuera de la linea entra (o sale)."""
    if line == "MZB":
        if lon > 2.2: return 621                       # Girona, Figueres, Francia
        if lat > 41.75 and -2.7 < lon < 0.5: return 306  # Huesca, Logrono, Pamplona: enlaza en Zaragoza
        if lon > 0.0 and lat < 41.2: return 521        # Tarragona, Valencia: enlaza en Camp de Tarragona
        return 0                                       # sur/oeste: enlaza en Madrid
    # MS
    if lat < 37.6 and lon > -5.5: return 358           # Malaga, Granada, Antequera, Puente Genil
    if lat < 37.6 and lon < -5.9: return 471           # Cadiz, Jerez, Huelva: siguen tras Sevilla
    if lat < 40.2 and lon > -3.6: return 25            # Cuenca, Valencia, Alicante, Murcia: LAV Levante
                                                       # comparte los primeros ~25 km (Torrejon de Velasco)
    if 39.7 < lat < 40.0 and -4.2 < lon < -3.9: return 53  # Toledo (bifurcacion La Sagra)
    return 0


# ----------------------------------------------------------------------------------------------
# Trenes de Iryo y Ouigo (no estan en el GTFS de Renfe).
# Iryo: horarios reales de lunes a viernes de octubre de 2026 publicados en blablacar.es/train/iryo
#       (consultados el 12/10/2026). Ouigo: frecuencias por sentido anunciadas desde el 14/12/2025
#       (Hosteltur); las horas no se han podido obtener (el GTFS de Ouigo en el Punto de Acceso
#       Nacional no es accesible desde este entorno), asi que se reparten entre las 7 y las 20 h.
# Cada tren se construye clonando el tren de Renfe con el mismo origen y destino mas parecido y
# ajustando su marcha a las horas de salida y llegada.
# formato: (operador, tipo de tren, origen, destino, [(salida, llegada), ...] o numero de trenes)
OTHER_OPERATORS = {
    "MZB": [
        ("Iryo", "IRYO", 0, 621, [("06:09", "09:35"), ("07:22", "10:24"), ("08:22", "11:24"),
            ("08:50", "11:52"), ("09:12", "12:29"), ("09:57", "13:21"), ("11:22", "14:39"),
            ("12:22", "15:39"), ("14:42", "18:13"), ("15:52", "18:54"), ("16:37", "19:39"),
            ("17:22", "20:42"), ("18:32", "21:44"), ("19:29", "22:50")]),
        ("Iryo", "IRYO", 621, 0, [("05:45", "09:02"), ("07:05", "10:07"), ("07:50", "11:15"),
            ("09:12", "12:40"), ("10:45", "13:49"), ("11:18", "14:42"), ("12:14", "15:16"),
            ("13:06", "16:23"), ("13:13", "16:37"), ("14:50", "17:52"), ("15:52", "19:16"),
            ("17:20", "20:22"), ("18:53", "22:10"), ("19:40", "22:42")]),
        ("Ouigo", "OUIGO", 0, 621, 6),
        ("Ouigo", "OUIGO", 621, 0, 6),
    ],
    "MS": [
        ("Iryo", "IRYO", 0, 471, [("06:50", "09:29"), ("07:54", "10:46"), ("12:25", "15:04"),
            ("13:05", "15:46"), ("14:50", "17:29"), ("17:00", "19:39"), ("19:05", "21:44")]),
        ("Iryo", "IRYO", 471, 0, [("06:54", "09:36"), ("10:20", "13:02"), ("12:25", "15:07"),
            ("13:58", "16:40"), ("16:20", "19:02"), ("20:57", "23:39")]),
        # Madrid-Malaga: usan la LAV hasta la bifurcacion de Malaga (PK 358)
        ("Iryo", "IRYO", 0, 358, [("07:36", "10:25"), ("09:50", "12:39"), ("15:05", "17:54"),
            ("20:55", "23:44")]),
        ("Iryo", "IRYO", 358, 0, [("08:52", "11:40"), ("11:34", "14:22"), ("13:50", "16:39"),
            ("18:35", "21:23")]),
        ("Ouigo", "OUIGO", 0, 471, 4), ("Ouigo", "OUIGO", 471, 0, 4),
        ("Ouigo", "OUIGO", 0, 358, 3), ("Ouigo", "OUIGO", 358, 0, 3),
    ],
}
