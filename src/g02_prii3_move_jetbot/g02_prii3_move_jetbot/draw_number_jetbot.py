import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import Trigger


class DrawNumberJetBot(Node):

    def __init__(self):
        super().__init__('draw_number')


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
        self.pausado = False


        self.create_service(
            Trigger,
            '/detener_dibujo',
            self.detener
        )

        self.create_service(
            Trigger,
            '/reanudar_dibujo',
            self.reanudar
        )

        self.create_service(
            Trigger,
            '/reiniciar_dibujo',
            self.reiniciar
        )


        self.timer = self.create_timer(0.1, self.mover)

        self.get_logger().info(
            'draw_number del JetBot iniciado'
        )



    def detener(self, request, response):
        self.pausado = True


        self.cmd_pub.publish(Twist())

        response.success = True
        response.message = 'Dibujo detenido'
        return response



    def reanudar(self, request, response):
        self.pausado = False

        response.success = True
        response.message = 'Dibujo reanudado'
        return response



    def reiniciar(self, request, response):


        self.tramo = 0
        self.ciclos = 0
        self.pausado = False

        self.cmd_pub.publish(Twist())

        response.success = True
        response.message = 'Dibujo reiniciado'
        return response



    def mover(self):

        msg = Twist()


        if self.pausado or self.tramo >= len(self.tramos):
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

    node = DrawNumberJetBot()

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
    