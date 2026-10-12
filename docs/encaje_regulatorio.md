# Encaje regulatorio: compartir la capacidad de acceso de una subestación de tracción con un centro de datos

Revisión a 12/10/2026. No es asesoramiento jurídico: es la lectura técnica de la normativa
para plantear el trabajo. Antes de publicar conviene que la revise alguien de derecho
energético.

## Resumen

- **Hoy no es viable en la forma literal** "el centro de datos (CD) usa la capacidad que Adif
  no consume". El permiso de acceso de Adif es suyo, para su consumo, y no se puede ceder ni
  subarrendar a otro consumidor. Tampoco cabe que Adif revenda energía al CD detrás de su
  contador.
- **Sí es viable hoy una variante**: el CD pide su propio permiso de acceso en el mismo nudo
  de la red de transporte (REE), con su transformador y su posición, y como **acceso flexible
  de transporte (Tipo 3)**, que REE puede recortar. La capacidad que la red tenga libre en ese
  nudo crece si Adif **reduce su propio permiso** al nivel que de verdad necesita.
- **Lo que falta** es una figura de "acceso compartido con prioridad" entre dos consumidores
  en un mismo punto: un límite conjunto en el punto de conexión, en el que el tren manda y
  el CD se recorta según la carga ferroviaria, no según la seguridad del sistema.
- **Para el paper**: presentarlo como capacidad de red infrautilizada y como propuesta
  regulatoria, cuantificando dos cosas: cuánta capacidad podría liberar Adif sin perder
  firmeza N-1, y cuánta podría absorber un CD flexible.

## 1. Cómo se otorga hoy el acceso a la demanda

| Norma | Qué aporta al caso |
|---|---|
| Ley 24/2013 del Sector Eléctrico | Acceso de terceros a la red con permiso de acceso y conexión por instalación. Solo distribuidores y comercializadores suministran a terceros. |
| RD 1183/2020 | Procedimiento de acceso y conexión. Para la demanda lo concreta la CNMC. |
| **Circular CNMC 1/2024** (BOE-A-2024-20760) | Metodología de acceso para la demanda. Define el **acceso flexible** (art. 3.2), permite pedir firme y flexible a la vez (art. 4.3), y permite compartir instalaciones de conexión con acuerdo entre las partes (art. 5.3 y 6.1.e). No regula la transmisión de un permiso de un titular a otro. |
| **Resolución CNMC de 1/12/2025** (BOE-A-2025-25253) | Cómo calcula REE la capacidad de demanda por nudo: criterio N y N-1 (sobrecargas del 15 % durante menos de 20 min), percentil 98 en 2026, factor de potencia 0,95, máximo 500 MW por posición de 400 kV y 300 MW a 220 kV. **Al calcular el margen se resta la capacidad de los consumidores con permiso concedido**, es decir, la capacidad de Adif cuenta entera aunque no la use. Cita las instalaciones ferroviarias de alta velocidad como cargas desequilibradas que exigen estudio de calidad de onda. |
| **RDL 7/2026** (BOE-A-2026-6544) | Concursos de capacidad de demanda en nudos saturados, prioridad para proyectos estratégicos, "prestación por reserva" anual desde que se concede el permiso, hitos para no perderlo y una **ventana para renunciar o reducir una vez la capacidad** sin ejecutar garantías. Mandata un real decreto específico para centros de datos. |
| **Resolución CNMC de 31/7/2026** (BOE-A-2026-17571, en vigor 1/9/2026) | Desarrolla los permisos flexibles. **Tipo 3** (transporte, más de 1 MW): la instalación debe poder reducir consumo cuando REE lo pida por seguridad. **Hasta el 1/1/2029 solo si el punto de conexión es una posición dedicada en exclusiva al titular.** El Tipo 0 (patrón horario autorizado) solo existe en distribución. |
| Proyecto de RD de centros de datos (2026, en audiencia) | CD de más de 1 MW: PUE < 1,15, WUE < 0,1 l/kWh, 80 % de consumo renovable cada hora con adicionalidad, declaración de soberanía digital. Su incumplimiento puede costar el permiso. |

## 2. Qué puede y qué no puede hacer Adif

- **Es un consumidor más de la red de transporte.** El convenio REE–Adif–Adif AV
  (BOE-A-2021-2109) confirma que Adif pide permisos de acceso y conexión y firma contratos
  técnicos de acceso como cualquier consumidor. Las posiciones de la subestación de REE son de
  REE; Adif no adquiere derechos sobre ellas.
- **No puede ceder ni vender su capacidad de acceso.** Ni la Circular 1/2024 ni el RDL 7/2026
  prevén la transmisión de permisos de demanda entre titulares. Si renuncia o reduce, la
  capacidad vuelve a REE, que la asigna por orden de prelación o la reserva para concurso. No
  hay forma de dirigirla a un CD concreto.
- **No puede revender energía a un CD detrás de su contador.** Adif AV compra la energía de
  tracción y la repercute a las empresas ferroviarias; eso es un servicio ferroviario
  complementario (Directiva 2012/34/UE, anexo II, "suministro de corriente de tracción"), no
  una licencia para suministrar a terceros. Las salidas de la Ley 24/2013 no encajan:
  - Líneas directas (art. 42): unen un generador con un consumidor, no a dos consumidores.
  - Redes de distribución cerradas (RD 314/2023): solo polígonos industriales (CNAE B o C) de
    hasta 8 km². Ni el ferrocarril ni un CD (CNAE 63.10) son industriales.
- **Sí puede poner suelo y conocimiento a disposición de terceros.** En el informe
  STP/DTSP/030/23 (septiembre de 2023) la CNMC recomendó a Adif AV publicar la ubicación y el
  consumo de sus subestaciones y ofrecer, de forma transparente y no discriminatoria, el suelo
  sin uso junto a ellas para plantas renovables. Es el precedente más cercano: abrir la
  subestación de tracción a un uso eléctrico de terceros.
- **Suelo.** La Ley 38/2015 del Sector Ferroviario solo permite obras en la zona de dominio
  público (8 m a cada lado de la plataforma) si son necesarias para el servicio ferroviario o
  de interés general (art. 13 y 16), y en la zona de protección (70 m) solo usos compatibles
  y autorizados. El CD tendría que ir en suelo patrimonial de Adif fuera de esas franjas, en
  cesión o arrendamiento, o en suelo privado junto a la subestación.

## 3. Vías para el modelo "el tren primero"

| Vía | ¿Posible hoy? | Comentario |
|---|---|---|
| A. CD conectado al embarrado de Adif, consumo neteado bajo el permiso de Adif | **No** | Sería suministro a un tercero sin ser distribuidor ni comercializador. |
| B. CD con permiso propio y **posición propia** en la subestación de REE, acceso flexible Tipo 3 | **Sí** | Encaje limpio. Pero el recorte lo decide REE por seguridad de red, no por la carga del tren. El CD solo obtiene capacidad si el nudo tiene margen después de restar el permiso completo de Adif. |
| C. Como B, más **reducción voluntaria del permiso de Adif** | **Sí, con riesgo** | Aumenta el margen del nudo, pero la capacidad liberada no se asigna al CD de forma directa. En nudos de concurso compite con todos. |
| D. CD compartiendo la posición de Adif con acceso flexible | **No hasta 2029** | El Tipo 3 exige posición dedicada hasta el 1/1/2029. Después la restricción decae, pero sigue sin haber un límite conjunto entre dos titulares. |
| E. "Permiso de acceso compartido con prioridad" | **Requiere cambio normativo** | Un límite conjunto en el punto de conexión igual al permiso actual de Adif. El tren tiene prioridad y el CD se recorta en tiempo real según la carga de tracción, con telemedida y disparo automático. |

Qué tendría que cambiar para la vía E:
1. Una figura de **permiso de acceso de demanda compartido** entre varios titulares en un
   mismo punto, con un límite conjunto y un orden de prioridad pactado. Ya existe algo parecido
   en generación con la hibridación, pero solo para un mismo titular.
2. Que la **señal de recorte** del acceso flexible pueda venir de la carga del otro titular
   (el tren) y no solo de REE o del distribuidor.
3. Que la capacidad que un consumidor reduce pueda **asignarse a un consumidor co-ubicado**
   sin pasar por concurso, si el nudo no empeora.
4. Que la CNMC o el Ministerio de Transportes aclaren que ofrecer capacidad o suelo de
   subestaciones a terceros no ferroviarios es compatible con las funciones de Adif.

## 4. Precedentes

- **TU Delft, metro de Rotterdam (2026).** *Load Hosting Capacity of Urban Traction Networks*
  (Dwarkasing, con RET) estima entre 2 y 5 MW alojables en las 12 subestaciones de la
  Calandlijn. Concluye que el límite es a veces el **tope contractual de toma de la red**, lo que
  se resuelve renegociando el contrato, y otras veces el límite térmico, lo que exige refuerzo.
  Es el mismo razonamiento que este trabajo, a escala de metro.
  https://repository.tudelft.nl/record/uuid:2d0dc733-75c5-423e-86d5-719b473f4b49
- **Network Rail y la Universidad de Leeds**, piloto de *energy hub* a 25 kV en Ayr (Escocia):
  uso de la red de tracción para cargas no ferroviarias.
- **CNMC 2023 sobre Adif AV**: autoconsumo renovable de las empresas ferroviarias y
  recomendación de abrir información y suelo de subestaciones.
- No he encontrado ningún caso en que un CD comparta la capacidad de acceso de una
  subestación de tracción de alta velocidad, ni en España ni fuera. Es un hueco, y también un
  riesgo: no hay jurisprudencia ni práctica administrativa que lo respalde.

## 5. Implicaciones técnicas que la regulación añade al modelo

- La carga de alta velocidad es **bifásica y desequilibrada**. REE la trata como carga
  perturbadora. Un CD trifásico en el mismo nudo no compensa el desequilibrio, pero sí obliga
  a un estudio conjunto de calidad de onda.
- REE calcula con **percentiles (98 % en 2026)** y admite sobrecargas N-1 breves. El modelo
  usa N-1 = +50 % del vecino más cargado. Conviene alinearlo con este criterio.
- Un CD en acceso flexible tiene que poder **reducir consumo con poco preaviso**. Encaja con la
  parte desplazable de la carga de IA y con baterías, y también ayuda a cumplir la casación
  horaria renovable del proyecto de RD.

## 6. Cómo plantearlo en el paper

1. **Tesis**: las subestaciones de tracción de alta velocidad reservan capacidad de acceso a
   la red de transporte muy por encima de su uso medio. Esa capacidad está bloqueada por
   diseño regulatorio, no por la física de la red.
2. **Escenarios regulatorios** que el modelo puede cuantificar:
   - Hoy (vía B/C): capacidad que Adif podría reducir manteniendo firmeza N-1, y CD en acceso
     flexible Tipo 3 con posición propia.
   - Reforma (vía E): permiso compartido con prioridad del tren, que es el escenario "normal"
     o "con batería" del modelo actual.
3. **Propuesta regulatoria concreta**: los cuatro cambios de la sección 3, como contribución
   del trabajo.
4. **Limitación explícita**: la capacidad real de acceso por subestación no es pública. Habría
   que pedirla a Adif o a REE, o estimarla por la potencia de los transformadores.

## Fuentes

- Circular 1/2024 de la CNMC, de 27 de septiembre: https://www.boe.es/buscar/doc.php?id=BOE-A-2024-20760
- Resolución CNMC de 1/12/2025, capacidad de acceso de la demanda: https://www.boe.es/buscar/doc.php?id=BOE-A-2025-25253
- CNMC, permisos de acceso flexibles (nota de prensa, 11/8/2026): https://www.cnmc.es/prensa/permisos-acceso-flexibles-20260811
- Real Decreto-ley 7/2026, de 20 de marzo: https://www.boe.es/buscar/act.php?id=BOE-A-2026-6544
- Pérez-Llorca, nota sobre las medidas energéticas del RDL 7/2026: https://www.perezllorca.com/wp-content/uploads/2026/03/Nota-Juridica-Principales-medidas-energeticas-contenidas-en-el-Real-Decreto-ley-7-2026.pdf
- Proyecto de RD de centros de datos (MITECO, audiencia pública): https://www.miteco.gob.es/en/energia/participacion/2026/detalle-participacion-publica-k-851.html
- Fedea, nota sobre el proyecto de RD de centros de datos (2026): https://documentos.fedea.net/pubs/ap/2026/ap2026-23.pdf
- Convenio REE–Adif–Adif AV (BOE-A-2021-2109): https://www.boe.es/diario_boe/txt.php?id=BOE-A-2021-2109
- CNMC, informe STP/DTSP/030/23 sobre autoconsumo en la Declaración sobre la Red de Adif AV: https://www.cnmc.es/prensa/autoconsumo_declaracion_red_20230913
- Ley 24/2013, art. 42 (líneas directas): https://www.iberley.es/legislacion/articulo-42-sector-electrico
- RD 314/2023, redes de distribución cerradas (nota de Pérez-Llorca): https://www.perezllorca.com/wp-content/uploads/2023/05/Nota-Juridica-Aprobada-la-regulacion-para-las-redes-de-distribucion-de-energia-electrica-cerradas.pdf
- Ley 38/2015 del Sector Ferroviario: https://www.boe.es/buscar/act.php?id=BOE-A-2015-11724
- Dwarkasing (2026), *Load Hosting Capacity of Urban Traction Networks*, TU Delft: https://repository.tudelft.nl/record/uuid:2d0dc733-75c5-423e-86d5-719b473f4b49
