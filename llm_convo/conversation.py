import logging
import json
import ast
import os
from typing import Optional

from llm_convo.agents import ChatAgent
from llm_convo.twilio_io import TwilioServer


def run_conversation(agent_a: ChatAgent, agent_b: ChatAgent, tws: Optional[TwilioServer]):
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
                    logging.info("Sending SMS for help")

                    if tws.entities:
                        to_number = os.getenv("REGISTERED_CONTACT")

                        try:
                            helplines = ast.literal_eval(os.getenv("HELPLINES"))
                            for k, v in helplines.items():
                                entity_text = '\n'.join([f"{kk}: {tws.entities[kk]}" for kk in tws.entities])
                                if k in entity_text:
                                    to_number = helplines[k]
                                    break
                        except Exception as e:
                            logging.error(f"Error while parsing for helplines: {e}")

                        summary = tws.summarize_agent.summarize(tws.entities)
                        # send message
                        message = tws.client.messages.create(
                            body=f"Received distress call with details: {summary}",
                            from_=tws.from_phone,
                            to=to_number,
                        )
                        logging.info(f"Sent SMS: {message.body}")

                        # make call
                        call = tws.client.calls.create(
                            twiml=f"<Response><Say>{summary}</Say></Response>",
                            from_=os.getenv("TWILIO_PHONE_NUMBER"),
                            to=to_number,
                        )
                        logging.info(f"Made a call: {call.sid}")

                    transcript.append("Thank you for your call. We have sent help.")
                    agent_a.get_response(transcript)
                    break
        except Exception as e:
            logging.error(e)
            break
