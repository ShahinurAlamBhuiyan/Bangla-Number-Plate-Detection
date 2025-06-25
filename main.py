# from ultralytics import YOLO
# import cv2
# from sort import *
# from banglaProcessing import *
#
#
# coco_model = YOLO('yolov8n.pt')
# license_plate_detector = YOLO('licensePlatemodel/best (1).pt')
#
# # Initialize video capture
# cap = cv2.VideoCapture('assets/premiovid.mp4')
#
# # Get video properties for output video
# width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# fps = int(cap.get(cv2.CAP_PROP_FPS))
#
# # Initialize video writer
# output_video = cv2.VideoWriter(
#     'HighwayHDoutput.mp4',
#     cv2.VideoWriter_fourcc(*'mp4v'),
#     fps,
#     (width, height)
# )
#
# # Initialize SORT tracker
# mot_tracker = Sort()
#
# frame_nmr = 0
#
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break
#
#     frame_nmr += 1
#
#     # Detect vehicles
#     detections = coco_model(frame)[0]
#     detections_ = []
#
#     # Filter and draw vehicle detections
#     for detection in detections.boxes.data.tolist():
#         x1, y1, x2, y2, score, class_id = detection
#         if int(class_id) in [2, 3, 4, 5, 6, 7]:  # Vehicle classes
#             detections_.append([x1, y1, x2, y2, score])
#             # Draw vehicle bounding box
#             cv2.rectangle(frame,
#                           (int(x1), int(y1)),
#                           (int(x2), int(y2)),
#                           (0, 0, 255), 2)
#
#     # Update tracker only if there are detections
#     if len(detections_) > 0:
#         track_ids = mot_tracker.update(np.asarray(detections_))
#     else:
#         track_ids = np.empty((0, 5))
#
#     # Detect license plates and process them
#     license_plates = license_plate_detector(frame)[0]
#     if len(license_plates.boxes) > 0:
#         # Process plates and get text
#         plates_text = process_plate_region(frame, license_plates)
#
#         # Draw license plate boxes
#         for plate in license_plates.boxes.data.tolist():
#             x1, y1, x2, y2, score, class_id = plate
#             cv2.rectangle(frame,
#                           (int(x1), int(y1)),
#                           (int(x2), int(y2)),
#                           (0, 255, 0), 2)
#
#     # Display the frame
#    # cv2.imshow("Vehicle and License Plate Detection", frame)
#
#     # Write frame to output video
#     output_video.write(frame)
#
#     # Break the loop if 'q' is pressed
#     # if cv2.waitKey(1) & 0xFF == ord('q'):
#     #     break
#
# # Release resources
# cap.release()
# output_video.release()
# # cv2.destroyAllWindows()
#
####END OF FINAL CODE



#EXPERIMENTAL CODE START



from ultralytics import YOLO
import cv2
from sort import *
from banglaProcessing import *
import numpy as np

# Load YOLO models
coco_model = YOLO('yolov8n.pt')
license_plate_detector = YOLO('licensePlatemodel/best (1).pt')

# Initialize video capture
cap = cv2.VideoCapture('assets/10tola2.mp4')

# Check if video file is opened successfully
if not cap.isOpened():
    print("Error: Cannot open video file.")
    exit()

# Get video properties for output
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Output video writer
output_video = cv2.VideoWriter(
    'output/video/10tola2.mp4',
    cv2.VideoWriter_fourcc(*'mp4v'),
    fps,
    (width, height)
)

# Initialize SORT tracker
mot_tracker = Sort()

# Skip logic
skip_frames = int(fps * 2)  # Skip 2 seconds' worth of frames
frame_nmr = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Finished processing video.")
        break

    # Skip frames
    if frame_nmr % (skip_frames + 1) != 0:
        frame_nmr += 1
        continue

    frame_nmr += 1

    # Vehicle detection
    detections = coco_model(frame)[0]
    detections_ = []

    # Filter and draw vehicle detections
    for detection in detections.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = detection
        if int(class_id) in [2, 3, 4, 5, 6, 7]:  # Vehicle classes
            detections_.append([x1, y1, x2, y2, score])
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)

    # Update tracker
    if len(detections_) > 0:
        track_ids = mot_tracker.update(np.asarray(detections_))
    else:
        track_ids = np.empty((0, 5))

    # License plate detection and processing
    license_plates = license_plate_detector(frame)[0]
    if len(license_plates.boxes) > 0:
        plates_text = process_plate_region(frame, license_plates)
        for plate in license_plates.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = plate
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

    # Write processed frame to output video
    output_video.write(frame)

# Release resources
cap.release()
output_video.release()
#cv2.destroyAllWindows()





#Image Implementation Only

# from ultralytics import YOLO
# import cv2
# import matplotlib.pyplot as plt
# from banglaProcessing import process_plate_region
#
#
# # Load the YOLO model
# license_plate_detector = YOLO('licensePlatemodel/best (1).pt')
# coco_model = YOLO('yolov8n.pt')
#
#
#
# def main():
#
#     image_path = "assets/premio.jpeg"
#     image = cv2.imread(image_path)
#
#     if image is None:
#         print("Error: Could not read the image file.")
#         return
#
#     print("Processing image...")
#
#     results = license_plate_detector(image)
#     annotated_image = results[0].plot()
#     plates_text = process_plate_region(annotated_image, results)
#
#     # Display results
#     for i, plate in enumerate(plates_text, 1):
#         print(f"\nPlate {i}:")
#         print(f"Original Text: {plate['original_text']}")
#         print(f"Modified Text: {plate['modified_text']}")
#
#     output_path = "output_image_with_text.jpg"
#     cv2.imwrite(output_path, annotated_image)
#
#     print(f"\nProcessing complete. Output saved to {output_path}")
#
#     plt.figure(figsize=(12, 8))
#     plt.imshow(cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB))
#     plt.axis('off')
#     plt.show()
