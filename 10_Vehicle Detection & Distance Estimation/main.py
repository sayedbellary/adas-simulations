import cv2
import numpy as np

# Camera Parameters (Monocular Camera Model)
CAMERA = {
    'focal_length': 800.0,      # Focal length in pixels (fx = fy)
    'principal_point': (400, 240), # (cx, cy) Image center
    'height': 1.5,              # Camera mounting height in meters
    'car_real_width': 1.8,      # Average car width in meters
    'car_real_height': 1.5      # Average car height in meters
}

def draw_realistic_car(img, center, box_w, box_h, color):
    """Draws a rear-profile car inside the detected bounding box."""
    x_center, y_bottom = center
    x_min = x_center - box_w // 2
    y_min = y_bottom - box_h

    # Car Body
    body_h = int(box_h * 0.55)
    body_y_min = y_bottom - body_h
    cv2.rectangle(img, (x_min, body_y_min), (x_min + box_w, y_bottom), (60, 60, 60), -1)

    # Cabin / Roof
    roof_w = int(box_w * 0.75)
    roof_x_min = x_center - roof_w // 2
    cv2.rectangle(img, (roof_x_min, y_min), (roof_x_min + roof_w, body_y_min), (40, 40, 40), -1)

    # Rear Window
    win_w = int(roof_w * 0.8)
    win_h = int((body_y_min - y_min) * 0.6)
    win_x = x_center - win_w // 2
    win_y = y_min + int((body_y_min - y_min) * 0.2)
    cv2.rectangle(img, (win_x, win_y), (win_x + win_w, win_y + win_h), (200, 200, 200), -1)

    # Tail Lights
    light_w = max(3, int(box_w * 0.18))
    light_h = max(3, int(body_h * 0.25))
    light_y = body_y_min + int(body_h * 0.2)
    cv2.rectangle(img, (x_min + 3, light_y), (x_min + 3 + light_w, light_y + light_h), (0, 0, 255), -1)
    cv2.rectangle(img, (x_min + box_w - 3 - light_w, light_y), (x_min + box_w - 3, light_y + light_h), (0, 0, 255), -1)

    # License Plate
    plate_w = int(box_w * 0.3)
    plate_h = int(body_h * 0.2)
    cv2.rectangle(img, (x_center - plate_w//2, y_bottom - plate_h - 4), 
                  (x_center + plate_w//2, y_bottom - 4), (255, 255, 255), -1)

def run_project_7():
    print("Running Project 10: Vehicle Detection & Distance Estimation...")
    print("Press 'q' in the video window to exit.")

    width, height = 800, 480
    fps = 30
    horizon_y = int(height * 0.45)

    # Simulated surrounding vehicles moving in 3D world space (Longitudinal distance X, Lateral Y in meters)
    vehicles = [
        {'id': 1, 'x': 32.0, 'y': 0.0,  'speed': -0.15},  # Lead vehicle directly ahead
        {'id': 2, 'x': 45.0, 'y': 2.2,  'speed': -0.10},  # Vehicle in right lane
        {'id': 3, 'x': 25.0, 'y': -2.2, 'speed': -0.05}   # Vehicle in left lane
    ]

    frame_idx = 0

    while True:
        frame_idx += 1
        frame = np.full((height, width, 3), (110, 110, 110), dtype=np.uint8)

        # Draw Sky and Horizon
        frame[:horizon_y] = (200, 160, 110)

        # Draw 3D Perspective Highway
        road_pts = np.array([
            [0, height],
            [int(width * 0.40), horizon_y],
            [int(width * 0.60), horizon_y],
            [width, height]
        ], np.int32)
        cv2.fillPoly(frame, [road_pts], (60, 60, 60))

        # Lane Markings
        dash_offset = (frame_idx * 12) % 50
        for y_pos in range(horizon_y + dash_offset, height, 35):
            scale = (y_pos - horizon_y) / (height - horizon_y)
            cx = int(width * 0.5)
            lw = max(1, int(6 * scale))
            lh = max(2, int(15 * scale))
            cv2.line(frame, (cx, y_pos), (cx, min(height, y_pos + lh)), (255, 255, 255), lw)

        # Process and track vehicles
        for v in vehicles:
            # Update distance (simulate vehicle relative motion)
            v['x'] += v['speed']
            if v['x'] < 5.0:
                v['x'] = 50.0  # Reset once vehicle passes ego car

            x_m = v['x']  # Longitudinal distance in meters
            y_m = v['y']  # Lateral distance in meters

            # Pinhole Camera Projection: Convert 3D world meters to 2D image pixels
            f = CAMERA['focal_length']
            cx, cy = CAMERA['principal_point']

            # Pixel bounding box calculation based on distance
            box_w = max(16, int((CAMERA['car_real_width'] * f) / x_m))
            box_h = max(14, int((CAMERA['car_real_height'] * f) / x_m))

            u_center = int(cx + (y_m * f) / x_m)
            v_bottom = int(cy + (CAMERA['height'] * f) / x_m)

            x_min = u_center - box_w // 2
            y_min = v_bottom - box_h

            # Draw vehicle rear profile
            draw_realistic_car(frame, (u_center, v_bottom), box_w, box_h, (50, 50, 50))

            # Proximity Warning Color Logic
            if x_m < 12.0:
                color = (0, 0, 255)       # RED: CRITICAL / COLLISION WARNING
                status = "CRITICAL"
            elif x_m < 22.0:
                color = (0, 255, 255)     # YELLOW: CAUTION
                status = "CAUTION"
            else:
                color = (0, 255, 0)       # GREEN: SAFE
                status = "SAFE"

            # Draw Bounding Box around vehicle
            cv2.rectangle(frame, (x_min, y_min), (x_min + box_w, v_bottom), color, 2)

            # Distance Label ($X$ distance, $Y$ offset)
            label = f"ID:{v['id']} Dist:{x_m:.1f}m ({status})"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
            text_y = max(th + 4, y_min - 6)

            cv2.rectangle(frame, (x_min, text_y - th - 4), (x_min + tw + 4, text_y + 2), color, -1)
            cv2.putText(frame, label, (x_min + 2, text_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 1)

        # Telemetry Dashboard
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (320, 75), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        cv2.putText(frame, "Vehicle Distance Estimation", (20, 32), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        cv2.putText(frame, f"Tracked Vehicles: {len(vehicles)}", (20, 55), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.imshow("Vehicle Detection & Distance Estimation", frame)

        if cv2.waitKey(1000 // fps) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_project_7()