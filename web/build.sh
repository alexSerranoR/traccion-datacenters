#!/bin/sh
# Genera la web en public/ a partir de los ficheros del repositorio (lo ejecuta Vercel, ver vercel.json)
set -e
rm -rf public
mkdir -p public
cp web/index.html public/
cp docs/esquema_instalacion.html public/esquema.html
cp video/trenes_y_centros_de_datos.mp4 public/video.mp4
