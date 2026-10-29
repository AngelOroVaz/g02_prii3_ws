import glob
import os

import cv2
import numpy as np

CHECKERBOARD = (13, 9)
FLAGS = (
    cv2.CALIB_CB_ADAPTIVE_THRESH
    + cv2.CALIB_CB_NORMALIZE_IMAGE
    + cv2.CALIB_CB_FAST_CHECK
)
FOTOS = 'calibracion/fotos'

criteria = (
    cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
    30,
    0.001,
)

objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

objpoints = []
imgpoints = []
nombres = []
imagenes = []

for extension in ('*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG'):
    imagenes.extend(glob.glob(os.path.join(FOTOS, extension)))
imagenes.sort()

gris = None

for ruta in imagenes:
    imagen = cv2.imread(ruta)
    if imagen is None:
        continue

    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    encontrado, esquinas = cv2.findChessboardCorners(gris, CHECKERBOARD, FLAGS)

    if encontrado:
        esquinas = cv2.cornerSubPix(gris, esquinas, (11, 11), (-1, -1), criteria)
        objpoints.append(objp)
        imgpoints.append(esquinas)
        nombres.append(os.path.basename(ruta))

if not objpoints:
    raise RuntimeError('No hay imagenes validas para calibrar')

error_global, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, gris.shape[::-1], None, None
)

errores = []
for i in range(len(objpoints)):
    # Proyectamos los puntos 3D y los comparamos con los corners detectados.
    proyectados, _ = cv2.projectPoints(
        objpoints[i], rvecs[i], tvecs[i], mtx, dist
    )
    diferencia = imgpoints[i] - proyectados
    error = np.sqrt(np.mean(np.sum(diferencia ** 2, axis=2)))
    errores.append((error, nombres[i]))

errores.sort(reverse=True)

print('Error global:', error_global)
print('Errores por imagen (peor -> mejor):')
for error, nombre in errores:
    print(f'{error:.3f} px  {nombre}')
