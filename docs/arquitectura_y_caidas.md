# Arquitectura de conexión y respuesta ante pérdida de suministro

Material de trabajo para el paper conceptual (17/10/2026). Las cifras salen del modelo v2 (acceso REE concedido, carga del tren ×1,0, margen del 90 %) y de `src/arquitectura.py` (tabla completa por subestación en `results/arquitectura.csv`). Los valores marcados como **supuesto** hay que confirmarlos.

## 1. Arquitectura de conexión

### 1.1 Cadena de potencia

```
Red de transporte REE (220/400 kV, nudo de la SET de tracción)
 ├─ Posición Adif → transformadores de tracción monofásicos → 2×25 kV → catenaria
 └─ Posición propia del CPD
      └─ 2 transformadores trifásicos 400(220)/30 kV, cada uno al 100 % (N-1 interno)
           └─ Barras de 30 kV (doble barra o anillo)
                ├─ BESS de MT, acoplado en alterna, inversor grid-forming
                │    └─ FV opcional acoplada en continua al BESS (inversor compartido)
                ├─ Grupos electrógenos de MT (solo pérdidas de suministro reales)
                └─ Salas: trafos 30/0,4 kV → SAI (Li-ion, 5-10 min) → IT
```

### 1.2 Decisiones y justificación

| Elemento | Opción elegida | Alternativa descartada | Motivo |
|---|---|---|---|
| Punto de conexión | Posición propia en el mismo parque de REE | Colgar del embarrado o de la línea de Adif | Exigido hoy (permiso propio, posición dedicada en acceso flexible hasta 1/1/2029); evita fallos en modo común con la alimentación de Adif. Con reforma se comparte el **límite de potencia del nudo**, no la aparamenta |
| Transformación | 2 × 100 % (≈2×50 MVA para 40 MW) | 1 trafo o 2 × 50 % | N-1 y mantenimiento concurrente (Tier III) |
| Distribución | 30 kV en anillo | 20 kV | Menos corriente para decenas de MW; estándar en España |
| BESS | MT, acoplado en AC, grid-forming | En la continua del SAI | Sirve a la vez para el recorte por prioridad del tren (lado red) y como puente ante caídas; puede mantener la isla de 30 kV |
| FV | Opcional, acoplada en DC al BESS, autoconsumo sin excedentes | Planta FV con vertido | No aumenta la capacidad (energía, no potencia); ≈10 MWp ≈ 16 GWh/año ≈ 5 % del consumo de un CPD de 40 MW (**supuesto** 1.600 kWh/kWp); sin excedentes no necesita permiso de acceso de generación |
| Grupos | MT, N+1, solo para pérdida de suministro | Usarlos para cubrir recortes | Horas de funcionamiento limitadas por emisiones; usarlos tras el límite equivaldría a generación no autorizada |

### 1.3 Control y prioridad del tren

Jerarquía por escala de tiempo:

1. **ms-1 s:** el BESS absorbe el exceso. Es el único recurso lo bastante rápido: la carga del tren salta **20-30 MW en 10 s** y hasta 47 MW en 1 s en la peor subestación (El Hornillo).
2. **1-10 s:** limitación de potencia de las GPU (power capping).
3. **Minutos:** pausa y migración de trabajos flexibles (checkpointing).
4. **Respaldo duro:** un relé limitador abre una salida del CPD si tren + CPD superan el límite durante más de X s. Es la garantía contractual de prioridad del tren.

La señal sería la medida de potencia de la posición de Adif (telemedida a 1 s), con el EMS del CPD calculando el hueco H(t) = C·0,9 − P_tren(t).

### 1.4 Resultados nuevos del modelo

**Batería de potencia muy exigida.** Con el dimensionado óptimo actual la relación P/E es de ≈4-5 (descarga completa en 12-15 min) y la batería hace una mediana de **5-6 ciclos equivalentes al día**: unos 2.000 al año, con lo que una LFP de unos 6.000 ciclos duraría ≈3 años. Si se limita a 2C (E ≥ P/2), los ciclos bajan a 2,5-3 al día (≈8 años de vida):

| Línea | BESS actual | Coste | BESS limitado a 2C | Coste |
|---|---|---|---|---|
| Madrid–Barcelona | 310 MW / 89 MWh | 84 M€ | 310 MW / 156 MWh | 101 M€ |
| Madrid–Sevilla | 185 MW / 36 MWh | 46 M€ | 185 MW / 93 MWh | 60 M€ |

Alternativas: celdas LTO (>15.000 ciclos) o un híbrido con supercondensadores o volantes de inercia para los picos de segundos. **Acción:** añadir al modelo la restricción de C-rate y el coste de degradación.

**La ventana de medida del límite domina el resultado.** Capacidad del CPD sin batería (hueco mínimo) según con qué media se vigile el límite:

| Línea | 1 s | 1 min (modelo) | 15 min |
|---|---|---|---|
| Madrid–Barcelona | 59 MW | 70 MW | 234 MW |
| Madrid–Sevilla | 210 MW | 227 MW | 337 MW |

El término de potencia se factura con el maxímetro cuartohorario, pero los límites de seguridad de REE y las protecciones actúan mucho más rápido. **Pregunta para Adif y REE:** con qué resolución se vigilaría un acceso compartido.

**Desequilibrio.** Estimado como VUF ≈ S_tren/Scc con el pico de 1 s y Scc **supuesta** de 12 GVA a 400 kV y 5 GVA a 220 kV (6 y 2,5 GVA en nudo débil): sale **0,2-0,8 %**, y hasta **1,9 %** en nudos débiles de 220 kV (Madrid–Sevilla, El Hornillo). Es conservador, porque la conexión en V de Adif y la rotación de fases entre subestaciones lo reducen. Referencias: nivel de planificación en AT ≈1,4 % (IEC TR 61000-3-13); los SAI con rectificador activo toleran ≈2 %; los motores de refrigeración se desclasifican por encima de ≈1 %. El CPD, que es una carga equilibrada, no empeora el desequilibrio. **Acción:** pedir a REE la Scc real de cada nudo.

**Armónicos.** Los trenes modernos llevan convertidores de 4 cuadrantes PWM y emiten poco en baja frecuencia, aunque pueden excitar resonancias. Los SAI y fuentes del CPD con rectificador activo también. Hace falta un estudio de armónicos por emplazamiento, pero no parece una barrera.

## 2. Respuesta ante pérdida de suministro

### 2.1 Tier III / IV

- Uptime Institute considera la red una fuente **económica**, no fiable: la fuente de respaldo de verdad son los grupos del emplazamiento, con combustible en sitio. Por tanto, conectarse en una subestación de tracción **no cambia** la certificación Tier.
- Tier III: mantenimiento concurrente, N+1, ≈99,982 %. Tier IV: tolerante a fallos, 2N, ≈99,995 %.

### 2.2 Eventos y escalas de tiempo

| Evento | Frecuencia | Duración | Efecto en el CPD | Respuesta |
|---|---|---|---|---|
| Hueco de tensión por falta en la red de transporte | Decenas al año | 80-150 ms (+ reenganches) | Ninguno si el SAI aguanta | SAI 0 ms. Riesgo sistémico: desconexión masiva simultánea |
| Cae una subestación vecina de Adif (N-1 del tren) | Rara | Minutos-horas | El tren carga más esta subestación → menos hueco | El BESS cubre los primeros segundos; después se recorta el bloque flexible |
| Fallo de un trafo o una línea del CPD | Rara | Horas | Ninguno | El segundo trafo toma la carga (<1 s, transferencia automática) |
| Pérdida del nudo de REE | Muy rara | Minutos-horas | Pérdida total de red | SAI/BESS grid-forming (0 ms) → grupos arrancan en 10-15 s y toman carga en 30-60 s → combustible ≥12 h |
| Apagón general (28/4/2025) | Excepcional | ≈10-16 h | Pérdida total de red; el tren también está parado | Igual que el caso anterior; no hay conflicto con el tren |

**El N-1 del tren fija el bloque interrumpible.** Si cae la vecina (que esta subestación asuma el 50 % de su carga es un **supuesto**), el CPD dimensionado con batería tiene que soltar:

| Línea | CPD con batería | Sostenible con vecina caída | A recortar |
|---|---|---|---|
| Madrid–Barcelona | 380 MW | 294 MW | 86 MW (mediana ≈25 % por emplazamiento) |
| Madrid–Sevilla | 412 MW | 350 MW | 62 MW (mediana ≈12 %) |

Esto cuadra con el supuesto del 30 % de carga flexible. El recorte se puede hacer en los minutos que tarda Adif en reconfigurar la catenaria, mientras el BESS cubre la transición.

**El BESS hace de puente.** Ejemplo en Anchuelo: con 27,8 MW / 5,4 MWh y el IT limitado a esa potencia aguanta ≈11 min, muy por encima de los 30-60 s que tardan los grupos. Basta con reservar un SoC mínimo (≈D × 2 min) para esta función.

### 2.3 Diseño en dos bloques

- **Bloque firme** (servicios críticos, inferencia, colocation): Tier III, SAI y grupos al 100 %, dimensionado con la capacidad firme.
- **Bloque flexible** (entrenamiento de IA, lotes, HPC): sin grupos o con grupos reducidos, recorte con checkpointing, ≈25-30 % de la potencia. Ahorra la inversión en grupos de esa parte.

### 2.4 Riesgo sistémico y requisitos para el paper

El 10/7/2024, en Virginia, una falta en una línea de 230 kV hizo que unos 60 CPD (≈1.500 MW) se pasaran a la vez a sus SAI y grupos (NERC). Trece CPD a lo largo de una LAV crean el mismo riesgo para REE. El paper debe exigir:

1. Que el CPD aguante huecos sin desconectarse de la red (ride-through).
2. Que la vuelta a red tras un evento sea gradual, con rampa limitada.
3. Que los grupos no se usen para los recortes por prioridad del tren.
4. Que las oscilaciones de potencia del entrenamiento de IA se filtren con el BESS.

## 3. Pendiente
- Introducir en el modelo la restricción de C-rate, la degradación, la ventana de medida (1 min frente a 15 min) y el recorte en N-1 de la vecina.
- Confirmar con Adif y Garrido el tiempo de reconfiguración de la catenaria en N-1 y si la protección de sobrecarga es por trafo o por posición.
- Pedir a REE la Scc de cada nudo.

## Fuentes
- NERC / DCD, evento de Virginia de 2024: https://datacenterdynamics.com/en/news/virginia-narrowly-avoided-power-cuts-when-60-data-centers-dropped-off-the-grid-at-once ; https://www.ferc.gov/sites/default/files/2025-04/Presentation%20NERC%20Seeks%20to%20Address%20Reliability%20Impacts%20from%C2%A0Large%20Load%20Integration_1.pdf
- Uptime Institute, sistemas de combustible: https://journal.uptimeinstitute.com/fuel-system-design-reliability/
- Spain DC sobre el apagón: https://www.datacenterdynamics.com/es/noticias/spain-dc-descarta-que-el-apag%C3%B3n-comprometa-nuevas-inversiones-en-el-sector-de-los-data-centers/
- Cálculo: `src/arquitectura.py` → `results/arquitectura.csv`. Esquema interactivo: `docs/esquema_instalacion.html`.
