import cv2
import numpy as np

def draw_car_right(img, x, y, color):
    """Draws a detailed vehicle moving right."""
    w, h = 90, 40
    # Main Body
    cv2.rectangle(img, (x - w, y - h), (x, y), color, -1)
    # Roof / Cabin
    cv2.rectangle(img, (x - int(w * 0.75), y - h - 20), (x - int(w * 0.25), y - h), (40, 40, 40), -1)
    # Windshield
    cv2.rectangle(img, (x - int(w * 0.35), y - h - 18), (x - int(w * 0.27), y - h - 2), (220, 220, 220), -1)
    # Headlights & Tail lights
    cv2.rectangle(img, (x - 4, y - h + 5), (x, y - h + 15), (0, 255, 255), -1)      # Yellow Headlight
    cv2.rectangle(img, (x - w, y - h + 5), (x - w + 4, y - h + 15), (0, 0, 255), -1) # Red Tail light
    # Wheels
    cv2.circle(img, (x - int(w * 0.75), y + 2), 8, (20, 20, 20), -1)
    cv2.circle(img, (x - int(w * 0.25), y + 2), 8, (20, 20, 20), -1)

def draw_car_left(img, x, y, color):
    """Draws a detailed vehicle moving left."""
    w, h = 90, 40
    # Main Body
    cv2.rectangle(img, (x, y - h), (x + w, y), color, -1)
    # Roof / Cabin
    cv2.rectangle(img, (x + int(w * 0.25), y - h - 20), (x + int(w * 0.75), y - h), (40, 40, 40), -1)
    # Windshield
    cv2.rectangle(img, (x + int(w * 0.27), y - h - 18), (x + int(w * 0.35), y - h - 2), (220, 220, 220), -1)
    # Headlights & Tail lights
    cv2.rectangle(img, (x, y - h + 5), (x + 4, y - h + 15), (0, 255, 255), -1)      # Yellow Headlight
    cv2.rectangle(img, (x + w - 4, y - h + 5), (x + w, y - h + 15), (0, 0, 255), -1) # Red Tail light
    # Wheels
    cv2.circle(img, (x + int(w * 0.25), y + 2), 8, (20, 20, 20), -1)
    cv2.circle(img, (x + int(w * 0.75), y + 2), 8, (20, 20, 20), -1)

def run_project_2():
    print("Running Project 2: Foreground Detection in Video Using Background Subtraction...")
    print("Press 'q' in the video window to exit.")

    width, height = 700, 400
    fps = 30
    frame_count = 0

    # Initialize MOG2 Background Subtractor
    backSub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=40, detectShadows=True)

    # Initial Vehicle Coordinates
    car1_x = 50
    car2_x = -250
    car_left_x = width + 100

    while True:
        frame_count += 1

        # 1. Generate Realistic Road Scene
        frame = np.full((height, width, 3), (100, 140, 100), dtype=np.uint8)  # Grass background
        cv2.rectangle(frame, (0, 80), (width, 320), (60, 60, 60), -1)         # Asphalt road surface
        cv2.line(frame, (0, 80), (width, 80), (255, 255, 255), 4)             # Top solid shoulder
        cv2.line(frame, (0, 320), (width, 320), (255, 255, 255), 4)            # Bottom solid shoulder

        # Animated Dashed Center Lane Line
        dash_offset = (frame_count * 10) % 40
        for x_pos in range(dash_offset - 40, width, 40):
            cv2.line(frame, (x_pos, 200), (x_pos + 20, 200), (0, 220, 255), 3)

        # 2. Render Moving Vehicles (Foreground Objects)
        car1_x = (car1_x + 6) % (width + 200)
        car2_x = (car2_x + 5) % (width + 200)
        car_left_x = (car_left_x - 4)
        if car_left_x < -150:
            car_left_x = width + 150

        draw_car_right(frame, car1_x, 290, (180, 40, 40))   # Red Car (Bottom Lane)
        draw_car_right(frame, car2_x, 290, (40, 80, 180))   # Blue Car (Bottom Lane)
        draw_car_left(frame, car_left_x, 160, (50, 150, 50)) # Green Car (Top Lane)

        # 3. MOG2 Background Subtraction Pipeline
        fgMask = backSub.apply(frame)

        # Morphological Filtering (Opening to remove noise, Closing to fill holes)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        fgMask_clean = cv2.morphologyEx(fgMask, cv2.MORPH_OPEN, kernel)
        fgMask_clean = cv2.morphologyEx(fgMask_clean, cv2.MORPH_CLOSE, kernel)

        # 4. Contour Extraction & Bounding Box Annotations
        contours, _ = cv2.findContours(fgMask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_vehicles = 0
        annotated_frame = frame.copy()

        for contour in contours:
            if cv2.contourArea(contour) > 800:  # Noise threshold
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Bounding Box Label Tag
                label = "Vehicle"
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
                cv2.rectangle(annotated_frame, (x, max(0, y - th - 6)), (x + tw + 4, y), (0, 255, 0), -1)
                cv2.putText(annotated_frame, label, (x + 2, max(th, y - 4)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
                detected_vehicles += 1

        # 5. Convert Binary Mask to 3-Channel Color for Split Display
        mask_bgr = cv2.cvtColor(fgMask_clean, cv2.COLOR_GRAY2BGR)

        # 6. Build Side-by-Side Dashboard View
        split_view = np.hstack((annotated_frame, mask_bgr))

        # HUD Telemetry Overlay
        overlay = split_view.copy()
        cv2.rectangle(overlay, (10, 10), (320, 65), (0, 0, 0), -1)
        cv2.rectangle(overlay, (width + 10, 10), (width + 280, 42), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.65, split_view, 0.35, 0, split_view)

        cv2.putText(split_view, "MOG2 Foreground Detection", (20, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        cv2.putText(split_view, f"Detected Vehicles: {detected_vehicles} | Frame: {frame_count}", (20, 52), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

        cv2.putText(split_view, "Binary Foreground Mask", (width + 20, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        # Divider Line between video streams
        cv2.line(split_view, (width, 0), (width, height), (0, 255, 255), 2)

        # Display Split View
        cv2.imshow("Project 2: Foreground Detection using Background Subtraction", split_view)

        if cv2.waitKey(1000 // fps) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_project_2()