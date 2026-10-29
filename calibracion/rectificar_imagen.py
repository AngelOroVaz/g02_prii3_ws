import cv2
import numpy as np

IMAGEN = 'calibracion/fotos/2026-09-24-194027.jpg'
CALIBRACION = 'calibracion/CameraModel.yml'
SALIDA = 'calibracion/comparacion_rectificacion.jpg'

# Cargar la calibracion.
fs = cv2.FileStorage(CALIBRACION, cv2.FILE_STORAGE_READ)
camera_matrix = fs.getNode('cameraMatrix').mat()
dist_coeffs = fs.getNode('distCoeffs').mat()
fs.release()

imagen = cv2.imread(IMAGEN)
if imagen is None:
    raise RuntimeError(f'No se pudo cargar {IMAGEN}')

h, w = imagen.shape[:2]
new_matrix, _ = cv2.getOptimalNewCameraMatrix(
    camera_matrix, dist_coeffs, (w, h), 1, (w, h)
)

# Corrige la distorsion de la lente usando la calibracion.
rectificada = cv2.undistort(
    imagen, camera_matrix, dist_coeffs, None, new_matrix
)

original = imagen.copy()
cv2.putText(original, 'ORIGINAL', (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
cv2.putText(rectificada, 'RECTIFICADA', (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

comparacion = np.hstack((original, rectificada))
cv2.imwrite(SALIDA, comparacion)

pantalla = cv2.resize(comparacion, None, fx=0.5, fy=0.5)
cv2.imshow('Original vs Rectificada', pantalla)
print('Comparacion guardada en', SALIDA)
cv2.waitKey(0)
cv2.destroyAllWindows()
