import random
import string
import sys

import cv2
import mediapipe as mp
import numpy as np

print("[SYPH] Initializing Profiler OS & Cinematic Lens...")

mp_face_detection = mp.solutions.face_detection
mp_selfie_segmentation = mp.solutions.selfie_segmentation

try:
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Could not open webcam index 0.")
        sys.exit()

    # Hardware Override: 1080p FHD
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    cv2.namedWindow("syph // profiler_os", cv2.WINDOW_NORMAL)

    current_crop_x, current_crop_y = 0.0, 0.0
    pan_smooth_factor = 0.15

    success, init_frame = cap.read()
    if not success:
        print("[ERROR] Failed to read initial frame from webcam.")
        cap.release()
        sys.exit()

    orig_h, orig_w, _ = init_frame.shape

    # --- CINEMATIC ZOOM VARIABLES ---
    target_zoom = 0.6
    current_zoom = 0.6
    zoom_smooth_factor = 0.08  # Lower = slower, heavier lens feel

    # Pre-compute one master Vignette mask for maximum performance
    X_kernel = cv2.getGaussianKernel(orig_w, orig_w / 2)
    Y_kernel = cv2.getGaussianKernel(orig_h, orig_h / 2)
    kernel = Y_kernel * X_kernel.T
    mask = kernel / kernel.max()
    master_vignette = np.dstack([mask] * 3)

    with mp_face_detection.FaceDetection(
        model_selection=0,
        min_detection_confidence=0.5,
    ) as face_detection, mp_selfie_segmentation.SelfieSegmentation(
        model_selection=0,
    ) as segmentation:
        while True:
            success, frame = cap.read()
            if not success:
                print("[ERROR] Lost video stream.")
                break

            if abs(target_zoom - current_zoom) > 0.001:
                current_zoom += (target_zoom - current_zoom) * zoom_smooth_factor
            else:
                current_zoom = target_zoom

            crop_w = int(orig_w * current_zoom)
            crop_h = int(orig_h * current_zoom)

            # Mirror & Darken
            frame = cv2.flip(frame, 1)
            frame = cv2.convertScaleAbs(frame, alpha=0.8, beta=-20)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 1. Neural Tracking
            results_face = face_detection.process(rgb_frame)
            target_center_x, target_center_y = orig_w // 2, orig_h // 2

            if results_face.detections:
                detection = results_face.detections[0]
                boxC = detection.location_data.relative_bounding_box

                x = max(0, int(boxC.xmin * orig_w))
                y = max(0, int(boxC.ymin * orig_h))
                w_box = int(boxC.width * orig_w)
                h_box = int(boxC.height * orig_h)

                target_center_x = x + (w_box // 2)
                target_center_y = y + (h_box // 2)

                cv2.drawMarker(
                    frame,
                    (target_center_x, target_center_y),
                    (255, 255, 255),
                    markerType=cv2.MARKER_CROSS,
                    markerSize=10,
                    thickness=1,
                )

            # 2. Neural Segmentation (Scrambler)
            results_seg = segmentation.process(rgb_frame)
            tiny_frame = cv2.resize(
                frame,
                (max(1, orig_w // 30), max(1, orig_h // 30)),
                interpolation=cv2.INTER_LINEAR,
            )
            pixelated_frame = cv2.resize(
                tiny_frame,
                (orig_w, orig_h),
                interpolation=cv2.INTER_NEAREST,
            )

            condition = np.stack((results_seg.segmentation_mask,) * 3, axis=-1) > 0.5
            frame = np.where(condition, pixelated_frame, frame)

            # 3. Smooth Camera Pan
            ideal_crop_x = target_center_x - (crop_w // 2)
            ideal_crop_y = target_center_y - (crop_h // 2)
            ideal_crop_x = max(0, min(ideal_crop_x, orig_w - crop_w))
            ideal_crop_y = max(0, min(ideal_crop_y, orig_h - crop_h))

            if current_crop_x == 0.0 and current_crop_y == 0.0:
                current_crop_x, current_crop_y = float(ideal_crop_x), float(ideal_crop_y)
            else:
                current_crop_x += (ideal_crop_x - current_crop_x) * pan_smooth_factor
                current_crop_y += (ideal_crop_y - current_crop_y) * pan_smooth_factor

            current_crop_x = max(0.0, min(current_crop_x, float(orig_w - crop_w)))
            current_crop_y = max(0.0, min(current_crop_y, float(orig_h - crop_h)))

            x1, y1 = int(current_crop_x), int(current_crop_y)
            cropped_frame = frame[y1:y1 + crop_h, x1:x1 + crop_w]

            # 4. Vignette Lighting
            vignette_mask = cv2.resize(master_vignette, (crop_w, crop_h))
            cropped_frame = (cropped_frame * vignette_mask).astype(np.uint8)

            # 5. ABSOLUTE HUD OVERLAYS
            h_c, w_c, _ = cropped_frame.shape
            margin = 40
            font = cv2.FONT_HERSHEY_SIMPLEX

            cv2.rectangle(
                cropped_frame,
                (margin, margin),
                (w_c - margin, h_c - margin),
                (100, 100, 100),
                1,
            )
            cv2.line(cropped_frame, (w_c // 2, 0), (w_c // 2, margin), (255, 255, 255), 1)
            cv2.line(
                cropped_frame,
                (w_c // 2, h_c - margin),
                (w_c // 2, h_c),
                (255, 255, 255),
                1,
            )
            cv2.line(cropped_frame, (0, h_c // 2), (margin, h_c // 2), (255, 255, 255), 1)
            cv2.line(
                cropped_frame,
                (w_c - margin, h_c // 2),
                (w_c, h_c // 2),
                (255, 255, 255),
                1,
            )

            ui_x = margin
            ui_y = int(h_c * 0.5) - 20
            img_size = 35
            font_main = 0.3
            font_sub = 0.25

            hex_top = f"Profiler_App v2.{random.randint(10, 99)}x"
            hex_bot = "-".join(
                ["".join(random.choices(string.hexdigits.upper(), k=3)) for _ in range(3)]
            )

            cv2.putText(
                cropped_frame,
                hex_top,
                (ui_x, ui_y - 6),
                font,
                0.25,
                (120, 120, 120),
                1,
            )
            cv2.rectangle(
                cropped_frame,
                (ui_x, ui_y),
                (ui_x + img_size, ui_y + img_size),
                (20, 20, 20),
                cv2.FILLED,
            )
            cv2.putText(
                cropped_frame,
                "IMG",
                (ui_x + 6, ui_y + 20),
                font,
                0.25,
                (100, 100, 100),
                1,
            )
            cv2.putText(
                cropped_frame,
                hex_bot,
                (ui_x, ui_y + img_size + 10),
                font,
                0.25,
                (120, 120, 120),
                1,
            )

            text_start_x = ui_x + img_size + 4
            pad_x, pad_y = 3, 3

            err_text = "Error"
            (tw1, th1), _ = cv2.getTextSize(err_text, font, font_main, 1)
            cv2.rectangle(
                cropped_frame,
                (text_start_x, ui_y),
                (text_start_x + tw1 + pad_x * 2, ui_y + th1 + pad_y * 2),
                (255, 255, 255),
                cv2.FILLED,
            )
            cv2.putText(
                cropped_frame,
                err_text,
                (text_start_x + pad_x, ui_y + th1 + pad_y),
                font,
                font_main,
                (0, 0, 0),
                1,
            )

            fail_text = "Facial recognition failed"
            (tw2, th2), _ = cv2.getTextSize(fail_text, font, font_main, 1)
            y_offset_2 = ui_y + th1 + pad_y * 2 + 2
            cv2.rectangle(
                cropped_frame,
                (text_start_x, y_offset_2),
                (text_start_x + tw2 + pad_x * 2, y_offset_2 + th2 + pad_y * 2),
                (255, 255, 255),
                cv2.FILLED,
            )
            cv2.putText(
                cropped_frame,
                fail_text,
                (text_start_x + pad_x, y_offset_2 + th2 + pad_y),
                font,
                font_main,
                (0, 0, 0),
                1,
            )

            sub_y = y_offset_2 + th2 + pad_y * 2 + 10
            cv2.putText(
                cropped_frame,
                "Age: Error",
                (text_start_x, sub_y),
                font,
                font_sub,
                (150, 150, 150),
                1,
            )
            cv2.putText(
                cropped_frame,
                "Occupation: Error",
                (text_start_x, sub_y + 10),
                font,
                font_sub,
                (150, 150, 150),
                1,
            )

            cv2.putText(
                cropped_frame,
                "TAP [-] ZOOM OUT   [=] ZOOM IN   [ESC] EXIT",
                (margin, h_c - margin - 10),
                font,
                0.4,
                (200, 200, 200),
                1,
            )

            cv2.imshow("syph // profiler_os", cropped_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord("q"):
                break
            elif key == ord("="):
                target_zoom = max(0.3, target_zoom - 0.1)
            elif key == ord("-"):
                target_zoom = min(1.0, target_zoom + 0.1)

    cap.release()
    cv2.destroyAllWindows()

except (cv2.error, RuntimeError):
    import traceback

    print("\n--- CRASH LOG ---")
    traceback.print_exc()
    sys.exit(1)