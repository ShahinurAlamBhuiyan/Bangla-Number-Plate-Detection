from sort import *
import numpy as np
import matplotlib.pyplot as plt
import imutils
from ultralytics import YOLO
import cv2
import easyocr
import re
import json
from datetime import datetime
import os


def save_to_json(standardized_text):
    """Save license plate data directly to JSON file"""
    try:
        # Prepare the new entry
        new_entry = {
            "location": "NotunBazar",
            "number": standardized_text,
            "datetime": f"{datetime.now()}"
        }

        file_path = 'data.json'

        try:
            # Try to read existing data
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is empty/invalid, start with empty list
            data = []

        # Append new entry
        data.append(new_entry)

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"Error saving to JSON: {e}")


def standardize_text(text):
    """Standardize the license plate text format."""
    print(text)
    try:
        parts = text.split(' ')

        if len(parts) >= 2:
            # Replace "চ" with "চট্ট" and "ঢ" with "ঢাকা"
            city_name = parts[0]
            if city_name == "চ":
                city_name = "চট্ট"
            elif city_name == "ঢ":
                city_name = "ঢাকা"

            number_part = parts[-1]

            middle_part = parts[1] if len(parts) > 1 else ""
            letter_after_hyphen = ""
            if '-' in middle_part:
                letter_after_hyphen = middle_part.split('-')[-1]

            # Format the number part
            if len(number_part) >= 6:  # Ensure there are enough digits
                number_part = f"{number_part[:2]}-{number_part[2:]}"

            # Construct the standardized text
            standardized = f"{city_name} মেট্রো-{letter_after_hyphen} {number_part}"

            # Directly save to JSON
            save_to_json(standardized)

            return standardized
        else:
            return "Error: Input text format is invalid."

    except Exception as e:
        return f"Error processing text: {e}"

def process_plate_region(image, results):
    """Extract and read text from detected license plates"""
    print(results)
    reader = easyocr.Reader(['bn'])
    plates_text = []

    if len(results.boxes) > 0:
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            plate_region = image[y1:y2, x1:x2]

            # Preprocess the plate region
            plate_region = cv2.resize(plate_region, None, fx=2, fy=2)
            gray = cv2.cvtColor(plate_region, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            denoised = cv2.fastNlMeansDenoising(enhanced)

            # Read text using EasyOCR
            ocr_results = reader.readtext(denoised)

            if ocr_results:
                original_text = " ".join([detection[1] for detection in ocr_results])
                modified_text = standardize_text(original_text)

                # Draw text on the original image
                cv2.putText(image, modified_text,
                            (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.9, (0, 255, 0), 2)

                plates_text.append({
                    'original_text': original_text,
                    'modified_text': modified_text,
                    'bbox': (x1, y1, x2, y2)
                })

    return plates_text