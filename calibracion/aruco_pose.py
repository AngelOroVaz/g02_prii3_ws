import cv2
import numpy as np

IMAGEN = 'calibracion/fotos/2026-09-24-194027.jpg'
CALIBRACION = 'calibracion/CameraModel.yml'
SALIDA = 'calibracion/aruco_detectado.jpg'
MARKER_SIZE = 0.05


def detectar_aruco(gris):
    if hasattr(cv2.aruco, 'ArucoDetector'):
        diccionario = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        detector = cv2.aruco.ArucoDetector(
            diccionario, cv2.aruco.DetectorParameters()
        )
        return detector.detectMarkers(gris)

    diccionario = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
    parametros = cv2.aruco.DetectorParameters_create()
    return cv2.aruco.detectMarkers(gris, diccionario, parameters=parametros)


def calcular_pose(corner, camera_matrix, dist_coeffs):

    if hasattr(cv2.aruco, 'estimatePoseSingleMarkers'):
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
            [corner], MARKER_SIZE, camera_matrix, dist_coeffs
        )
        return rvecs[0], tvecs[0]


    half = MARKER_SIZE / 2.0
    object_points = np.array([
        [-half,  half, 0.0],
        [ half,  half, 0.0],
        [ half, -half, 0.0],
        [-half, -half, 0.0],
    ], dtype=np.float32)

    ok, rvec, tvec = cv2.solvePnP(
        object_points,
        corner[0].astype(np.float32),
        camera_matrix,
        dist_coeffs,
        flags=cv2.SOLVEPNP_IPPE_SQUARE,
    )
    if not ok:
        raise RuntimeError('No se pudo calcular la pose del ArUco')
    return rvec, tvec


imagen = cv2.imread(IMAGEN)
if imagen is None:
    raise RuntimeError(f'No se pudo cargar {IMAGEN}')

gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)


fs = cv2.FileStorage(CALIBRACION, cv2.FILE_STORAGE_READ)
camera_matrix = fs.getNode('cameraMatrix').mat()
dist_coeffs = fs.getNode('distCoeffs').mat()
fs.release()

corners, ids, _ = detectar_aruco(gris)

if ids is None:
    print('No se han detectado ArUcos')
else:
    cv2.aruco.drawDetectedMarkers(imagen, corners, ids)

    for i, marker_id in enumerate(ids.flatten()):
        rvec, tvec = calcular_pose(corners[i], camera_matrix, dist_coeffs)
        print('ArUco detectado - ID:', int(marker_id))

        cv2.drawFrameAxes(
            imagen,
            camera_matrix,
            dist_coeffs,
            rvec,
            tvec,
            MARKER_SIZE * 0.5,
        )

        x, y = corners[i][0][0].astype(int)
        cv2.putText(
            imagen,
            f'ID: {int(marker_id)}',
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

cv2.imwrite(SALIDA, imagen)
cv2.imshow('Deteccion ArUco', cv2.resize(imagen, None, fx=0.6, fy=0.6))
cv2.waitKey(0)
cv2.destroyAllWindows()
