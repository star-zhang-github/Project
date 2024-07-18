import requests
import os 
import logging

# Define the API endpoint and headers (TBD, move to run.py)
api_url = "https://api.deepgram.com/v1/listen"
api_key = os.getenv("DEEPGRAM_API_KEY")

# Specify the audio file path
audio_file_path = None


def text_to_voice(api_url, api_key, audio_file_path):
        
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }

    # Load the audio file data, read binary
    with open(audio_file_path, "rb") as audio_file:
        audio_data = audio_file.read()

    # Define parameters for API request
    params = {
        "punctuate": True,
        "language": "en"
    }

    # Make the request to Deepgram API
    response = requests.post(api_url, headers=headers, params=params, data=audio_data)

    # Try three times text to voice before showing failing message.
    num = 0

    while num < 3:
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            # Extract the transcription text
            transcription = result.get("result", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
            return transcription
        else:
            logging.info("Error:", response.status_code, response.text)
            num += 1

    logging.error("Text to voice failed.")
    







