import numpy as np
import os
import sys
import yaml

class GridGenerator:
    def __init__(self, config_dir, world_filepath, nRobots, model_name):
        self.config_dir = config_dir
        self.world_filepath = world_filepath
        self.nRobots = nRobots
        self.model_name = model_name

        self.bottom_left = None
        self.top_right = None
        self.orientation = None
        self.grid_spacing = None
        self.poses = None

    def load_config_file(self):
        yaml_data = None
        with open(self.world_filepath, 'r') as stream:
            try:
                yaml_data =  yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        if yaml_data is not None:
            self.orientation = yaml_data["Orientation"]
            self.grid_spacing = yaml_data["Spacing"]
            self.bottom_left = yaml_data["BBox"]["BL"]
            self.top_right = yaml_data["BBox"]["TR"]

    def generate_poses(self):
        x_lims = sorted([self.bottom_left[0], self.top_right[0]])
        y_lims = sorted([self.bottom_left[1], self.top_right[1]])

        # Since np.arange does not include the stop value, add the grid spacing to include it.
        x_pos = np.arange(x_lims[0], x_lims[1] + self.grid_spacing, self.grid_spacing)
        y_pos = np.arange(y_lims[0], y_lims[1] + self.grid_spacing, self.grid_spacing)

        mesh = np.meshgrid(x_pos, y_pos)

        self.poses = []
        for i in range(mesh[0].shape[0]):
            for j in range(mesh[0].shape[1]):
                x = mesh[0][i, j]
                y = mesh[1][i, j]
                self.poses.append([x, y, self.orientation])

    def get_robot_config(self, id, x, y, theta):
        data = {'id': id, 'x': x, 'y': y, 'theta': theta, 'model': self.model_name}

        return'''\t<!-- ROBOT {id}-->
\t<group ns="robot{id}">
\t\t<param name="tf_prefix" value="robot{id}" />
\t\t<include file="$(find ropod_gazebo)/launch/spawn_single_urdf_robot.launch" >
\t\t\t<arg name="robot_id" value="robot{id}" />
\t\t\t<arg name="init_x" value="{x}" />
\t\t\t<arg name="init_y" value="{y}" />
\t\t\t<arg name="init_theta" value="{theta}" />
\t\t\t<arg name="model" value="{model}"/>
\t\t\t<arg name="map_offset_x" value="$(arg map_offset_x)" />
\t\t\t<arg name="map_offset_y" value="$(arg map_offset_y)" />
\t\t\t<arg name="map_offset_theta" value="$(arg map_offset_theta)" />
\t\t\t<arg name="start_move_base" value="$(arg start_move_base)"/>
\t\t\t<arg name="nav_name" value="$(arg nav_name)"/>
\t\t</include>
\t</group>\n\n'''.format(**data)

    def generate_launch_file(self, filename="spawn_multiple_robots"):
        self.load_config_file()
        self.generate_poses()

        if self.poses is not None:
            max_robots = len(self.poses)
            if self.nRobots > max_robots:
                print("WARNING: Cannot generate launch file for more than", max_robots, "robots")
                print("Limiting number of robots to", max_robots, "robots")
            curr_dir = os.path.abspath(os.path.split(os.path.abspath(os.path.abspath(sys.argv[0])))[0])
            main_dir = os.path.dirname(self.config_dir)
            generated_files_dir = os.path.join(main_dir, 'generated_files')
            launch_filepath = os.path.join(generated_files_dir, filename + '.launch')
            # Open file in write mode to overwrite existing contents
            header = '''<?xml version='1.0'?>
<launch>
\t<arg name="map_offset_x" default="0.0" />
\t<arg name="map_offset_y" default="0.0" />
\t<arg name="map_offset_theta" default="0.0" />
\t<arg name="start_move_base" default="true" />
\t<arg name="nav_name" default="move_base_dwa" />\n\n'''
            with open(launch_filepath, 'w') as f:
                f.write(header)

            # Open file in append mode to append robot configurations
            with open(launch_filepath, 'a') as f:
                for i, pose in enumerate(self.poses):
                    robot_id = i+1
                    f.write(self.get_robot_config(robot_id, pose[0], pose[1], pose[2]))
                    if robot_id >= self.nRobots:
                        break
                f.write("</launch>")
