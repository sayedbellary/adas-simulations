import cv2
import numpy as np

def vehicle_to_image(x_veh, y_veh, camera_matrix):
    """
    Transforms vehicle coordinates (meters) to image coordinates (pixels).
    """
    f_x, f_y = camera_matrix['focal_length']
    c_x, c_y = camera_matrix['principal_point']
    x_veh = max(x_veh, 0.1)  # Avoid division by zero
    
    u = int(c_x - (y_veh * f_x) / x_veh)
    v = int(c_y + (camera_matrix['height'] * f_y) / x_veh)
    return u, v

def draw_person_shape(frame, x_min, y_min, box_w, box_h, color=(0, 255, 255)):
    """
    Draws a person stick figure (head, body, arms, legs).
    """
    center_x = x_min + box_w // 2
    head_radius = max(3, box_w // 3)
    head_center = (center_x, y_min + head_radius + 2)
    
    # Head
    cv2.circle(frame, head_center, head_radius, color, 2)
    
    # Torso
    neck_y = head_center[1] + head_radius
    hip_y = y_min + int(box_h * 0.65)
    cv2.line(frame, (center_x, neck_y), (center_x, hip_y), color, 2)
    
    # Arms
    arm_y = neck_y + int((hip_y - neck_y) * 0.3)
    arm_span = max(4, box_w // 2)
    cv2.line(frame, (center_x - arm_span, arm_y + 4), (center_x + arm_span, arm_y + 4), color, 2)
    
    # Legs
    foot_y = y_min + box_h
    leg_span = max(4, box_w // 2)
    cv2.line(frame, (center_x, hip_y), (center_x - leg_span, foot_y), color, 2)
    cv2.line(frame, (center_x, hip_y), (center_x + leg_span, foot_y), color, 2)

def draw_car_shape(frame, x_min, y_min, box_w, box_h, color=(0, 255, 255)):
    """
    Draws a car profile (body, roof, windshield, and wheels).
    """
    # Car Body
    body_y_min = y_min + int(box_h * 0.4)
    cv2.rectangle(frame, (x_min, body_y_min), (x_min + box_w, y_min + box_h - 4), color, 2)
    
    # Roof / Cabin
    roof_margin = max(2, box_w // 5)
    pts = np.array([
        [x_min + roof_margin, body_y_min],
        [x_min + roof_margin + 4, y_min + 2],
        [x_min + box_w - roof_margin - 4, y_min + 2],
        [x_min + box_w - roof_margin, body_y_min]
    ], np.int32)
    cv2.polylines(frame, [pts], True, color, 2)
    
    # Wheels
    wheel_radius = max(2, box_h // 6)
    wheel_y = y_min + box_h - wheel_radius
    cv2.circle(frame, (x_min + int(box_w * 0.25), wheel_y), wheel_radius, color, -1)
    cv2.circle(frame, (x_min + int(box_w * 0.75), wheel_y), wheel_radius, color, -1)

def run_project_4():
    print("Running Project 4: Track Pedestrians from a Moving Car...")
    print("Press 'q' in the video window to exit.")

    width, height = 800, 450
    fps = 30

    camera_matrix = {
        'focal_length': (800, 800),
        'principal_point': (width // 2, height // 2),
        'height': 1.45
    }

    # Objects in 3D vehicle coordinates
    pedestrians = [
        {'id': 1, 'x': 25.0, 'y': -2.5, 'vx': -0.12, 'w': 0.6, 'h': 1.7, 'type': 'Pedestrian'},
        {'id': 2, 'x': 18.0, 'y': -3.0, 'vx': -0.10, 'w': 0.6, 'h': 1.6, 'type': 'Pedestrian'},
        {'id': 3, 'x': 20.0, 'y': 1.8,  'vx': -0.15, 'w': 1.8, 'h': 1.4, 'type': 'Car'},
        {'id': 4, 'x': 30.0, 'y': -0.5, 'vx': -0.18, 'w': 1.8, 'h': 1.4, 'type': 'Car'}
    ]

    while True:
        frame = np.full((height, width, 3), (110, 110, 110), dtype=np.uint8)

        # Draw left (dashed red) and right (solid green) lane boundaries
        x_pts = np.linspace(1, 40, 100)
        left_lane, right_lane = [], []
        for x in x_pts:
            u_l, v_l = vehicle_to_image(x, 1.75, camera_matrix)
            u_r, v_r = vehicle_to_image(x, -1.75, camera_matrix)
            if 0 <= u_l < width and 0 <= v_l < height:
                left_lane.append((u_l, v_l))
            if 0 <= u_r < width and 0 <= v_r < height:
                right_lane.append((u_r, v_r))

        if len(left_lane) > 1:
            for i in range(0, len(left_lane) - 1, 2):
                cv2.line(frame, left_lane[i], left_lane[i+1], (0, 0, 255), 2)
        if len(right_lane) > 1:
            cv2.polylines(frame, [np.array(right_lane, np.int32)], False, (0, 255, 0), 2)

        # Update position and draw custom shapes
        for p in pedestrians:
            p['x'] += p['vx']
            if p['x'] < 2.5:
                p['x'] = 35.0

            u, v = vehicle_to_image(p['x'], p['y'], camera_matrix)

            aspect_ratio = 3.0 if p['type'] == 'Pedestrian' else 0.85
            box_w = max(14, int((p['w'] * camera_matrix['focal_length'][0]) / p['x']))
            box_h = int(box_w * aspect_ratio)

            x_min = max(0, u - box_w // 2)
            y_min = max(0, v - box_h)

            # Draw outer yellow bounding box
            cv2.rectangle(frame, (x_min, y_min), (x_min + box_w, y_min + box_h), (0, 255, 255), 1)

            # Draw specific shape based on type
            if p['type'] == 'Pedestrian':
                draw_person_shape(frame, x_min, y_min, box_w, box_h, color=(0, 255, 255))
            else:
                draw_car_shape(frame, x_min, y_min, box_w, box_h, color=(0, 255, 255))

            # Label class name
            label = f"{p['type']}"
            text_y = max(20, y_min - 5)
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            cv2.rectangle(frame, (x_min, text_y - th - 2), (x_min + tw, text_y + 2), (0, 255, 255), -1)
            cv2.putText(frame, label, (x_min, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)

        # Display window
        cv2.imshow("Track Pedestrians from a Moving Car", frame)

        if cv2.waitKey(1000 // fps) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_project_4()