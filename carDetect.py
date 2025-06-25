import cv2
import numpy as np
from ultralytics import YOLO

# Load YOLO models
coco_model = YOLO('yolov8n.pt')  # Pre-trained COCO model for car detection
license_plate_detector = YOLO('licensePlatemodel/best (1).pt')  # Custom license plate model

# Open video file and get its properties
cap = cv2.VideoCapture('./assets/30fpsHighway.mp4')
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Initialize VideoWriter for output video
out = cv2.VideoWriter('output_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

# Define vehicle class IDs (e.g., cars, buses, trucks) based on COCO dataset
vehicles = [2, 3, 5, 7]  # Class IDs for car, motorcycle, bus, and truck
frame_nmr = 0

# Process each frame
while True:
    ret, frame = cap.read()
    if not ret:
        break  # Exit loop if no more frames

    frame_nmr += 1
    if frame_nmr > 200:  # Optional: Process only the first 200 frames
        break

    # Detect vehicles in the frame
    vehicle_detections = coco_model(frame)[0]
    for vehicle in vehicle_detections.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = vehicle

        # Filter for vehicles only
        if int(class_id) in vehicles:
            # Draw bounding box for the vehicle
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            cv2.putText(frame, f'Vehicle {score:.2f}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # Crop the detected vehicle region
            vehicle_crop = frame[int(y1):int(y2), int(x1):int(x2)]

            # Detect license plates within the vehicle crop
            license_plate_detections = license_plate_detector(vehicle_crop)[0]
            for license_plate in license_plate_detections.boxes.data.tolist():
                lx1, ly1, lx2, ly2, lscore, lclass_id = license_plate

                # Adjust license plate coordinates to match original frame
                adjusted_x1 = int(x1) + int(lx1)
                adjusted_y1 = int(y1) + int(ly1)
                adjusted_x2 = int(x1) + int(lx2)
                adjusted_y2 = int(y1) + int(ly2)

                # Draw bounding box for the license plate
                cv2.rectangle(frame, (adjusted_x1, adjusted_y1), (adjusted_x2, adjusted_y2), (0, 255, 0), 2)
                cv2.putText(frame, f'Plate {lscore:.2f}', (adjusted_x1, adjusted_y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Optional: Save cropped license plate
                license_plate_crop = frame[adjusted_y1:adjusted_y2, adjusted_x1:adjusted_x2]
                filename = f'license_plate_frame{frame_nmr}_{lscore:.2f}.jpg'
                cv2.imwrite(filename, license_plate_crop)

    # Write annotated frame to the output video
    out.write(frame)

    # Optional: Display the frame (for debugging)
    # cv2.imshow('Video', frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

# Release resources

