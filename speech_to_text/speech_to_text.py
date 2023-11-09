import time
import os

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv() # import .env variables (API keys)

subscription_key = os.getenv('SUBSCRIPTION_KEY')
service_region = os.getenv('SERVICE_REGION')


def transcribe_speech():
    """Performs continuous speech recognition with input from the microphone and returns the transcribed text after 4 seconds of silence."""
    
    # Set up the speech configuration using the provided subscription key and service region
    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)
    
    # Create a recognizer with the given settings
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    
    # Variable to store the recognized text
    full_text = []
    
    # To signal when the last speech was detected
    last_speech_detected_time = time.time()
    
    # To keep track of silence duration
    silence_duration = 4
    
    # Set up a flag to monitor the recognition status
    recognition_active = True
    
    def recognized_cb(evt):
        """Callback for recognized event"""
        nonlocal last_speech_detected_time
        # If speech is recognized, reset the last speech detected time
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            full_text.append(evt.result.text)
            last_speech_detected_time = time.time()

    def recognizing_cb(evt):
        """Callback for recognizing event (intermediate results)"""
        nonlocal last_speech_detected_time
        # Update the last speech detected time for intermediate results too
        last_speech_detected_time = time.time()

    # Connect callbacks to the events fired by the speech recognizer
    speech_recognizer.recognized.connect(recognized_cb)
    speech_recognizer.recognizing.connect(recognizing_cb)

    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()

    try:
        # While recognition is active, check the duration of silence after speech is detected
        while recognition_active:
            time.sleep(0.1)
            if time.time() - last_speech_detected_time > silence_duration:
                # Once we detect silence for 4 seconds, stop recognition
                recognition_active = False
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Stop the continuous recognition once we detect silence for 4 seconds
        speech_recognizer.stop_continuous_recognition()
    
    return " ".join(full_text)  # Return the concatenated recognized text
