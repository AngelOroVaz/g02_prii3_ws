import glob
import os

import cv2

CHECKERBOARD = (13, 9)  # Esquinas interiores
FOTOS = 'calibracion/fotos'

# Buscar todas las imagenes de calibracion.
imagenes = []
for extension in ('*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG'):
    imagenes.extend(glob.glob(os.path.join(FOTOS, extension)))
imagenes.sort()

validas = 0
print(f'Imagenes encontradas: {len(imagenes)}')

for ruta in imagenes:
    imagen = cv2.imread(ruta)
    if imagen is None:
        print(f'[ERROR] {ruta}')
        continue

    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    # Detecta las 13 x 9 esquinas interiores del tablero.
    encontrado, esquinas = cv2.findChessboardCorners(
        gris,
        CHECKERBOARD,
        cv2.CALIB_CB_ADAPTIVE_THRESH
        + cv2.CALIB_CB_NORMALIZE_IMAGE
        + cv2.CALIB_CB_FAST_CHECK,
    )

    nombre = os.path.basename(ruta)
    if encontrado:
        validas += 1
        print(f'[OK] {nombre}')

        # Solo sirve para comprobar visualmente que la deteccion es correcta.
        cv2.drawChessboardCorners(imagen, CHECKERBOARD, esquinas, encontrado)
        cv2.imshow('Esquinas detectadas', imagen)
        cv2.waitKey(0)
    else:
        print(f'[NO] {nombre}')

cv2.destroyAllWindows()
print(f'Imagenes validas: {validas}/{len(imagenes)}')
