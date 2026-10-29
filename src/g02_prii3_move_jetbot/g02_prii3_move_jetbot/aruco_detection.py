import os

import cv2
import numpy as np
import rclpy
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class ArucoDetection(Node):
    """Subscriber de la camara que detecta ID y pose 3D de ArUcos."""

    def __init__(self):
        super().__init__('aruco_detection')
        self.bridge = CvBridge()

        self.declare_parameter('image_topic', '/camera/image_raw')
        self.declare_parameter('marker_size', 0.05)
        image_topic = self.get_parameter('image_topic').value
        self.marker_size = float(self.get_parameter('marker_size').value)

        package = get_package_share_directory('g02_prii3_move_jetbot')
        calibration_file = os.path.join(package, 'config', 'CameraModel.yml')

        fs = cv2.FileStorage(calibration_file, cv2.FILE_STORAGE_READ)
        self.camera_matrix = fs.getNode('cameraMatrix').mat()
        self.dist_coeffs = fs.getNode('distCoeffs').mat()
        fs.release()

        if self.camera_matrix is None or self.dist_coeffs is None:
            raise RuntimeError('No se pudo cargar CameraModel.yml')

        # Preparamos el detector segun la version de OpenCV.
        if hasattr(cv2.aruco, 'ArucoDetector'):
            dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
            self.detector = cv2.aruco.ArucoDetector(
                dictionary, cv2.aruco.DetectorParameters()
            )
        else:
            self.detector = None
            self.dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
            self.parameters = cv2.aruco.DetectorParameters_create()

        # SUBSCRIBER: recibe cada frame publicado por la camara.
        self.image_sub = self.create_subscription(
            Image, image_topic, self.image_callback, 10
        )

        self.get_logger().info(f'Esperando imagenes en {image_topic}')

    def detectar(self, gray):
        if self.detector is not None:
            return self.detector.detectMarkers(gray)
        return cv2.aruco.detectMarkers(
            gray, self.dictionary, parameters=self.parameters
        )

    def calcular_pose(self, corner):
        if hasattr(cv2.aruco, 'estimatePoseSingleMarkers'):
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                [corner],
                self.marker_size,
                self.camera_matrix,
                self.dist_coeffs,
            )
            return rvecs[0], tvecs[0]

        half = self.marker_size / 2.0
        object_points = np.array([
            [-half,  half, 0.0],
            [ half,  half, 0.0],
            [ half, -half, 0.0],
            [-half, -half, 0.0],
        ], dtype=np.float32)

        ok, rvec, tvec = cv2.solvePnP(
            object_points,
            corner[0].astype(np.float32),
            self.camera_matrix,
            self.dist_coeffs,
            flags=cv2.SOLVEPNP_IPPE_SQUARE,
        )
        if not ok:
            raise RuntimeError('No se pudo calcular la pose')
        return rvec, tvec

    def image_callback(self, msg):
        try:
            image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as error:
            self.get_logger().error(str(error))
            return

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.detectar(gray)

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(image, corners, ids)

            for i, marker_id in enumerate(ids.flatten()):
                try:
                    rvec, tvec = self.calcular_pose(corners[i])
                except RuntimeError as error:
                    self.get_logger().error(str(error))
                    continue

                cv2.drawFrameAxes(
                    image,
                    self.camera_matrix,
                    self.dist_coeffs,
                    rvec,
                    tvec,
                    self.marker_size * 0.5,
                )

                x, y = corners[i][0][0].astype(int)
                cv2.putText(
                    image,
                    f'ID: {int(marker_id)}',
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                )

        cv2.imshow('Deteccion ArUco', image)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = ArucoDetection()

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
