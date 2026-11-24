import cv2
import numpy as np

def draw_car(img, center, size, color, label=""):
    """Draws a top-down view of a vehicle with orientation and label."""
    x, y = center
    w, h = size
    
    # Vehicle Body Box
    cv2.rectangle(img, (x - w//2, y - h//2), (x + w//2, y + h//2), color, -1)
    cv2.rectangle(img, (x - w//2, y - h//2), (x + w//2, y + h//2), (255, 255, 255), 1)
    
    # Windshield / Headlights indicator
    cv2.rectangle(img, (x - w//2 + 2, y - h//2 + 2), (x + w//2 - 2, y - h//4), (220, 220, 220), -1)
    
    # Wheels
    wheel_w, wheel_h = 4, 8
    cv2.rectangle(img, (x - w//2 - wheel_w, y - h//3), (x - w//2, y - h//3 + wheel_h), (0, 0, 0), -1)
    cv2.rectangle(img, (x + w//2, y - h//3), (x + w//2 + wheel_w, y - h//3 + wheel_h), (0, 0, 0), -1)
    cv2.rectangle(img, (x - w//2 - wheel_w, y + h//6), (x - w//2, y + h//6 + wheel_h), (0, 0, 0), -1)
    cv2.rectangle(img, (x + w//2, y + h//6), (x + w//2 + wheel_w, y + h//6 + wheel_h), (0, 0, 0), -1)

    if label:
        cv2.putText(img, label, (x - w, y + h//2 + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

def run_project_7():
    print("Running Project 7: Collision Avoidance with Path Planning...")
    print("Press 'q' in the video window to exit.")

    width, height = 800, 500
    fps = 30

    # Multi-lane Road geometry (Top-down Birds-Eye View)
    lane_width = 100
    lane_centers = [width//2 - lane_width, width//2, width//2 + lane_width]  # Left, Center, Right

    # Ego vehicle initial status
    ego_x = lane_centers[1]  # Start in center lane
    ego_y = 420
    ego_speed = 3.0
    target_lane = 1          # 0=Left, 1=Center, 2=Right
    
    # Obstacle vehicle directly in ego car path
    obstacle_x = lane_centers[1]
    obstacle_y = 180
    obstacle_speed = 0.5     # Slow moving obstacle

    # Dynamic path trajectory points
    path_points = []
    
    frame_idx = 0

    while True:
        frame_idx += 1
        frame = np.full((height, width, 3), (40, 40, 40), dtype=np.uint8)

        # Draw 3 Lanes
        for i in range(4):
            x_line = width//2 - int(1.5 * lane_width) + i * lane_width
            if i == 0 or i == 3:
                # Solid Road Outer Boundaries
                cv2.line(frame, (x_line, 0), (x_line, height), (255, 255, 255), 3)
            else:
                # Dashed Lane Dividers
                dash_offset = (frame_idx * 8) % 40
                for y_dash in range(dash_offset - 40, height, 40):
                    cv2.line(frame, (x_line, y_dash), (x_line, y_dash + 20), (255, 255, 255), 2)

        # Distance calculation between Ego Car and Stationary/Slow Obstacle
        distance_to_obstacle = ego_y - obstacle_y

        # Collision Avoidance Path Planner Logic
        status = "PATH CLEAR - MAINTAINING LANE"
        status_color = (0, 255, 0)

        if distance_to_obstacle < 180 and target_lane == 1:
            status = "OBSTACLE DETECTED! PLANNING OVERTAKE PATH"
            status_color = (0, 255, 255)
            target_lane = 0  # Plan path trajectory to Left Lane (Overtake Maneuver)

        if distance_to_obstacle < 100 and target_lane == 1:
            status = "CRITICAL DISTANCE! EMERGENCY PATH DEVIATION"
            status_color = (0, 0, 255)

        # Smooth steering controller towards target planned path
        target_x = lane_centers[target_lane]
        ego_x += (target_x - ego_x) * 0.08

        # Reset maneuver cycle after passing obstacle
        if ego_y < obstacle_y - 80:
            target_lane = 1  # Return to center lane
            if ego_x < lane_centers[1] + 5 and ego_y < 100:
                ego_y = 420
                obstacle_y = 180

        # Move obstacle slowly forward
        obstacle_y -= obstacle_speed

        # Record trajectory for path visualization
        path_points.append((int(ego_x), int(ego_y)))
        if len(path_points) > 40:
            path_points.pop(0)

        # Render Planned Path Line
        for k in range(1, len(path_points)):
            cv2.line(frame, path_points[k-1], path_points[k], (0, 255, 255), 2)

        # Draw Target Lane Center Marker Line
        cv2.line(frame, (lane_centers[target_lane], 0), 
                 (lane_centers[target_lane], height), (0, 165, 255), 1)

        # Draw Vehicles
        draw_car(frame, (int(obstacle_x), int(obstacle_y)), (30, 50), (0, 0, 200), "Obstacle Car")
        draw_car(frame, (int(ego_x), int(ego_y)), (30, 50), (0, 200, 0), "Ego Vehicle")

        # Visual Safety Bubble / Sensor Field around Ego Vehicle
        cv2.circle(frame, (int(ego_x), int(ego_y)), 120, (255, 255, 0), 1)

        # Telemetry Dashboard
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (450, 95), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        cv2.putText(frame, "Collision Avoidance & Path Planning", (20, 32), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        cv2.putText(frame, f"Obstacle Distance: {max(0, distance_to_obstacle):.1f} px", (20, 55), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Status: {status}", (20, 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, status_color, 2)

        cv2.imshow("Collision Avoidance with Path Planning", frame)

        if cv2.waitKey(1000 // fps) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_project_7()