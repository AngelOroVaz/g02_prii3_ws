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
UMBRAL_ERROR = 3.0
FOTOS = 'calibracion/fotos'
SALIDA = 'calibracion/CameraModel_filtrado.yml'

criteria = (
    cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
    30,
    0.001,
)

# Coordenadas 3D conocidas del tablero plano (Z = 0).
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

objpoints = []
imgpoints = []
imagenes = []

for extension in ('*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG'):
    imagenes.extend(glob.glob(os.path.join(FOTOS, extension)))
imagenes.sort()

gris = None

# 1) Detectar y refinar corners.
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
    raise RuntimeError('No hay imagenes validas para calibrar')

# 2) Primera calibracion con todas las imagenes validas.
_, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, gris.shape[::-1], None, None
)

obj_filtrados = []
img_filtrados = []

# 3) Calcular error de reproyeccion y quitar imagenes con error alto.
for i in range(len(objpoints)):
    proyectados, _ = cv2.projectPoints(
        objpoints[i], rvecs[i], tvecs[i], mtx, dist
    )
    diferencia = imgpoints[i] - proyectados
    error = np.sqrt(np.mean(np.sum(diferencia ** 2, axis=2)))

    if error <= UMBRAL_ERROR:
        obj_filtrados.append(objpoints[i])
        img_filtrados.append(imgpoints[i])

if not obj_filtrados:
    raise RuntimeError('El filtro ha descartado todas las imagenes')

print('Imagenes iniciales:', len(objpoints))
print('Imagenes tras filtrado:', len(obj_filtrados))

# 4) Calibracion final usando solo las imagenes buenas.
error, camera_matrix, dist_coeffs, _, _ = cv2.calibrateCamera(
    obj_filtrados,
    img_filtrados,
    gris.shape[::-1],
    None,
    None,
)

print('Error de calibracion filtrada:', error)
print('Matriz de camara:\n', camera_matrix)
print('Coeficientes de distorsion:\n', dist_coeffs)

fs = cv2.FileStorage(SALIDA, cv2.FILE_STORAGE_WRITE)
fs.write('cameraMatrix', camera_matrix)
fs.write('distCoeffs', dist_coeffs)
fs.release()

print('Guardado en', SALIDA)
