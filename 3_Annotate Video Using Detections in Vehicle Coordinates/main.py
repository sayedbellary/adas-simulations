import cv2
import numpy as np

def vehicle_to_image(x_veh, y_veh, camera_matrix):
    """
    Transforms vehicle/world coordinates (in meters) to image coordinates (pixels)
    using a monocular camera projection model.
    """
    f_x, f_y = camera_matrix['focal_length']
    c_x, c_y = camera_matrix['principal_point']
    
    # Avoid division by zero
    x_veh = max(x_veh, 0.1)
    
    u = int(c_x - (y_veh * f_x) / x_veh)
    v = int(c_y + (camera_matrix['height'] * f_y) / x_veh)
    return u, v

def run_project_3():
    print("Running Project 3: Annotate Video Using Detections in Vehicle Coordinates...")
    print("Press 'q' in the video window to exit.")

    width, height = 800, 450
    fps = 30
    
    # Monocular camera parameters
    camera_matrix = {
        'focal_length': (800, 800),
        'principal_point': (width // 2, height // 2),
        'height': 1.5  # Camera mounting height in meters
    }

    # Objects in vehicle coordinates (X = distance ahead, Y = lateral offset)
    tracked_objects = [
        {'id': 1, 'class': 'Pedestrian', 'x': 28.0, 'y': -2.2, 'w': 0.6, 'h': 1.7},
        {'id': 2, 'class': 'Car', 'x': 22.0, 'y': 1.5, 'w': 1.8, 'h': 1.5},
        {'id': 3, 'class': 'Pedestrian', 'x': 14.0, 'y': -1.2, 'w': 0.5, 'h': 1.6}
    ]

    while True:
        # Base road frame setup
        frame = np.full((height, width, 3), (100, 100, 100), dtype=np.uint8)
        
        # Draw parabolic lane boundaries projected from 3D vehicle coordinates
        x_pts = np.linspace(1, 40, 100)
        left_lane_pts = []
        right_lane_pts = []
        
        for x in x_pts:
            u_l, v_l = vehicle_to_image(x, 1.75, camera_matrix)
            u_r, v_r = vehicle_to_image(x, -1.75, camera_matrix)
            
            if 0 <= u_l < width and 0 <= v_l < height:
                left_lane_pts.append((u_l, v_l))
            if 0 <= u_r < width and 0 <= v_r < height:
                right_lane_pts.append((u_r, v_r))
                
        if len(left_lane_pts) > 1:
            cv2.polylines(frame, [np.array(left_lane_pts, np.int32)], False, (0, 0, 255), 2)
        if len(right_lane_pts) > 1:
            cv2.polylines(frame, [np.array(right_lane_pts, np.int32)], False, (0, 255, 0), 2)

        # Update and annotate tracked objects
        for idx, obj in enumerate(tracked_objects):
            # Move objects toward vehicle (simulate forward motion)
            obj['x'] -= 0.15
            if obj['x'] < 3.0:
                obj['x'] = 32.0  # Reset object position once passed

            # Project vehicle 3D coordinates into 2D image coordinates
            u, v = vehicle_to_image(obj['x'], obj['y'], camera_matrix)
            
            # Estimate bounding box width/height in pixel space
            box_w = int((obj['w'] * camera_matrix['focal_length'][0]) / obj['x'])
            box_h = int((obj['h'] * camera_matrix['focal_length'][1]) / obj['x'])
            
            x_min = max(0, u - box_w // 2)
            y_min = max(0, v - box_h)
            
            # Draw yellow bounding box around detection
            cv2.rectangle(frame, (x_min, y_min), (x_min + box_w, y_min + box_h), (0, 255, 255), 2)
            
            # Formulate text label with clean offset to prevent overlap
            label = f"{obj['class']} x={obj['x']:.1f}m, y={obj['y']:.1f}m"
            text_y = max(20, y_min - 10 - (idx * 15))
            
            # Filled background box for clear text readability
            (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            cv2.rectangle(frame, (x_min, text_y - text_h - 2), (x_min + text_w, text_y + 2), (0, 0, 0), -1)
            cv2.putText(frame, label, (x_min, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

        # Display live window
        cv2.imshow("Annotate Video Using Detections in Vehicle Coordinates", frame)

        if cv2.waitKey(1000 // fps) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_project_3()