import cv2
import numpy as np

def draw_car(img, center, size, color, label=""):
    """Draws a top-down view of a vehicle with orientation and label."""
    x, y = center
    w, h = size
    
    # Body
    cv2.rectangle(img, (x - w//2, y - h//2), (x + w//2, y + h//2), color, -1)
    cv2.rectangle(img, (x - w//2, y - h//2), (x + w//2, y + h//2), (255, 255, 255), 1)
    
    # Windshield
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

def run_project_9():
    print("Running Project 9: Blind Spot Detection (BSD)...")
    print("Press 'q' in the video window to exit.")

    width, height = 800, 500
    fps = 30

    lane_width = 110
    center_x = width // 2
    
    # Ego vehicle position (Center Lane)
    ego_x = center_x
    ego_y = 260
    
    # Target vehicles overtaking in Left and Right lanes
    left_target_y = 480   # Starts behind ego vehicle in left lane
    right_target_y = -60  # Starts ahead of ego vehicle in right lane

    frame_idx = 0

    while True:
        frame_idx += 1
        frame = np.full((height, width, 3), (35, 35, 35), dtype=np.uint8)

        # Draw 3 Highway Lanes
        for i in range(4):
            x_line = center_x - int(1.5 * lane_width) + i * lane_width
            if i == 0 or i == 3:
                cv2.line(frame, (x_line, 0), (x_line, height), (255, 255, 255), 3)
            else:
                dash_offset = (frame_idx * 10) % 40
                for y_dash in range(dash_offset - 40, height, 40):
                    cv2.line(frame, (x_line, y_dash), (x_line, y_dash + 20), (255, 255, 255), 2)

        # Update overtaking vehicles positions
        left_target_y -= 2.5
        if left_target_y < -80:
            left_target_y = 520

        right_target_y += 2.0
        if right_target_y > 560:
            right_target_y = -80

        left_x = center_x - lane_width
        right_x = center_x + lane_width

        # Define Blind Spot Zones (Left and Right adjacent rear zones)
        left_bs_zone = (left_x - 45, ego_y - 20, left_x + 45, ego_y + 110)
        right_bs_zone = (right_x - 45, ego_y - 20, right_x + 45, ego_y + 110)

        # Check if vehicles are inside Blind Spot Zones
        left_bsd_alert = (left_bs_zone[1] <= left_target_y <= left_bs_zone[3])
        right_bsd_alert = (right_bs_zone[1] <= right_target_y <= right_bs_zone[3])

        # Draw Blind Spot Monitoring Radar Zones (Translucent Fill)
        overlay = frame.copy()
        left_zone_color = (0, 0, 255) if left_bsd_alert else (0, 200, 255)
        right_zone_color = (0, 0, 255) if right_bsd_alert else (0, 200, 255)

        cv2.rectangle(overlay, (left_bs_zone[0], left_bs_zone[1]), (left_bs_zone[2], left_bs_zone[3]), left_zone_color, -1)
        cv2.rectangle(overlay, (right_bs_zone[0], right_bs_zone[1]), (right_bs_zone[2], right_bs_zone[3]), right_zone_color, -1)
        cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)

        # Zone Outlines
        cv2.rectangle(frame, (left_bs_zone[0], left_bs_zone[1]), (left_bs_zone[2], left_bs_zone[3]), left_zone_color, 2)
        cv2.rectangle(frame, (right_bs_zone[0], right_bs_zone[1]), (right_bs_zone[2], right_bs_zone[3]), right_zone_color, 2)

        # Draw Side Mirrors with Active BSD Indicators
        # Left Mirror
        mirror_color_l = (0, 0, 255) if left_bsd_alert else (100, 100, 100)
        cv2.circle(frame, (ego_x - 28, ego_y - 15), 8, mirror_color_l, -1)
        cv2.circle(frame, (ego_x - 28, ego_y - 15), 8, (255, 255, 255), 1)

        # Right Mirror
        mirror_color_r = (0, 0, 255) if right_bsd_alert else (100, 100, 100)
        cv2.circle(frame, (ego_x + 28, ego_y - 15), 8, mirror_color_r, -1)
        cv2.circle(frame, (ego_x + 28, ego_y - 15), 8, (255, 255, 255), 1)

        # Draw Vehicles
        draw_car(frame, (ego_x, ego_y), (36, 60), (0, 180, 0), "Ego Vehicle")
        draw_car(frame, (left_x, int(left_target_y)), (34, 55), (180, 50, 50), "Target Left")
        draw_car(frame, (right_x, int(right_target_y)), (34, 55), (50, 100, 180), "Target Right")

        # Telemetry Dashboard
        dash_overlay = frame.copy()
        cv2.rectangle(dash_overlay, (10, 10), (420, 110), (0, 0, 0), -1)
        cv2.addWeighted(dash_overlay, 0.65, frame, 0.35, 0, frame)

        cv2.putText(frame, "Blind Spot Detection (BSD)", (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        
        status_l_text = "WARNING: VEHICLE IN LEFT BLIND SPOT!" if left_bsd_alert else "Left Blind Spot: CLEAR"
        color_l = (0, 0, 255) if left_bsd_alert else (0, 255, 0)
        cv2.putText(frame, status_l_text, (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color_l, 2 if left_bsd_alert else 1)

        status_r_text = "WARNING: VEHICLE IN RIGHT BLIND SPOT!" if right_bsd_alert else "Right Blind Spot: CLEAR"
        color_r = (0, 0, 255) if right_bsd_alert else (0, 255, 0)
        cv2.putText(frame, status_r_text, (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color_r, 2 if right_bsd_alert else 1)

        cv2.imshow("Blind Spot Detection (BSD)", frame)

        if cv2.waitKey(1000 // fps) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_project_9()