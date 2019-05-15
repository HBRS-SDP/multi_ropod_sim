# ROPOD
Contains URDF model for ROPOD and gazebo worlds for test environments at `BRSU` and `AMK`

## Launch single robot simulation

```roslaunch ropod_gazebo ropod_sim.launch```


## Launch multi robot simulation
Launch the default configuration using:

```roslaunch ropod_gazebo multi_robot.launch```

To launch a simulation in a specific world use the `world` argument as shown below:

```roslaunch ropod_gazebo multi_robot.launch world:=amk_basement```

## Generate multi robot launch files
It is possible to use a script to generate a launch file to spawn multiple robots. The script can be launched as follows:

```python3 ropod_gazebo/scripts/GenerateMultiRobotLaunch.py brsu_ground_floor```

Optionally, the number of robots to be launched or the robot URDF model can be specified using the script parameters as shown below:

```python3 ropod_gazebo/scripts/GenerateMultiRobotLaunch.py brsu_ground_floor --nRobots=5 --model=dummyModel```
