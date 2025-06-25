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
import difflib
from dbConnect import vatara


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


# def standardize_text(text):
#     """Standardize the license plate text format."""
#     print(text)
#     try:
#         parts = text.split(' ')
#
#         if len(parts) >= 2:
#             # Replace "চ" with "চট্ট" and "ঢ" with "ঢাকা"
#             city_name = parts[0]
#             if city_name == "চ":
#                 city_name = "চট্ট"
#             elif city_name == "ঢ":
#                 city_name = "ঢাকা"
#
#             number_part = parts[-1]
#
#             middle_part = parts[1] if len(parts) > 1 else ""
#             letter_after_hyphen = ""
#             if '-' in middle_part:
#                 letter_after_hyphen = middle_part.split('-')[-1]
#
#             # Format the number part
#             if len(number_part) >= 6:  # Ensure there are enough digits
#                 number_part = f"{number_part[:2]}-{number_part[2:]}"
#
#             # Construct the standardized text
#             standardized = f"{city_name} মেট্রো-{letter_after_hyphen} {number_part}"
#
#             # Directly save to JSON
#             save_to_json(standardized)
#
#             return standardized
#         else:
#             return "Error: Input text format is invalid."
#
#     except Exception as e:
#         return f"Error processing text: {e}"

import json
from datetime import datetime
import difflib
from translate import Translator


translator = Translator(from_lang="bn", to_lang="en")

# Read area words with UTF-8 encoding
with open('areas.txt', 'r', encoding='utf-8') as f:
    words = f.read().splitlines()

# Vehicle class characters in Bangla
vclass = [
    'গ', 'হ', 'ল', 'ঘ', 'চ', 'ট', 'থ', 'এ',
    'ক', 'খ', 'ভ', 'প', 'ছ', 'জ', 'ঝ', 'ব',
    'স', 'ত', 'দ', 'ফ', 'ঠ', 'ম', 'ন', 'অ',
    'ড', 'উ', 'ঢ', 'শ', 'ই', 'য', 'র'
]

# Generate area dictionary
area_dictionary = [f'{w}-{c}' for w in words for c in vclass]

# Bangla numerals set
nums = set('০১২৩৪৫৬৭৮৯')


def transliterate(text):
    """Transliterate Bangla text into English."""
    if not text.strip():
        return text  # Return original if text is empty
    try:
        result = text.replace('গ', 'G')
        result = translator.translate(result)
          # Force 'গ' to be transliterated as 'G'
        return result
    except Exception as e:
        print(f"Error in transliteration: {e} for text: {text}")
        return text  # Fallback to original text


def is_valid_license(area, number):
    """Check if the area and number contain only valid characters."""
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789- ")
    return all(c in allowed_chars for c in area + number)


def extract_license_text(text):
    print(text)
    result = text.strip()
    area = ""
    number = ""

    # Extract area and number from the text
    for c in result[::-1]:
        if c == "-":
            if len(number) <= 4:
                number += "-"
            else:
                area += "-"
        elif c in nums:
            number += c
        else:
            area += c

    area = area[::-1]
    match = difflib.get_close_matches(area, area_dictionary, n=1, cutoff=0.5)

    if match:
        area = match[0]

    number = number[::-1]

    # Ensure proper formatting for the number part
    if number.find("-") == -1 and len(number) == 6:
        number = number[:2] + "-" + number[2:]

    # Transliterate area and number
    area_english = transliterate(area)
    number_english = transliterate(number)

    # Validate license plate
    if not is_valid_license(area_english, number_english):
        print(f"Invalid license plate: {area_english}-{number_english}")
        return None, None  # Skip saving and return nothing

    # If the number length is incorrect, skip it
    if len(number_english) != 7:
        print(f"Invalid license number length: {number_english}")
        return None, None  # Skip saving and return nothing

    license_data = {
        "timestamp": datetime.now().isoformat(),
        "area_bangla": area.strip(),
        "area_english": area_english.strip(),
        "number_bangla": number.strip(),
        "number_english": number_english.strip(),
        "original_text": text
    }

    # Save to JSON file
    try:
        # Read existing data if file exists
        try:
            with open('license_plates.json', 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        # Append new data
        existing_data.append(license_data)

        # Write back to file with all data
        with open('license_plates.json', 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"Error saving to JSON file: {e}")

    return area.strip(), number.strip()

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


def process_plate_region(image, results, reader=None):
    """
    Extract and read text from detected license plates
    Args:
        image: Input image
        results: Detection results
        reader: EasyOCR reader instance (optional)
    Returns:
        List of dictionaries containing plate information
    """
    if reader is None:
        reader = easyocr.Reader(['bn'])

    plates_text = []

    try:
        if not results.boxes:
            return plates_text

        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Input validation
            if not all(x >= 0 for x in [x1, y1, x2, y2]):
                continue

            plate_region = image[y1:y2, x1:x2]

            # Basic checks
            if plate_region.size == 0:
                continue

            # Preprocess plate region
            plate_region = cv2.resize(plate_region, None, fx=2, fy=2)
            gray = cv2.cvtColor(plate_region, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            denoised = cv2.fastNlMeansDenoising(enhanced)

            # OCR processing
            ocr_results = reader.readtext(denoised)

            if ocr_results:
                original_text = " ".join([detection[1] for detection in ocr_results])
                area, number = extract_license_text(original_text)
                modified_text = f"{area} {number}"

                # Draw text on image
                cv2.putText(image, modified_text,
                            (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.9, (0, 255, 0), 2)

                plates_text.append({
                    'original_text': original_text,
                    'modified_text': (area, number),
                    'bbox': (x1, y1, x2, y2)
                })

    except Exception as e:
        print(f"Error processing plate region: {e}")

    return plates_text