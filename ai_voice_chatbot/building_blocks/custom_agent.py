from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class CustomAgent():
    def __init__(self, question_prompt, question_type):
        self.question_prompt = question_prompt
        self.question_type = question_type
        self.file_path = './building_blocks/data.json'
        self.questions_dic = self._load_questions_dic()
        self.conversations = {} # dictionary mapping responses to questions

    def _load_questions_dic(self):
        with open(self.file_path, 'r') as file:
            questions_dic = json.load(file)["questions_list"][self.question_type]
        return questions_dic

    def get_question(self, question_idx):
        if question_idx < len(self.questions_dic):
            question = self.questions_dic[question_idx]["question"]
        else:
            # no more questions
            return -1
        return question
    
    def get_format(self, question_idx):
        if question_idx < len(self.questions_dic):
            format = self.questions_dic[question_idx]["format"]
        else:
            # no more questions
            return -1
        return format

    # define value response function
    def get_response(self, question, response, format):
        prompt = f"""
            From the text provided for the question, extract and return answer in given format format.
            If the text provided does not contain the information about the question, return False
            Example:
                Question: 'what is your name?' 
                Text: 'My name is Charlie Brown'
                Example format: 'a string for name'
                Return: 'Charlie Brown'
            Actual:
                Question: {question}
                Text: {response}
                Format: {format}
            """
        result = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
            {"role": "system", "content": "you are a call agent who extract the key word answer from the text for the question provided in required format"},
            {"role": "user", "content": prompt}
            ]
        )
        result_text = result.choices[0].message.content
        return result_text

    def add_record(self):
        with open(self.file_path, 'r') as file:
            data = json.load(file)
    
        data["records"].append(self.conversations)

        with open(self.file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        

# if __name__ == "__main__":

#     #define the prompt templates for asking questions
#     question_prompt = ChatPromptTemplate.from_messages([
#         ("system", "You are a chatbot acting as a call center to receive patient calls for doctor appointment"),
#         ("ai", "{question}")
#         ])
#     custom_agent = CustomAgent(question_prompt=question_prompt)
#     conversations = custom_agent.run_agent()
#     for question, response in conversations.items():
#         print(f"Question: {question} \n")
#         print(f"Response: {response} \n")


