from flask import Flask, request, redirect, url_for, session
from twilio.twiml.voice_response import VoiceResponse
# from twilio.rest import Client
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
import building_blocks.custom_agent as custom_agent
from building_blocks.speech_to_text import STT
import logging
import time


logging.basicConfig(filename='app.log', filemode='a', level=logging.INFO)

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

recording_sid, recording_status, recording_url = None, None, None
transcription = None
new_voice_flag = None

# define the prompt templates for asking questions and initialize the custom_agent
question_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a chatbot acting as a call center to receive patient calls for doctor appointment. "),
    ("ai", "{question}")
    ])
custom_agent = custom_agent.CustomAgent(question_prompt=question_prompt, question_type="doctor_appointment")

@app.before_request
def initialize_session():
    if 'question_idx' not in session:
        session['question_idx'] = 0

@app.route("/answer", methods=['GET','POST'])
def answer_call():
    # global question_idx
    # question_idx = 0
    # finished_asked_idx = -1

    logging.info("Entering answer_call(): Call received")

    response = VoiceResponse()
    
    
    response.say("Welcome. You can press # sign when finish recording. Your information will only be stored when all questions are answered.")
    response.redirect(url_for('ask_question', _external=True))

    logging.info("answer_call(): redirected to ask_question()")

    return str(response)

@app.route("/ask-question", methods=['GET', 'POST'])
def ask_question():
    # global current_question, question_idx

    logging.info(f"Entering ask_question()")
    response = VoiceResponse()
    question_idx = session.get('question_idx', 0)
    current_question = custom_agent.get_question(question_idx)
    logging.info(f"ask_question(): question_idx --> '{question_idx}'")

    if request.args.get('Retry') == 'true':
        response.say("Sorry, your answer doesn't seem right. Let's try again.")

    if current_question != -1:

        logging.info(f"ask_question(): started recording for '{current_question}'")
        
        response.say(current_question)
        response.record(max_length=10, 
                        action = url_for("wait", _external=True),
                        method="POST", 
                        finishOnKey="#", 
                        recording_status_callback='/recording-status', 
                        recordingStatusCallbackMethod="POST", 
                        recordingStatusCallbackEvent="completed")

        logging.info(f"ask_question(): finished recording for '{current_question}'")
    else:
        logging.info(f"ask_question(): custom_agent.conversations --> '{custom_agent.conversations}'")
        custom_agent.add_record()
        response.say("Finished collecting all information. Bye!")
        logging.info(f"ask_question(): End of the call'")

    return str(response)

@app.route("/recording-status", methods=['GET','POST'])
def recording_status():
    global recording_sid, recording_status, recording_url
    recording_sid = request.form.get("RecordingSid")
    recording_status = request.form.get("RecordingStatus")
    recording_url = request.form.get('RecordingUrl')

    logging.info(f"recording_status(): Recording SID --> {recording_sid}, Status --> {recording_status}")
    return "Recording finished", 200


@app.route("/wait", methods=['POST','GET'])
def wait():
    response = VoiceResponse()
    time.sleep(1)
    response.redirect(url_for('recording_received', _external=True))
    return str(response)


@app.route("/recording-received", methods=['GET','POST'])
def recording_received():
    global recording_sid, recording_status, recording_url

    response = VoiceResponse()
    while recording_status!="completed":
        response.redirect(url_for('wait', _external=True))
        return str(response)
    logging.info(f"recording-received(): recording_status: {recording_status}")
    logging.info(f"recording-received(): recording_url --> {recording_url}")
    
    recording_status = None # reset recording status for next question
    response.redirect(url_for('transcribe_response', _external=True))
    return str(response)

@app.route("/transcribe-response", methods=['GET','POST'])
def transcribe_response():
    global transcription

    response = VoiceResponse()
    stt = STT(url=recording_url)
    transcription = stt.transcribe_audio()
    logging.info(f"transcribe_response(): transcription--> {transcription}")
    response.redirect(url_for('format_response', _external=True))

    return str(response)

@app.route("/format-response", methods=['POST','GET'])
def format_response():
    global transcription
    question_idx = session.get('question_idx', 0)
    format = custom_agent.get_format(question_idx)
    current_question = custom_agent.get_question(question_idx)
    format_transcription = custom_agent.get_response(current_question, transcription, format)
    print(f"Question: {current_question}")
    print(f"Your answer: {transcription}")
    print(f"Stored answer: {format_transcription}")

    logging.info(f"format_response(): format_transcription --> {format_transcription}")

    response = VoiceResponse()
    if "False" in format_transcription:
        response.redirect(url_for('ask_question', _external=True, Retry='true'))
    else:
        custom_agent.conversations[current_question] = format_transcription
        session['question_idx'] = question_idx + 1
        response.redirect(url_for('ask_question', _external=True))
    return str(response)

@app.route("/")
def home():
    logging.info("Flask application is running")
    return "Flask application is running"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
    
