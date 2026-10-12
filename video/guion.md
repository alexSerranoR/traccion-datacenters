# Guion: «Trenes y centros de datos» (55 s)

Vídeo 1920×1080, sin voz, con subtítulos incrustados. Los tiempos sirven para grabar una voz en off encima.

| Tiempo | Imagen | Texto (subtítulo / voz) |
|---|---|---|
| 0:00–0:04 | Torres eléctricas con el sello «SATURADA» | La red eléctrica española está saturada. |
| 0:04–0:09 | Centro de datos desconectado, reloj de «años de espera» | Un centro de datos puede esperar años para conseguir conexión. |
| 0:09–0:13 | Línea Madrid–Zaragoza–Barcelona, aparecen las 13 subestaciones, pasa un tren | Pero junto a las vías del AVE ya hay subestaciones… |
| 0:13–0:17 | Cada subestación se enlaza con la red de alta tensión | …con grandes conexiones a esa misma red. |
| 0:17–0:22.5 | Gráfica de 24 h: límite de la conexión y consumo real de los trenes (picos) | Los trenes solo las usan a ratos: picos cortos al pasar. |
| 0:22.5–0:29 | Se sombrea la noche y el hueco libre: «Capacidad sin usar», «Uso medio ≈ 10 %» | De noche, casi nada. De media, alrededor de un 10 %. |
| 0:29–0:35 | El centro de datos (azul) llena el hueco por debajo del tren | La idea: un centro de datos flexible al lado, que use ese hueco. |
| 0:35–0:41 | Los picos del tren «empujan» al centro de datos hacia abajo; aparece la batería | El tren siempre tiene prioridad. Una batería cubre los picos. |
| 0:41–0:46 | «≈ 380 MW», 13 subestaciones iluminadas | En Madrid–Barcelona cabrían unos 380 MW de centros de datos… |
| 0:46–0:51 | «Con baterías y una reforma de la normativa · sin nuevas líneas eléctricas» | …con un cambio de normativa y conexiones que ya existen. |
| 0:51–0:55 | Cierre: «Trenes y centros de datos, compartiendo la misma conexión a la red» | (sin texto) |

## De dónde salen las cifras (modelo v2)
- Gráfica: consumo minuto a minuto simulado en la subestación de Brihuega (día laborable, Renfe + Iryo + Ouigo) frente a sus 45 MW de acceso concedido según REE. Uso medio 10,5 %; en la línea va del 6 % al 15 % según la subestación.
- Centro de datos de la gráfica: 33 MW, el valor con batería óptima para Brihuega.
- 380 MW: suma de las 13 subestaciones de Madrid–Barcelona en el escenario «con reforma + batería», dentro del acceso que Adif ya tiene concedido. Hoy, sin reforma, la cifra firme es unos 35 MW.

## Cómo rehacerlo
Desde esta carpeta, con Playwright (Node) y ffmpeg: `node render.js "" trenes_y_centros_de_datos.mp4`. Para sacar fotogramas sueltos de prueba: `node render.js 3,21,44`. Los textos están en la lista `SUBS` y en cada escena de `escena.html`.
