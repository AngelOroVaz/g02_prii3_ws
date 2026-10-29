# Resumen de codigos

## Sprint 1

- `dibujar_2.py`: publica velocidades para dibujar el 2 en turtlesim y ofrece tres servicios de control.

## Sprint 2 - simulacion

- `draw_number.py`: publisher de `/cmd_vel` que ejecuta los cuatro tramos del numero 2.
- `trail_node.py`: subscriber de `/odom` y publisher de `/robot_path` para ver el recorrido en RViz.
- `laser_filter.py`: subscriber de `/scan`, filtra por angulo/distancia y publica `/filtered_scan`.
- `collision_avoidance.py`: subscriber del LiDAR y publisher de `/cmd_vel`; para y reanuda el dibujo.
- `draw_number.launch.py`: abre Gazebo + draw_number + trail_node + RViz.
- `collision_avoidance.launch.py`: abre Gazebo + laser_filter + collision_avoidance + trail_node + RViz.

## Sprint 2 - JetBot

- `draw_number_jetbot.py`: movimiento del numero 2 con valores ajustados al robot real.
- `laser_filter.py`: filtra el `/scan` real y publica `/filtered_scan`.
- `collision_avoidance.py`: para el JetBot ante un obstaculo y continua al retirarlo.
- `camera_rectification.py`: subscriber de `/camera/image_raw`; muestra original y rectificada.
- `aruco_detection.py`: subscriber de `/camera/image_raw`; detecta ID y pose 3D de ArUcos.

## Calibracion

- `comprobar_tablero.py`: comprueba y dibuja los corners 13 x 9.
- `calibrar_camara.py`: obtiene `cameraMatrix` y `distCoeffs`.
- `comprobar_error.py`: calcula el error de reproyeccion de cada foto.
- `calibrar_filtrado.py`: elimina fotos con error alto y vuelve a calibrar.
- `rectificar_imagen.py`: corrige la distorsion con `cv2.undistort()`.
- `comprobar_aruco.py`: prueba varios diccionarios ArUco.
- `aruco_pose.py`: detecta el ArUco, su ID y dibuja ejes XYZ.
- `publicar_imagen_ros.py`: publisher que simula la camara publicando una imagen en ROS.
