# Helpline_Triager

Use ChatGPT over Twilio to create an AI phone agent to redirect distress calls to relevant helpline.

### How it works

Twilio Webhook -> Flask app -> Twilio Media Stream (websocket) -> Whisper -> ChatGPT API -> Google TTS -> Twilio Play Audio

### How to use

1. `pip install -r requirements.txt`
2. Set environment variables in `keys.env` file

```
OPENAI_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
NGROK_DOMAIN=localhost
```


### Demo

#### Basic Text Chat

Try `PYTHONPATH=. python examples/keyboard_chat_with_gpt.py` to chat with GPT through terminal.

#### Twilio Helpline Receiver

Try `PYTHONPATH=. python examples/twilio_triage_receiver.py --preload_whisper --start_ngrok`. This requires whisper installed locally.

This will create an ngrok tunnel and provide a webhook URL to point to in Twilio settings for a purchased phone number.

<img width="1169" alt="chrome_VZSfJHN6FV" src="https://github.com/sshh12/llm_convo/assets/6625384/1fe9468d-0eb3-4309-9b81-1d2f3d02c353">

#### Twilio Helpline Caller

Try `PYTHONPATH=. python examples/twilio_triage_caller.py --preload_whisper --start_ngrok --phone_number "+1.........."`. This requires whisper installed locally.

This will create an ngrok tunnel and provide a webhook URL to point to in Twilio settings for a purchased phone number. Once the webhook is updated, it will start an outgoing call to the provided phone number.
