# tortoisebot_waypoints

ROS1 (Noetic) integration tests for the TortoiseBot waypoint action server.

## Prerequisites

Two terminals must be running before executing the tests:

**Start Gazebo simulation:**
```bash
source /opt/ros/noetic/setup.bash
source ~/simulation_ws/devel/setup.bash
roslaunch tortoisebot_gazebo tortoisebot_playground.launch
```

**Build:**
```bash
source /opt/ros/noetic/setup.bash
cd ~/simulation_ws && catkin_make && source devel/setup.bash
```

**Start Waypoint Action Server**
```bash
source /opt/ros/noetic/setup.bash
cd ~/simulation_ws && catkin_make && source devel/setup.bash
rosrun tortoisebot_waypoints tortoisebot_action_server.py
```

> The test launch file starts the action server automatically, so no need to run `rosrun` separately.

Just to test if action server is working as intended.
```bash
source ~/simulation_ws/devel/setup.bash
rostopic pub /tortoisebot_as/goal tortoisebot_waypoints/WaypointActionActionGoal "{header: {seq: 0, stamp: {secs: 0, nsecs: 0}, frame_id: ''}, goal_id: {stamp: {secs: 0, nsecs: 0}, id: ''}, goal: {position: {x: 0.5, y: 0.5, z: 0.0}}}"
```
---

## Running Tests

**Terminal 2 (after building):**
```bash
rostest tortoisebot_waypoints waypoints_test.test --reuse-master
```

---

## Switching Between Passing and Failing Conditions

Open `test/waypoints_test.test` in an editor.

### Passing conditions (default)

Comment the pass condition and uncomment the fail line:

```xml
  <!-- Pass Condition -->
  <!-- <test test-name="test_waypoints" pkg="tortoisebot_waypoints" type="test_waypoints_reached.py" /> -->
  <!-- Fail condition -->
  <test test-name="test_waypoints" pkg="tortoisebot_waypoints" type="test_waypoints_fail.py" />
```

Expected output:
```
[ROSTEST]-----------------------------------------------------------------------

SUMMARY
 * RESULT: SUCCESS
 * TESTS: 2
 * ERRORS: 0
 * FAILURES: 0
```

### Failing conditions

Comment out the `test_waypoints_reached.py` line and uncomment the `test_waypoints_fail.py` line:

```xml
<!-- <test test-name="test_waypoints" pkg="tortoisebot_waypoints" type="test_waypoints_reached.py" /> -->
<!-- For fail case -->
<test test-name="test_waypoints" pkg="tortoisebot_waypoints" type="test_waypoints_fail.py" />
```

Rebuild, then run the same rostest command:
```bash
cd ~/simulation_ws && catkin_make && source devel/setup.bash
rostest tortoisebot_waypoints waypoints_test.test --reuse-master
```

Expected output:
```
[ROSTEST]-----------------------------------------------------------------------

SUMMARY
 * RESULT: FAIL
 * TESTS: 1
 * ERRORS: 1
 * FAILURES: 0
```

**Why it fails:** The fail test sends the robot to a position (5.0, 0.0) that is unreachable within 10 seconds. When the timeout expires, the test raises a `RuntimeError`, which rostest counts as an ERROR (not a FAILURE).