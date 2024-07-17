from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from typing import Callable

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
'''
Use LangChain to handle the conversation dynamically 
'''

class CustomAgent():
    def __init__(self, question_prompt, questions, validate_response: Callable):
        self.question_prompt = question_prompt
        self.questions = questions
        self.validate_response = validate_response
        self.conversations = {}
        self.question_idx = 0

    def _ask_question(self, question):
        prompt = self.question_prompt.format(question=question)
        # TTS to ask the question
        response = input(f"{prompt}: ")
        # response = VoiceResponse()
        # response.say(prompt)

        # take the voice input from twilio and transform it back to text
        # response = (the text transformed)
        #print(response)
        return response

    
    def run_agent(self):

        for question in self.questions:
            valid_response = False
            while not valid_response:
                response = self._ask_question(question=question)
    
                valid_response = self.validate_response(question, response)
                if valid_response:
                    self.conversations[question] = response
                else:
                    print("I didn't quite get that. Please say again.")
        
        return self.conversations

    def ask_question(self):
        question = self.questions(self.question_idx)
        return question


# define the prompt templates for asking questions
question_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a chatbot acting as a call center to receive patient calls for doctor appointment"),
    ("ai", "{question}")
    ])

# load the list of questions from json file
with open('./building_blocks/questions.json', 'r') as file:
    questions = json.load(file)["questions"]


# define value response function
def validate_response(question, response):
    validation_prompt = f"Question: {question}\nResponse: {response}\nIs this response acceptable and reasonable? Answer with 'yes' or 'no' and explain why."
    validation_result = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": "you are a call agent who can validate if the response given to the questions are valid and response with 'yes' or 'no'"},
        {"role": "user", "content": validation_prompt}
        ]
    )
    result_text = validation_result.choices[0].message.content
    print(f"result_text: {result_text}")
    return "yes" in result_text.lower()


if __name__ == "__main__":
    custom_agent = CustomAgent(question_prompt=question_prompt, questions=questions, validate_response=validate_response)
    conversations = custom_agent.run_agent()
    for question, response in conversations.items():
        print(f"Question: {question} \n")
        print(f"Response: {response} \n")


