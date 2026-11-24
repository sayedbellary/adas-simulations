# Project 10: Vehicle Detection & Distance Estimation

## Overview
This project detects lead and surrounding vehicles on a highway and calculates their real-time longitudinal distance ($X$ in meters) and lateral displacement ($Y$ in meters) relative to the ego vehicle using a monocular camera pinhole projection model. It also applies dynamic color-coded proximity alerts (Green for Safe, Yellow for Caution, and Red for Critical).

---

## Aim
To detect vehicles in video frames, estimate their real-world 3D spatial distances ($X, Y$ in meters) using monocular camera geometry, and trigger collision warnings based on proximity thresholds.

---

## Objectives
- Implement monocular camera intrinsic projection equations ($u = c_x + \frac{Y \cdot f}{X}$, $v = c_y + \frac{H \cdot f}{X}$).
- Estimate physical vehicle bounding box dimensions dynamically from 3D coordinates.
- Calculate real-world longitudinal distance ($X$) to lead vehicles.
- Implement proximity warning thresholds (**Safe** $>22$m, **Caution** $12-22$m, **Critical** $<12$m).

---

## Folder Structure
```text
10_Vehicle Detection & Distance Estimation/
│
├── main.py        # Main execution script (Python + OpenCV GUI)
└── README.md      # Project documentation