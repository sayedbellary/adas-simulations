import cv2
import numpy as np

def draw_rear_car(img, center, box_w, box_h, brake_on=False):
    """Draws rear profile of lead vehicle with brake light activation."""
    x_center, y_bottom = center
    x_min = x_center - box_w // 2
    body_h = int(box_h * 0.55)
    body_y_min = y_bottom - body_h

    # Body & Cabin
    cv2.rectangle(img, (x_min, body_y_min), (x_min + box_w, y_bottom), (50, 50, 50), -1)
    roof_w = int(box_w * 0.75)
    cv2.rectangle(img, (x_center - roof_w//2, y_bottom - box_h), (x_center + roof_w//2, body_y_min), (30, 30, 30), -1)

    # Rear Window
    win_w = int(roof_w * 0.8)
    win_h = int((box_h - body_h) * 0.6)
    cv2.rectangle(img, (x_center - win_w//2, y_bottom - box_h + 4), (x_center + win_w//2, y_bottom - box_h + 4 + win_h), (180, 180, 180), -1)

    # Tail/Brake Lights
    light_w = max(4, int(box_w * 0.2))
    light_h = max(4, int(body_h * 0.3))
    light_y = body_y_min + int(body_h * 0.2)
    
    # Bright Red when Brake Light is Active
    light_color = (0, 0, 255) if brake_on else (0, 0, 120)
    cv2.rectangle(img, (x_min + 3, light_y), (x_min + 3 + light_w, light_y + light_h), light_color, -1)
    cv2.rectangle(img, (x_min + box_w - 3 - light_w, light_y), (x_min + box_w - 3, light_y + light_h), light_color, -1)
    
    if brake_on: # Outer Glow Effect for Braking
        cv2.rectangle(img, (x_min + 1, light_y - 2), (x_min + 5 + light_w, light_y + light_h + 2), (0, 0, 255), 1)
        cv2.rectangle(img, (x_min + box_w - 5 - light_w, light_y - 2), (x_min + box_w - 1, light_y + light_h + 2), (0, 0, 255), 1)

def run_project_8():
    print("Running Project 8: Automatic Emergency Braking (AEB)...")
    print("Press 'q' in the video window to exit.")

    width, height = 800, 480
    fps = 30
    horizon_y = int(height * 0.45)

    # Kinematic Variables for Ego Vehicle & Lead Vehicle
    ego_speed_kph = 60.0       # Initial Ego Vehicle Speed (km/h)
    lead_distance_m = 50.0     # Initial distance to lead vehicle (meters)
    lead_speed_kph = 0.0       # Stationary vehicle ahead
    
    aeb_active = False
    brake_applied = False
    stopped = False

    frame_idx = 0

    while True:
        frame_idx += 1
        frame = np.full((height, width, 3), (110, 110, 110), dtype=np.uint8)

        # Draw Horizon & Perspective Road
        frame[:horizon_y] = (200, 160, 110)
        road_pts = np.array([[0, height], [int(width * 0.4), horizon_y], 
                             [int(width * 0.6), horizon_y], [width, height]], np.int32)
        cv2.fillPoly(frame, [road_pts], (60, 60, 60))

        # Lane Markings (Speed-based animated dashes)
        dash_offset = int(frame_idx * (ego_speed_kph / 5.0)) % 40
        for y_pos in range(horizon_y + dash_offset, height, 35):
            scale = (y_pos - horizon_y) / (height - horizon_y)
            cx = int(width * 0.5)
            lw = max(1, int(6 * scale))
            lh = max(2, int(15 * scale))
            cv2.line(frame, (cx, y_pos), (cx, min(height, y_pos + lh)), (255, 255, 255), lw)

        # Relative Speed (m/s) & Time-To-Collision (TTC) Calculation
        rel_speed_mps = (ego_speed_kph - lead_speed_kph) * (1000.0 / 3600.0)
        
        if rel_speed_mps > 0:
            ttc = lead_distance_m / rel_speed_mps
        else:
            ttc = 99.9

        # AEB Controller Decision Logic
        if ttc <= 1.5 and not stopped:  # Critical Threshold -> Trigger Emergency Brake
            aeb_active = True
            brake_applied = True
            ego_speed_kph = max(0.0, ego_speed_kph - 2.5) # Hard Braking Deceleration
            status = "AEB ACTIVATED - HARD BRAKING!"
            alert_color = (0, 0, 255)
        elif ttc <= 3.0 and not stopped: # Warning Phase
            aeb_active = False
            brake_applied = False
            status = "WARNING: COLLISION RISK! PRE-CHARGE BRAKES"
            alert_color = (0, 255, 255)
        elif ego_speed_kph == 0.0:
            stopped = True
            aeb_active = False
            brake_applied = True
            status = "VEHICLE STOPPED SAFELY"
            alert_color = (0, 255, 0)
        else:
            aeb_active = False
            brake_applied = False
            status = "NORMAL DRIVING - FCW MONITORING"
            alert_color = (0, 255, 0)

        # Update Distance Kinematics
        if not stopped:
            lead_distance_m -= rel_speed_mps * (1.0 / fps)
            if lead_distance_m <= 3.0: # Minimum safe gap
                lead_distance_m = 3.0
                ego_speed_kph = 0.0
                stopped = True

        # Render Lead Vehicle with Monocular Projection
        focal_len = 800.0
        box_w = max(20, int((1.8 * focal_len) / lead_distance_m))
        box_h = max(16, int((1.5 * focal_len) / lead_distance_m))
        u_center = width // 2
        v_bottom = int(horizon_y + (1.5 * focal_len) / lead_distance_m)

        draw_rear_car(frame, (u_center, v_bottom), box_w, box_h, brake_on=brake_applied)

        # Draw Target Bounding Box
        x_min = u_center - box_w // 2
        y_min = v_bottom - box_h
        cv2.rectangle(frame, (x_min, y_min), (x_min + box_w, v_bottom), alert_color, 2)

        # Visual Flash Banner on AEB Activation
        if aeb_active and (frame_idx % 6 < 3):
            cv2.putText(frame, "BRAKE!", (width//2 - 120, 120), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 255), 4)

        # Dashboard Telemetry Overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (450, 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        cv2.putText(frame, "Automatic Emergency Braking (AEB)", (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        cv2.putText(frame, f"Ego Speed: {ego_speed_kph:.1f} km/h", (20, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Lead Distance: {lead_distance_m:.1f} m", (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"TTC: {ttc:.2f} s", (260, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Status: {status}", (20, 102), cv2.FONT_HERSHEY_SIMPLEX, 0.45, alert_color, 2)

        cv2.imshow("Automatic Emergency Braking (AEB)", frame)

        # Reset scenario loop after stopping for 3 seconds
        if stopped and frame_idx % 120 == 0:
            ego_speed_kph = 60.0
            lead_distance_m = 50.0
            stopped = False

        if cv2.waitKey(1000 // fps) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_project_8()