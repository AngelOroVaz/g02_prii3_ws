import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import Empty, Trigger


class DibujarDos(Node):

    def __init__(self):
        super().__init__('dibujar_2')


        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)


        self.acciones = [
            (1.0, 0.0, 2.0),
            (1.0, -1.0, 1.57),
            (0.0, -1.0, 0.78),
            (1.0, 0.0, 4.0),
            (0.0, 1.0, 2.35),
            (1.0, 0.0, 2.5),
        ]

        self.periodo = 0.05
        self.accion = 0
        self.tiempo = 0.0
        self.pausado = False
        self.finalizado = False


        self.create_service(Trigger, '/detener_dibujo', self.detener)
        self.create_service(Trigger, '/reanudar_dibujo', self.reanudar)
        self.create_service(Trigger, '/reiniciar_dibujo', self.reiniciar)


        self.reset_client = self.create_client(Empty, '/reset')

        self.timer = self.create_timer(self.periodo, self.control)
        self.get_logger().info('Nodo dibujar_2 iniciado')

    def control(self):
        msg = Twist()

        if self.pausado or self.finalizado:
            self.cmd_pub.publish(msg)
            return

        lineal, angular, duracion = self.acciones[self.accion]
        msg.linear.x = lineal
        msg.angular.z = angular
        self.cmd_pub.publish(msg)

        self.tiempo += self.periodo
        if self.tiempo >= duracion:
            self.accion += 1
            self.tiempo = 0.0

            if self.accion >= len(self.acciones):
                self.finalizado = True
                self.cmd_pub.publish(Twist())
                self.get_logger().info('Dibujo terminado')

    def detener(self, request, response):
        self.pausado = True
        self.cmd_pub.publish(Twist())
        response.success = True
        response.message = 'Dibujo detenido'
        return response

    def reanudar(self, request, response):
        self.pausado = False
        response.success = not self.finalizado
        response.message = 'Dibujo reanudado' if not self.finalizado else 'El dibujo ya termino'
        return response

    def reiniciar(self, request, response):
        self.pausado = True
        self.cmd_pub.publish(Twist())

        if not self.reset_client.wait_for_service(timeout_sec=1.0):
            response.success = False
            response.message = 'No se encuentra /reset'
            return response

        future = self.reset_client.call_async(Empty.Request())
        future.add_done_callback(self.reset_terminado)

        response.success = True
        response.message = 'Reinicio solicitado'
        return response

    def reset_terminado(self, future):
        try:
            future.result()
            self.accion = 0
            self.tiempo = 0.0
            self.pausado = False
            self.finalizado = False
            self.get_logger().info('Dibujo reiniciado')
        except Exception as error:
            self.get_logger().error(f'Error al reiniciar: {error}')


def main(args=None):
    rclpy.init(args=args)
    node = DibujarDos()

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
