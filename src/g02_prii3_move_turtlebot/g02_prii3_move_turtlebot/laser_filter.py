import math
from copy import deepcopy

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class LaserFilter(Node):

    def __init__(self):
        super().__init__('laser_filter')


        self.declare_parameter('laser_angle', 180.0)
        self.declare_parameter('distance', 5.0)
        self.declare_parameter('front_offset_deg', 0.0)


        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            qos_profile_sensor_data,
        )


        self.scan_pub = self.create_publisher(
            LaserScan,
            '/filtered_scan',
            qos_profile_sensor_data,
        )

        self.get_logger().info('/scan -> laser_filter -> /filtered_scan')



    def scan_callback(self, msg):


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



        filtered = deepcopy(msg)

        filtered.ranges = list(msg.ranges)
        filtered.intensities = list(msg.intensities)



        for i, distance in enumerate(msg.ranges):


            angle = msg.angle_min + i * msg.angle_increment


            relative = math.atan2(
                math.sin(angle - offset),
                math.cos(angle - offset),
            )


            valid_distance = (
                math.isfinite(distance)
                and msg.range_min <= distance <= msg.range_max
                and distance <= max_distance
            )


            if abs(relative) > half_angle or not valid_distance:
                filtered.ranges[i] = 0.0

                if i < len(filtered.intensities):
                    filtered.intensities[i] = 0.0



        self.scan_pub.publish(filtered)


def main(args=None):


    rclpy.init(args=args)

    node = LaserFilter()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()