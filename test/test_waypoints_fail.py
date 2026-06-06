#! /usr/bin/env python

import rospy
import rostest
import unittest
import actionlib

from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point
from std_srvs.srv import Empty, EmptyRequest
from tortoisebot_waypoints.msg import WaypointActionAction, WaypointActionGoal

PKG = 'tortoisebot_waypoints'
NAME = 'test_waypoints_fail'

# Goal placed well outside the room so the robot cannot reach it in time.
_UNREACHABLE_X = 5.0
_UNREACHABLE_Y = 5.0
# _TIMEOUT_SECS = 10.0
_TIMEOUT_SECS = 2.0


class TestWaypointsFail(unittest.TestCase):

    def setUp(self):
        rospy.init_node('test_waypoints_fail')

        self._odom_sub = rospy.Subscriber('/odom', Odometry, self._odom_callback)
        rospy.wait_for_message('/odom', Odometry, timeout=10)

        rospy.wait_for_service('/gazebo/reset_world')
        reset = rospy.ServiceProxy('/gazebo/reset_world', Empty)
        reset(EmptyRequest())

        client = actionlib.SimpleActionClient('tortoisebot_as', WaypointActionAction)
        client.wait_for_server()

        goal = WaypointActionGoal()
        goal.position = Point(x=_UNREACHABLE_X, y=_UNREACHABLE_Y, z=0.0)
        client.send_goal(goal)
        self._finished = client.wait_for_result(rospy.Duration(_TIMEOUT_SECS))
        if not self._finished:
            client.cancel_goal()

    def _odom_callback(self, msg):
        pass

    def test_goal_position_reached(self):
        if not self._finished:
            raise RuntimeError(
                "Action did not complete: robot could not reach goal (%.1f, %.1f) "
                "within %.0f seconds" % (_UNREACHABLE_X, _UNREACHABLE_Y, _TIMEOUT_SECS)
            )


if __name__ == '__main__':
    rostest.rosrun(PKG, NAME, TestWaypointsFail)