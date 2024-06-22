from gevent import monkey

monkey.patch_all()

from dotenv import load_dotenv
from pathlib import Path
import os
load_dotenv(f"{Path(os.path.dirname(__file__)).parent}/keys.env")

import logging
import argparse
import tempfile
import time
from llm_convo.agents import OpenAIChat, TwilioCaller
from llm_convo.audio_input import get_whisper_model
from llm_convo.twilio_io import TwilioServer
from llm_convo.conversation import run_conversation
from pyngrok import ngrok


def main(port, remote_host, start_ngrok):
    if start_ngrok:
        ngrok_http = ngrok.connect(port, domain=remote_host)
        remote_host = ngrok_http.public_url.split("//")[1]
        logging.info(f"ngrok tunnel: {ngrok_http.public_url}")

    static_dir = os.path.join(tempfile.gettempdir(), "twilio_static")
    os.makedirs(static_dir, exist_ok=True)

    logging.info(f"Starting server at {remote_host} from local:{port}, serving static content from {static_dir}")
    logging.info(f"Set call webhook to https://{remote_host}/incoming-voice")

    tws = TwilioServer(remote_host=remote_host, port=port, static_dir=static_dir)
    tws.start()
    agent_a = OpenAIChat(
        system_prompt="You are a machine learning assistant. Answer the users questions about machine learning with short rhymes. Ask follow up questions when needed to help clarify their question.",
        init_phrase="Hello! Welcome to the Machine Learning hotline, how can I help?",
    )

    def run_chat(sess):
        agent_b = TwilioCaller(sess, thinking_phrase="One moment.")
        while not agent_b.session.media_stream_connected():
            time.sleep(0.1)
        run_conversation(agent_a, agent_b)

    tws.on_session = run_chat


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--preload_whisper", action="store_true")
    parser.add_argument("--start_ngrok", action="store_true")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--remote_host", type=str,
                        default=(os.getenv("NGROK_DOMAIN")
                                 if os.getenv("NGROK_DOMAIN")
                                 else "localhost")
                        )
    args = parser.parse_args()
    if args.preload_whisper:
        get_whisper_model()
    main(args.port, args.remote_host, args.start_ngrok)
