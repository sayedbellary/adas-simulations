# Project 6: Traffic Sign Detection & Classification

## Overview
This project detects, isolates, and accurately classifies multiple regulatory traffic signs (such as **STOP**, **Speed Limit 50**, **Yield**, and **Do Not Enter** signs) in a dynamic 3D roadside perspective feed using HSV color space segmentation, shape geometry analysis, and real-time bounding box annotations.

---

## Aim
To detect and classify roadside traffic signs in real time while estimating their motion relative to an ego vehicle for driver assistance and autonomous driving systems.

---

## Objectives
- Isolate red traffic sign regions using dual-range HSV color thresholding.
- Render dynamic 3D perspective road flow with roadside sign posts and preceding vehicle traffic.
- Accurately classify sign geometries (**Octagon** for STOP, **Inverted Triangle** for Yield, **Circle with inner ring** for Speed Limit, and **Circle with horizontal bar** for Do Not Enter).
- Draw live bounding boxes with high-contrast text labels and display a telemetry dashboard counting active detections.

---

## Folder Structure
```text
6_Traffic Sign Detection/
│
├── main.py        # Main execution script (Python + OpenCV GUI)
└── README.md      # Project documentation