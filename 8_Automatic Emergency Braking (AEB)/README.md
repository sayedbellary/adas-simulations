# Project 8: Automatic Emergency Braking (AEB)

## Overview
This project implements an Automatic Emergency Braking (AEB) safety feature. It continuously estimates the Time-To-Collision (TTC) to a lead vehicle, displays Forward Collision Warnings (FCW), and automatically initiates emergency hard braking to prevent a rear-end collision.

---

## Aim
To model an Automatic Emergency Braking system that monitors relative speed and distance to lead obstacles, calculates Time-To-Collision (TTC), and triggers automated deceleration.

---

## Objectives
- Calculate real-time Time-To-Collision ($\text{TTC} = \frac{D_{\text{lead}}}{V_{\text{rel}}}$).
- Implement Forward Collision Warning (FCW) stages (**Safe**, **Pre-Charge Warning**, **AEB Activated**).
- Simulate hard braking deceleration curves and brake light visual feedback.
- Display real-time telemetry metrics (Ego Speed, Distance, TTC, and AEB Alert Status).

---

## Folder Structure
```text
8_Automatic Emergency Braking (AEB)/
│
├── main.py        # Main execution script (Python + OpenCV GUI)
└── README.md      # Project documentation