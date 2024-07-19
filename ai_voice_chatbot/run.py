from flask import Flask, request, redirect, url_for
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
import building_blocks.custom_agent as custom_agent
import time
import logging
from archives.get_transcript import user_response_transcript

logging.basicConfig(filename='app.log', filemode='a', level=logging.INFO)


app = Flask(__name__)
app.config['TIMEOUT'] = 500
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")


# Initialize Twilio client
client = Client(account_sid, auth_token)
response = VoiceResponse()


# define the prompt templates for asking questions and initialize the custom_agent
question_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a chatbot acting as a call center to receive patient calls for doctor appointment. "),
    ("ai", "{question}")
    ])

custom_agent = custom_agent.CustomAgent(question_prompt=question_prompt)
questions = custom_agent.questions
current_question = None
question_idx = 0
finished_asked_idx = -1

@app.route("/answer", methods=['GET','POST'])
def answer_call():
    global question_idx, finished_asked_idx
    question_idx = 0
    finished_asked_idx = -1
    app.config['TIMEOUT'] = 500

    logging.info("Entering answer_call(): Call received")

    response = VoiceResponse()
    response.say("Welcome to booking your doctor appointment. ")
    response.redirect(url_for('ask_question', _external=True))

    logging.info("answer_call(): redirected to ask_question()")

    return str(response)

@app.route("/ask-question", methods=['GET', 'POST'])
def ask_question():
    global current_question, question_idx, finished_asked_idx
    app.config['TIMEOUT'] = 500
    response = VoiceResponse()
    logging.info(f"Entering ask_question()")
    
    logging.info(f"request.args.get('Retry') {request.args.get('Retry')}")
    if request.args.get('Retry') == 'true':

        logging.info(f"ask_question(): request.args.get('Retry') == 'true'")
        response.say("Sorry, I didn't quite get that. Let's try again.")
        response.pause(length=1)

    logging.info(f"ask_question(): finished_asked_idx --> '{finished_asked_idx}'")
    logging.info(f"ask_question(): question_idx --> '{question_idx}'")

    # start_time = time.time()
    # while finished_asked_idx == question_idx:
    #     time.sleep(0.1)
    # end_time = time.time()
    # elapsed_time = end_time - start_time

    # logging.info(f"ask_question(): elapsed_time --> '{elapsed_time}'")
    if finished_asked_idx == question_idx:
        logging.info("=======")
        response.redirect(url_for('process_recording', _external=True))


    current_question = custom_agent.get_question(question_idx)
    if current_question != -1:
        response = VoiceResponse()
        response.say(current_question) 
        finished_asked_idx = question_idx
        response.pause(length=1)

        logging.info(f"ask_question(): started recording for '{current_question}'")
        response.record(max_length=6, transcribe=True, recording_status_callback=url_for('process_recording', _external=True))
        logging.info(f"ask_question(): finished recording for '{current_question}'")
        logging.info(f"ask_question(): redirect to process_recording()")
    else:
        logging.info(f"ask_question(): custom_agent.conversations --> '{custom_agent.conversations}'")
        response = VoiceResponse()
        custom_agent.add_record()
        response.say("Finished collecting all information. Bye!")
        logging.info(f"ask_question(): End of the call'")

    return str(response)

@app.route("/process-recording", methods=['GET', 'POST'])
def process_recording():
    response = VoiceResponse()
    process_status, _ = user_response_transcript(account_sid, auth_token)
    logging.info(f"process_recording(): process_status --> {process_status}")
    if process_status != "completed":
        response.redirect(url_for('wait_for_transcript', _external=True))
        #wait_for_transcript()
    elif process_status == "completed":
        response.redirect(url_for('handle_response', _external=True))
        logging.info(f"process_recording(): finished transcript for {current_question}")
        logging.info(f"process_recording(): heading to handle_response")
    return str(response)


@app.route("/wait-for-transcript", methods=['GET','POST'])
def wait_for_transcript():
    response = VoiceResponse()
    time.sleep(5)
    #process_recording()
    response.redirect(url_for('process_recording', _external=True))
    return str(response)


@app.route("/handle-response", methods=['GET', 'POST'])
def handle_response():
    logging.info("Entering handle_response()")
    global current_question, question_idx
    app.config['TIMEOUT'] = 500

    response_transcript = user_response_transcript(account_sid, auth_token)
    logging.info("handle_response(): response_transcript received")
    logging.info(f"handle_response(): response_transcript --> '{response_transcript}'")

    if not response_transcript:
        logging.info("handle_response(): response_transcript is None")
        response = VoiceResponse()
        #response.say("I'm sorry, but I couldn't process your response. Let's try again.")
        response.redirect(url_for('ask_question', Retry='true', _external=True))
        logging.info("handle_response(): redirect to ask_question() due to empty transcript")
        return str(response)
    else:
        logging.info("handle_response(): response_transcript is not None")
        valid_response = custom_agent.get_response(current_question, response_transcript)
        logging.info(f"handle_response(): valid_response processed --> '{valid_response}'")

        response = VoiceResponse()
        if valid_response:
            response = VoiceResponse()
            logging.info(f"handle_response(): valid_response is not None")

            custom_agent.conversations[current_question] = valid_response
            question_idx += 1  # Move to the next question

            logging.info(f"handle_response(): '{current_question}' collected successfully")
            logging.info(f"handle_response(): '{current_question}: {custom_agent.conversations[current_question]}'")
            logging.info(f"handle_response(): updated question_idx --> '{question_idx}'")

            response.redirect(url_for('ask_question', _external=True, intial='true'))

            logging.info(f"handle_response(): redirect to ask_question() due to success")
        else:
            response = VoiceResponse()
            logging.info(f"handle_response(): valid_response is None")
            response.redirect(url_for('ask_question', Retry='true', _external=True))
            logging.info(f"handle_response(): redirect to ask_question() and retry='True'")
    
    return str(response)


@app.route("/")
def home():
    logging.info("Flask application is running")
    return "Flask application is running"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
    
