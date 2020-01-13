#!/usr/bin/env python
# coding: utf-8

import numpy as np
import os
import sys
import yaml
import argparse

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

        return'''   <!-- BEGIN ROBOT {id}-->
        <group ns="robot{id}">
            <param name="tf_prefix" value="robot{id}" />
            <include file="$(find ropod_gazebo)/launch/spawn_single_urdf_robot.launch" >
                <arg name="robot_id" value="robot{id}" />
                <arg name="init_x" value="{x}" />
                <arg name="init_y" value="{y}" />
                <arg name="init_theta" value="{theta}" />
                <arg name="model" value="{model}"/>
            </include>
        </group>\n\n'''.format(**data)

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
            with open(filepath, 'w') as f:
                f.write("<launch>\n")

            # Open file in append mode to append robot configurations
            with open(filepath, 'a') as f:
                for i, pose in enumerate(self.poses):
                    robot_id = i+1
                    f.write(self.get_robot_config(robot_id, pose[0], pose[1], pose[2]))
                    if robot_id >= self.nRobots:
                        break
                f.write("</launch>")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("world", type=str, help="Name of the world which will be used for launching the robots")
    parser.add_argument("--nRobots", type=int, help="Number of robots to be placed", default=2)
    parser.add_argument("--model", type=str, help="Name of the URDF model to be used for the robots", default="ropod")
    args = parser.parse_args()

    # curr_dir = os.path.abspath(os.path.split(os.path.abspath(os.path.abspath(sys.argv[0])))[0])
    scripts_dir = os.path.abspath(os.path.dirname(__file__))
    main_dir = os.path.dirname(scripts_dir)
    config_filepath = os.path.abspath(main_dir + "/config/" + args.world + ".yaml")

    if os.path.isfile(config_filepath):
        grid_gen = GridGenerator(config_filepath, args.nRobots, args.model)
        grid_gen.generate_launch_file()
    else:
        print("Error! Config file for world", args.world, "not found at", config_filepath)

if __name__ == "__main__":
    main()
