#!/usr/bin/env python

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
   packages=['ropod_gazebo'],
   package_dir={'ropod_gazebo': 'ros/src/ropod_gazebo'}
)

setup(**d)
