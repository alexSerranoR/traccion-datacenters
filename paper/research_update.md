# Research update (15 October – 16 November 2026)

Sources consulted on 16 November 2026. Each entry states what changes for the paper.

## 1. Data-centre Royal Decree (mandated by RDL 7/2026)

**Status: not yet approved.** The Consejo de Estado issued a unanimous favourable opinion on 6 November 2026; the Government
targets the Council of Ministers of 17 or 24 November 2026, before the general election of 29 November 2026. Not in the BOE
at the time of writing. The paper must describe it as a draft and cite both versions.

Revised draft sent to the Consejo de Estado (unofficial text, law-firm analysis of 3 November 2026) versus the
August 2026 public-hearing draft:

| Topic | August draft | Revised draft |
|---|---|---|
| Scope | ≥ 1 MW of access capacity | **≥ 10 MW** |
| Transitional PUE / WUE | 1.15 / 0.1 L/kWh | **1.25** / 0.1 L/kWh (1.25 until 31/12/2031 for access contracts signed before 1/1/2029) |
| Additionality | 80 %, plants ≤ 18 months old, PPA ≥ 10 years | 80 %, **≤ 36 months**, **PPA ≥ 6 years**; storage, repowering and uncontracted PV admitted |
| Hourly matching | 80 % every hour | 80 % every hour; **storage discharge counted as renewable** |
| Flexibility | not recognised | **New transitional regime: centres that join the automatic power reduction system (SRAP) get a reduced hourly-matching target (60 % in P1 until 2028; 70 % in P1 and 60 % in P2 from 2029) for five years, if in operation before 31/12/2030** |
| Surcharges | tiers 10/30/50 % by share of failing hours | five tiers 10–100 % on the monthly mean of hourly percentages; additionality surcharges 100–500 % |
| Ministerial discretion | Ministry could change the 80 % threshold | Consejo de Estado asks to remove that discretion and to define sanctions and permit loss more precisely |

Consequences for the paper:
- The flexibility that yields power to the train is now explicitly rewarded (SRAP regime). This strengthens the central thesis.
- All but the smallest modelled sites exceed 10 MW; the model already ignores sites below 10 MW in the financial results.
- The model keeps PUE = 1.15 (within the sensitivity range 1.10–1.30); the revised cap of 1.25 is stated in the text.
- Storage counting towards hourly matching makes the "4-hour shifting battery" row of `results/renovable_horaria.csv` directly relevant.

Sources:
- El Periódico de la Ingeniería, 6/10/2026: https://elperiodicodelaingenieria.es/el-gobierno-acelera-el-decreto-de-centros-de-datos-para-aprobarlo-antes-de-las-elecciones/
- Mundiario, 7/11/2026 (Consejo de Estado opinion): https://www.mundiario.com/economia/decision-que-permite-gobierno-acelerar-decreto-centros-datos/20261107122123451488.html
- Ashurst, 3/11/2026 (changes in the revised draft): https://www.ashurstperkinscoie.com/es-es/insights/data-centres-what-has-changed-in-the-draft-royal-decree/
- Public-hearing draft (MITECO): https://www.miteco.gob.es/content/dam/miteco/es/energia/files-1/es-ES/Participacion/Documents/anexos/aeip-rd-cpds-sostenibles/PRD%20CPDs%20audiencia%20publica.pdf

## 2. Grid access (CNMC / REE)

- REE map of 1 October 2026: 18.52 GW of demand access granted on the transmission grid, of which 6.33 GW (34 %) to data centres
  (none in service) and 3.55 GW to railway infrastructure. No newer map found.
  https://www.pv-magazine.es/2026/10/02/red-electrica-asigna-633-gw-de-acceso-a-centros-de-datos-el-34-de-los-1852-gw-otorgados-a-la-demanda/
- REE (February 2026): about one in four transmission nodes can still take new demand; 11.8 GW of demand permits granted since 2022, none in operation.
  https://www.democrata.es/economia/ree-senala-que-uno-de-cada-cuatro-nudos-de-su-red-de-transporte-aun-admite-nueva-demanda/
- Flexible access (CNMC resolution of 31/7/2026, in force 1/9/2026): no change found since October.
- No change: the paper keeps the two scenarios ("today" and "with reform").

## 3. Railway sector: safety and security context in 2026

- **Adamuz (Córdoba), 18 January 2026**, Madrid–Seville high-speed line: derailment of an Iryo train and collision with a Renfe Alvia;
  46 dead, 292 injured. Preliminary findings point to a rail break at a defective weld and to deficient inspection and alarm thresholds.
  Line closed until 17 February 2026. https://en.wikipedia.org/wiki/2026_Adamuz_rail_disaster
- **Urda (Toledo), 28 October 2026**, Madrid–Seville high-speed line, km 118: after a computer failure of the LZB signalling system on a 64 km
  section, trains were authorised to move under the degraded manual mode; an AVE ran into a stationary Iryo train; 69 dead, more than 200 injured.
  Preliminary cause: human error in the control centre during degraded operation; investigation open. Unions report understaffing in the control centre.
  High-speed services Madrid–Andalusia suspended. https://en.wikipedia.org/wiki/2026_Toledo_train_collision
- **Institutional consequences**: the Minister of Transport resigned on 3 November 2026 and the president of Adif left on 4 November; the acting minister
  announced a 50 % increase in rail investment over five years (to nearly €19 billion). Strike called at Adif for 17 November.
  https://www.infobae.com/espana/2026/11/04/reacciones-a-la-dimision-de-oscar-puente-en-directo-ultima-hora-del-accidente-de-urda-y-las-elecciones-generales-en-espana-el-29-n/
- **Cable theft**: repeated copper thefts disrupted high-speed traffic in 2026 (three in three days between Toledo and Ciudad Real in July; Barcelona–Girona in July;
  Madrid–Barcelona line in Zaragoza province on 4 November 2026).
  https://metropoliabierta.elespanol.com/movilidad/20261104/retrasos-alta-velocidad-madrid-barcelona-robo-cable/1003742809026_0.html
  https://www.elespanol.com/eldigitalcastillalamancha/sociedad/sucesos/20260709/adif-reforzara-vigilancia-toledo-ciudad-real-sufrir-robos-cable-linea-tren-solo-dias/1003744315426_0.html
- **Cyber incident, September 2026**: Adif and Renfe acknowledged on 25 September 2026 an intrusion into corporate (IT) systems with exfiltration of about 500 GB
  of user data, reportedly AI-assisted. No effect on operational systems or traffic was reported.
  https://www.moncloa.com/2026/09/28/ciberataque-adif-renfe-150-millones-datos-3439250/

Consequences for the paper:
- Both accidents happened on the Madrid–Seville line, one of the two case studies, and neither involved the traction power supply.
  They nevertheless set the bar: any proposal that adds a third party next to railway infrastructure must demonstrate that it adds **no** new failure mode
  to railway operation, including in degraded modes. The security section is written around that requirement (electrical, physical and cyber independence).
- The Urda sequence (failure of an automatic system followed by unsafe manual fallback) motivates a design rule: the train-priority limiter must fail safe
  (loss of measurement or communication → data centre curtails), with no manual override that can raise the data-centre limit.
- The September 2026 breach motivates strict IT/OT separation and a one-way measurement interface.
- The investment cycle announced after Urda prioritises safety and maintenance; the proposal must be revenue-positive and resource-neutral for the infrastructure manager.
- Results were computed on the October 2026 timetable (before the suspension of Madrid–Andalusia services); stated as such in Methods.

## 4. Not verified in this update (network limits)

- Text of the decree if approved on 17 or 24 November 2026: check the BOE before submission.
- Newer REE monthly capacity maps (November 2026).
- Adif tenders on substations/storage after October 2026.
