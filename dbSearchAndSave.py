from sort import *
import numpy as np
import cv2
import json
from datetime import datetime
import difflib
import easyocr
from translate import Translator
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI, HTTPException

# DATABASE
app = FastAPI()

# MongoDB URI
uri = "mongodb+srv://admin:admin@cluster0.evtt2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Initialize MongoDB client
my_client = AsyncIOMotorClient(uri)

# Access the database and collection
db = my_client.DhakaTraffic
vatara = db["Vatara"]
culprit = db["Culprit"]

# Initialize translator
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
        return result
    except Exception as e:
        print(f"Error in transliteration: {e} for text: {text}")
        return text  # Fallback to original text


def is_valid_license(area, number):
    """Check if the area and number contain only valid characters."""
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789- ")
    return all(c in allowed_chars for c in area + number)


#Find Culprit
async def find_culprit(area_english: str, number_english: str):
    """
    Function to find a culprit by area_english and number_english.
    Args:
        area_english (str): English area name to match.
        number_english (str): English license plate number to match.
    Returns:
        dict: The matched culprit document, or raises an exception if not found.
    """
    try:
        query = {
            "area_english": area_english,
            "number_english": number_english
        }
        result = await culprit.find_one(query)

        if result:
            print("Culprit Detected")
        else:
            raise HTTPException(status_code=404, detail="No match found for the given license plate.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while searching: {e}")

async def insert_to_db(data):
    """Insert data into MongoDB asynchronously."""
    try:
        result = await vatara.insert_one(data)
        print(f"Data inserted with ID: {result.inserted_id}")
    except Exception as e:
        print(f"Error inserting into database: {e}")


def extract_license_text(text, speed):
    """Extract and validate license text from OCR result."""
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
        "original_text": text,
        "speed": round(speed, 2)
    }

    # Add to database using event loop
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(find_culprit(license_data["area_english"], license_data["number_english"]))
        loop.run_until_complete(insert_to_db(license_data))
    except RuntimeError as e:
        print(f"Event loop error: {e}")
    except Exception as e:
        print(f"Error saving to database: {e}")

    return area_english, number_english


def process_plate_region(image, results, speed, reader=None):
    """Process detected license plate regions."""
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
                area, number = extract_license_text(original_text, speed)
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
