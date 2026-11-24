# Project 2: Foreground Detection in Video Using Background Subtraction

## Overview
This project isolates moving vehicles from a static background video feed using background subtraction techniques in OpenCV. It models the background, filters out noise blobs, and overlays bounding boxes around detected moving objects in real-time.

---

## Aim
To detect and highlight moving vehicles in a video stream by separating foreground objects from the static background and displaying bounding boxes around detections.

---

## Objectives
- Implement a background subtractor (`MOG2`) to construct a background model.
- Apply morphological operations (`bwareaopen` equivalent) to filter out small noise artifacts.
- Extract bounding boxes for detected vehicles and render them onto the original video stream.

---

## Folder Structure
```text
2_Foreground Detection in Video Using Background Subtraction/
│
├── main.py        # Main execution script (Python + OpenCV)
└── README.md      # Project documentation