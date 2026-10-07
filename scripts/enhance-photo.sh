#!/bin/zsh
# Mejora una foto para superponerla: doble resolución, menos ruido, más luz en rostros,
# corrige tono amarillento y da nitidez, sin alterar a las personas.
# Uso: FF=... ./scripts/enhance-photo.sh "/ruta/foto.png" public/nombre-mejorada.jpg
$FF -hide_banner -loglevel error -y -i "$1" -vf "scale=iw*2:ih*2:flags=lanczos,hqdn3d=2:1.5:3:3,\
eq=brightness=0.035:contrast=1.08:gamma=1.12:saturation=1.04,colorbalance=rm=-0.03:bm=0.04:rh=-0.02:bh=0.03,\
unsharp=5:5:1.1:5:5:0.0" -q:v 2 "$2" && echo "listo: $2"
