#!/bin/sh
# Genera public/ para Vercel: la web y los ficheros que enlaza, sin duplicarlos en el repositorio
set -e
rm -rf public && mkdir -p public
cp web/index.html public/
cp docs/esquema_instalacion.html public/esquema.html
cp video/trenes_y_centros_de_datos.mp4 public/video.mp4
