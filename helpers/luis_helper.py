# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext

from booking_details import BookingDetails


class Intent(Enum):
    BOOK_FLIGHT = "BookFlight"
    CANCEL = "Cancel"
    GET_WEATHER = "GetWeather"
    NONE_INTENT = "NoneIntent"


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    print('5')
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> (Intent, object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)

            intent = (
                sorted(
                    recognizer_result.intents,
                    key=recognizer_result.intents.get,
                    reverse=True,
                )[:1][0]
                if recognizer_result.intents
                else None
            )

            if intent == Intent.BOOK_FLIGHT.value:
                print('6')
                result = BookingDetails()
                print(recognizer_result.entities.get("$instance", {}))
                
                # We need to get the result from the LUIS JSON which at every level returns an array.
                # this is the result providing the destination
                to_entities = recognizer_result.entities.get("$instance", {}).get("To", [])
                if len(to_entities) > 0:
                    if recognizer_result.entities.get("To", [{"$instance": {}}])[0]:
                        print(to_entities[0]["text"].capitalize())
                        result.destination = to_entities[0]["text"].capitalize()
                    else:
                        result.unsupported_airports.append(
                            to_entities[0]["text"].capitalize()
                        )
                # this is the result providing the starting point
                from_entities = recognizer_result.entities.get("$instance", {}).get("From", [])
                if len(from_entities) > 0:
                    if recognizer_result.entities.get("From", [{"$instance": {}}])[0]:
                        result.origin = from_entities[0]["text"].capitalize()
                        print(from_entities[0]["text"].capitalize())
                    else:
                        result.unsupported_airports.append(
                            from_entities[0]["text"].capitalize()
                        )
                
                # this is the result providing the amount of money to spend
                money_entities = recognizer_result.entities.get("$instance", {}).get("money", [])                       
                if len(money_entities) > 0:
                    if recognizer_result.entities.get("money", [{"$instance": {}}])[0]:
                        result.money = money_entities[0]["text"]
                        print(money_entities[0]["text"])
                    else:
                        result.money = None
 
                # this is the result providing the traveling Date
                ondate_entities = recognizer_result.entities.get("$instance", {}).get("ondate", [])
                #print(ondate_entities)
                if len(ondate_entities) > 0:
                    if recognizer_result.entities.get("ondate", [{"$instance": {}}])[0]:
                        result.travel_date = ondate_entities[0]["text"]
                        print('test on:', ondate_entities[0]["text"])
                    else:
                        result.travel_date = None

                # this is the result providing the returning Date
                backdate_entities = recognizer_result.entities.get("$instance", {}).get("backdate", [])
                #print(backdate_entities)
                if len(backdate_entities) > 0:
                    if recognizer_result.entities.get("backdate", [{"$instance": {}}])[0]:
                        result.travel_date_back = backdate_entities[0]["text"]
                        print('test back:', backdate_entities[0]["text"])
                    else:
                        result.travel_date_back = None
                        
                        
                        
                # This value will be a TIMEX. And we are only interested in a Date so grab the first result and drop
                # the Time part. TIMEX is a format that represents DateTime expressions that include some ambiguity.
                # e.g. missing a Year.
                #date_entities = recognizer_result.entities.get("datetime", [])
                #dates = recognizer_result.entities.get("$instance", {}).get("ondate", [])
                #date_entities = dates.get("datetime", [])
                #print('essai ondate:', dates.get("datetime", []))
                #if date_entities:
                #    timex = date_entities[0]["timex"]
#
                 #   if timex:
                 #       datetime = timex[0].split("T")[0]
                 #       
#
 #                       result.travel_date = datetime
#
 #               else:
  #                  result.travel_date = None                      
                            


        except Exception as exception:
            print(exception)

        return intent, result
