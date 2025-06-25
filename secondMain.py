#With Skip
from ultralytics import YOLO
import cv2
from sort import *
from secondBanglaProcess import *
import numpy as np
import os

# Create directory for saving crops if it doesn't exist
# os.makedirs('output/image', exist_ok=True)

# Translator
DROIDCAM_URL = "http://192.168.0.103:4747/video"
license_plate_detector = YOLO('licensePlatemodel/best (1).pt')

# Initialize video capture
cap = cv2.VideoCapture("assets/chuwadanga.mp4")

if not cap.isOpened():
    print("Error: Cannot open video file.")
    exit()

# Get original video properties
original_fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Set target FPS
target_fps = 30

# Calculate frame skip interval
skip_interval = max(1, round(original_fps / target_fps))

# Output video writer with target FPS
output_video = cv2.VideoWriter(
    'output/video/chuwa.mp4',
    cv2.VideoWriter_fourcc(*'mp4v'),
    target_fps,
    (width, height)
)

frame_nmr = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Finished processing video.")
        break

    frame_nmr += 1

    # Skip frames based on calculated interval
    if frame_nmr % skip_interval != 0:
        continue

    # License plate detection and processing
    license_plates = license_plate_detector(frame)[0]
    if len(license_plates.boxes) > 0:
        plates_text = process_plate_region(frame, license_plates)
        for idx, plate in enumerate(license_plates.boxes.data.tolist()):
            x1, y1, x2, y2, score, class_id = plate

            # Convert coordinates to integers
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # Draw rectangle on main frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Crop license plate
            plate_crop = frame[y1:y2, x1:x2]

            # Save the crop
            crop_filename = f'output/image/plate_{frame_nmr}_{idx}.jpg'
            cv2.imwrite(crop_filename, plate_crop)

            # Display the crop in a separate window
            # cv2.imshow(f'License Plate {idx}', plate_crop)

    # Display the main frame
    # cv2.imshow('Processing', frame)

    # Write processed frame to output video
    output_video.write(frame)

    # Break loop if 'q' is pressed
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

# Release resources
cap.release()
output_video.release()
cv2.destroyAllWindows()




#Without SKip
# from ultralytics import YOLO
# import cv2
# from sort import *
# from secondBanglaProcess import *
# import numpy as np
#
#
#
# #Translator
# import cv2
#
# DROIDCAM_URL = "http://192.168.0.103:4747/video"
# license_plate_detector = YOLO('licensePlatemodel/best (1).pt')
#
#
# # Initialize video capture
# cap = cv2.VideoCapture("assets/closeup2.mp4")
#
# # Check if video file is opened successfully
# if not cap.isOpened():
#     print("Error: Cannot open video file.")
#     exit()
#
# # Get video properties for output
# width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# fps = int(cap.get(cv2.CAP_PROP_FPS))
#
# # Output video writer
# output_video = cv2.VideoWriter(
#     'output/video/nHighway4.mp4',
#     cv2.VideoWriter_fourcc(*'mp4v'),
#     fps,
#     (width, height)
# )
#
# # Initialize SORT tracker
# #mot_tracker = Sort()
#
# # Skip logic
# #skip_frames = int(fps * 2)  # Skip 2 seconds' worth of frames
# frame_nmr = 0
#
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Finished processing video.")
#         break
#     frame_nmr += 1
#
#     # Vehicle detection
#     # detections = coco_model(frame)[0]
#     # detections_ = []
#
#     # Filter and draw vehicle detections
#     # for detection in detections.boxes.data.tolist():
#     #     x1, y1, x2, y2, score, class_id = detection
#     #     if int(class_id) in [2, 3, 4, 5, 6, 7]:  # Vehicle classes
#     #         detections_.append([x1, y1, x2, y2, score])
#     #         cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
#
#     # Update tracker
#     # if len(detections_) > 0:
#     #     track_ids = mot_tracker.update(np.asarray(detections_))
#     # else:
#     #     track_ids = np.empty((0, 5))
#     # License plate detection and processing
#     license_plates = license_plate_detector(frame)[0]
#     if len(license_plates.boxes) > 0:
#         plates_text = process_plate_region(frame, license_plates)
#         for plate in license_plates.boxes.data.tolist():
#             x1, y1, x2, y2, score, class_id = plate
#             cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
#
#     # Write processed frame to output video
#     output_video.write(frame)
#
# # Release resources
# cap.release()
# output_video.release()
# #cv2.destroyAllWindows()
