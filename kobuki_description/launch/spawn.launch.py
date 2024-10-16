# Copyright (c) 2024 Intelligent Robotics Lab (URJC)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Modified by Juan Carlos Manzanares Serrano

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    kobuki_dir = get_package_share_directory('kobuki_description')

    declare_x_cmd = DeclareLaunchArgument('x', default_value='0.0')
    declare_y_cmd = DeclareLaunchArgument('y', default_value='0.0')
    declare_z_cmd = DeclareLaunchArgument('z', default_value='0.0')
    declare_roll_cmd = DeclareLaunchArgument('R', default_value='0.0')
    declare_pitch_cmd = DeclareLaunchArgument('P', default_value='0.0')
    declare_yaw_cmd = DeclareLaunchArgument('Y', default_value='0.0')
    model_name = DeclareLaunchArgument('model_name', default_value='kobuki')
    gazebo_arg = DeclareLaunchArgument('gazebo', default_value='true')
    
    robot_description = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('kobuki_description'),
            'launch/'), 'kobuki_description.launch.py']),
    )

    gazebo_spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=[
            "-model",
            LaunchConfiguration('model_name'),
            "-topic",
            "robot_description",
            "-x", LaunchConfiguration('x'),
            "-y", LaunchConfiguration('y'),
            "-z", LaunchConfiguration('z'),
            "-R", LaunchConfiguration('R'),
            "-P", LaunchConfiguration('P'),
            "-Y", LaunchConfiguration('Y'),
        ],
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='bridge_ros_gz',
        parameters=[
            {
                'config_file': os.path.join(
                    kobuki_dir, 'config/bridge', 'kobuki_bridge.yaml'
                ),
                'use_sim_time': True,
            }
        ],
        output='screen',
    )

    ld = LaunchDescription()
    ld.add_action(declare_x_cmd)
    ld.add_action(declare_y_cmd)
    ld.add_action(declare_z_cmd)
    ld.add_action(declare_roll_cmd)
    ld.add_action(declare_pitch_cmd)
    ld.add_action(declare_yaw_cmd)
    ld.add_action(model_name)
    ld.add_action(gazebo_arg)
    ld.add_action(robot_description)
    ld.add_action(gazebo_spawn_robot)
    ld.add_action(bridge)

    return ld
