# Paper notes

## How to build

```
python paper/check_numbers.py --write   # numbers.tex and tables.tex from results/*.csv
python paper/figures.py                 # paper/figures/*.pdf from results/*.csv
cd paper && latexmk -pdf main.tex       # main.pdf (not versioned)
python paper/check_numbers.py           # fails if any quoted figure differs from results/
```

Requirements: Python with pandas, numpy and matplotlib; TeX Live with `elsarticle`, `siunitx` and `xurl`.

## Files

| File | Content |
|---|---|
| `main.tex`, `sec_*.tex` | Manuscript (elsarticle, review layout) |
| `refs.bib` | 63 references |
| `numbers.tex`, `tables.tex` | Generated: every model result quoted in the text is a macro defined here |
| `figures.py` | Generates the 10 figures; `fig_sld` doubles as graphical abstract |
| `check_numbers.py` | Regenerates and checks the macros; flags headline values typed by hand |
| `research_update.md` | Developments from 15 October to 16 November 2026 |
| `cover_letter.tex` | Cover letter |

## Decisions

- **Language and template.** English; Elsevier `elsarticle`, numeric citations.
- **Target journal.** *Applied Energy* (first choice: energy systems, demand flexibility, storage, strong policy angle).
  Alternatives: *Energy* (same template) and *IEEE Transactions on Transportation Electrification* (would need IEEEtran,
  a shorter text and more weight on the traction model).
- **Authors.** The author block is generic on purpose (no personal data in the repository). Complete names, affiliations,
  CRediT statement and competing interests at submission.
- **Model run.** `python run_all.py` was re-run with the GTFS feed of 12 October 2026 (day simulated: 21 October 2026) and
  reproduced `results/` exactly (no differences in git). The paper uses `results/` as committed.
- **Numbers.** No model result is typed by hand. The prompt figures are reproduced: 516/512 MW granted; firm 35/174 MW;
  shared 70/227 MW; flexible 100/314 MW; battery 385 MW-161 MWh-103 M EUR / 417 MW-99 MWh-63 M EUR; window 70 to 234 MW;
  N-1 curtailment 71/385 and 57/417 MW; electrical cost 317/296 M EUR; 9.5 vs 6.75 MW of renewables per MW.
- **Battery wording.** Text says 15-20 min of discharge and 3-4 years of life for the minimum-energy battery and 6-8 years
  with the 2C limit (line-level arithmetic from `results/arquitectura.csv`), slightly more cautious than `docs/`.
- **PUE.** The model keeps 1.15; the revised draft decree relaxes the transitional cap to 1.25. Stated in the text.
- **Railway context of 2026.** Adamuz (January) and Urda (October), cable thefts and the September data breach are used as
  context and as the source of three design requirements (independence, fail-safe degraded modes, no added burden). The
  text states that none of them involved the traction power supply.
- **Security section.** Written at design level; no site-specific detail that could help an attacker.
- **Figures.** Not versioned (`paper/figures/` is in `.gitignore`); they are rebuilt by `figures.py`.

## Reference verification

- **Checked against Crossref or arXiv on 16 November 2026 (title, authors, journal, year match):** moraski2023, wierman2014,
  gonzalezgil2013, sengor2018, pilo2015 (volume and pages not returned, so omitted), krastev2016, masanet2020, liu2014,
  zhang2020, preger2020, khodaparastan2019, ratniyomchai2014, douglas2015, zheng2020, kour2020, lopez2015, sun2018,
  schmidt2019, rochard2000, gazafrudi2015, lindley1952, riepin2024, xu2024, colangelo2025, li2024.
- **URL opened and content read on 16 November 2026:** ashurst2026, mundiario2026, infobae2026, cable2026, cyber2026,
  adamuz2026, urda2026, ree2026nudos.
- **URL found by search, document not opened:** norris2025, nerc2025, entsoe2026, epri2024.
- **Carried over from `docs/` (checked when those documents were written):** BOE and CNMC references, REE documents,
  prd2026, cnmc2026ipn, dwarkasing2026.
- **Not checked online in this session (network limits): confirm before submission:** iea2025, lin2020, uptime2018, the
  ELI links of ley242013, rd11832020, ley382015, ley82011, ens2022, nis2, cer2022, and the standards (IEC 62443,
  IEC 62351, CLC/TS 50701, IEC TR 61000-3-13), which are cited by number without URL.
- **Dropped because they could not be verified:** two candidate references whose DOI did not resolve to the expected paper.

## Before submission

1. Check the BOE for the data-centre decree (Council of Ministers of 17 or 24 November 2026) and update Section 6.2,
   `research_update.md` and the two decree references.
2. Replace the two Wikipedia entries on the 2026 accidents by the official investigation reports when published.
3. Validate the simulated loads with measured substation load curves; update the limitations if data become available.
4. Complete authors, affiliations, CRediT, funding and the repository link in "Data availability".
5. Have a native speaker or the journal language service proofread the final text.
6. Switch `\documentclass` options if the journal asks for the final two-column layout.
