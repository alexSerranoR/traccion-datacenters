"""Generates every figure of the paper from results/*.csv (vector PDF, uniform style, English labels).
Usage:  python paper/figures.py      -> paper/figures/*.pdf   (not versioned; rebuilt before compiling)
"""
import pathlib
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES, OUT = ROOT / "results", ROOT / "paper" / "figures"
OUT.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.family": "serif", "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8.5,
    "legend.fontsize": 7, "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.5,
    "lines.linewidth": 1.0, "pdf.fonttype": 42, "savefig.bbox": "tight", "savefig.pad_inches": 0.02})
C = dict(train="#3b4a5a", dc="#1f77b4", flex="#6baed6", bat="#e6862a", firm="#2a7f62", lim="#b22222", grey="#9aa0a6")
NAME = {"MZB": "Madrid–Barcelona", "MS": "Madrid–Seville"}
W1, W2 = 3.5, 7.2          # single / double column width (in)

cap = pd.read_csv(RES / "capacidad.csv")
arq = pd.read_csv(RES / "arquitectura.csv")
base = cap[(cap.acceso == "REE") & (cap.carga_x == 1.0)]


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf"); plt.close(fig)


# ---- Fig. 1: daily traction load of both lines and of one substation against its granted access
def fig_profile():
    fig, ax = plt.subplots(1, 2, figsize=(W2, 2.3))
    h = np.arange(1440) / 60
    for line, ls in (("MZB", "-"), ("MS", "--")):
        m = pd.read_csv(RES / f"perfil_minuto_{line}.csv").drop(columns="minuto")
        tot = m.sum(axis=1).rolling(15, center=True, min_periods=1).mean()
        ax[0].plot(h, tot, ls, color=C["train"], label=f"{NAME[line]} (15-min mean)")
    ax[0].set(xlabel="Hour of day", ylabel="Traction demand of the line (MW)", xlim=(0, 24), xticks=range(0, 25, 4),
              title="(a) Whole line")
    ax[0].legend(frameon=False, loc="upper left")
    m = pd.read_csv(RES / "perfil_minuto_MZB.csv"); se = "Anchuelo"
    acc = float(base[(base.linea == "MZB") & (base.se == se)].acceso_MW.iloc[0])
    ax[1].fill_between(h, m[se], color=C["train"], lw=0, alpha=0.85, label="Traction load (1-min mean)")
    ax[1].axhline(acc, color=C["lim"], lw=0.9, label=f"Granted access ({acc:.0f} MW)")
    ax[1].axhline(0.9 * acc, color=C["lim"], lw=0.7, ls=":", label="Joint limit (90 %)")
    ax[1].set(xlabel="Hour of day", ylabel="Power at the substation (MW)", xlim=(0, 24), xticks=range(0, 25, 4),
              ylim=(0, acc * 1.25), title=f"(b) {se} substation (400 kV)")
    ax[1].legend(frameon=False, loc="upper left", ncol=1)
    save(fig, "fig_profile")


# ---- Fig. 2: granted access, peaks and mean use per substation
def fig_substations():
    fig, ax = plt.subplots(2, 1, figsize=(W2, 3.9))
    for a, line in zip(ax, ("MZB", "MS")):
        d = base[base.linea == line]; x = np.arange(len(d))
        a.bar(x, d.acceso_MW, 0.72, color="#dfe3e8", label="Granted access capacity")
        a.bar(x - 0.18, d.pico_N1, 0.3, color=C["bat"], label="Peak with neighbour out (N-1), 1 min")
        a.bar(x + 0.18, d.pico_min, 0.3, color=C["train"], label="Peak in normal operation, 1 min")
        a.plot(x, d.media, "o", ms=3, color=C["lim"], label="Daily mean")
        a.set_xticks(x); a.set_xticklabels(d.se, rotation=30, ha="right")
        a.set(ylabel="MW", title=f"{NAME[line]} ({len(d)} substations)"); a.grid(axis="x", visible=False)
    ax[0].legend(frameon=False, ncol=2, loc="upper right")
    fig.tight_layout(); save(fig, "fig_substations")


# ---- Fig. 3: hosting capacity by option and line
def fig_capacity():
    opts = [("firme", "Firm\n(today)", C["firm"]), ("firme_flex", "Firm +\n30 % flexible", "#74c2a4"),
            ("sin_bateria", "Shared,\nno storage", C["dc"]), ("flexible", "Shared +\n30 % flexible", C["flex"]),
            ("bateria_opt", "Shared +\nbattery", C["bat"])]
    fig, ax = plt.subplots(figsize=(5.2, 2.6)); w = 0.38
    for i, line in enumerate(("MZB", "MS")):
        t = base[base.linea == line][[o for o, _, _ in opts]].sum()
        x = np.arange(len(opts)) + (i - 0.5) * w
        b = ax.bar(x, t.values, w, color=[c for _, _, c in opts], edgecolor="k", lw=0.4, hatch="" if i == 0 else "///")
        for xi, v in zip(x, t.values): ax.text(xi, v + 6, f"{v:.0f}", ha="center", va="bottom", fontsize=6)
    ax.set_xticks(range(len(opts))); ax.set_xticklabels([l for _, l, _ in opts])
    ax.set(ylabel="Data-centre capacity (MW)"); ax.grid(axis="x", visible=False)
    ax.bar(0, 0, color="w", edgecolor="k", lw=0.4, label=NAME["MZB"]); ax.bar(0, 0, color="w", edgecolor="k", lw=0.4, hatch="///", label=NAME["MS"])
    ax.axvline(1.5, color=C["grey"], lw=0.6, ls="--")
    ax.text(0.5, ax.get_ylim()[1] * 0.93, "current rules", ha="center", fontsize=6.5, style="italic")
    ax.text(3.0, ax.get_ylim()[1] * 0.93, "shared access permit", ha="center", fontsize=6.5, style="italic")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.88))
    save(fig, "fig_capacity")


# ---- Fig. 4: battery sizing curves (line totals) and optimum
def fig_battery():
    cb = pd.read_csv(RES / "curvas_bateria.csv"); cb = cb[cb.acceso == "REE"]
    fig, ax = plt.subplots(1, 2, figsize=(W2, 2.3))
    for line, ls in (("MZB", "-"), ("MS", "--")):
        d = cb[cb.linea == line]
        for se, g in d.groupby("subestacion"):
            ax[0].plot(g.cpd_MW, g.bateria_MWh, ls, color=C["grey"], lw=0.5, alpha=0.7)
        o = base[base.linea == line]
        ax[0].plot(o.bateria_opt, o.batopt_MWh, "o" if line == "MZB" else "s", ms=3, color=C["bat"], mec="k", mew=0.3,
                   label=f"Selected size, {NAME[line]}")
    ax[0].set(xlabel="Data-centre power at the site (MW)", ylabel="Battery energy required (MWh)", ylim=(0, 45), xlim=(0, 60),
              title="(a) Storage needed per substation")
    ax[0].legend(frameon=False, loc="upper left")
    x = np.arange(2); w = 0.36
    t = arq.groupby("linea")[["bat_MWh_minima", "bat_MWh"]].sum().loc[["MZB", "MS"]]
    cy = arq.groupby("linea")[["bat_ciclos_dia_minima", "bat_ciclos_dia"]].median().loc[["MZB", "MS"]]
    ax[1].bar(x - w / 2, t.bat_MWh_minima, w, color=C["grey"], label="Minimum energy")
    ax[1].bar(x + w / 2, t.bat_MWh, w, color=C["bat"], label="Limited to 2C (model)")
    for i in range(2):
        ax[1].text(x[i] - w / 2, t.bat_MWh_minima.iloc[i] + 3, f"{cy.bat_ciclos_dia_minima.iloc[i]:.1f} cycles/day", ha="center", fontsize=6)
        ax[1].text(x[i] + w / 2, t.bat_MWh.iloc[i] + 3, f"{cy.bat_ciclos_dia.iloc[i]:.1f} cycles/day", ha="center", fontsize=6)
    ax[1].set_xticks(x); ax[1].set_xticklabels([NAME["MZB"], NAME["MS"]]); ax[1].grid(axis="x", visible=False)
    ax[1].set(ylabel="Installed battery energy (MWh)", title="(b) Line totals and median cycling"); ax[1].legend(frameon=False)
    save(fig, "fig_battery")


# ---- Fig. 5: effect of the averaging window used to enforce the joint limit
def fig_window():
    t = arq.groupby("linea")[["hueco_min_1s_MW", "hueco_min_1min_MW", "hueco_min_15min_MW"]].sum().loc[["MZB", "MS"]]
    fig, ax = plt.subplots(figsize=(W1, 2.2)); x = np.arange(3); w = 0.38
    for i, line in enumerate(("MZB", "MS")):
        v = t.loc[line].values
        ax.bar(x + (i - 0.5) * w, v, w, color=C["dc"] if i == 0 else C["flex"], edgecolor="k", lw=0.4, label=NAME[line])
        for xi, vi in zip(x + (i - 0.5) * w, v): ax.text(xi, vi + 5, f"{vi:.0f}", ha="center", fontsize=6)
    ax.set_xticks(x); ax.set_xticklabels(["1 s", "1 min", "15 min"]); ax.grid(axis="x", visible=False)
    ax.set(xlabel="Averaging window of the joint limit", ylabel="Capacity without storage (MW)"); ax.legend(frameon=False, loc="upper left")
    save(fig, "fig_window")


# ---- Fig. 6: N-1 curtailment per substation
def fig_n1():
    fig, ax = plt.subplots(figsize=(W2, 2.3))
    d = arq.copy(); x = np.arange(len(d)); n = (d.linea == "MZB").sum()
    ax.bar(x, d.cpd_N1_vecina_MW, color=C["dc"], label="Sustained with a neighbouring substation out")
    ax.bar(x, d.recorte_N1_MW, bottom=d.cpd_N1_vecina_MW, color=C["bat"], label="Curtailed (flexible block)")
    ax.plot(x, 0.7 * d.cpd_bateria_MW, "_", color="k", ms=7, label="Firm block (70 %)")
    ax.axvline(n - 0.5, color=C["grey"], lw=0.6, ls="--")
    ax.set_xticks(x); ax.set_xticklabels(d.se, rotation=40, ha="right"); ax.grid(axis="x", visible=False)
    ax.set(ylabel="Data-centre power (MW)"); ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.18))
    save(fig, "fig_n1")


# ---- Fig. 7: sensitivity to access scenario and traffic growth
def fig_sensitivity():
    fig, ax = plt.subplots(1, 2, figsize=(W2, 2.3), sharey=True)
    sc = ["30", "REE", "60", "trafo", "120"]; lab = ["30 MW", "Granted\n(REE)", "60 MW", "Transformer\nrating", "120 MW"]
    for a, line in zip(ax, ("MZB", "MS")):
        for f, ls in ((1.0, "-"), (1.5, "--")):
            t = cap[(cap.linea == line) & (cap.carga_x == f)].groupby("acceso")[["firme", "flexible", "bateria_opt"]].sum().loc[sc]
            for col, c, l in (("firme", C["firm"], "Firm"), ("flexible", C["dc"], "Shared + flexible"), ("bateria_opt", C["bat"], "Shared + battery")):
                a.plot(range(5), t[col], ls, marker="o", ms=2.5, color=c, label=f"{l}, traffic ×{f:g}")
        a.set_xticks(range(5)); a.set_xticklabels(lab); a.set(title=NAME[line], xlabel="Access capacity per substation")
    ax[0].set(ylabel="Data-centre capacity (MW)"); ax[0].legend(frameon=False, ncol=1, loc="upper left", fontsize=6)
    save(fig, "fig_sensitivity")


# ---- Fig. 8: renewable portfolio needed for 80 % hourly matching
def fig_renewable():
    r = pd.read_csv(RES / "renovable_horaria.csv"); r = r[r.limite_horas_fallo_pct == 5]
    lab = {(0, False): "Flat load", (0, True): "Flexible\nblock", (4, False): "4 h storage", (4, True): "Flexible +\n4 h storage"}
    r = r[[(b, f) in lab for b, f in zip(r.bateria_h, r.flexible)]]
    fig, ax = plt.subplots(figsize=(W1, 2.3)); x = np.arange(len(r))
    ax.bar(x, r.eolica_MW, 0.6, color="#5b8db8", label="Wind")
    ax.bar(x, r.fv_MW, 0.6, bottom=r.eolica_MW, color="#f2c14e", label="Solar PV")
    ax2 = ax.twinx(); ax2.plot(x, r.coste_neto_EUR_MWh_cpd, "D-", color=C["lim"], ms=3, label="Net cost"); ax2.grid(False)
    ax2.spines["right"].set_visible(True); ax2.set(ylabel="Net cost (EUR/MWh consumed)", ylim=(0, 80))
    ax.set_xticks(x); ax.set_xticklabels([lab[(b, f)] for b, f in zip(r.bateria_h, r.flexible)]); ax.grid(axis="x", visible=False)
    ax.set(ylabel="New renewable capacity\n(MW per MW of data centre)", ylim=(0, 11))
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, frameon=False, ncol=3, loc="upper center")
    save(fig, "fig_renewable")


# ---- Fig. 9: single-line diagram of the proposed installation (schematic, drawn by code)
def fig_sld():
    fig, ax = plt.subplots(figsize=(W2, 4.2)); ax.axis("off"); ax.set(xlim=(0, 100), ylim=(0, 62))
    def box(x, y, w, h, t, fc="#eef2f6", ec="k", fs=6.5):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=0.8", fc=fc, ec=ec, lw=0.6))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs)
    def line(xs, ys, **k): ax.plot(xs, ys, color=k.pop("color", "k"), lw=k.pop("lw", 0.8), **k)
    def trafo(x, y):
        for dy in (0.9, -0.9): ax.add_patch(plt.Circle((x, y + dy), 1.4, fc="w", ec="k", lw=0.6))
    def brk(x, y): ax.add_patch(plt.Rectangle((x - 0.8, y - 0.8), 1.6, 1.6, fc="w", ec="k", lw=0.6))
    # transmission busbar
    line([4, 96], [56, 56], lw=2.2); ax.text(4, 58, "Transmission substation busbar, 400 (220) kV — TSO", fontsize=7, weight="bold")
    # railway bay
    line([16, 16], [56, 44]); brk(16, 51); trafo(12, 41); trafo(20, 41); line([16, 12], [44, 44]); line([16, 20], [44, 44])
    line([12, 12], [44, 43.3]); line([20, 20], [44, 43.3]); line([12, 12], [38.7, 34]); line([20, 20], [38.7, 34])
    box(6, 28, 20, 6, "2×25 kV catenary\n(single-phase traction load)", fc="#e9edf1")
    ax.text(16, 47.3, "Railway bay", fontsize=6.5, ha="center", bbox=dict(fc="w", ec="none", pad=0.5))
    ax.text(1.5, 41, "2 × 60 MVA", fontsize=6, rotation=90, va="center")
    # measurement and joint limit
    box(30, 47.5, 18, 5.5, "Joint limit:\n$P_{train}+P_{DC}\\leq 0.9\\,C$", fc="#fbe9e7", ec=C["lim"])
    line([17, 30], [51, 50.5], color=C["lim"], ls=":"); line([48, 61.2], [50.5, 51], color=C["lim"], ls=":")
    ax.text(23.5, 52.2, "P meas.", fontsize=5.5, color=C["lim"], ha="center"); ax.text(54.5, 52.2, "trip", fontsize=5.5, color=C["lim"], ha="center")
    # data-centre bay
    line([62, 62], [56, 46]); brk(62, 51); line([56, 68], [46, 46]); trafo(56, 43); trafo(68, 43); line([56, 56], [46, 45.3]); line([68, 68], [46, 45.3])
    line([56, 56], [40.7, 37]); line([68, 68], [40.7, 37])
    ax.text(62, 48, "Data-centre bay", fontsize=6.5, ha="center", bbox=dict(fc="w", ec="none", pad=0.5))
    ax.text(73, 43, "2 × 100 %\n400(220)/30 kV", fontsize=6, va="center")
    line([40, 96], [37, 37], lw=1.6); ax.text(96, 38.3, "30 kV ring", fontsize=6.5, ha="right")
    for x in (45, 58, 72, 86): line([x, x], [37, 31]); brk(x, 34)
    box(38, 22, 14, 9, "BESS\ngrid-forming\n(≈2C, 30 min)", fc="#fdebd5", ec=C["bat"])
    box(38, 11, 14, 6, "Optional PV\n(DC-coupled)", fc="#fff7d6"); line([45, 45], [22, 17])
    box(53, 22, 11, 9, "MV gensets\nN+1", fc="#eeeeee")
    box(66, 22, 13, 9, "Firm block\n(70 %): UPS +\ngensets, Tier III", fc="#dbe9f6", ec=C["dc"])
    box(81, 22, 14, 9, "Flexible block\n(30 %): no gensets,\ncurtailable", fc="#e6f2fb", ec=C["flex"])
    box(38, 2, 57, 5.5, "EMS: battery (ms–s)  →  GPU power capping (s)  →  job pausing / migration (min)", fc="#f4f4f4", fs=6.5)
    line([88, 88], [22, 7.5], color=C["grey"], ls=":"); line([45, 45], [11, 7.5], color=C["grey"], ls=":")
    save(fig, "fig_sld")


# ---- Fig. 10: response timeline after loss of a neighbouring substation (graphical abstract of the control hierarchy)
def fig_timeline():
    se = arq[(arq.linea == "MZB") & (arq.se == "Anchuelo")].iloc[0]
    D, Dn1, Pb = se.cpd_bateria_MW, se.cpd_N1_vecina_MW, se.bat_MW
    mid = D - 0.5 * (D - Dn1)
    t = np.array([-60, 0, 5, 120, 600]); it = np.array([D, D, mid, Dn1, Dn1]); grid = np.array([D, Dn1, Dn1, Dn1, Dn1])
    fig, ax = plt.subplots(figsize=(W1, 2.2))
    ax.step(t, it, where="post", color=C["dc"], label="Data-centre load")
    ax.step(t, grid, where="post", color=C["lim"], ls="--", label="Power available from the grid")
    ax.fill_between(t, grid, it, step="post", color=C["bat"], alpha=0.5, label="Supplied by the battery")
    ax.set(xlabel="Time after the neighbouring substation trips (s)", ylabel="Power (MW)", xlim=(-60, 600), ylim=(Dn1 - 8, D + 6))
    ax.annotate("GPU capping", (5, mid), (60, D - 1), fontsize=6, arrowprops=dict(arrowstyle="-", lw=0.4))
    ax.annotate("jobs paused", (120, Dn1), (200, Dn1 + 3), fontsize=6, arrowprops=dict(arrowstyle="-", lw=0.4))
    ax.legend(frameon=False, loc="lower left", fontsize=6)
    save(fig, "fig_timeline")


if __name__ == "__main__":
    for f in (fig_profile, fig_substations, fig_capacity, fig_battery, fig_window, fig_n1, fig_sensitivity, fig_renewable, fig_sld, fig_timeline):
        f(); print("ok", f.__name__)
