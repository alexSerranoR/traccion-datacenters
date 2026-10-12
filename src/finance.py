"""Paso 4: cifras financieras orientativas a partir de la capacidad compartible.
Uso: python finance.py <dir_trabajo> <dir_results>

Todo son SUPUESTOS de orden de magnitud para una propuesta de investigacion, no una valoracion.
Se escriben en results/supuestos_financieros.csv para que se puedan discutir y cambiar.
"""
import sys, json
import pandas as pd

W, OUT = sys.argv[1], sys.argv[2]

# parametro: (valor central, bajo, alto, unidad, fuente / razonamiento)
A = {
    "canon_adif": (40, 20, 80, "EUR/kW·año",
                   "Supuesto: pago del CPD a Adif por usar capacidad de acceso ya construida. Del orden de 2-4 veces "
                   "los peajes y cargos de potencia de alta tension, como prima por acceso inmediato"),
    "pue": (1.3, 1.2, 1.4, "-", "PUE de un CPD moderno; la potencia de red incluye refrigeracion"),
    "factor_carga": (0.85, 0.75, 0.95, "-", "Uso medio de la potencia contratada por el CPD"),
    "precio_energia": (70, 50, 100, "EUR/MWh", "Precio medio de la electricidad para el CPD (mercado + peajes)"),
    "capex_cpd": (9, 7, 12, "M EUR/MW IT", "Coste de construir un CPD (orden de magnitud de informes de mercado 2024-2025)"),
    "ebitda_cpd": (0.8, 0.5, 1.2, "M EUR/MW IT·año",
                   "Margen anual de colocation mayorista (~150 EUR/kW IT·mes con ~45 % de margen)"),
    "espera_evitada": (3, 2, 6, "años", "Retraso tipico para obtener acceso y conexion propios en un nudo saturado"),
    "conexion_evitada": (10, 5, 20, "M EUR por emplazamiento",
                         "Nueva posicion de 220/400 kV, linea y subestacion propias que el CPD no necesita construir"),
    "bat_P": (0.20, 0.15, 0.30, "M EUR/MW", "Bateria de ion-litio: parte de potencia (inversores, conexion)"),
    "bat_E": (0.25, 0.18, 0.35, "M EUR/MWh", "Bateria de ion-litio: parte de energia (celdas, contenedores)"),
    "bat_om": (2, 1.5, 3, "%/año", "Operacion y mantenimiento de la bateria sobre su inversion"),
    "tasa": (7, 5, 10, "%", "Tasa de descuento real"),
    "horizonte": (20, 15, 25, "años", "Vida del acuerdo de uso compartido"),
    "min_cpd": (10, 5, 20, "MW", "Tamano minimo de CPD para que un emplazamiento cuente"),
}
v = {k: x[0] for k, x in A.items()}


def annuity(rate, n):
    r = rate / 100
    return (1 - (1 + r) ** -n) / r


OPTIONS = [("firme", "Hoy: capacidad firme que Adif libera"),
           ("firme_flex", "Hoy + CPD flexible"),
           ("sin_bateria", "Reforma: acceso compartido sin batería"),
           ("flexible", "Reforma + CPD flexible (30 %)"),
           ("bateria_opt", "Reforma + batería óptima")]
rows = []
for line in ("MZB", "MS"):
    r = json.load(open(f"{W}/res_{line}.json"))
    for e in r["escenarios"]:
        for opt, label in OPTIONS:
            sites = [f for f in e["filas"] if f[opt] >= v["min_cpd"]]
            MW = sum(f[opt] for f in sites)
            it = MW / v["pue"]
            bat = sum(f["batopt_MEUR"] for f in sites) if opt == "bateria_opt" else 0.0
            ann = annuity(v["tasa"], v["horizonte"])
            canon = MW * 1000 * v["canon_adif"] / 1e6                       # M EUR/año
            rows.append(dict(
                linea=line, acceso=e["acceso"], carga_x=e["f"], opcion=opt, opcion_txt=label,
                emplazamientos=len(sites), cpd_MW_red=round(MW, 1), cpd_MW_IT=round(it, 1),
                energia_GWh_año=round(MW * 8760 * v["factor_carga"] / 1000, 0),
                factura_energia_MEUR_año=round(MW * 8760 * v["factor_carga"] * v["precio_energia"] / 1e6, 0),
                inversion_cpd_MEUR=round(it * v["capex_cpd"], 0),
                inversion_bateria_MEUR=round(bat, 1),
                bateria_anual_MEUR=round(bat / ann + bat * v["bat_om"] / 100, 1),
                ingreso_adif_MEUR_año=round(canon, 1),
                ingreso_adif_VAN_MEUR=round(canon * ann, 0),
                ingreso_adif_bajo_MEUR_año=round(MW * 1000 * A["canon_adif"][1] / 1e6, 1),
                ingreso_adif_alto_MEUR_año=round(MW * 1000 * A["canon_adif"][2] / 1e6, 1),
                conexiones_evitadas_MEUR=round(len(sites) * v["conexion_evitada"], 0),
                valor_adelanto_MEUR=round(it * v["ebitda_cpd"] * v["espera_evitada"], 0),
            ))
pd.DataFrame(rows).to_csv(f"{OUT}/finanzas.csv", index=False)
pd.DataFrame([dict(parametro=k, valor=x[0], bajo=x[1], alto=x[2], unidad=x[3], fuente=x[4]) for k, x in A.items()]
             ).to_csv(f"{OUT}/supuestos_financieros.csv", index=False)
df = pd.DataFrame(rows)
print(df[(df.carga_x == 1.0) & (df.acceso == "60")][["linea", "opcion", "emplazamientos", "cpd_MW_red",
      "inversion_bateria_MEUR", "ingreso_adif_MEUR_año", "valor_adelanto_MEUR"]].to_string(index=False))
