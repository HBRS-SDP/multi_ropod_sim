# ROPOD Gazebo
Package to simulate a multi-robot scenario with BRSU Topological Map.

## Setting initial position of robots
It is possible to change the initial poses of the robots. You can do so be editting the following file:
[spawn_multiple_robots.launch](ros/generated_files/spawn_multiple_robots.launch)

## Changing the XY and Theta goal tolerance 
It is possible to tighten or loosen the tolerance level for the move_base goals in term of xy and theta. This can be done in the following file:
[base_local_planner_params.yaml](ros/config/move_base_config/base_local_planner_params.yaml)

## Generate multi robot launch files (DISABLED - Need to be refactored)
It is possible to use a script to generate a launch and configuration file to spawn multiple robots and create a RViz config file to visualize the simulations. The script can be launched as follows:

```
python3 ros/scripts/generate_multi_robot_launch.py brsu_ground_floor
```

Optionally, the number of robots to be launched can be specified using the script parameters as shown below:

```
python3 ros/scripts/generate_multi_robot_launch.py brsu_ground_floor --nRobots=5
```

It is also possible to use custom spawn positions for the robots instead of the automatically generating them. The spawn poses have to be defined in a YAML config file named `<world_name>_init_poses.yaml` (for example `brsu_ground_floor_init_poses.yaml`) in the directory `ropod_gazebo/ros/config/spawn_pose_config/`. To use the custom spawn poses, execute the script with the `custom_poses` flag as

```
python3 ros/scripts/generate_multi_robot_launch.py brsu_ground_floor --custom_poses
```

## Launch multi robot simulation
Launch the default configuration using:

```
roslaunch ropod_gazebo multi_robot.launch
```

The launch file supports the following additional commonly used params:
1. `start_move_base`: Activate/Deactivate the move_base package. (Default: `true`)
2. `gui`: Launch the Gazebo Client (i.e. the GUI). (Default: `false`)
3. `start_rviz`: Launch RViz. (Default: `true`)

For example to use the TEB navigation stack instead of the default DWA, launch the simulation using:

```
roslaunch ropod_gazebo multi_robot.launch gui:=true
```

## Teleoperate the robots
It is possible to teleoperate the the robots using the `teleop_keyboard.launch` file. This uses the turtlebot teleop package and allows for a diferential drive motion. This can be used to localize the robots at launch or to manually move the robot through narrow passages where `move_base` fails to plan or execute the path. To control a robot who's `ID` is 2 use the command

```
roslaunch ropod_gazebo teleop_keyboard.launch robot_id:=2
```
