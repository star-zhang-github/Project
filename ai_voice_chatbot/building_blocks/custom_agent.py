from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class CustomAgent():
    def __init__(self, question_prompt):
        self.question_prompt = question_prompt
        self.file_path = './building_blocks/data.json'
        self.questions = self._load_questions()
        self.conversations = {} # dictionary mapping responses to questions

    def _load_questions(self):
        with open(self.file_path, 'r') as file:
            questions = json.load(file)["questions"]
        return questions

    def get_question(self, question_idx):
        if question_idx < len(self.questions):
            question = self.questions[question_idx]
        else:
            # no more questions
            return -1
        return question

    # define value response function
    def get_response(self, question, response):
        prompt = f"""
            Extract and return the key word answer from the text provided for the question.\n
            Here is an example what you should do --> Example Question: 'what is your name?' Example Text: 'My name is Star Zhang, it spells like S T A R Z H A N G'. Example Return: 'Star Zhang' \n
            Here are the actual question and text following -->
            Actual Question: {question}\n 
            Actual Text: {response}\n. 
            """
        result = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
            {"role": "system", "content": "you are a call agent who extract the key word answer from the text for the question provided"},
            {"role": "user", "content": prompt}
            ]
        )
        result_text = result.choices[0].message.content
        print(f"result_text: {result_text}")
        return result_text

    def add_record(self):
        with open(self.file_path, 'r') as file:
            data = json.load(file)
    
        data["records"].append(self.conversations)

        with open(self.file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        

if __name__ == "__main__":

    #define the prompt templates for asking questions
    question_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a chatbot acting as a call center to receive patient calls for doctor appointment"),
        ("ai", "{question}")
        ])
    custom_agent = CustomAgent(question_prompt=question_prompt)
    conversations = custom_agent.run_agent()
    for question, response in conversations.items():
        print(f"Question: {question} \n")
        print(f"Response: {response} \n")


