import numpy as np
import os
import sys
import yaml

class GridGenerator:

    """Generate a grid of robots considering num of robots and walls

    :config_dir: str
    :world_filepath: str
    :num_of_robots: int
    :model_name: str
    
    """

    def __init__(self, config_dir, world_filepath, num_of_robots, model_name):
        self._config_dir = config_dir
        self._world_filepath = world_filepath
        self._num_of_robots = num_of_robots
        self._model_name = model_name

        self.bottom_left = None
        self.top_right = None
        self.orientation = None
        self.grid_spacing = None
        self.poses = None

    def load_config_file(self):
        yaml_data = None
        with open(self._world_filepath, 'r') as stream:
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
        data = {'id': id, 'x': x, 'y': y, 'theta': theta, 'model': self._model_name}
        launch_config_dir = os.path.join(self._config_dir, 'launch_config')
        robot_group_filepath = os.path.join(launch_config_dir, 'robot_group')
        with open(robot_group_filepath, 'r') as file_obj:
            robot_group_str = file_obj.read()

        return robot_group_str.format(**data)

    def generate_launch_file(self, filename="spawn_multiple_robots"):
        self.load_config_file()
        self.generate_poses()

        if self.poses is not None:
            max_robots = len(self.poses)
            if self._num_of_robots > max_robots:
                print("WARNING: Cannot generate launch file for more than", max_robots, "robots")
                print("Limiting number of robots to", max_robots, "robots")
            main_dir = os.path.dirname(self._config_dir)
            generated_files_dir = os.path.join(main_dir, 'generated_files')
            launch_filepath = os.path.join(generated_files_dir, filename + '.launch')

            # read the header for launch file
            launch_config_dir = os.path.join(self._config_dir, 'launch_config')
            pre_group_filepath = os.path.join(launch_config_dir, 'pre_group')
            with open(pre_group_filepath, 'r') as file_obj:
                pre_group_str = file_obj.read()

            # Open file in write mode to overwrite existing contents
            with open(launch_filepath, 'w') as f:
                f.write(pre_group_str)

            # Open file in append mode to append robot configurations
            with open(launch_filepath, 'a') as f:
                for i, pose in enumerate(self.poses):
                    robot_id = i+1
                    f.write(self.get_robot_config(robot_id, pose[0], pose[1], pose[2]))
                    if robot_id >= self._num_of_robots:
                        break
                f.write("</launch>")
