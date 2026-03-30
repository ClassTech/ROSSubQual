# Autonomous Underwater Vehicle (AUV) Simulator - Pre-Qualification Course

## Description 🌊

This project simulates an Autonomous Underwater Vehicle (AUV) performing a pre-qualification course consisting of navigating through a gate and maneuvering around a marker pole. It was originally based on the [ClassTech/RoboSim](https://github.com/ClassTech/RoboSim) project but has been significantly modified for 6-DOF (Degrees of Freedom) submarine simulation.

The simulator uses **Pygame** for 2D top-down map visualization and provides a **simulated 3D camera view** from the AUV's perspective. The AUV operates underwater and uses a 6-thruster configuration (4 vectored horizontal, 2 vertical) for propulsion, steering, and depth control. The physics model includes mass, inertia, distinct drag coefficients for surge, sway, heave, yaw, and pitch, as well as buoyancy effects.

---

## Features ✨

* **2D Map View:** Top-down visualization of the AUV and course elements.
* **3D Camera Simulation:** Renders a first-person view from the AUV, including course elements.
* **6-DOF AUV Physics Model:** Simulates a 6-thruster submarine with mass, rotational inertia (pitch/yaw), distinct linear and angular drag coefficients, and buoyancy.
* **Modular AI (Task/Subtask Architecture):**
    * **Tasks:** Define high-level mission goals (e.g., `GateTask`, `OrbitTurnTask`). They manage a sequence of subtasks.
    * **Subtasks:** Define reusable actions (e.g., `DiveToDepth`, `AlignToObjectX`, `DynamicOrbitPole`, `SwayUntilTargetLost`). Subtasks communicate via a shared `context` dictionary.
    * **Failure Handling:** Tasks can define recovery behavior when a subtask fails.
* **Computer Vision Simulation:** Uses OpenCV (`cv2`) via the `ai.vision.find_blobs_hsv` function and the `Vision` class to simulate blob detection based on HSV color ranges defined in `config.py`.
* **Configurable:** Key parameters (world dimensions, physics coefficients, colors, AI tuning gains, subtask parameters) are defined in `config.py`.

---

## Current Course (Pre-Qualification) 🏊‍♂️

The simulated environment contains:

1.  **Gate:** A horizontal bar 6.6 ft (2 m) long, positioned 3.3 ft (1 m) below the water surface. Two vertical poles support it from below, extending to the floor. The bar is drawn gray, the poles red.
2.  **Marker:** A vertical green pole located 33 ft (10 m) beyond the gate, extending from the floor and breaking the surface.

The current mission objective (`main.py`) is:
1.  Start submerged near the surface, 9.8 ft (3m) behind the gate.
2.  Dive to mission depth (`DiveToDepth` subtask within `GateTask`).
3.  Pass through the gate (`GateTask`).
4.  Stabilize briefly (`StabilizeTask`).
5.  Find, approach (centered), and orbit the green marker pole (centered orbit using sway/yaw/surge) until the gate and pole are simultaneously centered (`OrbitTurnTask`).
6.  Sway left until the pole is lost (`SwayUntilTargetLost` subtask within `OrbitTurnTask`).
7.  Stabilize briefly (`StabilizeTask`).
8.  Return through the gate (`GateTask`).
9.  Stabilize at depth (`StabilizeTask`).
10. Surface (`StabilizeTask` targeting surface depth).

---

## Setup and Installation 🛠️

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-name>
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install pygame numpy opencv-python
    ```
    *(Ensure you have Python 3 installed. Tested with Python 3.12.)*

---

## Usage ▶️

Run the main simulation script from the root directory:

```bash
python main.py