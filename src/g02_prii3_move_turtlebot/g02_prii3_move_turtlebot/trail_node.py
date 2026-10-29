import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry, Path


class TrailNode(Node):
    """Convierte la odometria del robot en un camino visible en RViz."""

    def __init__(self):
        super().__init__('trail_node')

        self.path = Path()
        self.path.header.frame_id = 'odom'

        # SUBSCRIBER: recibe la posicion del TurtleBot3.
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10
        )

        # PUBLISHER: envia el recorrido acumulado a RViz.
        self.path_pub = self.create_publisher(Path, '/robot_path', 10)

    def odom_callback(self, msg):
        pose = PoseStamped()
        pose.header = msg.header
        pose.pose = msg.pose.pose

        self.path.header.stamp = self.get_clock().now().to_msg()
        self.path.poses.append(pose)
        self.path_pub.publish(self.path)


def main(args=None):
    rclpy.init(args=args)
    node = TrailNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
