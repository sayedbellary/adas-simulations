import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

def create_car_patch(x, y, heading_rad, color, label):
    """
    Creates a rotated vehicle polygon with windshield and direction indicator.
    """
    length, width = 6.0, 3.0
    
    # Base box coordinates relative to center
    rect_coords = np.array([
        [-length/2, -width/2],
        [ length/2, -width/2],
        [ length/2,  width/2],
        [-length/2,  width/2]
    ])
    
    # Rotation matrix
    rot_matrix = np.array([
        [np.cos(heading_rad), -np.sin(heading_rad)],
        [np.sin(heading_rad),  np.cos(heading_rad)]
    ])
    
    transformed_coords = rect_coords @ rot_matrix.T + np.array([x, y])
    return Polygon(transformed_coords, closed=True, facecolor=color, edgecolor='white', linewidth=1.5, zorder=5, label=label)

def run_project_1():
    print("Running Project 1: Enhanced Car Foreground Detection & Driving Scenario Simulation...")

    # 1. Setup Oval Track Road Network (matching lab manual roadCenters)
    theta = np.linspace(0, 2 * np.pi, 300)
    
    # Track geometry (X, Y in meters)
    x_center = 60 * np.cos(theta)
    y_center = 100 * np.sin(theta)

    # Waypoints for Ego Car and Fast Car
    x_ego_path = 57 * np.cos(theta)
    y_ego_path = 95 * np.sin(theta)

    x_fast_path = 63 * np.cos(theta)
    y_fast_path = 105 * np.sin(theta)

    # Set up Dark-Themed Matplotlib Plot
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(9, 8))
    fig.canvas.manager.set_window_title("Project 1: ADAS Driving Scenario Simulation")
    
    ax.set_title("ADAS Driving Scenario Simulation", fontsize=14, fontweight='bold', pad=12, color='cyan')
    ax.set_xlabel("Y Position (m)", fontsize=10)
    ax.set_ylabel("X Position (m)", fontsize=10)
    ax.set_facecolor('#1a1a1a')  # Dark ground background
    ax.grid(True, color='#333333', linestyle='--', alpha=0.6)

    # 2. Render Road Network Surface (Asphalt & Markings)
    # Outer & Inner Asphalt boundaries
    x_outer = 68 * np.cos(theta)
    y_outer = 112 * np.sin(theta)
    x_inner = 52 * np.cos(theta)
    y_inner = 88 * np.sin(theta)

    # Fill Asphalt Track
    road_outer_pts = np.column_stack((y_outer, x_outer))
    road_inner_pts = np.column_stack((y_inner, x_inner))[::-1]
    track_polygon = np.vstack((road_outer_pts, road_inner_pts))
    
    ax.fill(track_polygon[:, 0], track_polygon[:, 1], color='#3d3d3d', zorder=1)  # Asphalt
    ax.plot(y_outer, x_outer, color='white', linewidth=2, zorder=2)               # Outer Solid White Line
    ax.plot(y_inner, x_inner, color='white', linewidth=2, zorder=2)               # Inner Solid White Line
    ax.plot(y_center, x_center, color='#ffcc00', linestyle='--', linewidth=1.5, zorder=2) # Yellow Center Line

    # 3. Telemetry HUD Text Box
    hud_text = ax.text(0.03, 0.93, "", transform=ax.transAxes, fontsize=9,
                       color='white', verticalalignment='top',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='#000000', alpha=0.7, edgecolor='#00ffcc'))

    ax.set_xlim([-135, 135])
    ax.set_ylim([-85, 85])
    ax.set_aspect('equal')

    plt.ion()
    plt.show()

    current_ego_patch = None
    current_fast_patch = None

    # Simulation loop
    for i in range(len(theta)):
        ego_idx = i
        fast_idx = (i * 2) % len(theta)

        # Positions (Y mapped to Horizontal, X mapped to Vertical)
        e_y, e_x = y_ego_path[ego_idx], x_ego_path[ego_idx]
        f_y, f_x = y_fast_path[fast_idx], x_fast_path[fast_idx]

        # Calculate Heading Angles for vehicle alignment
        next_ego_idx = (ego_idx + 1) % len(theta)
        next_fast_idx = (fast_idx + 1) % len(theta)

        ego_heading = np.arctan2(x_ego_path[next_ego_idx] - e_x, y_ego_path[next_ego_idx] - e_y)
        fast_heading = np.arctan2(x_fast_path[next_fast_idx] - f_x, y_fast_path[next_fast_idx] - f_y)

        # Remove previous frame vehicle shapes
        if current_ego_patch:
            current_ego_patch.remove()
        if current_fast_patch:
            current_fast_patch.remove()

        # Render new vehicle polygons
        current_ego_patch = create_car_patch(e_y, e_x, ego_heading, '#ff3333', 'Ego Car (30 m/s)')
        current_fast_patch = create_car_patch(f_y, f_x, fast_heading, '#3399ff', 'Fast Car (50 m/s)')

        ax.add_patch(current_ego_patch)
        ax.add_patch(current_fast_patch)

        # Update HUD Telemetry
        hud_text.set_text(
            f"SIMULATION TELEMETRY\n"
            f"--------------------\n"
            f"Ego Car  : [X: {e_x:5.1f}m, Y: {e_y:5.1f}m] | Speed: 30 m/s\n"
            f"Fast Car : [X: {f_x:5.1f}m, Y: {f_y:5.1f}m] | Speed: 50 m/s"
        )

        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.02)

    plt.ioff()
    plt.show()

if __name__ == "__main__":
    run_project_1()