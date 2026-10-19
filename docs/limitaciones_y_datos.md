# Limitaciones y datos no públicos

El modelo se apoya en datos públicos (REE, CNMC, BOE, horarios abiertos de los operadores). Varios parámetros con
influencia notable en los resultados no se publican y se han **estimado**. Esta nota los recoge, indica su efecto
sobre los resultados y el parámetro del modelo al que afectan, ordenados por su peso en las conclusiones.

## 1. Subestaciones de tracción y explotación ferroviaria

| # | Dato no público | Efecto sobre los resultados | Parámetro del modelo |
|---|---|---|---|
| 1 | **Resolución temporal con la que se controla el límite de potencia** de cada posición (maxímetro cuartohorario, medias de 1 min o protección instantánea) y posibles límites físicos o contractuales inferiores a la capacidad de acceso | Es la hipótesis más influyente: sin batería, la capacidad para el CPD en Madrid–Barcelona pasa de 70 a 234 MW si el límite se evalúa con medias de 15 min en lugar de 1 min | `analysis.py` (medias de 1 min) y ventana de `arquitectura.py` |
| 2 | **Curva de carga cuartohoraria real** de cada subestación y su energía anual | Impide validar la simulación. En 8 subestaciones el pico simulado supera el 90 % del acceso concedido | Calibración de `sim.py` |
| 3 | **Tramo alimentado por cada subestación** (PK de inicio y fin, zonas neutras) y su PK exacto | Los PK se han estimado con una incertidumbre de ±10 km, lo que altera el reparto de trenes entre subestaciones | `data/subestaciones_traccion.csv` |
| 4 | **Reconfiguración ante la pérdida de una subestación** (tiempo, modo automático o telemandado, reparto de carga entre vecinas) | Determina el tiempo disponible para que el CPD reduzca carga y la magnitud de esa reducción. Se supone que cada vecina asume el 50 % de la carga | `N1_SHARE` en `analysis.py` y `arquitectura.py` |
| 5 | **Transformadores de tracción** (número, potencia asignada, conexión en V o monofásica) y carga máxima registrada | Acota el escenario de ampliación (~100 MW en Madrid–Barcelona, ~55 MW en Madrid–Sevilla) | `acceso_escenario_alto_MW` |
| 6 | **Potencia contratada por periodo (P1–P6)** | Condiciona el margen que podría liberar una reducción voluntaria del permiso de acceso | Escenario "firme" |
| 7 | **Disponibilidad de suelo** junto a cada subestación para una posición nueva, transformadores, baterías y el CPD | Determina qué emplazamientos son viables | Lista de emplazamientos |
| 8 | **Red de conexión** de seis subestaciones sin posición identificada en REE (Feria de Muestras, Lleida, Sant Boi, La Lancha, Lora del Río, Rinconada) | Se les asignan 35–40 MW de acceso | `data/subestaciones_traccion.csv` |

## 2. Red de transporte

| # | Dato no público o no incorporado | Efecto sobre los resultados |
|---|---|---|
| 9 | **Potencia de cortocircuito** (mínima y máxima) de cada nudo | El cálculo del desequilibrio usa valores supuestos (12 GVA a 400 kV y 5 GVA a 220 kV) |
| 10 | **Margen de capacidad de acceso** por nudo (fichero `GRT_demanda.xlsx` de REE, público pero aún no incorporado) | Indica cuánto puede ampliarse el acceso sin refuerzos de red |
| 11 | **Viabilidad operativa de un acceso compartido con prioridad** (límite conjunto tren + CPD en el nudo con señal de reducción) | Es la reforma que propone el trabajo; su implementación práctica está sin contrastar con el operador del sistema |

## 3. Material rodante

| # | Dato no público | Efecto sobre los resultados |
|---|---|---|
| 12 | **Consumo real por tren-km** y potencia máxima en pantógrafo en ambas líneas | El modelo obtiene 12,8 y 10,9 kWh/tren-km, valores probablemente bajos |
| 13 | **Curvas de tracción y freno** (esfuerzo-velocidad) y servicios auxiliares de las series S-103, S-112, Avril, Frecciarossa y Euroduplex | Determinan los picos de potencia, que son los que ocupan el acceso |
| 14 | **Fracción de la energía de frenado devuelta a la red** de 25 kV | El modelo estima unos 27 MWh/día (<3 %) |

## Tratamiento en el trabajo

Los resultados se presentan como estimaciones preliminares, con análisis de sensibilidad sobre los parámetros 1, 4 y
9. La validación con datos reales de explotación queda como trabajo futuro.
