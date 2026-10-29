import math

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


class CollisionAvoidance(Node):
    """Detiene el JetBot si detecta un obstaculo delante."""

    def __init__(self):
        super().__init__('collision_avoidance')

        # Parametros del LiDAR
        self.declare_parameter('scan_topic', '/scan')
        self.declare_parameter('distance', 0.30)
        self.declare_parameter('front_angle_deg', 30.0)

        # El frente del LiDAR real esta desplazado 180 grados
        self.declare_parameter('front_offset_deg', 180.0)

        scan_topic = self.get_parameter('scan_topic').value

        # Subscriber del LiDAR
        self.scan_sub = self.create_subscription(
            LaserScan,
            scan_topic,
            self.scan_callback,
            qos_profile_sensor_data,
        )

        # Publisher de velocidades
        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Trayectoria del numero 2 en el JetBot
        # (velocidad lineal, angular, ciclos)
        self.tramos = [
            (0.12, -0.55, 75),  # Curva superior
            (0.12, 0.00, 35),   # Diagonal
            (0.00, 0.80, 34),   # Giro
            (0.12, 0.00, 33),   # Base
        ]

        # Estado de la trayectoria
        self.tramo = 0
        self.ciclos = 0
        self.obstaculo = False

        # Ejecuta mover() cada 0.1 segundos
        self.timer = self.create_timer(0.1, self.mover)

        self.get_logger().info(f'Leyendo LiDAR de {scan_topic}')


    # Procesar datos del LiDAR
    def scan_callback(self, msg):

        distancia_limite = float(
            self.get_parameter('distance').value
        )

        # Mitad del sector frontal: 30 grados -> +/-15 grados
        medio_sector = math.radians(
            float(self.get_parameter('front_angle_deg').value) / 2.0
        )

        # Correccion de orientacion del LiDAR
        offset = math.radians(
            float(self.get_parameter('front_offset_deg').value)
        )

        distancias = []

        # Recorrer todas las medidas del LiDAR
        for i, distancia in enumerate(msg.ranges):

            # Calcular el angulo de cada medida
            angulo = msg.angle_min + i * msg.angle_increment

            # Aplicar offset y normalizar el angulo
            relativo = math.atan2(
                math.sin(angulo - offset),
                math.cos(angulo - offset),
            )

            # Comprobar que la lectura sea valida
            lectura_valida = (
                math.isfinite(distancia)
                and msg.range_min <= distancia <= msg.range_max
            )

            # Guardar solo las distancias del sector frontal
            if abs(relativo) <= medio_sector and lectura_valida:
                distancias.append(distancia)

        # Obtener el obstaculo mas cercano delante
        minima = min(distancias) if distancias else math.inf

        antes = self.obstaculo

        # Hay obstaculo si esta dentro de la distancia limite
        self.obstaculo = minima < distancia_limite

        # Mensajes cuando cambia el estado
        if self.obstaculo and not antes:
            self.get_logger().info(
                'Obstaculo detectado: JetBot detenido'
            )

        elif antes and not self.obstaculo:
            self.get_logger().info(
                'Camino libre: reanudando dibujo'
            )


    # Movimiento principal
    def mover(self):

        # Twist vacio = velocidad cero
        msg = Twist()

        # Si hay obstaculo, detener y no avanzar la trayectoria
        if self.obstaculo:
            self.cmd_pub.publish(msg)
            return

        # Si hemos terminado todos los tramos, detener
        if self.tramo >= len(self.tramos):
            self.cmd_pub.publish(msg)
            return

        # Obtener tramo actual
        lineal, angular, duracion = self.tramos[self.tramo]

        msg.linear.x = lineal
        msg.angular.z = angular

        # Publicar velocidad en /cmd_vel
        self.cmd_pub.publish(msg)

        # Contar ciclos y pasar al siguiente tramo
        self.ciclos += 1

        if self.ciclos >= duracion:
            self.tramo += 1
            self.ciclos = 0


def main(args=None):

    # Iniciar ROS 2
    rclpy.init(args=args)

    node = CollisionAvoidance()

    try:
        # Mantener el nodo activo
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        # Detener el JetBot antes de cerrar
        node.cmd_pub.publish(Twist())

        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()