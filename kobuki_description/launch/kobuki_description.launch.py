# Copyright 2022 Intelligent Robotics Lab
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

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import launch_ros.descriptions
from launch.substitutions import Command
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration


def start_bridge(context):
    if LaunchConfiguration('gazebo').perform(context) == 'true':
        kobuki_pkg = get_package_share_directory('kobuki_description')

        bridge = Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='bridge_ros_gz',
            parameters=[
                {
                    'config_file': os.path.join(
                        kobuki_pkg, 'config/bridge', 'kobuki_bridge.yaml'
                    ),
                    'use_sim_time': True,
                }
            ],
            output='screen',
        )

        return [bridge]
    
    return []

def start_camera(context):
    if LaunchConfiguration('camera').perform(context) == 'true' and LaunchConfiguration('gazebo').perform(context) == 'true':
        camera_bridge_image = Node(
            package='ros_gz_image',
            executable='image_bridge',
            name='bridge_gz_ros_camera_image',
            output='screen',
            parameters=[{
                'use_sim_time': True,
            }],
            arguments=['/rgbd_camera/image'])

        camera_bridge_depth = Node(
            package='ros_gz_image',
            executable='image_bridge',
            name='bridge_gz_ros_camera_depth',
            output='screen',
            parameters=[{
                'use_sim_time': True,
            }],
            arguments=['/rgbd_camera/depth_image'])
        
        return [camera_bridge_image, camera_bridge_depth]
   
    return []

def generate_launch_description():

    kobuki_pkg = get_package_share_directory('kobuki_description')

    lidar_arg = DeclareLaunchArgument(
        'lidar', default_value='false',
        description='Enable lidar sensor')
    
    camera_arg = DeclareLaunchArgument(
        'camera', default_value='false',
        description='Enable camera sensor')

    structure_arg = DeclareLaunchArgument(
        'structure', default_value='true',
        description='Enable structure elements')
    
    gazebo_arg = DeclareLaunchArgument(
        'gazebo', default_value='false',
        description='Enable gazebo plugins')

    description_file = DeclareLaunchArgument(
        'description_file',
        default_value=os.path.join(kobuki_pkg, 'urdf', 'kobuki.urdf.xacro'),
        description='Absolute path to the robot description file'
    )

    namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='',
        description='Namespace to apply to the nodes'
    )

    robot_model = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace=LaunchConfiguration('namespace'),
        parameters=[{
            'robot_description': launch_ros.descriptions.ParameterValue(
                Command([
                    'xacro ', LaunchConfiguration('description_file'),
                    ' lidar:=', LaunchConfiguration('lidar'),
                    ' camera:=', LaunchConfiguration('camera'),
                    ' structure:=', LaunchConfiguration('structure'),
                    ' gazebo:=', LaunchConfiguration('gazebo')
                ]), value_type=str),
        }],
        remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')]
    )

    # TF Tree
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        namespace=LaunchConfiguration('namespace'),
        remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')]
    )

    ld = LaunchDescription()
    ld.add_action(lidar_arg)
    ld.add_action(camera_arg)
    ld.add_action(structure_arg)
    ld.add_action(gazebo_arg)
    ld.add_action(description_file)
    ld.add_action(namespace_arg)
    ld.add_action(robot_model)
    ld.add_action(joint_state_publisher_node)
    ld.add_action(OpaqueFunction(function=start_bridge))
    ld.add_action(OpaqueFunction(function=start_camera))

    return ld