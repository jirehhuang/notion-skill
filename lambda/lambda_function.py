# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

## my packages
import re
import datetime
import requests
import json
# import urllib.request

## Replace with inputs
WEBHOOK_URL = ''
WEBHOOK_SECRET = ''

## globals
MODE = ""
# MODE = "other"
if (MODE == "other"):
    REQUIRED_USER_ID = ""
else:
    REQUIRED_USER_ID = "amzn1.ask.account.AMAYQMU7DJOT2MUABCHD2BAPCEQFFAI4JEDTFIZN7NVKWQDGJJFRJS5E7K3KT2TVLX5SEK45BMDXGYFPXHXAZRLGTWHPCDKVL4S7ZFSGFNKZF34MBYLLHN6U5FA74GI6KELVTCDGVAGU4CTKJ4GFIGBVZW3VWTIR2AMRBJDPMVZE3TUOXLD3OPTYPWQS24B4NABVR7USHUQZVXPW6C3HABDTLWH4MF55XK5JA7VFEDGQ"


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Yes?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class QueryIntentHandler(AbstractRequestHandler):
    """Handler for QueryIntent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("QueryIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        ## check user
        user_id = ask_utils.request_util.get_user_id(handler_input)
        if (user_id not in ["", REQUIRED_USER_ID]):
            return (
                handler_input.response_builder
                    # .speak("Invalid user")
                    .speak("Invalid user: " + user_id)
                    .response
            )
            
        slots = handler_input.request_envelope.request.intent.slots
        query = slots["item_query"].value
        
        if (query in ["", "nevermind"]):
            reprompt = "I didn't catch that. Please try again."
            return handler_input.response_builder.ask(reprompt).response
        
        payload = {
            'secret': WEBHOOK_SECRET,
            'fn': 'new_page',
            'database': 'task',
            'title_text': query
        }
        post_response = requests.post(WEBHOOK_URL, json=payload)
        
        if post_response.status_code == 200:
            # speak_output = "Done."
            # ask_output = "Anything else?"
            speak_output = "Done. Anything else?"
        else:
            # speak_output = "Sorry, I couldn't do that."
            # ask_output = "Please try again."
            speak_output = "Please try again."
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask(ask_output)  # for some reason ask() isn't working
                .response
        )


class MarkDisciplineIntentHandler(AbstractRequestHandler):
    """Handler for MarkDisciplineIntent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("MarkDisciplineIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        def collapse_strings(strings):
            if len(strings) == 0:
                return ""
            elif len(strings) == 1:
                return strings[0]
            elif len(strings) == 2:
                return f"{strings[0]} and {strings[1]}"
            else:
                # Join all but the last element with ", " and append the last element with " and "
                return ", ".join(strings[:-1]) + f", and {strings[-1]}"
        
        ## check user
        user_id = ask_utils.request_util.get_user_id(handler_input)
        if (user_id not in ["", REQUIRED_USER_ID]):
            return (
                handler_input.response_builder
                    # .speak("Invalid user")
                    .speak("Invalid user: " + user_id)
                    .response
            )
            
        # slots = handler_input.request_envelope.request.intent.slots
        # discipline = slots["item_discipline"].value
        # payload = {
        #     'secret': WEBHOOK_SECRET,
        #     'fn': 'mark_discipline',
        #     'discipline': discipline
        # }
        # post_response = requests.post(WEBHOOK_URL, json=payload)
        
        # if post_response.status_code == 200:
        #     speak_output = "Done. Anything else?"
        # else:
        #     speak_output = "Please try again."
        
        ## initialize speak output
        speak_output = "Please try again."
        
        try:
            slots = ask_utils.get_simple_slot_values(ask_utils.get_slot_value_v2(handler_input, "item_discipline"))
            disciplines = []
            for x in slots:
                
                try:
                    # Attempt to access nested attributes
                    if x.resolutions is not None and \
                       x.resolutions.resolutions_per_authority is not None and \
                       x.resolutions.resolutions_per_authority[0].values is not None and \
                       x.resolutions.resolutions_per_authority[0].values[0].value is not None and \
                       x.resolutions.resolutions_per_authority[0].values[0].value.name is not None:
                         
                        disciplines.append(x.resolutions.resolutions_per_authority[0].values[0].value.name)
                        
                except AttributeError:
                    # Handle the case where any attribute is None or doesn't exist
                    continue
            payload = {
                'secret': WEBHOOK_SECRET,
                'fn': 'mark_disciplines',
                'disciplines': disciplines
            }
            post_response = requests.post(WEBHOOK_URL, json=payload)
            
            if post_response is not None and \
               post_response.status_code is not None and \
               post_response.status_code == 200:
                speak_output = f"Marked {collapse_strings(disciplines)}. Anything else?"
                    
        except Exception as e:
            speak_output = f"An unexpected error occurred: {e}"
            
        if (len(speak_output) == 0):
            speak_output = "Done."
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Would you like to add something to your list?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                # .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(QueryIntentHandler())
sb.add_request_handler(MarkDisciplineIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()