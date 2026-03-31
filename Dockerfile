FROM ros:humble-ros-base

# Install Python ROS2 bindings, CV Bridge, and Cyclone DDS
RUN apt-get update && apt-get install -y \
    ros-humble-rclpy \
    python3-opencv \
    ros-humble-cv-bridge \
    python3-pygame \
    ros-humble-rmw-cyclonedds-cpp \
    && rm -rf /var/lib/apt/lists/**

# Set the workspace
WORKDIR /ros2_ws/src/sub_ai_sim
COPY . .

# Ensure the environment is sourced for all shells
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

# Set the default shell to bash
SHELL ["/bin/bash", "-c"]