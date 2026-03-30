#!/usr/bin/env python3
"""
Main entry point for the Autonomous Submarine Simulator.
Assembles and starts the simulation.
"""
from simulator import SubmarineSimulator
from ai.submarine import Submarine
# --- Absolute imports from ai.tasks package ---
from ai.tasks import GateTask, StabilizeTask, OrbitTurnTask, ShutdownTask
# ---

if __name__ == "__main__":
    # --- SET MISSION DEPTH ---
    MISSION_DEPTH = 1.5 # Run 1.5m deep
    SURFACE_DEPTH = 0.1 # Just under the surface
    # ---

    # --- Create task instances, passing target_depth ---
    first_gate_task = GateTask(target_depth=MISSION_DEPTH)
    stabilize_after_gate1 = StabilizeTask(duration=2.0, target_depth=MISSION_DEPTH)

    # --- USE NEW ORBIT TASK ---
    # --- REMOVED initial_align_fraction argument ---
    orbit_task = OrbitTurnTask(target_depth=MISSION_DEPTH,
                               approach_height_px=180,
                               orbit_target_fraction=0.5,
                               orbit_sway_power=-0.5,      # Negative = Left for orbit
                               orbit_yaw_gain=4.5,
                               orbit_target_width_px=40,
                               final_sway_power=-0.5)      
    # ---

    stabilize_after_turn = StabilizeTask(duration=2.0, target_depth=MISSION_DEPTH)
    return_gate_task = GateTask(target_depth=MISSION_DEPTH)

    stabilize_before_surface = StabilizeTask(duration=2.0, target_depth=MISSION_DEPTH)
    surface_task = StabilizeTask(duration=10.0, target_depth=SURFACE_DEPTH)
    shutdown_task = ShutdownTask()
    # ---

    # --- Set search direction for the return GateTask ---
    return_gate_task.search_direction = -1
    # ---

    # --- Define mission plan using the instances ---
    mission = [
        first_gate_task,
        stabilize_after_gate1,
        orbit_task,
        stabilize_after_turn,
        return_gate_task,
        stabilize_before_surface,
        surface_task,
        shutdown_task
    ]

    submarine_ai = Submarine(mission_plan=mission)
    sim = SubmarineSimulator(submarine_ai=submarine_ai)
    sim.run()