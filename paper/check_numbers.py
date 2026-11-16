"""Single source of truth for every model figure quoted in the paper.

  python paper/check_numbers.py --write   regenerates paper/numbers.tex (macros) and paper/tables.tex from results/*.csv
  python paper/check_numbers.py           checks that both files match results/ and that every macro used in the
                                          .tex sources exists (exit code 1 otherwise)

The manuscript never types a model result by hand: it uses the macros defined here.
"""
import pathlib, re, sys
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES, P = ROOT / "results", ROOT / "paper"
cap = pd.read_csv(RES / "capacidad.csv"); arq = pd.read_csv(RES / "arquitectura.csv")
fin = pd.read_csv(RES / "finanzas.csv"); sim = pd.read_csv(RES / "simulacion.csv")
ren = pd.read_csv(RES / "renovable_horaria.csv")
L = {"MZB": "mzb", "MS": "ms"}
M = {}


def put(name, value, dec=0):
    s = f"{value:,.{dec}f}"
    M[name] = s


def tot(line, acc, f):
    return cap[(cap.linea == line) & (cap.acceso == acc) & (cap.carga_x == f)]


for line, p in L.items():
    s = sim[(sim.linea == line) & sim.escenario.str.contains("Iryo")].iloc[0]
    put(p + "Trains", s.trenes); put(p + "TrainKm", s.tren_km); put(p + "Energy", s.energia_red_MWh)
    put(p + "Specific", s.kWh_tren_km, 1); put(p + "MeanMW", s.potencia_media_linea_MW, 1); put(p + "PeakMW", s.pico_linea_MW, 0)
    put(p + "Regen", s.energia_red_MWh and s.regenerada_MWh, 0); put(p + "Back", s.devuelta_red_MWh, 0)
    put(p + "BackPct", 100 * s.devuelta_red_MWh / s.energia_red_MWh, 1); put(p + "IdleMin", s.minutos_sin_trenes)
    b = tot(line, "REE", 1.0); t = b.sum(numeric_only=True)
    put(p + "Subs", len(b)); put(p + "Access", t.acceso_MW); put(p + "UsePct", 100 * s.potencia_media_linea_MW / t.acceso_MW, 0)
    put(p + "AccessMin", b.acceso_MW.min()); put(p + "AccessMax", b.acceso_MW.max()); put(p + "AccessMed", b.acceso_MW.median())
    put(p + "Tight", int((b.pico_min > 0.9 * b.acceso_MW).sum()))
    for col, n in (("firme", "Firm"), ("firme_flex", "FirmFlex"), ("sin_bateria", "NoBat"), ("flexible", "Flex"), ("bateria_opt", "Bat")):
        put(p + n, t[col])
    put(p + "BatMW", t.batopt_MW); put(p + "BatMWh", t.batopt_MWh); put(p + "BatCost", t.batopt_MEUR)
    put(p + "FlexCurt", b.flex_recorte_pct.max(), 1)
    g = tot(line, "REE", 1.5).sum(numeric_only=True)
    for col, n in (("firme", "FirmGrowth"), ("sin_bateria", "NoBatGrowth"), ("flexible", "FlexGrowth"), ("bateria_opt", "BatGrowth")):
        put(p + n, g[col])
    x = tot(line, "trafo", 1.0).sum(numeric_only=True)
    put(p + "AccessTrafo", x.acceso_MW); put(p + "FirmTrafo", x.firme); put(p + "FlexTrafo", x.flexible); put(p + "BatTrafo", x.bateria_opt)
    a = arq[arq.linea == line]; at = a.sum(numeric_only=True)
    put(p + "GapS", at.hueco_min_1s_MW); put(p + "GapMin", at.hueco_min_1min_MW); put(p + "GapQ", at.hueco_min_15min_MW)
    put(p + "NoneSust", at.cpd_N1_vecina_MW); put(p + "NoneCut", at.recorte_N1_MW); put(p + "NoneCutPct", 100 * at.recorte_N1_MW / at.cpd_bateria_MW, 0)
    put(p + "NoneCutMed", a.recorte_N1_pct.median(), 0)
    put(p + "BatMinMWh", at.bat_MWh_minima); put(p + "CycMin", a.bat_ciclos_dia_minima.median(), 1); put(p + "Cyc", a.bat_ciclos_dia.median(), 1)
    put(p + "RampS", a.rampa_1s_MW.max(), 0); put(p + "RampSMed", a.rampa_1s_MW.median(), 0); put(p + "RampTen", a.rampa_10s_MW.max(), 0)
    put(p + "PeakS", a.pico_tren_1s_MW.max(), 0)
    put(p + "VufMin", a.desequilibrio_pct.min(), 1); put(p + "VufMax", a.desequilibrio_pct.max(), 1); put(p + "VufWeak", a.desequilibrio_nudo_debil_pct.max(), 1)
    f = fin[(fin.linea == line) & (fin.acceso == "REE") & (fin.carga_x == 1.0)].set_index("opcion")
    o = f.loc["bateria_opt"]
    put(p + "FinSites", o.emplazamientos); put(p + "FinMW", o.cpd_MW_red); put(p + "FinIT", o.cpd_MW_IT); put(p + "FinGWh", o.energia_GWh_año)
    put(p + "CapexDC", o.inversion_cpd_MEUR); put(p + "CapexBay", o.inversion_posicion_trafos_MEUR); put(p + "CapexBat", o.inversion_bateria_MEUR)
    put(p + "CapexGen", o.inversion_grupos_MEUR); put(p + "CapexEl", o.inversion_electrica_MEUR); put(p + "GenSaved", o.ahorro_grupos_bloque_flexible_MEUR)
    put(p + "CapexPV", o.inversion_fv_opcional_MEUR); put(p + "ElPct", 100 * o.inversion_electrica_MEUR / o.inversion_cpd_MEUR, 0)
    put(p + "Fee", o.ingreso_adif_MEUR_año, 1); put(p + "FeeLow", o.ingreso_adif_bajo_MEUR_año, 1); put(p + "FeeHigh", o.ingreso_adif_alto_MEUR_año, 1)
    put(p + "FeeNPV", o.ingreso_adif_VAN_MEUR); put(p + "FeeFirm", f.loc["firme"].ingreso_adif_MEUR_año, 1); put(p + "FeeFlex", f.loc["flexible"].ingreso_adif_MEUR_año, 1)
    put(p + "BatAnnual", o.bateria_anual_MEUR, 1)

an = arq[arq.se == "Anchuelo"].iloc[0]; ac = cap[(cap.se == "Anchuelo") & (cap.acceso == "REE") & (cap.carga_x == 1.0)].iloc[0]
put("anAccess", ac.acceso_MW); put("anLimit", an.limite_MW, 1); put("anDC", an.cpd_bateria_MW); put("anBatMW", an.bat_MW, 1); put("anBatMWh", an.bat_MWh, 1)
put("anNone", an.cpd_N1_vecina_MW, 1); put("anCut", an.recorte_N1_MW, 1); put("anCutPct", an.recorte_N1_pct); put("anMean", ac.media, 1)
put("anUse", ac.uso_medio_pct, 1); put("anPeak", ac.pico_min, 1); put("anPeakS", an.pico_tren_1s_MW, 1); put("anGapMin", an.hueco_min_1min_MW, 1)
put("anGapQ", an.hueco_min_15min_MW, 1); put("anFirm", ac.firme, 1); put("anBridgeMin", 60 * an.bat_MWh / an.bat_MW, 0)
put("anFirmBlock", 0.7 * an.cpd_bateria_MW, 0)
put("allTight", int(M["mzbTight"]) + int(M["msTight"]))


def rr(lim, bat, flex):
    return ren[(ren.limite_horas_fallo_pct == lim) & (ren.bateria_h == bat) & (ren.flexible == flex)].iloc[0]


for tag, r in (("Flat", rr(5, 0, False)), ("Flex", rr(5, 0, True)), ("Sto", rr(5, 4, False)), ("Both", rr(5, 4, True)),
               ("FlatLoose", rr(20, 0, False)), ("FlexLoose", rr(20, 0, True))):
    put("res" + tag + "Wind", r.eolica_MW, 2); put("res" + tag + "PV", r.fv_MW, 2); put("res" + tag + "Tot", r.eolica_MW + r.fv_MW, 2)
    put("res" + tag + "Ratio", r.renovable_sobre_consumo, 2); put("res" + tag + "Curt", r.recorte_pct, 1); put("res" + tag + "Cost", r.coste_neto_EUR_MWh_cpd, 0)
flexval = rr(5, 0, False).coste_neto_EUR_MWh_cpd - rr(5, 0, True).coste_neto_EUR_MWh_cpd
put("resFlexValue", flexval, 1)
put("resFlexValueMzb", flexval * float(M["mzbFinGWh"].replace(",", "")) / 1000, 0)

numbers = "% Generated by paper/check_numbers.py --write from results/*.csv. Do not edit by hand.\n" + \
          "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in M.items())

# ---------------- tables ----------------
EN = {"Añover": "A\\~nover", "Peñalba": "Pe\\~nalba", "Rueda de Jalón": "Rueda de Jal\\'on", "Venta La Inés": "Venta La In\\'es",
      "Lora del Río": "Lora del R\\'{\\i}o"}
rows = []
for line in L:
    b = tot(line, "REE", 1.0).reset_index(drop=True); a = arq[arq.linea == line].reset_index(drop=True)
    rows.append(f"\\multicolumn{{11}}{{l}}{{\\textit{{{'Madrid--Barcelona' if line == 'MZB' else 'Madrid--Seville'}}}}}\\\\")
    for i in range(len(b)):
        r, q = b.iloc[i], a.iloc[i]
        rows.append(f"{EN.get(r.se, r.se)} & {q.tension_kV} & {r.acceso_MW:.0f} & {r.media:.1f} & {r.pico_min:.1f} & {r.pico_N1:.1f} & "
                    f"{r.firme:.1f} & {r.sin_bateria:.1f} & {r.flexible:.1f} & {r.bateria_opt:.0f} & {r.batopt_MW:.1f}/{r.batopt_MWh:.1f}\\\\")
    t = b.sum(numeric_only=True)
    rows.append(f"\\textbf{{Total}} & & \\textbf{{{t.acceso_MW:.0f}}} & \\textbf{{{t.media:.1f}}} & & & \\textbf{{{t.firme:.1f}}} & \\textbf{{{t.sin_bateria:.1f}}} & "
                f"\\textbf{{{t.flexible:.1f}}} & \\textbf{{{t.bateria_opt:.0f}}} & \\textbf{{{t.batopt_MW:.1f}/{t.batopt_MWh:.1f}}}\\\\[2pt]")
tables = "% Generated by paper/check_numbers.py --write from results/*.csv. Do not edit by hand.\n" + \
         "\\newcommand{\\substationrows}{%\n" + "\n".join(rows) + "}\n"

if "--write" in sys.argv:
    (P / "numbers.tex").write_text(numbers, encoding="utf-8"); (P / "tables.tex").write_text(tables, encoding="utf-8")
    print(f"written: {len(M)} macros"); sys.exit(0)

ok = True
for name, txt in (("numbers.tex", numbers), ("tables.tex", tables)):
    if not (P / name).exists() or (P / name).read_text(encoding="utf-8") != txt:
        print(f"MISMATCH: paper/{name} does not match results/. Run with --write."); ok = False
src = "".join(f.read_text(encoding="utf-8") for f in P.glob("*.tex") if f.name not in ("numbers.tex", "tables.tex"))
used = set(re.findall(r"\\((?:mzb|ms|an|res|all)[A-Z][A-Za-z]*)", src))
missing = sorted(u for u in used if u not in M)
if missing: print("UNDEFINED macros used in the text:", missing); ok = False
# hand-typed model results are not allowed: flag headline values typed literally
for lit in (M["mzbBat"], M["msBat"], M["mzbFirm"], M["msFirm"], M["mzbGapQ"], M["mzbCapexEl"], M["msCapexEl"]):
    for m in re.finditer(rf"(?<![\d.,]){re.escape(lit)}(?![\d.,])\s*(MW|M\\texteuro)", src):
        print("LITERAL model value typed by hand:", m.group(0)); ok = False
print(f"{len(M)} macros defined, {len(used)} used in the text;", "OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
