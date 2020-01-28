import os
import numpy as np
from matplotlib import cm
import glob
import shutil

class Utils(object):

    """Utility functions for multi ropod simulation"""

    @staticmethod
    def generate_rviz_config(generated_files_dir, config_dir, num_of_robots,
                             filename="multi_ropod_sim"):
        """Generate rviz config file containing all robots along with their
           necessary topics

        :generated_files_dir: str
        :config_dir: str
        :num_of_robots: int
        :filename:str
        :returns: None

        """
        rviz_config_file = os.path.join(generated_files_dir, filename + '.rviz')
        with open(rviz_config_file, 'w') as rviz_cfg:
            rviz_config_dir = os.path.join(config_dir, "rviz_config")
            pre_group_cfg = os.path.join(rviz_config_dir, "pre_group_config.yaml")
            post_group_cfg = os.path.join(rviz_config_dir, "post_group_config.yaml")
            robot_group_cfg = os.path.join(rviz_config_dir, "robot_group_config.yaml")

            # Write the rviz config sections that appear before the robot configurations 
            with open(pre_group_cfg, 'r') as pre_group:
                rviz_cfg.write(pre_group.read())

            # Write configurations for each individual robots
            with open(robot_group_cfg, 'r') as robot_group:
                group_description = robot_group.read()
                cmap =  cm.get_cmap('gist_rainbow')
                color_id = np.linspace(0.0, 1.0, num_of_robots)
                for i in range(num_of_robots):
                    color = (np.array(cmap(color_id[i]))[0:3] * 255).astype(int)
                    data = {'id':i+1, 'r':color[0], 'g':color[1], 'b':color[2]}
                    rviz_cfg.write(group_description.format(**data))

            # Write th rviz config that should follow the robots configurations
            with open(post_group_cfg, 'r') as post_group:
                rviz_cfg.write(post_group.read())

    @staticmethod
    def generate_move_base_configs(generated_files_dir, config_dir, num_of_robots):
        """Generate costmap config files for each robot

        :generated_files_dir: str
        :config_dir: str
        :num_of_robots: int
        :returns: None

        """
        move_base_config_dir = os.path.join(config_dir, "move_base_config")

        # Read costmap param template files
        move_base_params = {}
        param_names = ["costmap_common_params", "global_costmap_params", "local_costmap_params"]
        for param_name in param_names:
            param_filepath = os.path.join(move_base_config_dir, param_name + '_template.yaml')
            with open(param_filepath, 'r') as f:
                move_base_params[param_name] = f.read()

        # Create new costmap param files for all the robots
        for i in range(num_of_robots):
            # Create a directory for the current robot config
            dir_name = os.path.join(generated_files_dir, "robot" + str(i+1))
            os.mkdir(dir_name)
            # Generate the costmap param files
            data = {'id':i+1}
            for param_name in param_names:
                param_filepath = os.path.join(dir_name, param_name + '.yaml')
                with open(param_filepath, 'w') as f:
                    f.write(move_base_params[param_name].format(**data))

    @staticmethod
    def reinitialise_generated_files_dir(generated_files_dir):
        """Deletes all files inside `generated_files_dir` directory.
           Assumption: generated_files_dir is an absolute path

        :generated_files_dir: str
        :returns: None

        """
        shutil.rmtree(generated_files_dir, ignore_errors=True)
        os.mkdir(generated_files_dir)
