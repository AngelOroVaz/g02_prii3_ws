import math

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


class CollisionAvoidance(Node):

    def __init__(self):
        super().__init__('collision_avoidance')


        self.declare_parameter('scan_topic', '/scan')
        self.declare_parameter('distance', 0.30)
        self.declare_parameter('front_angle_deg', 30.0)


        self.declare_parameter('front_offset_deg', 180.0)

        scan_topic = self.get_parameter('scan_topic').value


        self.scan_sub = self.create_subscription(
            LaserScan,
            scan_topic,
            self.scan_callback,
            qos_profile_sensor_data,
        )


        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )



        self.tramos = [
            (0.12, -0.55, 75),
            (0.12, 0.00, 35),
            (0.00, 0.80, 34),
            (0.12, 0.00, 33),
        ]


        self.tramo = 0
        self.ciclos = 0
        self.obstaculo = False


        self.timer = self.create_timer(0.1, self.mover)

        self.get_logger().info(f'Leyendo LiDAR de {scan_topic}')



    def scan_callback(self, msg):

        distancia_limite = float(
            self.get_parameter('distance').value
        )


        medio_sector = math.radians(
            float(self.get_parameter('front_angle_deg').value) / 2.0
        )


        offset = math.radians(
            float(self.get_parameter('front_offset_deg').value)
        )

        distancias = []


        for i, distancia in enumerate(msg.ranges):


            angulo = msg.angle_min + i * msg.angle_increment


            relativo = math.atan2(
                math.sin(angulo - offset),
                math.cos(angulo - offset),
            )


            lectura_valida = (
                math.isfinite(distancia)
                and msg.range_min <= distancia <= msg.range_max
            )


            if abs(relativo) <= medio_sector and lectura_valida:
                distancias.append(distancia)


        minima = min(distancias) if distancias else math.inf

        antes = self.obstaculo


        self.obstaculo = minima < distancia_limite


        if self.obstaculo and not antes:
            self.get_logger().info(
                'Obstaculo detectado: JetBot detenido'
            )

        elif antes and not self.obstaculo:
            self.get_logger().info(
                'Camino libre: reanudando dibujo'
            )



    def mover(self):


        msg = Twist()


        if self.obstaculo:
            self.cmd_pub.publish(msg)
            return


        if self.tramo >= len(self.tramos):
            self.cmd_pub.publish(msg)
            return


        lineal, angular, duracion = self.tramos[self.tramo]

        msg.linear.x = lineal
        msg.angular.z = angular


        self.cmd_pub.publish(msg)


        self.ciclos += 1

        if self.ciclos >= duracion:
            self.tramo += 1
            self.ciclos = 0


def main(args=None):


    rclpy.init(args=args)

    node = CollisionAvoidance()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:

        node.cmd_pub.publish(Twist())

        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()