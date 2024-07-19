# AI_VOICE_CHATBOT
## Section 1: Summary: The AI voice chatbot that collects information on your behalf
This is a voice chatbot I built using OpenAI llm and twilio APIs.
The chatbot allows you to call a twilio provided number. During the call, the AI chatbot will ask you a list of questions from *building_blocks/data.json*, for each question you will have 15 seconds to respond. If you didn't respond to the question, the chatbot will repeat the question and allow you to record again. 

After recording each question, the program will transcribe the recording to transcript and extract out the keyword of the transcript for the question asked.

The final output of all the answers to the list of predefined questions are stored in building_blocks/data.json. 

FYI: You can modify the question list to customize it for your own.

## Section 2: Steps to run the program locally:
1. Create a virtual environment, run in terminal *pip install -r requirements.txt*
2. create an .env file and store all needed API credentials
    - OPENAI_API_KEY
    - ngrok_token_key
    - TWILIO_ACCOUNT_SID
    - TWILIO_AUTH_TOKEN
    - FLASK_SECRET_KEY
3. Run in terminal *python run.py*
4. Open a new terminal, run *ngrok http 5000*
    - URL: Copy the forwarding address and add */answer* to the end of the address, example: *https://5ad3-68-129-210-90.ngrok-free.app/answer*
    - Copy the URL above to the URL textbox of the *A call comes in* section on website https://console.twilio.com/us1/develop/phone-numbers/manage/incoming/, and save
5. Call the twilio provided number and enjoy your time! You can check the logs of the program during and after the call in the *app.log* file.

## Section 3: Try out the product without setting up
6. If To try out Star Zhang's Twilio number (855) 778-1299
 please contact first to add your phone number to the incoming call permission list.