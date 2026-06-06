#! /usr/bin/env python

import rospy
import rostest
import unittest
import actionlib
import math

from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point
from std_srvs.srv import Empty, EmptyRequest
from tf.transformations import euler_from_quaternion
from tortoisebot_waypoints.msg import WaypointActionAction, WaypointActionGoal

PKG = 'tortoisebot_waypoints'
NAME = 'test_waypoints_reached'


class TestWaypointsReached(unittest.TestCase):

    _dist_precision = 0.1
    _yaw_precision = math.pi / 10

    def setUp(self):
        rospy.init_node('test_waypoints_reached')

        self._current_position = Point()
        self._current_yaw = 0.0

        self._target_x = rospy.get_param('target_x', 0.5)
        self._target_y = rospy.get_param('target_y', 0.5)

        self._odom_sub = rospy.Subscriber('/odom', Odometry, self._odom_callback)
        rospy.wait_for_message('/odom', Odometry, timeout=10)

        rospy.wait_for_service('/gazebo/reset_world')
        reset = rospy.ServiceProxy('/gazebo/reset_world', Empty)
        reset(EmptyRequest())

        client = actionlib.SimpleActionClient('tortoisebot_as', WaypointActionAction)
        client.wait_for_server()

        goal = WaypointActionGoal()
        goal.position = Point(x=self._target_x, y=self._target_y, z=0.0)
        client.send_goal(goal)
        client.wait_for_result()

    def _odom_callback(self, msg):
        self._current_position = msg.pose.pose.position
        q = msg.pose.pose.orientation
        _, _, self._current_yaw = euler_from_quaternion([q.x, q.y, q.z, q.w])

    def test_goal_position_reached(self):
        dist = math.sqrt(
            pow(self._target_x - self._current_position.x, 2) +
            pow(self._target_y - self._current_position.y, 2)
        )
        self.assertLess(
            dist, self._dist_precision,
            "Position error %.4f m exceeds threshold %.4f m" % (dist, self._dist_precision)
        )

    def test_goal_yaw_reached(self):
        desired_yaw = math.atan2(self._target_y, self._target_x)
        err_yaw = abs(desired_yaw - self._current_yaw)
        if err_yaw > math.pi:
            err_yaw = 2 * math.pi - err_yaw
        self.assertLess(
            err_yaw, self._yaw_precision,
            "Yaw error %.4f rad exceeds threshold %.4f rad" % (err_yaw, self._yaw_precision)
        )


if __name__ == '__main__':
    rostest.rosrun(PKG, NAME, TestWaypointsReached)