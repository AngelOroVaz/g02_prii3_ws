import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import Trigger


class DrawNumber(Node):
    """Dibuja el numero 2 publicando velocidades en /cmd_vel."""

    def __init__(self):
        super().__init__('draw_number')

        # Publisher de velocidades
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Trayectoria: (velocidad lineal, angular, ciclos)
        self.tramos = [
            (0.12, -0.55, 70),  # Curva superior
            (0.12, 0.00, 55),   # Diagonal
            (0.00, 0.80, 28),   # Giro
            (0.12, 0.00, 40),   # Base
        ]

        # Estado de la trayectoria
        self.tramo = 0
        self.ciclos = 0
        self.pausado = False

        # Servicios de control
        self.create_service(Trigger, '/detener_dibujo', self.detener)
        self.create_service(Trigger, '/reanudar_dibujo', self.reanudar)
        self.create_service(Trigger, '/reiniciar_dibujo', self.reiniciar)

        # Ejecuta mover() cada 0.1 segundos
        self.timer = self.create_timer(0.1, self.mover)

        self.get_logger().info('draw_number iniciado')


    # Detener dibujo
    def detener(self, request, response):
        self.pausado = True
        self.cmd_pub.publish(Twist())

        response.success = True
        response.message = 'Dibujo detenido'
        return response


    # Reanudar dibujo
    def reanudar(self, request, response):
        self.pausado = False

        response.success = True
        response.message = 'Dibujo reanudado'
        return response


    # Reiniciar dibujo
    def reiniciar(self, request, response):
        self.tramo = 0
        self.ciclos = 0
        self.pausado = False

        self.cmd_pub.publish(Twist())

        response.success = True
        response.message = 'Dibujo reiniciado'
        return response


    # Movimiento principal
    def mover(self):
        msg = Twist()

        # Si esta pausado o terminado, velocidad cero
        if self.pausado or self.tramo >= len(self.tramos):
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

    node = DrawNumber()

    try:
        # Mantener el nodo activo
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        # Parar el robot antes de cerrar
        node.cmd_pub.publish(Twist())

        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()