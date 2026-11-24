# Project 4: Track Pedestrians from a Moving Car

## Overview
This project detects and tracks multiple pedestrians and surrounding vehicles from a camera mounted on a moving ego-vehicle. It estimates real-world object distances, maintains continuous track continuity using motion prediction, and overlays dynamic bounding boxes with aspect ratio scaling onto the live frame.

---

## Aim
To detect and track pedestrians and vehicles using a monocular camera on a moving car, maintaining robust tracking and distance estimation across frames.

---

## Objectives
- Model monocular camera intrinsics and mounting extrinsics (`setupMonoCamera`).
- Convert 3D world detections into image-space coordinates (`vehicleToImage`).
- Implement aspect-ratio based bounding box generation (3:1 ratio for pedestrians, 0.85 for vehicles).
- Annotate tracked pedestrians and vehicles alongside left (dashed) and right (solid) lane boundaries.

---

## Folder Structure
```text
4_Track Pedestrians from a Moving Car/
│
├── main.py        # Main execution script (Python + OpenCV GUI)
└── README.md      # Project documentation