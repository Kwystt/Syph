# Syph // profiler_os

A real-time, stylized facial tracking and heads-up display (HUD) engine built with Python. 

Syph uses OpenCV and MediaPipe to map facial landmarks, overlaying a custom dystopian-style surveillance UI. It features intentional anonymization states (pixelation and simulated failure readouts) to create a cinematic "profiler" aesthetic.

## Visuals

*(Anonymization state and error simulation)*
![Syph Profiler View](<img width="2877" height="1791" alt="Screenshot 2026-09-14 133829" src="https://github.com/user-attachments/assets/d3632f4d-3b12-4b49-98cd-b54d756b8ce5" />
)

*(HUD element detail and dynamic text rendering)*
![HUD Overlay Detail](<img width="1095" height="997" alt="Screenshot 2026-09-14 134039" src="https://github.com/user-attachments/assets/d6be20b7-5152-4b36-b50c-7cf293e6505d" />)

## Core Features
*   **Real-Time Tracking:** Utilizes MediaPipe's facial mesh to lock onto subjects dynamically.
*   **Custom HUD Overlays:** Renders crosshairs, bounding boxes, and dynamic text fields directly onto the video feed.
*   **Anonymization Filter:** Applies dynamic pixelation masking over the tracked facial region.
*   **Simulated OS Environment:** Features faux error states ("Facial recognition failed") and null data readouts for a cyberpunk aesthetic.
*   **Keyboard Controls:** Map custom inputs (e.g., zoom in/out, exit) directly through the interface.

## Tech Stack
*   **Python 3.x**
*   **OpenCV** (Computer vision and image processing)
*   **MediaPipe** (Facial landmark tracking)

## Quick Start

1. Clone the repository:
   ```bash
   git clone [https://github.com/Kwystt/syph.git](https://github.com/Kwystt/syph.git)
   cd syph
