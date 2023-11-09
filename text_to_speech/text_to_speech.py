from functions import *

from pydub import AudioSegment
import requests
import json
import os
import base64

import azure.cognitiveservices.speech as speechsdk

from dotenv import load_dotenv

load_dotenv() # import .env variables (API keys)

subscription_key = os.getenv('SUBSCRIPTION_KEY')
service_region = os.getenv('SERVICE_REGION')
speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)

base_folder = "ssml_files" # here I store tuned voice configurations. they are called SSML files
voice_configurations = generate_voice_configurations(base_folder)


SELECTED_VOICE = "Sara" # choose voice configuration (SSML file, basically)

AUDIO_FILENAME = "generated_speech.wav" 


def generate_speech_from_text(text_prompt, audio_filename=AUDIO_FILENAME, selected_voice=SELECTED_VOICE):
    selected_voice += "Neural" # I separated it so it would be more convenient to choose voice (above)

    ssml_string = voice_configurations["en"][selected_voice].read_text()
    ssml_string_modified = modify_ssml(ssml_string, text_prompt)

    # Specify the output audio configuration

    audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_filename) # save file locally after generation

    # Create the speech synthesizer with the speech config and audio config
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    result = speech_synthesizer.speak_ssml(ssml_string_modified) # audio file is generated and saved locally
    
    return audio_filename