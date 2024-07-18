from flask import Flask, request, redirect, url_for
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
import llm
import time


app = Flask(__name__)
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
verify_service_sid = os.getenv("VERIFY_SERVICE_SID")


# Initialize Twilio client
client = Client(account_sid, auth_token)


# define the prompt templates for asking questions and initialize the custom_agent
question_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a chatbot acting as a call center to receive patient calls for doctor appointment. "),
    ("ai", "{question}")
    ])

custom_agent = llm.CustomAgent(question_prompt=question_prompt)
questions = custom_agent.questions
current_question = None
question_idx = 0
finished_asking_which_question = -1

@app.route("/answer", methods=['GET','POST'])
def answer_call():
    global question_idx, finished_asking_which_question
    question_idx = 0
    finished_asking_which_question = -1
    print("Received call")
    response = VoiceResponse()

    response.say("Welcome to booking your doctor appointment. Please note that to deliver high quality automated service, you might have to wait a few seconds for the AI call assistant to respond.")
    response.redirect(url_for('ask_question', _external=True))

    return str(response)

@app.route("/ask-question", methods=['GET', 'POST'])
def ask_question():
    global current_question, question_idx, finished_asking_which_question
    print(f"[DBG] ask question, question_idx: {question_idx}")
    
    response = VoiceResponse()
    if request.args.get('Retry') == 'true':
        response.say("Sorry, I didn't quite get that. Let's try again.")
        response.pause(length=1)

    while finished_asking_which_question == question_idx:
        time.sleep(0.1)
    current_question = custom_agent.get_question(question_idx)

    if current_question != -1:
        response.say(current_question) 
        finished_asking_which_question = question_idx
        response.pause(length=1)
        print(f"question asked: {current_question} and recording for it")
        response.record(max_length=15, transcribe=True, transcribe_callback=url_for('handle_response', _external=True))

    else:
        print(custom_agent.conversations)
        custom_agent.add_record()
        response.say("Finished collecting all information. Bye!")

    return str(response)



@app.route("/handle-response", methods=['GET', 'POST'])
def handle_response():
    print("[DBG] passed into handle_response")
    global current_question, question_idx

    response_transcript = request.values.get('TranscriptionText')
    print(f"response_transcript: {response_transcript}")

    if not response_transcript:
        print("Failed to get transcription after multiple attempts")
        response = VoiceResponse()
        response.say("I'm sorry, but I couldn't process your response. Let's try again.")
        response.redirect(url_for('ask_question', _external=True, Retry='true'))
        return str(response)
    else:
        valid_response = custom_agent.get_response(current_question, response_transcript)
        print(f"valid_response: {valid_response}")

        response = VoiceResponse()
        if valid_response:
            custom_agent.conversations[current_question] = valid_response
            question_idx += 1  # Move to the next question
            print(f"{current_question} collected successfully")
            response.redirect(url_for('ask_question', _external=True, intial='true'))
        else:
            print(f"Sorry, I didn't quite get {current_question}. Let's try again.")
            response.redirect(url_for('ask_question', _external=True, Retry='true'))
    
    return str(response)


@app.route("/")
def home():
    return "Flask application is running"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
    
