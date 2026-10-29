import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class ImagePublisher(Node):
    """Simula una camara ROS publicando repetidamente una imagen guardada."""

    def __init__(self):
        super().__init__('image_publisher')

        self.bridge = CvBridge()
        self.image = cv2.imread('calibracion/imagen_prueba.jpg')
        if self.image is None:
            raise RuntimeError('No se pudo cargar calibracion/imagen_prueba.jpg')

        # PUBLISHER: los nodos de vision se suscriben a este topic.
        self.image_pub = self.create_publisher(Image, '/camera/image_raw', 10)
        self.timer = self.create_timer(0.5, self.publish_image)

        self.get_logger().info('Publicando en /camera/image_raw')

    def publish_image(self):
        msg = self.bridge.cv2_to_imgmsg(self.image, encoding='bgr8')
        self.image_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ImagePublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
