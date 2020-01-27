#!/usr/bin/env python
# coding: utf-8

import numpy as np
import os
import sys
import yaml
import argparse
from matplotlib import cm
import glob
import shutil

class GridGenerator:
    def __init__(self, config_filepath, nRobots, model_name):
        self.config_filepath = config_filepath
        self.nRobots = nRobots
        self.model_name = model_name

        self.bottom_left = None
        self.top_right = None
        self.orientation = None
        self.grid_spacing = None
        self.poses = None

    def load_config_file(self):
        yaml_data = None
        with open(self.config_filepath, 'r') as stream:
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
            filepath = os.path.abspath(curr_dir + "/../launch/" + filename + ".launch")
            # Open file in write mode to overwrite existing contents
            header = '''<?xml version='1.0'?>
<launch>
\t<arg name="map_offset_x" default="0.0" />
\t<arg name="map_offset_y" default="0.0" />
\t<arg name="map_offset_theta" default="0.0" />\n\n'''
            with open(filepath, 'w') as f:
                f.write(header)

            # Open file in append mode to append robot configurations
            with open(filepath, 'a') as f:
                for i, pose in enumerate(self.poses):
                    robot_id = i+1
                    f.write(self.get_robot_config(robot_id, pose[0], pose[1], pose[2]))
                    if robot_id >= self.nRobots:
                        break
                f.write("</launch>")

def generate_rviz_config(nRobots, filename="multi_ropod_sim"):
    main_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    rviz_config_file = os.path.abspath(main_dir + "/config/" + filename + ".rviz")
    with open(rviz_config_file, 'w') as rviz_cfg:
        rviz_config_dir = os.path.abspath(main_dir + "/config/rviz_config")
        pre_group_cfg = os.path.abspath(rviz_config_dir + "/pre_group_config.yaml")
        post_group_cfg = os.path.abspath(rviz_config_dir + "/post_group_config.yaml")
        robot_group_cfg = os.path.abspath(rviz_config_dir + "/robot_group_config.yaml")

        # Write the rviz config sections that appear before the robot configurations 
        with open(pre_group_cfg, 'r') as pre_group:
            rviz_cfg.write(pre_group.read())

        # Write configurations for each individual robots
        with open(robot_group_cfg, 'r') as robot_group:
            group_description = robot_group.read()
            cmap =  cm.get_cmap('gist_rainbow')
            color_id = np.linspace(0.0, 1.0, nRobots)
            for i in range(nRobots):
                color = (np.array(cmap(color_id[i]))[0:3] * 255).astype(int)
                data = {'id':i+1, 'r':color[0], 'g':color[1], 'b':color[2]}
                rviz_cfg.write(group_description.format(**data))

        # Write th rviz config that should follow the robots configurations
        with open(post_group_cfg, 'r') as post_group:
            rviz_cfg.write(post_group.read())

def generate_move_base_configs(nRobots):
    main_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    move_base_config_dir = os.path.abspath(main_dir + "/config/move_base_config")

    # Clear any existing params directories
    for dirname in glob.glob(move_base_config_dir + "/robot*"):
        shutil.rmtree(dirname, ignore_errors=True)

    # Read param config and template files
    move_base_params = {}
    param_names = ["costmap_common_params", "global_costmap_params", "local_costmap_params"]
    for i in range(len(param_names)):
        with open(os.path.abspath(move_base_config_dir + "/" + param_names[i] + "_template.yaml"), 'r') as f:
            move_base_params[param_names[i]] = f.read()

    # Create new config files for all the robots
    for i in range(nRobots):
        # Create a directory for the current robot config
        dir_name = move_base_config_dir + "/robot"+str(i+1)
        os.mkdir(dir_name)
        # Generate the config files
        data = {'id':i+1}
        for j in range(len(param_names)):
            with open(os.path.abspath(dir_name + "/" + param_names[j] + ".yaml"), 'w') as f:
                f.write(move_base_params[param_names[j]].format(**data))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("world", type=str, help="Name of the world which will be used for launching the robots")
    parser.add_argument("--nRobots", type=int, help="Number of robots to be placed", default=2)
    parser.add_argument("--model", type=str, help="Name of the URDF model to be used for the robots", default="ropod")
    args = parser.parse_args()

    scripts_dir = os.path.abspath(os.path.dirname(__file__))
    main_dir = os.path.dirname(scripts_dir)
    config_filepath = os.path.abspath(main_dir + "/config/" + args.world + ".yaml")

    if os.path.isfile(config_filepath):
        grid_gen = GridGenerator(config_filepath, args.nRobots, args.model)
        grid_gen.generate_launch_file()
    else:
        print("Error! Config file for world", args.world, "not found at", config_filepath)

    generate_rviz_config(args.nRobots)
    generate_move_base_configs(args.nRobots)

if __name__ == "__main__":
    main()
