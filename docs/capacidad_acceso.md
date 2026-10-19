# Capacidad de acceso de las subestaciones de tracción (SET): fuentes y método

Los datos están en [`data/subestaciones_traccion.csv`](../data/subestaciones_traccion.csv) (una fila por SET; líneas MZB = Madrid–Zaragoza–Barcelona, MS = Madrid–Sevilla).

## Fuente principal
REE, "Capacidad de acceso de demanda ocupada por posición", publicada el 1-10-2026:
https://www.ree.es/sites/default/files/12_CLIENTES/Documentos/2026_10_01_Demanda_por_posicion.pdf
(página: https://www.ree.es/es/clientes/consumidor/acceso-conexion/conoce-la-capacidad-de-acceso).
Lista cada posición de la red de transporte con la capacidad de acceso de demanda que tiene concedida (MW).
Las posiciones de Adif se reconocen por su código: `GIF` (líneas construidas por el antiguo GIF: Madrid–Barcelona),
`AD…` (Adif) y `TF`/`TRP` (tracción; se confirma porque las SET de Segovia y Olmedo, en Madrid–Valladolid, son `TRP`).
`acceso_ocupado_MW` = ese valor. El texto extraído del PDF no separa "en servicio" y "pendiente"; para SET antiguas se asume en servicio.

Mismo día, REE publicó el total por tipo de consumo: infraestructuras ferroviarias 3.551 MW concedidos en la red de
transporte (2.836 en servicio); centros de datos 6.328 MW (ninguno en servicio).
https://www.ree.es/sites/default/files/2026-10/0110_NP_Mapa_capacidades_demanda.pdf

## Lista y ubicación de SET
- MZB: 13 SET según el dossier de Adif de la LAV Madrid–Barcelona–Frontera (https://www.barcelonasagrera.com/wp-content/uploads/2015/04/1581.pdf); nudos REE confirmados con informes CNMC/BOE (ver columna `fuente_set`).
- MS: 12 SET según elEconomista (07-2025, pliego de Adif) y Transportes (06-02-2024): https://www.eleconomista.es/transportes-turismo/noticias/13459992/07/25/la-obsolescencia-de-las-subestaciones-pone-en-jaque-la-linea-madridsevilla.html , https://www.transportes.gob.es/ministerio/comunicacion/sala-prensa/mar-06022024-1219
- PK: estimaciones propias por geografía (ninguna fuente pública da el PK de las SET). Confianza baja-media; ±10 km.

## Transformadores
No hay potencia por SET publicada. Valores típicos: 2×60 MVA en 2×25 kV (MZB; Syneox lo confirma para las 3 SET de Lleida–Barcelona,
400/25 kV) y 2×30 MVA en 1×25 kV (MS; Técnica Industrial). MS está renovando 11 SET con "transformadores de mayor capacidad" (2024-2026, sin cifra).

## Escenarios propuestos para el modelo (columnas `acceso_escenario_*`)
- **bajo / real** = capacidad de acceso concedida hoy por REE. Donde falta (5 SET), 35–40 MW (mediana de la línea redondeada a la baja).
  Rueda de Jalón (12 MW) es sospechosa; conviene probar el modelo también con 35 MW.
- **alto / ampliación** = lo que admitirían los transformadores de tracción si Adif (o el CPD) obtuviera más acceso de REE:
  ~100 MW en MZB (2×60 MVA, fp≈0,95, con margen) y ~55 MW en MS (2×30 MVA). Depende del margen del nudo REE, que es dato público
  (fichero por nudo, columnas "MARGEN CAPACIDAD DE ACCESO TOTAL PARA CONEXIÓN A LA RDT"):
  https://www.ree.es/sites/default/files/12_CLIENTES/Documentos/2026_10_01_GRT_demanda.xlsx
  No se pudo descargar desde la nube (bloqueo de red); hay que bajarlo a mano y cruzarlo por `nudo_ree`.

## Pendiente
- Nudo y acceso de: Feria de Muestras, Lleida, Sant Boi (MZB); La Lancha, Lora del Río, Rinconada (MS). Probablemente conectadas a distribución.
- Pliego técnico de la renovación de MS (Plataforma de Contratación, DocumentId 3de12f87-5e1d-4230-b1cd-18e92e232472): probablemente lista las 12 SET con datos.
- Solicitud por transparencia: [`solicitud_transparencia_adif.md`](solicitud_transparencia_adif.md).
