# Syph // profiler_os

A real-time, stylized facial tracking and heads-up display (HUD) engine built with Python. 

Syph uses OpenCV and MediaPipe to map facial landmarks, overlaying a custom dystopian-style surveillance UI. It features intentional anonymization states (pixelation and simulated failure readouts) to create a cinematic "profiler" aesthetic.

## Visuals

*(Anonymization state and error simulation)*
![Syph Profiler View](https://github.com/Kwystt/Syph/blob/fbe1674e004e9c9ae1cad9501713f38f0ea74e78/profiler.png)

*(HUD element detail and dynamic text rendering)*
![HUD Overlay Detail](https://github.com/Kwystt/Syph/blob/14e66d29c53422b9984d8c5443b3f5c71ba47e3b/hud.png)

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
