import logging
import json
from typing import Optional

from llm_convo.agents import ChatAgent
from llm_convo.twilio_io import TwilioServer


def run_conversation(agent_a: ChatAgent, agent_b: ChatAgent, tws: Optional[TwilioServer], kwargs):
    transcript = []
    while True:
        try:
            text_a = agent_a.get_response(transcript)
            transcript.append(text_a)
            print("->", text_a)
            text_b = agent_b.get_response(transcript)
            transcript.append(text_b)
            print("->", text_b)
            print("===>", transcript)

            if tws:
                entities = tws.entity_agent.get_extracted_entities(transcript)
                try:
                    tws.entities = json.loads(entities)
                    logging.info(f"Extracted entities: {tws.entities}")
                except Exception as e:
                    logging.error(f"Error while parsing for entities: {e}\n"
                                  f"entities: {entities}")
                    pass

                is_call_end = tws.call_end_agent.is_call_end(transcript)
                logging.info(f"Is call end: {is_call_end}")
                if "yes" in is_call_end.strip().lower():
                    break
        except Exception as e:
            logging.error(e)
            break

    logging.info("Sending SMS for help")
    if tws.entities:
        message = tws.client.messages.create(
            body=f"Received distress call with details: {tws.entities}",
            from_=tws.from_phone,
            to="",
        )
        logging.info(f"Sent SMS: {message.body}")

