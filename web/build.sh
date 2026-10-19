#!/bin/sh
# Genera la web en public/ a partir de los ficheros del repositorio (lo ejecuta Vercel, ver vercel.json)
set -e
rm -rf public
mkdir -p public/datos
cp web/index.html public/
cp results/dashboard.html public/panel.html
cp docs/esquema_instalacion.html public/esquema.html
cp video/trenes_y_centros_de_datos.mp4 public/video.mp4
cp results/capacidad.csv results/lineas.json public/datos/
