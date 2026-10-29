# g02_prii3_ws

Workspace de ROS 2 del grupo 02 para la asignatura Robots Inteligentes.

Incluye el dibujo autónomo del número 2, los servicios de control y la parada ante obstáculos con LiDAR, tanto en simulación como en el robot real JetBot.

## Requisitos

Para ejecutar la simulación en el ordenador:

1. Ubuntu 22.04 LTS.
2. ROS 2 Humble.
3. Python 3 y colcon.
4. TurtleBot3 Gazebo, RViz y turtlesim.

Con ROS 2 Humble instalado, instalar las herramientas y paquetes necesarios:

```bash
sudo apt update
sudo apt install python3-colcon-common-extensions ros-humble-turtlebot3-gazebo ros-humble-rviz2 ros-humble-turtlesim
```

Para el robot real se utiliza ROS 2 Foxy y el paquete de la base `jetbot_pro_ros2`. Las rutas y la conexión del JetBot se detallan en su apartado y deben comprobarse en el propio robot.

## Paquetes

El workspace contiene los siguientes paquetes:

- `g02_prii3_turtlesim`: dibuja el número 2 con turtlesim. Corresponde al Sprint 1.
- `g02_prii3_move_turtlebot`: dibuja el número 2 con TurtleBot3 en Gazebo y permite probar la detección de obstáculos.
- `g02_prii3_move_jetbot`: ejecuta el movimiento y la detección de obstáculos en el JetBot real. También contiene los nodos de visión documentados por separado.

Los nodos de dibujo disponen de servicios ROS 2 para:

- Detener el dibujo.
- Reanudar el dibujo.
- Reiniciar el dibujo.

Los nodos `collision_avoidance` ejecutan su propia trayectoria y se detienen automáticamente ante un obstáculo. No ofrecen los tres servicios anteriores.

## Compilación

Los comandos suponen que el proyecto está en `~/g02_prii3_ws`, dentro de la carpeta personal del usuario. Al descargarlo, colocar o renombrar la carpeta como `g02_prii3_ws` en esa ubicación.


Situarse en la raíz del workspace y cargar ROS 2 Humble:

```bash
cd ~/g02_prii3_ws
source /opt/ros/humble/setup.bash
```

Compilar los paquetes de simulación:

```bash
colcon build --symlink-install --packages-select g02_prii3_turtlesim g02_prii3_move_turtlebot
```

Cargar el workspace:

```bash
source ~/g02_prii3_ws/install/setup.bash
```

## Ejecución

### Simulación con TurtleBot3

Preparar la terminal:

```bash
cd ~/g02_prii3_ws
source /opt/ros/humble/setup.bash
source ~/g02_prii3_ws/install/setup.bash
export ROS_DOMAIN_ID=42
export ROS_LOCALHOST_ONLY=1
```

Estos valores separan la simulación del dominio utilizado por el robot real. Utilizarlos en todas las terminales de la simulación.

Ejecutar el dibujo:

```bash
ros2 launch g02_prii3_move_turtlebot draw_number.launch.py
```

Se abrirán Gazebo y RViz. El TurtleBot3 realizará el dibujo y RViz mostrará el recorrido recibido de la odometría.

Para finalizar, pulsar `Ctrl+C` en la terminal del launch.

### Simulación con turtlesim

Con el mismo entorno preparado, ejecutar:

```bash
ros2 launch g02_prii3_turtlesim dibujar_2.launch.py
```

La tortuga dibujará automáticamente el número 2. Ejecutar esta demostración por separado para evitar servicios duplicados.

## Servicios

Con el launch de dibujo activo, abrir otra terminal y cargar el entorno:

```bash
cd ~/g02_prii3_ws
source /opt/ros/humble/setup.bash
source ~/g02_prii3_ws/install/setup.bash
export ROS_DOMAIN_ID=42
export ROS_LOCALHOST_ONLY=1
```

Detener el dibujo:

```bash
ros2 service call /detener_dibujo std_srvs/srv/Trigger "{}"
```

Reanudar el dibujo:

```bash
ros2 service call /reanudar_dibujo std_srvs/srv/Trigger "{}"
```

Reiniciar el dibujo:

```bash
ros2 service call /reiniciar_dibujo std_srvs/srv/Trigger "{}"
```

Reanudar continúa un dibujo pausado; si ha terminado, utilizar reiniciar. En TurtleBot3 y JetBot, reiniciar vuelve al primer tramo desde la posición actual: no devuelve el robot al origen ni borra el rastro de RViz. En turtlesim se llama al servicio `/reset`.

## Evitación de obstáculos

Cerrar primero el launch de dibujo con `Ctrl+C`. Con el entorno de simulación preparado, ejecutar:

```bash
ros2 launch g02_prii3_move_turtlebot collision_avoidance.launch.py
```

El launch arranca Gazebo, el filtro del LiDAR, el nodo de movimiento con detección de obstáculos, el rastro y RViz.

Para comprobar el funcionamiento:

1. Esperar a que aparezca el robot y comience el dibujo.
2. Colocar una caja delante del robot en Gazebo.
3. Comprobar que se detiene cuando detecta el obstáculo a menos de 0,45 m dentro del sector frontal.
4. Retirar la caja y comprobar que continúa el dibujo.

El contador del dibujo queda congelado mientras hay un obstáculo. El robot espera a que se retire; no calcula una ruta para rodearlo.

No ejecutar `draw_number` y `collision_avoidance` al mismo tiempo, porque ambos publican velocidades en `/cmd_vel`.

## Robot real JetBot

Los siguientes datos proceden de la documentación del grupo; no se han comprobado mediante una conexión al robot:

- Usuario: `jetbot`.
- IP documentada: `172.16.190.184`.
- ROS 2: Foxy.
- `ROS_DOMAIN_ID`: `2`.

Estos comandos se ejecutan en el JetBot mediante SSH, no en el ordenador de simulación. Dentro de una sesión SSH, `~` representa la carpeta personal del usuario del robot. Las rutas `~/jetbot_ws` y `~/g02_prii3_ws` son las documentadas para el JetBot y deben existir allí. Si su usuario, IP o carpetas son distintos, ajustar esos datos antes de ejecutar los comandos.

### Arrancar la base

Conectar al robot:

```bash
ssh jetbot@172.16.190.184
```

En esa sesión, ejecutar:

```bash
source /opt/ros/foxy/setup.bash
source ~/jetbot_ws/install/setup.bash
export ROS_DOMAIN_ID=2
export ROS_LOCALHOST_ONLY=0
ros2 launch jetbot_pro_ros2 jetbot.py
```

Dejar esta terminal abierta.

### Compilar y ejecutar el proyecto

Abrir otra sesión SSH. El proyecto debe estar disponible en `~/g02_prii3_ws` dentro del robot.

```bash
cd ~/g02_prii3_ws
source /opt/ros/foxy/setup.bash
source ~/jetbot_ws/install/setup.bash
export ROS_DOMAIN_ID=2
export ROS_LOCALHOST_ONLY=0
colcon build --packages-select g02_prii3_move_jetbot
source install/setup.bash
```

Para dibujar el número 2:

```bash
ros2 launch g02_prii3_move_jetbot draw_number_jetbot.launch.py
```

Para utilizar los servicios, abrir otra sesión SSH y preparar el entorno:

```bash
source /opt/ros/foxy/setup.bash
source ~/jetbot_ws/install/setup.bash
source ~/g02_prii3_ws/install/setup.bash
export ROS_DOMAIN_ID=2
export ROS_LOCALHOST_ONLY=0
```

Después utilizar los mismos comandos de detener, reanudar y reiniciar del apartado Servicios.

Para probar los obstáculos, cerrar primero el launch de dibujo. Comprobar que el LiDAR publica datos:

```bash
ros2 topic hz /scan
```

Pulsar `Ctrl+C` para terminar la comprobación y ejecutar:

```bash
ros2 launch g02_prii3_move_jetbot collision_avoidance_jetbot.launch.py
```

En el JetBot, la distancia inicial de parada es 0,30 m. El código considera el frente del LiDAR desplazado 180 grados y utiliza un sector frontal total de 30 grados.

La versión actual no detiene automáticamente el robot por pérdida de datos del LiDAR; comprobar el sensor antes de la prueba y mantener disponible la parada de la base.

## Comprobaciones

Con el entorno de la demostración cargado, consultar los nodos, topics y servicios:

```bash
ros2 node list
ros2 topic list
ros2 service list
```

Comprobar quién publica las velocidades y los datos del LiDAR:

```bash
ros2 topic info /cmd_vel -v
ros2 topic info /scan -v
ros2 topic info /filtered_scan -v
```

El flujo de detección de obstáculos es:

```text
/scan -> laser_filter -> /filtered_scan -> collision_avoidance -> /cmd_vel
```

Si Gazebo se abre pero no aparece el robot, revisar la terminal del launch. Un error de `spawn_entity` indica que ha fallado la creación del robot; los servicios de dibujo no lo crean.



## Uso de Inteligencia Artificial

Se ha utilizado IA como apoyo para organizar, revisar y documentar parte del código.
