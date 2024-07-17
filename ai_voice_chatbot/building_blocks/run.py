from flask import Flask, request, Response, url_for
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import requests
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
import llm
from get_transcript import user_response_transcript

app = Flask(__name__)
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
verify_service_sid = os.getenv("VERIFY_SERVICE_SID")


# Initialize Twilio client
client = Client(account_sid, auth_token)

# Disable SSL verification (Not recommended for production)
#client.http_client.session.verify = False

# define the prompt templates for asking questions and initialize the custom_agent
question_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a chatbot acting as a call center to receive patient calls for doctor appointment"),
    ("ai", "{question}")
    ])

custom_agent = llm.CustomAgent(question_prompt=question_prompt)

@app.route("/answer", methods=['GET', 'POST'])
def answer_call():
    print("received call")
    response = VoiceResponse()
    question = custom_agent.get_question()
    
    if question != -1:
        response.say(question)
        response.record(max_length=5, transcribe=True, transcribe_callback=url_for('handle_transcription', _external=True))
    else:
        response.say("No more questions. Goodbye.")
    
    return str(response)

@app.route("/handle-transcription", methods=['GET', 'POST'])
def handle_transcription():
    #transcription = request.form['TranscriptionText']
    transcription = user_response_transcript(account_sid, auth_token)
    print(f"transcription: {transcription}")

    question = custom_agent.get_question()  # Assume this method gives you the current question being asked
    valid_response = custom_agent.validate_response(question, transcription)
    
    response = VoiceResponse()
    
    if valid_response:
        custom_agent.conversations[question] = transcription
        next_question = custom_agent.get_question()
        
        if next_question != -1:
            response.say(next_question)
            #response.record(max_length=3, transcribe=True, transcribe_callback=url_for('handle_transcription', _external=True))
            response.record(max_length=3)
        else:
            response.say("Thank you for your responses. Goodbye.")
    else:
        response.say("Sorry, I didn't quite get that. Please respond again.")
        # response.record(max_length=3, transcribe=True, transcribe_callback=url_for('handle_transcription', _external=True))
        response.record(max_length=3)
    
    return str(response)


# def get_transcription():
#     url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Transcriptions.json'

#     response = requests.values.get(url)
#     if response.status_code == 200:
#         transcription_json = response.json()
#     print(f"status code: {response.status_code}")

#     print(transcription_json)
    # transcription_json = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Transcriptions.json"
    
    # transcriptions = client.transcriptions.list()
    # print(transcriptions)
    # transcription_sid = transcriptions[0].sid
    # print(transcription_sid)
    # transcription = client.transcriptions(transcription_sid).fetch()
    # print(transcription.transcription_text)
    # return transcription.transcription_text

    # recording_sid = recording_url.split('/')[-1]
    # # Download the recording from Twilio
    # media_url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Transcriptions/{recording_sid}.txt'
    # /2010-04-01/Accounts/{AccountSid}/Transcriptions/{TranscriptionSid}.txt
    # return media_url



# @app.route("/answer", methods=['GET', 'POST'])
# def answer_call():
#     print("received call")
#     response = VoiceResponse()
#     return ask_questions(response)

# def ask_questions(response):
#     while True:
#         question = custom_agent.get_question()
#         print(f"question: {question}")
#         print("debug1")
#         if question == -1:
#             print("debug2")
#             break

#         # valid_response = False
#         user_response_txt = ""
#         # while not valid_response:
#         for _ in range(5):
#             response.say(question)
#             print("debug3")
#             response.record(max_length=3, transcribe=True, transcribe_callback="handle-transcription")
#             print("debug4")
#             # print(f"[DBG] user response txt: {user_response_txt}")

#             # valid_response = custom_agent.validate_response(question, user_response_txt)
#             # if not valid_response:
#             #     response.say("Sorry, I didn't quite get that. Please respond again.")
#         custom_agent.conversations[question] = user_response_txt

#     return str(response)

# def ask_and_get_answer(question, response_obj):
#     response_obj.say(question)
#     response_obj.record(max_length=3, transcribe=True, transcribe_callback="handle-transcription")

        # while not valid_response:
        #     response.say(question)
        #     # response.record(max_length=3, action="handle-recording")
        #     response.record(max_length=3, transcribe=True, transcribe_callback="handle-transcription")
        #     print(f"[DBG] user response txt: {user_response_txt}")
            
        #     valid_response = custom_agent.validate_response(question, user_response_txt)
        #     if not valid_response:
        #         response.say("Sorry, I didn't quite get that. Please respond again.")
        
        # custom_agent.conversations[question] = user_response_txt

# @app.route("/handle-transcription", methods=['POST'])
# def handle_transcription():
#     transcription_text = request.form['TranscriptionText']
#     print(f"Transcription: {transcription_text}")
#     return Response(status=200)

# def get_media_url(recording_url):
#     recording_sid = recording_url.split('/')[-1]
#     # Download the recording from Twilio
#     media_url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Recordings/{recording_sid}.mp3'
#     return media_url

# @app.route("/handle-recording", methods=['GET', 'POST'])
# def handle_recording():
#     recording_url = request.values.get("RecordingUrl")
#     print(f"Received recording: {recording_url}")

#     media_url = get_media_url(recording_url)
#     response = VoiceResponse()
#     response.play(media_url)
#     return str(response)

@app.route("/")
def home():
    return "Flask application is running"

# +18557781299

if __name__ == "__main__":
    app.run(debug=True, port=5000)
