from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
from twilio.rest import Client

load_dotenv()
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class STT():
    def __init__(self, url, local_filename=None):
        self.url = url+".mp3"
        self.local_filename = local_filename or "./audio_recording/temp_audio.mpeg"

    def download_audio(self):

        try:
            response = requests.get(self.url, stream=True, auth=(account_sid, auth_token))
        except requests.exceptions.RequestException as e:
            print(f"Failed to download audio file: {e}")
            raise


        try:
            os.makedirs(os.path.dirname(self.local_filename), exist_ok=True)    
            # Download the audio file
            with open(self.local_filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        file.write(chunk)
        except IOError as e:
            print(f"Failed to save audio file: {e}")
            raise


        return self.local_filename


    def translate_audio(self):
        
        if not os.path.exists(self.local_filename):
            self.download_audio()
        with open(self.local_filename, "rb") as audio_file:
            translation = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            language="en",
            response_format='text',
            temperature = 0.8
            )
        return translation

