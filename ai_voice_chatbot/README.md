# AI_VOICE_CHATBOT
## Section 1: Summary
This is a voice chatbot I built using OpenAI llm and twilio APIs.
The chatbot allows you to call a twilio provided number. During the call, the AI chatbot will ask you a lsit of questions, for each question you will have 15 seconds to respond. If you didn't respond to the question, the chatbot will repeat the question and allow you to record again. 

The final output of all the answers to the list of predefined questions and the question list is stored in building_blocks/data.json

## Section 2: Steps to run the program:
1. Create a virtual environment, run in terminal *pip install -r requirements.txt*
2. Run in terminal *python .\building_blocks\run.py*
3. Open a new terminal, run *ngrok http 5000*
    - URL: Copy the forwarding address and add */answer* to the end of the address, example: *https://5ad3-68-129-210-90.ngrok-free.app/answer*
    - Copy the URL above to the URL textbox of the *A call comes in* section, and save
4. Call the twilio provided number and enjoy your time! You can check the logs of the program during and after the call in the terminal used in step 2.