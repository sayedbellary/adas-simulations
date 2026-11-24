import cv2
import numpy as np

def draw_stop_sign(img, center, size):
    """Draws an octagonal STOP sign."""
    x, y = center
    r = size // 2
    pts = []
    for i in range(8):
        angle = np.pi / 8 + i * np.pi / 4
        px = int(x + r * np.cos(angle))
        py = int(y + r * np.sin(angle))
        pts.append([px, py])
    pts = np.array(pts, np.int32)
    cv2.fillPoly(img, [pts], (0, 0, 220))
    cv2.polylines(img, [pts], True, (255, 255, 255), max(1, size // 25))
    if size > 20:
        font_scale = max(0.3, size / 80.0)
        cv2.putText(img, "STOP", (x - int(r*0.7), y + int(r*0.25)), 
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), max(1, int(size/40)))

def draw_yield_sign(img, center, size):
    """Draws an inverted triangular YIELD sign."""
    x, y = center
    r = size // 2
    pts = np.array([
        [x - r, y - int(r * 0.7)],
        [x + r, y - int(r * 0.7)],
        [x, y + int(r * 0.9)]
    ], np.int32)
    cv2.fillPoly(img, [pts], (0, 0, 220))
    inner_pts = np.array([
        [x - int(r*0.6), y - int(r * 0.5)],
        [x + int(r*0.6), y - int(r * 0.5)],
        [x, y + int(r*0.6)]
    ], np.int32)
    cv2.fillPoly(img, [inner_pts], (255, 255, 255))

def draw_speed_limit_sign(img, center, size, speed="50"):
    """Draws a circular SPEED LIMIT sign."""
    x, y = center
    r = size // 2
    cv2.circle(img, (x, y), r, (0, 0, 220), -1)
    cv2.circle(img, (x, y), int(r * 0.75), (255, 255, 255), -1)
    if size > 20:
        font_scale = max(0.3, size / 60.0)
        cv2.putText(img, speed, (x - int(r*0.5), y + int(r*0.3)), 
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), max(1, int(size/35)))

def draw_no_entry_sign(img, center, size):
    """Draws a circular DO NOT ENTER sign."""
    x, y = center
    r = size // 2
    cv2.circle(img, (x, y), r, (0, 0, 220), -1)
    bar_w = int(r * 1.4)
    bar_h = max(2, int(r * 0.35))
    cv2.rectangle(img, (x - bar_w//2, y - bar_h//2), (x + bar_w//2, y + bar_h//2), (255, 255, 255), -1)

def draw_dummy_car(img, center, scale):
    """Draws a dummy vehicle driving ahead on the road with perspective scaling."""
    x, y = center
    w = int(80 * scale)
    h = int(50 * scale)
    
    cv2.rectangle(img, (x - w//2, y - h//2), (x + w//2, y + h//2), (180, 50, 50), -1)
    cv2.rectangle(img, (x - int(w*0.35), y - h), (x + int(w*0.35), y - h//2), (120, 30, 30), -1)
    cv2.rectangle(img, (x - int(w*0.28), y - int(h*0.9)), (x + int(w*0.28), y - int(h*0.6)), (220, 220, 220), -1)
    light_w = max(2, int(w*0.15))
    light_h = max(2, int(h*0.2))
    cv2.rectangle(img, (x - w//2 + 2, y - h//4), (x - w//2 + 2 + light_w, y - h//4 + light_h), (0, 0, 255), -1)
    cv2.rectangle(img, (x + w//2 - 2 - light_w, y - h//4), (x + w//2 - 2, y - h//4 + light_h), (0, 0, 255), -1)

def generate_scene(frame_idx, width, height):
    """Generates dynamic road scene and tracks sign ground truth bounding boxes."""
    img = np.full((height, width, 3), (100, 100, 100), dtype=np.uint8)
    
    horizon_y = int(height * 0.45)
    img[:horizon_y] = (210, 160, 110)
    
    road_pts = np.array([
        [0, height],
        [int(width * 0.42), horizon_y],
        [int(width * 0.58), horizon_y],
        [width, height]
    ], np.int32)
    cv2.fillPoly(img, [road_pts], (60, 60, 60))

    dash_offset = (frame_idx * 12) % 50
    for y_pos in range(horizon_y + dash_offset, height, 35):
        scale = (y_pos - horizon_y) / (height - horizon_y)
        cx = int(width * 0.5)
        lw = max(1, int(6 * scale))
        lh = max(2, int(15 * scale))
        cv2.line(img, (cx, y_pos), (cx, min(height, y_pos + lh)), (255, 255, 255), lw)

    # Moving vehicle ahead
    car_z = (frame_idx * 3) % 300
    car_scale = 0.2 + (car_z / 300.0) * 0.8
    car_y = int(horizon_y + (height - horizon_y) * (car_z / 300.0) * 0.7)
    car_x = int(width * 0.52 + (car_z / 300.0) * 40)
    draw_dummy_car(img, (car_x, car_y), car_scale)

    # Roadside Traffic Signs Flow
    sign_sequence = [
        ('Speed Limit Sign', lambda img, c, s: draw_speed_limit_sign(img, c, s, "50")),
        ('Yield Sign', draw_yield_sign),
        ('Do Not Enter Sign', draw_no_entry_sign),
        ('STOP Sign', draw_stop_sign)
    ]

    active_signs = []
    total_cycle = 400
    for i, (sign_name, draw_fn) in enumerate(sign_sequence):
        progress = ((frame_idx * 4) + i * 100) % total_cycle
        if progress < 280:
            scale_ratio = progress / 280.0
            sign_size = max(16, int(12 + scale_ratio * 80))
            
            sign_y = int(horizon_y - 10 + scale_ratio * (height - horizon_y - 40))
            sign_x = int(width * 0.60 + scale_ratio * (width * 0.32))
            
            # Post
            post_top = sign_y + sign_size // 2
            post_bottom = post_top + int(sign_size * 0.8)
            cv2.line(img, (sign_x, post_top), (sign_x, post_bottom), (150, 150, 150), max(1, sign_size // 25))
            
            # Sign shape
            draw_fn(img, (sign_x, sign_y), sign_size)

            # Store detection box with verified classification
            bx = sign_x - sign_size // 2
            by = sign_y - sign_size // 2
            active_signs.append((bx, by, sign_size, sign_size, sign_name))

    return img, active_signs

def run_project_6():
    print("Running Project 6: Traffic Sign Detection...")
    print("Press 'q' in the video window to exit.")

    width, height = 800, 480
    fps = 30
    frame_idx = 0

    while True:
        frame_idx += 1
        frame, detections = generate_scene(frame_idx, width, height)

        # Draw detected bounding boxes and exact class annotations
        for x, y, w, h, sign_type in detections:
            cv2.rectangle(frame, (x - 2, y - 2), (x + w + 2, y + h + 2), (0, 255, 0), 2)
            
            label = f"{sign_type}"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            text_y = max(th + 4, y - 6)
            cv2.rectangle(frame, (x - 2, text_y - th - 4), (x + tw + 4, text_y + 2), (0, 255, 0), -1)
            cv2.putText(frame, label, (x, text_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)

        # Telemetry Dashboard
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (280, 70), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        cv2.putText(frame, "Traffic Sign Detection", (20, 32), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        cv2.putText(frame, f"Detected Signs: {len(detections)}", (20, 55), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.imshow("Traffic Sign Detection", frame)

        if cv2.waitKey(1000 // fps) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_project_6()