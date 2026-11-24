import cv2
import numpy as np
import time

class LaneDetection:
    def __init__(self):
        self.threshold = 50.0  # Pixel threshold for lane departure alert
        self.warning_time = 0
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0.0

    def roi(self, img):
        """Applies Region of Interest (ROI) mask to focus on road area."""
        h, w = img.shape[:2]
        pts = np.array([[
            (int(w * 0.1), int(h * 0.95)),
            (int(w * 0.4), int(h * 0.6)),
            (int(w * 0.6), int(h * 0.6)),
            (int(w * 0.9), int(h * 0.95))
        ]], np.int32)
        
        mask = np.zeros_like(img)
        cv2.fillPoly(mask, pts, 255)
        return cv2.bitwise_and(img, mask), pts

    def color_filter(self, img):
        """Isolates white and yellow lane markings in HLS color space."""
        hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
        white = cv2.inRange(hls, (0, 180, 0), (255, 255, 255))
        yellow = cv2.inRange(hls, (15, 30, 115), (35, 204, 255))
        return cv2.bitwise_or(white, yellow)

    def average_line(self, lines, h):
        """Fits a smooth line equation y = m*x + b to detected line segments."""
        if not lines:
            return None
        xs, ys = [], []
        for l in lines:
            x1, y1, x2, y2 = l
            xs += [x1, x2]
            ys += [y1, y2]
        if len(xs) < 2:
            return None
        m, b = np.polyfit(ys, xs, 1)
        return [(int(m * h + b), h), (int(m * h * 0.6 + b), int(h * 0.6))]

    def generate_realistic_road(self, h, w, frame_idx):
        """Generates realistic highway road background with moving lane markings."""
        img = np.zeros((h, w, 3), dtype=np.uint8)
        img[:int(h*0.55)] = (180, 140, 100) # Soft horizon background
        img[int(h*0.55):] = (70, 70, 70)    # Dark asphalt surface

        # Draw perspective side grass borders
        left_grass = np.array([[0, int(h*0.55)], [int(w*0.25), int(h*0.55)], [0, h]], np.int32)
        right_grass = np.array([[w, int(h*0.55)], [int(w*0.75), int(h*0.55)], [w, h]], np.int32)
        cv2.fillPoly(img, [left_grass], (30, 80, 30))
        cv2.fillPoly(img, [right_grass], (30, 80, 30))

        # Ego vehicle lateral sway simulation
        drift = int(12 * np.sin(frame_idx * 0.05))

        # Solid Left White Boundary
        cv2.line(img, (int(w*0.28) + drift, int(h*0.6)), (int(w*0.12) + drift, h), (255, 255, 255), 8)
        
        # Solid Right Yellow Boundary
        cv2.line(img, (int(w*0.72) + drift, int(h*0.6)), (int(w*0.88) + drift, h), (0, 220, 255), 8)

        # Animated Dashed Center Lane Marking
        dash_offset = (frame_idx * 15) % 60
        for y_pos in range(int(h*0.6) + dash_offset, h, 40):
            scale = (y_pos - h*0.55) / (h*0.45)
            x_pos = int(w*0.5 + drift * scale)
            length = int(15 * scale)
            cv2.line(img, (x_pos, y_pos), (x_pos, min(h, y_pos + length)), (255, 255, 255), max(2, int(4*scale)))

        return img, drift

    def process(self, frame, frame_idx):
        h, w = frame.shape[:2]

        # 1. Pipeline Processing
        mask = self.color_filter(frame)
        edges = cv2.Canny(mask, 50, 150)
        roi_edges, roi_pts = self.roi(edges)

        # Hough transform line detection
        lines = cv2.HoughLinesP(roi_edges, 1, np.pi / 180, 20, minLineLength=30, maxLineGap=100)
        
        left, right = [], []
        if lines is not None:
            for l in lines:
                # Safe unpacking regardless of HoughLinesP shape variation
                coords = l[0] if len(l.shape) > 1 else l
                x1, y1, x2, y2 = coords
                
                if x2 - x1 == 0:
                    continue
                slope = (y2 - y1) / (x2 - x1)
                if abs(slope) > 0.3:
                    (left if slope < 0 else right).append((x1, y1, x2, y2))

        L = self.average_line(left, h)
        R = self.average_line(right, h)

        # Calculate deviation from lane center
        if L and R:
            lane_center = (L[0][0] + R[0][0]) // 2
        else:
            lane_center = w // 2

        image_center = w // 2
        dev = float(lane_center - image_center)

        # 2. Overlay Detected Lanes
        if L:
            cv2.line(frame, L[0], L[1], (0, 255, 0), 4)       # Left detected lane (Green)
        if R:
            cv2.line(frame, R[0], R[1], (0, 255, 255), 4)     # Right detected lane (Yellow)

        # Draw vehicle position vs lane center marker
        cv2.line(frame, (lane_center, h), (lane_center, int(h * 0.7)), (255, 0, 0), 3)
        cv2.line(frame, (image_center, h), (image_center, int(h * 0.7)), (255, 255, 255), 2)
        cv2.circle(frame, (image_center, int(h * 0.9)), 8, (255, 0, 0), -1)

        # Draw ROI Boundary Polygon
        cv2.polylines(frame, roi_pts, True, (0, 165, 255), 2)

        # 3. Telemetry Overlay Dashboard
        self.frame_count += 1
        if time.time() - self.start_time >= 1.0:
            self.fps = self.frame_count / (time.time() - self.start_time)
            self.frame_count = 0
            self.start_time = time.time()

        status = "WARNING" if abs(dev) > self.threshold else "NORMAL"
        
        # Transparent Telemetry Box
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (320, 130), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        cv2.putText(frame, "Lane Detection System", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Deviation: {dev:.1f} pixels", (20, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Threshold: {self.threshold:.0f} pixels", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        status_color = (0, 0, 255) if status == "WARNING" else (0, 255, 0)
        cv2.putText(frame, f"Status: {status}", (20, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (w - 120, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Large Lane Departure Alert Box
        if abs(dev) > self.threshold and time.time() - self.warning_time > 1.5:
            cv2.putText(frame, "LANE DEPARTURE!", (int(w*0.25), 60), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 255), 3)
            self.warning_time = time.time()

        return frame

    def run(self):
        print("Running Project 5: Lane Detection & Monitoring...")
        print("Press 'q' in the video window to exit.")

        width, height = 640, 480
        frame_idx = 0

        while True:
            frame_idx += 1
            road_frame, _ = self.generate_realistic_road(height, width, frame_idx)
            processed_frame = self.process(road_frame, frame_idx)

            cv2.imshow("Lane Detection & Monitoring", processed_frame)

            if cv2.waitKey(30) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

if __name__ == "__main__":
    LaneDetection().run()