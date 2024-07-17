from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import requests
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
verify_service_sid = os.getenv("VERIFY_SERVICE_SID")

# Initialize Twilio client
client = Client(account_sid, auth_token)

custom_agent = llm.CustomAgent(question_prompt=question_prompt, questions=questions, validate_response=validate_response)

def make_message():
    return "hello thanks for calling"

@app.route("/answer", methods=['GET', 'POST'])
def answer():
    print("received a call")
    response = VoiceResponse()
    response.say(make_message())
    response.record(max_length=5, action="/handle-recording")

    conversations = custom_agent.run_agent()

    return str(response)

@app.route("/handle-recording", methods=['GET', 'POST'])
def handle_recording():
    recording_url = request.values.get("RecordingUrl")
    print(f"Received recording: {recording_url}")

    media_url = get_media_url(recording_url)
    response = VoiceResponse()
    # response.play(media_url)
    response.say("Thank you for your message. Goodbye!")
    return str(response)

def get_media_url(recording_url):
    #local_filename = "C:/Users/Lichen/Downloads/recording.mp3"
    recording_sid = recording_url.split('/')[-1]

    # Download the recording from Twilio
    media_url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Recordings/{recording_sid}.mp3'
    return media_url

@app.route("/")
def home():
    return "Flask application is running"

# +18557781299

# 41f63713f93cb22954146c5d4c4b5400

if __name__ == "__main__":
    app.run(debug=True, port=5000)
