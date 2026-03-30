# Use the official ARM64 compatible image
FROM arm64v8/ros:humble-ros-base

# Install system dependencies for OpenCV and Pygame
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-opencv \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
RUN pip3 install pygame numpy opencv-python cv_bridge

# Set working directory
WORKDIR /ros2_ws/src/sub_ai_sim
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
