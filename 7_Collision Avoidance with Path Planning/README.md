# Project 7: Collision Avoidance with Path Planning

## Overview
This project simulates real-time ADAS collision avoidance and path planning algorithms. When an obstacle vehicle is detected in the ego-vehicle's path, the system dynamically calculates a smooth lane-change trajectory to avoid collision and executes an overtake maneuver.

---

## Aim
To implement a collision avoidance and local path planning system that monitors obstacle distance and generates real-time trajectory steering paths around obstacles.

---

## Objectives
- Detect distance to stationary or slow-moving obstacles in the vehicle's driving path.
- Trigger real-time obstacle alert statuses (**Path Clear**, **Path Planning**, **Critical Deviation**).
- Generate local waypoint trajectories for lane-change maneuvers using smooth interpolation.
- Render top-down bird's-eye telematics with planned path lines, sensor coverage bubbles, and telemetry overlay.

---

## Folder Structure
```text
7_Collision Avoidance with Path Planning/
│
├── main.py        # Main execution script (Python + OpenCV GUI)
└── README.md      # Project documentation