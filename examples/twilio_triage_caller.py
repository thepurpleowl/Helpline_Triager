from gevent import monkey

monkey.patch_all()

from dotenv import load_dotenv
from pathlib import Path
import os
load_dotenv(f"{Path(os.path.dirname(__file__)).parent}/keys.env")

import logging
import argparse
import tempfile
import os
import time
import sys
from llm_convo.agents import OpenAIChat, TwilioCaller
from llm_convo.audio_input import get_whisper_model
from llm_convo.twilio_io import TwilioServer
from llm_convo.conversation import run_conversation
from pyngrok import ngrok


def main_caller(port, remote_host, start_ngrok, phone_number):
    if start_ngrok:
        ngrok_http = ngrok.connect(port, domain=remote_host)
        remote_host = ngrok_http.public_url.split("//")[1]
        logging.info(f"ngrok tunnel public url: {ngrok_http.public_url}")

    static_dir = os.path.join(tempfile.gettempdir(), "twilio_static")
    os.makedirs(static_dir, exist_ok=True)

    logging.info(
        f"Starting server at {remote_host} from local:{port}, serving static content from {static_dir}, will call {phone_number}"
    )
    logging.info(f"Set call webhook to https://{remote_host}/incoming-voice")

    input(" >>> Press enter to start the call after ensuring the webhook is set. <<< ")

    tws = TwilioServer(remote_host=remote_host, port=port, static_dir=static_dir)
    tws.start()
    agent_a = OpenAIChat(
        system_prompt="""
    You are a distress call handler. You are responsible for informing the {helpline} helpline with following possible distress details.
    Keep in mind that you are making this call on behalf of another caller. If they ask for information not known, make use of following details.

    Available helpline and distress details are:
    * Helpline type: {helpline}
    * Incident type: {distress}
    * Caller Name: {name}
    * Incident location: {location}
    * Incident time: {time}
    * Incident description: {description}
    """,
        init_phrase="Hi, I want to report a incident.",
    )

    def run_chat(sess, tws: TwilioServer):
        agent_b = TwilioCaller(sess, thinking_phrase="One moment.")
        while not agent_b.session.media_stream_connected():
            time.sleep(0.1)
        run_conversation(agent_a, agent_b, tws)
        sys.exit(0)

    tws.on_session = run_chat
    tws.start_call(phone_number)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--phone_number", type=str)
    parser.add_argument("--preload_whisper", action="store_true")
    parser.add_argument("--start_ngrok", action="store_true")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--remote_host", type=str, default="localhost")
    args = parser.parse_args()
    if args.preload_whisper:
        get_whisper_model()
    main_caller(args.port, args.remote_host, args.start_ngrok, args.phone_number)
