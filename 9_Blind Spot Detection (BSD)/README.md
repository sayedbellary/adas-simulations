# Project 9: Blind Spot Detection (BSD)

## Overview
This project models a Blind Spot Detection (BSD) driver assistance system. It uses side radar/camera detection zones to identify vehicles in adjacent left and right blind spot areas, illuminating mirror warning indicators and displaying real-time driver alerts.

---

## Aim
To implement a Blind Spot Detection system that tracks surrounding vehicles in adjacent lanes, identifies blind spot occupancy, and triggers mirror warnings and telemetry alerts.

---

## Objectives
- Define spatial radar detection zones for left and right adjacent blind spots.
- Monitor target vehicles overtaking or driving in adjacent lanes.
- Illuminate simulated side-mirror warning LEDs upon blind spot entry.
- Display real-time telemetry warnings for blind spot hazards.

---

## Folder Structure
```text
9_Blind Spot Detection (BSD)/
│
├── main.py        # Main execution script (Python + OpenCV GUI)
└── README.md      # Project documentation