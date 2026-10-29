import math
from copy import deepcopy

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class LaserFilter(Node):
    """Filtra /scan por angulo y distancia y publica /filtered_scan."""

    def __init__(self):
        super().__init__('laser_filter')

        # Parametros del filtro
        self.declare_parameter('laser_angle', 180.0)
        self.declare_parameter('distance', 5.0)
        self.declare_parameter('front_offset_deg', 0.0)

        # Subscriber del LiDAR
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            qos_profile_sensor_data,
        )

        # Publisher del LaserScan filtrado
        self.scan_pub = self.create_publisher(
            LaserScan,
            '/filtered_scan',
            qos_profile_sensor_data,
        )

        self.get_logger().info('/scan -> laser_filter -> /filtered_scan')


    # Procesar cada LaserScan recibido
    def scan_callback(self, msg):

        # Leer parametros actuales
        angle_deg = float(
            self.get_parameter('laser_angle').value
        )

        max_distance = float(
            self.get_parameter('distance').value
        )

        offset = math.radians(
            float(self.get_parameter('front_offset_deg').value)
        )

        half_angle = math.radians(angle_deg / 2.0)


        # Crear una copia del mensaje original
        filtered = deepcopy(msg)

        filtered.ranges = list(msg.ranges)
        filtered.intensities = list(msg.intensities)


        # Recorrer todas las medidas del LiDAR
        for i, distance in enumerate(msg.ranges):

            # Calcular el angulo de la medida
            angle = msg.angle_min + i * msg.angle_increment

            # Aplicar offset y normalizar el angulo
            relative = math.atan2(
                math.sin(angle - offset),
                math.cos(angle - offset),
            )

            # Comprobar si la distancia es valida
            valid_distance = (
                math.isfinite(distance)
                and msg.range_min <= distance <= msg.range_max
                and distance <= max_distance
            )

            # Descartar medidas fuera del angulo o distancia permitidos
            if abs(relative) > half_angle or not valid_distance:
                filtered.ranges[i] = 0.0

                if i < len(filtered.intensities):
                    filtered.intensities[i] = 0.0


        # Publicar el LaserScan filtrado
        self.scan_pub.publish(filtered)


def main(args=None):

    # Iniciar ROS 2
    rclpy.init(args=args)

    node = LaserFilter()

    try:
        # Mantener el nodo activo
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()