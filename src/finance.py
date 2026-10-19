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
    "pue": (1.15, 1.10, 1.30, "-", "Tope del proyecto de RD de centros de datos (regimen transitorio, PUE <= 1,15); "
                               "la potencia de red incluye refrigeracion"),
    "factor_carga": (0.85, 0.75, 0.95, "-", "Uso medio de la potencia contratada por el CPD"),
    "precio_energia": (70, 50, 100, "EUR/MWh", "Precio medio de la electricidad para el CPD (mercado + peajes)"),
    "capex_cpd": (9, 7, 12, "M EUR/MW IT", "Coste de construir un CPD (orden de magnitud de informes de mercado 2024-2025)"),
    "ebitda_cpd": (0.8, 0.5, 1.2, "M EUR/MW IT·año",
                   "Margen anual de colocation mayorista (~150 EUR/kW IT·mes con ~45 % de margen)"),
    "espera_evitada": (3, 2, 6, "años", "Retraso tipico para obtener acceso y conexion propios en un nudo saturado"),
    "conexion_evitada": (7, 3, 15, "M EUR por emplazamiento",
                         "Linea de AT y subestacion o ampliacion de nudo que un CPD en un nudo nuevo necesitaria. "
                         "La posicion y los transformadores propios los paga igual (ver inversion electrica)"),
    "posicion_AT": (3, 2, 5, "M EUR por emplazamiento",
                    "Posicion propia de 220/400 kV en el parque de REE: interruptor, seccionadores, medida, protecciones"),
    "trafo": (0.04, 0.025, 0.06, "M EUR/MVA",
              "Transformador 400(220)/30 kV instalado. Dos por emplazamiento, cada uno de D/0,9 MVA (N-1)"),
    "grupos": (0.5, 0.35, 0.7, "M EUR/MW",
               "Grupos electrogenos de MT instalados (con combustible para >=12 h), N+1 = 1,1 x potencia respaldada. "
               "En las opciones flexibles solo se respalda el bloque firme (1 - 30 %)"),
    "fv": (0.55, 0.45, 0.7, "M EUR/MWp", "FV opcional acoplada a la bateria, 0,25 MWp por MW de CPD (no cuenta en el total)"),
    "bat_vida": (8, 6, 12, "años",
                 "Vida de la bateria limitada a 2C: ~2,5-3 ciclos/dia, ~1.000/año, LFP de 6.000-8.000 ciclos"),
    "bat_P": (0.20, 0.15, 0.30, "M EUR/MW", "Bateria de ion-litio: parte de potencia (inversores, conexion)"),
    "bat_E": (0.25, 0.18, 0.35, "M EUR/MWh", "Bateria de ion-litio: parte de energia (celdas, contenedores)"),
    "bat_om": (2, 1.5, 3, "%/año", "Operacion y mantenimiento de la bateria sobre su inversion"),
    "tasa": (7, 5, 10, "%", "Tasa de descuento real"),
    "horizonte": (20, 15, 25, "años", "Vida del acuerdo de uso compartido"),
    "min_cpd": (10, 5, 20, "MW", "Tamano minimo de CPD para que un emplazamiento cuente"),
}
v = {k: x[0] for k, x in A.items()}
FLEX = 0.30            # igual que analysis.py: parte recortable del CPD, sin grupos


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
            flex_opt = opt in ("firme_flex", "flexible", "bateria_opt")
            pos_trafo = sum(v["posicion_AT"] + 2 * f[opt] / 0.9 * v["trafo"] for f in sites)
            grupos = 1.1 * MW * (1 - FLEX if flex_opt else 1.0) * v["grupos"]
            ahorro_grupos = 1.1 * MW * v["grupos"] - grupos
            canon = MW * 1000 * v["canon_adif"] / 1e6                       # M EUR/año
            rows.append(dict(
                linea=line, acceso=e["acceso"], carga_x=e["f"], opcion=opt, opcion_txt=label,
                emplazamientos=len(sites), cpd_MW_red=round(MW, 1), cpd_MW_IT=round(it, 1),
                energia_GWh_año=round(MW * 8760 * v["factor_carga"] / 1000, 0),
                factura_energia_MEUR_año=round(MW * 8760 * v["factor_carga"] * v["precio_energia"] / 1e6, 0),
                inversion_cpd_MEUR=round(it * v["capex_cpd"], 0),
                inversion_bateria_MEUR=round(bat, 1),
                bateria_anual_MEUR=round(bat / annuity(v["tasa"], v["bat_vida"]) + bat * v["bat_om"] / 100, 1),
                inversion_posicion_trafos_MEUR=round(pos_trafo, 1),
                inversion_grupos_MEUR=round(grupos, 1),
                ahorro_grupos_bloque_flexible_MEUR=round(ahorro_grupos, 1),
                inversion_electrica_MEUR=round(pos_trafo + grupos + bat, 1),
                inversion_fv_opcional_MEUR=round(0.25 * MW * v["fv"], 1),
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
print(df[(df.carga_x == 1.0) & (df.acceso == "REE")][["linea", "opcion", "emplazamientos", "cpd_MW_red",
      "inversion_bateria_MEUR", "inversion_electrica_MEUR", "ahorro_grupos_bloque_flexible_MEUR", "inversion_cpd_MEUR",
      "ingreso_adif_MEUR_año", "valor_adelanto_MEUR"]].to_string(index=False))
