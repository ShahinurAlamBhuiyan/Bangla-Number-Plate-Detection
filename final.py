from ultralytics import YOLO
import cv2
from sort import *
from finalBanglaProcess import *
import numpy as np
import os
import math

# Load YOLO models
vehicle_detector = YOLO('yolov8n.pt')
license_plate_detector = YOLO('licensePlatemodel/best (1).pt')

# Initialize tracker
tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

# Constants
PIXEL_TO_METER_RATIO = 0.1
DROIDCAM_URL = "http://192.168.0.100:4747/video"
OUTPUT_VIDEO_PATH = 'output/video/PlatePremioSpeed.mp4'
CROPPED_IMAGE_DIR = 'output/image/'
os.makedirs(CROPPED_IMAGE_DIR, exist_ok=True)

# Open video capture
cap = cv2.VideoCapture('assets/premiovid.mp4')
if not cap.isOpened():
    print("Error: Cannot open video file.")
    exit()

# Set video capture resolution (optional, based on camera capability)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Max resolution supported by your camera
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# Video properties
original_fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
target_fps = 30
skip_interval = max(1, round(original_fps / target_fps))

# Video writer
output_video = cv2.VideoWriter(
    OUTPUT_VIDEO_PATH,
    cv2.VideoWriter_fourcc(*'mp4v'),
    target_fps,
    (width, height)
)

# Variables
frame_nmr = 0
tracked_objects = {}
speed = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Finished processing video.")
        break

    frame_nmr += 1
    if frame_nmr % skip_interval != 0:
        continue

    # Detect vehicles
    vehicle_results = vehicle_detector(frame)[0]
    vehicle_boxes = []

    # Filter for vehicles (class 2: car, 3: motorcycle, 5: bus, 7: truck)
    for box in vehicle_results.boxes.data.tolist():
        if int(box[5]) in [2, 3, 5, 7]:
            vehicle_boxes.append(box[:5])  # [x1, y1, x2, y2, conf]

    detections = np.array(vehicle_boxes) if vehicle_boxes else np.empty((0, 5))
    tracked_objects_array = tracker.update(detections)

    # Process tracked vehicles
    for track in tracked_objects_array:
        track_id = int(track[4])
        current_center = (int((track[0] + track[2]) / 2), int((track[1] + track[3]) / 2))
        current_time = frame_nmr / target_fps

        if track_id in tracked_objects:
            prev_center, prev_time = tracked_objects[track_id]
            time_diff = current_time - prev_time

            if time_diff > 0:
                # Calculate speed
                distance_pixels = math.sqrt((current_center[0] - prev_center[0]) ** 2 +
                                            (current_center[1] - prev_center[1]) ** 2)
                speed = (distance_pixels * PIXEL_TO_METER_RATIO / time_diff) * 3.6

                # Display speed
                cv2.rectangle(frame,
                              (int(track[0]), int(track[1])),
                              (int(track[2]), int(track[3])),
                              (255, 0, 0), 2)
                cv2.putText(frame, f"{speed:.1f} km/h",
                            (int(track[0]), int(track[1] - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        tracked_objects[track_id] = (current_center, current_time)

    # Process license plates
    license_plates = license_plate_detector(frame)[0]
    if len(license_plates.boxes) > 0:
        plates_text = process_plate_region(frame, license_plates, speed)
        for idx, plate in enumerate(license_plates.boxes.data.tolist()):
            x1, y1, x2, y2, score, class_id = plate
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # Add padding around the bounding box
            padding = 10
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(frame.shape[1], x2 + padding)
            y2 = min(frame.shape[0], y2 + padding)

            # Crop the license plate region
            plate_crop = frame[y1:y2, x1:x2]

            # Resize and enhance the cropped image
            larger_crop = cv2.resize(plate_crop, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            gray_plate = cv2.cvtColor(larger_crop, cv2.COLOR_BGR2GRAY)
            enhanced_plate = cv2.equalizeHist(gray_plate)

            # Save the enhanced image
            crop_filename = os.path.join(CROPPED_IMAGE_DIR, f'plate_{frame_nmr}_{idx}.jpg')
            cv2.imwrite(crop_filename, enhanced_plate)

            # Draw bounding box on the original frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"Plate {idx + 1}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Write the processed frame to the output video
    output_video.write(frame)

# Release resources
cap.release()
output_video.release()
cv2.destroyAllWindows()
