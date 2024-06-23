# Helpline Triager

Use ChatGPT over Twilio to create an AI phone agent to redirect distress calls to relevant helpline.

While reporting or seeking help in a distress situations, finding the appropriate help can be challenging. This project aims to streamline the process by providing a single helpline number that redirects caller-provided information to the relevant helpline.
Such an approach address common obstacles faced during distress situations such as lack of internet access, reluctance to self-identify, and the precious time-consuming task of locating the correct helpline number. 
By offering a centralized and user-friendly solution, this project aims to facilitate prompt access to the necessary support during times of distress.

### How it works

Twilio Webhook -> Flask app -> Twilio Media Stream (websocket) -> Whisper -> ChatGPT API -> Google TTS -> Twilio Play Audio

### How to use

1. `pip install -r requirements.txt`
2. Set environment variables in `keys.env` file

```
OPENAI_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=+1...
NGROK_DOMAIN=localhost
HELPLINES={'health': '+91...', 'fire': '', 'police': '', 'ambulance': ''}
REGISTERED_CONTACT='+91...'
```

Run `PYTHONPATH=. python examples/twilio_triage_receiver.py --preload_whisper --start_ngrok`. 

Note: This requires whisper installed locally. This will create an ngrok tunnel and provide a webhook URL to point to in Twilio settings for a purchased phone number. 

The server is now ready to receive calls. When someone calls the `TWILIO_PHONE_NUMBER`, based on the conversation the call will be redirected to the available helpline number provided in `HELPLINES`. Additionally, a message is also sent.

### Note
- You can use [twilio dev-phone](https://www.twilio.com/docs/labs/dev-phone) to test the application without using a real phone number.
- `REGISTERED_CONTACT` can be another twilio number or a real phone number. This number will receive a message/call when the call is redirected.
- This server endpoint can be extended to be used with widget, gestures, or other input methods to avoid explicit calling. Such use of this endpoint can be crucial save precious time in distress situations.