# Project 5: Lane Detection & Monitoring

## Overview
This project isolates road lane boundaries, calculates vehicle center deviation, and provides real-time Lane Departure Warnings (LDWS) using classical computer vision techniques (HLS color space filtering, Canny edge detection, Region of Interest masking, and Hough Line Transforms).

---

## Aim
To detect and monitor lane boundaries on roads using computer vision techniques, and provide real-time lane departure warnings for driver assistance systems.

---

## Objectives
- Isolate white and yellow lane markings in HLS color space.
- Apply a Region of Interest (ROI) perspective mask to restrict detection to the road surface.
- Perform Canny Edge Detection and Progressive Probabilistic Hough Line Transform (`cv2.HoughLinesP`).
- Safely extract line coordinates across diverse OpenCV environments and fit lane boundary equations.
- Calculate lateral vehicle deviation from the lane center and trigger real-time `LANE DEPARTURE!` visual warnings.

---

## Folder Structure
```text
5_Lane Detection & Monitoring/
│
├── main.py        # Main execution script (Python + OpenCV GUI)
└── README.md      # Project documentation