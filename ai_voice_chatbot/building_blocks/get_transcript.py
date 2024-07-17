import requests
import os
# from requests.auth import HTTPBasicAuth
#from dotenv import load_dotenv
# from twilio.rest import Client
import certifi

#load_dotenv()
# account_sid = os.getenv("TWILIO_ACCOUNT_SID")
# auth_token = os.getenv("TWILIO_AUTH_TOKEN")



def user_response_transcript(account_sid, auth_token):
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Transcriptions.json"
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
    response = requests.get(url, auth=(account_sid, auth_token))

    if response.status_code == 200:
        transcription_json = response.json()
    print(f"status code: {response.status_code}")

    transcription = transcription_json['transcriptions'][0]
    user_response = transcription['transcription_text']
    return user_response


#print(user_response_transcript(account_sid, auth_token))


# if __name__ == "__main__":
#     print(f"status code: {response.status_code}")
#     print(transcription_json)

# def message():
#     client = Client(account_sid, auth_token)
#     print(client)
#     transcription = client.transcriptions.list(limit=1)
#     print(transcription)
#     sid = transcription[0].sid
#     t = client.transcriptions(sid).fetch()
#     print(t.transcription_text)
#     return str(sid)

# if __name__ == '__main__':
#     message()

# # Your credentials
# username = 'your_username'
# password = 'your_password'
# # Send a GET request to the URL with Basic Auth
# response = requests.get(url, auth=HTTPBasicAuth(username, password))


