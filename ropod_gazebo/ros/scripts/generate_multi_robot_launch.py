#!/usr/bin/env python
# coding: utf-8

import os
import argparse
from ropod_gazebo.grid_generator import GridGenerator
from ropod_gazebo.utils import Utils

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("world", type=str, help="Name of the world which will be used for launching the robots")
    parser.add_argument("--nRobots", type=int, help="Number of robots to be placed", default=2)
    parser.add_argument("--model", type=str, help="Name of the URDF model to be used for the robots", default="ropod")
    args = parser.parse_args()

    scripts_dir = os.path.abspath(os.path.dirname(__file__))
    main_dir = os.path.dirname(scripts_dir)
    config_dir = os.path.join(main_dir, 'config')
    world_filepath = os.path.join(config_dir, args.world + '_BBox.yaml')
    generated_files_dir = os.path.join(main_dir, 'generated_files')

    Utils.reinitialise_generated_files_dir(generated_files_dir)

    if os.path.isfile(world_filepath):
        grid_gen = GridGenerator(config_dir, world_filepath, args.nRobots, args.model)
        pose_list = grid_gen.generate_poses()
        Utils.generate_launch_file(pose_list, args.nRobots, config_dir, args.model)
    else:
        print("Error! Config file for world", args.world, "not found at", config_dir)

    Utils.generate_rviz_config(generated_files_dir, config_dir, args.nRobots)
    Utils.generate_move_base_configs(generated_files_dir, config_dir, args.nRobots)

if __name__ == "__main__":
    main()
