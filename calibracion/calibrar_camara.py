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
SALIDA = 'calibracion/CameraModel.yml'

# Criterio usado por cornerSubPix para mejorar la precision de las esquinas.
criteria = (
    cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
    30,
    0.001,
)

# Puntos teoricos del tablero: (0,0,0), (1,0,0), ...
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

objpoints = []  # Puntos 3D conocidos del tablero
imgpoints = []  # Puntos 2D detectados en las fotos
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

if not objpoints:
    raise RuntimeError('No se ha detectado el tablero en ninguna imagen')

# Calcula cameraMatrix, distCoeffs y la pose del tablero en cada foto.
error, camera_matrix, dist_coeffs, _, _ = cv2.calibrateCamera(
    objpoints,
    imgpoints,
    gris.shape[::-1],
    None,
    None,
)

print('Imagenes validas:', len(objpoints))
print('Error de calibracion:', error)
print('Matriz de camara:\n', camera_matrix)
print('Coeficientes de distorsion:\n', dist_coeffs)

# Guardar los parametros que usaremos para rectificar y calcular poses ArUco.
fs = cv2.FileStorage(SALIDA, cv2.FILE_STORAGE_WRITE)
fs.write('cameraMatrix', camera_matrix)
fs.write('distCoeffs', dist_coeffs)
fs.release()

print('Guardado en', SALIDA)
