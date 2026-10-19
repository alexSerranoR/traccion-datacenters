# Preguntas para Adif, REE y el material rodante

Son los datos que el modelo hoy **supone** y que más cambian los resultados. Cada pregunta dice para qué sirve y qué
parte del modelo cambiaría. Están ordenadas por lo que pesan en el paper.

## Adif: subestaciones y explotación

| # | Pregunta | Por qué importa | Qué cambia en el modelo |
|---|---|---|---|
| 1 | **¿Con qué resolución se controla y se penaliza la potencia de cada posición?** ¿Maxímetro de 15 min, medias de 1 min o protección instantánea? ¿Existe algún límite físico o contractual por debajo de la capacidad de acceso? | Es lo que más mueve los números: sin batería, el CPD pasa de 70 a 234 MW en Madrid–Barcelona si el límite se vigila con medias de 15 min en vez de 1 min | `analysis.py` (medias de 1 min) y la ventana de `arquitectura.py` |
| 2 | **Curva de carga cuartohoraria real** de cada subestación en un laborable tipo y en el día de máxima demanda, y su energía anual | Para validar la simulación. En 8 subestaciones el pico simulado ya pasa del 90 % del acceso concedido | Calibrar `sim.py` (consumos, zonas) |
| 3 | **Zona que alimenta cada subestación** (PK de inicio y fin, zonas neutras) y su PK exacto | Los PK son estimados (±10 km) y cambian qué trenes carga cada una | `data/subestaciones_traccion.csv` |
| 4 | **Cuando cae una subestación, ¿cuánto se tarda en alimentar su tramo desde las vecinas?** ¿Es automático o por telemando? ¿Cuánta carga asume cada vecina? | Fija cuánto tiempo tiene el CPD para recortar y cuánto recorta. Hoy se supone que cada vecina asume el 50 % de su carga | `N1_SHARE` en `analysis.py` y `arquitectura.py` |
| 5 | **Transformadores de cada subestación** (número, MVA, conexión en V o monofásica) y su carga máxima registrada | Fija el techo del escenario de ampliación (~100 MW en Madrid–Barcelona, ~55 MW en Madrid–Sevilla) | `acceso_escenario_alto_MW` |
| 6 | **Potencia contratada por periodo (P1–P6)** y si Adif ha pensado reducir algún permiso de acceso | Es la vía "hoy": Adif reduce su permiso y el CPD pide el suyo en el mismo nudo | Escenario "firme" |
| 7 | **¿Hay espacio libre en el parque de REE o en el terreno de Adif junto a la subestación** para una posición nueva, dos transformadores, baterías y el CPD? | Sin suelo no hay emplazamiento | Lista de emplazamientos viables |
| 8 | Las 6 subestaciones sin posición identificada en REE (Feria de Muestras, Lleida, Sant Boi, La Lancha, Lora del Río, Rinconada): ¿de qué red cuelgan? | Hoy se les supone 35–40 MW | `data/subestaciones_traccion.csv` |

## REE: nudos

| # | Pregunta | Por qué importa |
|---|---|---|
| 9 | **Potencia de cortocircuito** de cada nudo (mínima y máxima) | Con ella se cierra el cálculo de desequilibrio, hoy con Scc supuesta (12 GVA a 400 kV, 5 GVA a 220 kV) |
| 10 | **Margen de capacidad de acceso** de cada nudo (fichero `GRT_demanda.xlsx` de REE) | Dice cuánto se puede ampliar el acceso sin obras |
| 11 | ¿Admitiría REE un **acceso compartido con prioridad** (un límite conjunto tren + CPD en el nudo, con señal de recorte)? | Es la reforma que propone el paper |

## Material rodante (Talgo / UPM)

| # | Pregunta | Por qué importa |
|---|---|---|
| 12 | **Consumo real por tren-km** de un AVE en Madrid–Barcelona y Madrid–Sevilla, y potencia máxima en pantógrafo | El modelo da 12,8 y 10,9 kWh/tren-km, que parece bajo |
| 13 | **Curvas de tracción y de freno** (esfuerzo-velocidad) y servicios auxiliares de los S-103, S-112, Avril, Frecciarossa y Euroduplex | Fijan los picos de cada tren, que son los que llenan el acceso |
| 14 | ¿Qué parte de la energía de frenado vuelve a la red en 25 kV y cuánta se pierde? | El modelo da unos 27 MWh/día (<3 %) |

## Cómo pedirlo

- La vía rápida es un contacto directo con la Dirección de Energía de Adif a través de la universidad.
- La vía formal es la solicitud de transparencia ya redactada en [`solicitud_transparencia_adif.md`](solicitud_transparencia_adif.md).
  Cubre las preguntas 2 a 6. Conviene añadirle la 1 y la 7, y pedir acceso parcial si alguna se considera
  infraestructura crítica.
