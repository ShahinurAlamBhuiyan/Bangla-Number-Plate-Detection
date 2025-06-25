# from translate import Translator
#
#
# translator = Translator(from_lang="bn", to_lang="en")
# def transliterate(text):
#     """Transliterate Bangla text into English."""
#     if not text.strip():
#         return text  # Return original if text is empty
#     try:
#         result = text.replace('গ', 'G')
#         result = translator.translate(result)
#           # Force 'গ' to be transliterated as 'G'
#         return result
#     except Exception as e:
#         print(f"Error in transliteration: {e} for text: {text}")
#         return text  # Fallback to original text
# print(transliterate("চট্র"))




import cv2

# Replace with the URL shown in the DroidCam app
DROIDCAM_URL = "http://192.168.0.107:4747/video"

def process_droidcam_feed():
    # Open the video stream from DroidCam
    cap = cv2.VideoCapture(DROIDCAM_URL)

    if not cap.isOpened():
        print("Error: Unable to access the DroidCam video stream.")
        return

    print("Press 'q' to quit.")

    while True:
        # Read a frame from the video stream
        ret, frame = cap.read()
        if not ret:
            print("Failed to retrieve frame.")
            break

        # Display the video feed
        #cv2.imshow("DroidCam Feed", frame)

        # Quit on 'q' key press
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    # Release resources and close windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    process_droidcam_feed()
