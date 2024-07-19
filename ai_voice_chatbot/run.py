from flask import Flask, request, redirect, url_for, session
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
import building_blocks.custom_agent as custom_agent
from building_blocks.speech_to_text import STT
import logging


logging.basicConfig(filename='app.log', filemode='a', level=logging.INFO)

load_dotenv()
app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")


# Initialize Twilio client
client = Client(account_sid, auth_token)


# define the prompt templates for asking questions and initialize the custom_agent
question_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a chatbot acting as a call center to receive patient calls for doctor appointment. "),
    ("ai", "{question}")
    ])
custom_agent = custom_agent.CustomAgent(question_prompt=question_prompt, question_type="doctor_appointment")
# questions = custom_agent.questions

@app.before_request
def initialize_session():
    if 'question_idx' not in session:
        session['question_idx'] = 0
        # session['current_question'] = None
        session['translation'] = None
        session['format_translation'] = None
# question_idx = 0
# finished_asked_idx = -1

@app.route("/answer", methods=['GET','POST'])
def answer_call():
    # global question_idx
    # question_idx = 0
    # finished_asked_idx = -1

    logging.info("Entering answer_call(): Call received")

    response = VoiceResponse()
    # response.say("Welcome to booking your doctor appointment. Please note that to deliver high quality automated service, you might have to wait a few seconds for the AI call assistant to respond.")
    
    response.say("Welcome")
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

    # if request.args.get('Retry') == 'true':

    #     logging.info(f"ask_question(): request.args.get('Retry') == 'true'")

    #     response.say("Sorry, I didn't quite get that. Let's try again.")
    #     response.pause(length=1)

    if current_question != -1:
        response.say(current_question) 
        # finished_asked_idx = question_idx
        # response.pause(length=1)

        logging.info(f"ask_question(): started recording for '{current_question}'")
        response.record(max_length=10, action="/handle-recording", finishOnKey="#", method="POST", recording_status_callback='/recording-status')
        logging.info(f"ask_question(): finished recording for '{current_question}'")
    else:
        logging.info(f"ask_question(): custom_agent.conversations --> '{custom_agent.conversations}'")
        custom_agent.add_record()
        response.say("Finished collecting all information. Bye!")
        logging.info(f"ask_question(): End of the call'")

    return str(response)

@app.route("/handle-recording", methods=['POST'])
def handle_recording():
    global question_idx

    response = VoiceResponse()
    recording_url = request.form["RecordingUrl"]

    if not recording_url:
        return "No recording URL provided", 400
    # Play back the recordingd
    # response.say("Thank you for your message. Here is what you said.")
    logging.info(f"handle_recording(): recording_url --> {recording_url}")
    stt = STT(url=recording_url)
    translation = stt.translate_audio()
    session['translation'] = translation
    response.redirect(url_for('format_response'))

    return str(response)

@app.route("/format-response", methods=['POST','GET'])
def format_response():
    question_idx = session.get('question_idx', 0)
    format = custom_agent.get_format(question_idx)
    current_question = custom_agent.get_question(question_idx)
    translation = session['translation']
    format_translation = custom_agent.get_response(current_question, translation, format)
    custom_agent.conversations[current_question] = format_translation

    logging.info(f"format_response(): translation --> {translation} ")
    logging.info(f"format_response(): format_translation --> {format_translation}")
    session['question_idx'] = question_idx + 1
    session['format_translation'] = format_translation

    response = VoiceResponse()
    response.redirect(url_for('ask_question'))
    return str(response)


# Optional: Endpoint to handle recording status
@app.route("/recording-status", methods=['POST'])
def recording_status():
    recording_sid = request.form.get("RecordingSid")
    recording_status = request.form.get("RecordingStatus")
    logging.info(f"Recording SID: {recording_sid}, Status: {recording_status}")
    return ("", 204)


@app.route("/")
def home():
    logging.info("Flask application is running")
    return "Flask application is running"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
    
