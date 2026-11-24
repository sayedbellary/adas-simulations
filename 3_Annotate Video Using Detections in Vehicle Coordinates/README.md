# Project 3: Annotate Video Using Detections in Vehicle Coordinates

## Overview
This project converts object detections and lane markings from 3D vehicle coordinates (meters relative to ego vehicle) to 2D image coordinates (pixels). It displays live bounding boxes, distance overlays ($x, y$ in meters), and projected lane markings in real-time using monocular camera projection equations.

---

## Aim
To annotate a driving video with detected objects and lane boundaries by transforming detections from vehicle coordinates into image coordinates for accurate visualization.

---

## Objectives
- Apply monocular camera transformation parameters (`monoCamera` projection model).
- Transform 3D vehicle coordinates ($x, y$ in meters) to 2D pixel coordinates ($u, v$).
- Render parabolic lane boundaries and yellow object bounding boxes onto live video frames.
- Display dynamic coordinates ($x, y$) for each tracked object relative to the car.

---

## Folder Structure
```text
3_Annotate Video Using Detections in Vehicle Coordinates/
│
├── main.py        # Main execution script (Python + OpenCV GUI)
└── README.md      # Project documentation