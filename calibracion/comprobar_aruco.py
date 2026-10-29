import cv2

IMAGEN = 'calibracion/fotos/2026-09-24-194027.jpg'

imagen = cv2.imread(IMAGEN)
if imagen is None:
    raise RuntimeError(f'No se pudo cargar {IMAGEN}')

gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

# Probamos varios diccionarios para comprobar a cual pertenece el marcador.
diccionarios = {
    'DICT_4X4_50': cv2.aruco.DICT_4X4_50,
    'DICT_4X4_100': cv2.aruco.DICT_4X4_100,
    'DICT_4X4_250': cv2.aruco.DICT_4X4_250,
    'DICT_5X5_50': cv2.aruco.DICT_5X5_50,
    'DICT_5X5_100': cv2.aruco.DICT_5X5_100,
    'DICT_6X6_50': cv2.aruco.DICT_6X6_50,
    'DICT_6X6_100': cv2.aruco.DICT_6X6_100,
    'DICT_7X7_50': cv2.aruco.DICT_7X7_50,
    'DICT_ARUCO_ORIGINAL': cv2.aruco.DICT_ARUCO_ORIGINAL,
}

for nombre, codigo in diccionarios.items():
    # API actual de OpenCV.
    if hasattr(cv2.aruco, 'ArucoDetector'):
        diccionario = cv2.aruco.getPredefinedDictionary(codigo)
        parametros = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(diccionario, parametros)
        _, ids, _ = detector.detectMarkers(gris)
    # Compatibilidad con versiones antiguas (por ejemplo algunas de ROS 2 Foxy).
    else:
        diccionario = cv2.aruco.Dictionary_get(codigo)
        parametros = cv2.aruco.DetectorParameters_create()
        _, ids, _ = cv2.aruco.detectMarkers(
            gris, diccionario, parameters=parametros
        )

    if ids is not None:
        print(nombre, '-> IDs:', ids.flatten().tolist())
