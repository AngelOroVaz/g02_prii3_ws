import os

import cv2
import rclpy
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class CameraRectification(Node):
    """Recibe imagenes ROS y muestra original y rectificada."""

    def __init__(self):
        super().__init__('camera_rectification')
        self.bridge = CvBridge()

        self.declare_parameter('image_topic', '/camera/image_raw')
        image_topic = self.get_parameter('image_topic').value

        # Cargamos cameraMatrix y distCoeffs obtenidos en la calibracion.
        package = get_package_share_directory('g02_prii3_move_jetbot')
        calibration_file = os.path.join(package, 'config', 'CameraModel.yml')

        fs = cv2.FileStorage(calibration_file, cv2.FILE_STORAGE_READ)
        self.camera_matrix = fs.getNode('cameraMatrix').mat()
        self.dist_coeffs = fs.getNode('distCoeffs').mat()
        fs.release()

        if self.camera_matrix is None or self.dist_coeffs is None:
            raise RuntimeError('No se pudo cargar CameraModel.yml')

        # SUBSCRIBER: recibe cada frame de la camara del JetBot.
        self.image_sub = self.create_subscription(
            Image, image_topic, self.image_callback, 10
        )

        self.get_logger().info(f'Esperando imagenes en {image_topic}')

    def image_callback(self, msg):
        try:
            image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as error:
            self.get_logger().error(str(error))
            return

        h, w = image.shape[:2]
        new_matrix, _ = cv2.getOptimalNewCameraMatrix(
            self.camera_matrix, self.dist_coeffs, (w, h), 1, (w, h)
        )

        rectified = cv2.undistort(
            image,
            self.camera_matrix,
            self.dist_coeffs,
            None,
            new_matrix,
        )

        original = image.copy()
        cv2.putText(original, 'ORIGINAL', (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        cv2.putText(rectified, 'RECTIFICADA', (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

        comparison = cv2.hconcat([original, rectified])
        comparison = cv2.resize(comparison, None, fx=0.5, fy=0.5)
        cv2.imshow('Original vs Rectificada', comparison)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = CameraRectification()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
