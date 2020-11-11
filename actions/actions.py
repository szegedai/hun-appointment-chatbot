# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import json
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

"""
class ActionListSpecificDate(Action):
    def __init__(self):
        with open('test_data.json', 'r') as f:
            self.data = json.load(f)


    def name(self) -> Text:
        return "action_list_specific"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(tracker.latest_message)
        print(tracker.slots)
        response = 'Elérhető időpontok\n'
        for entity in tracker.latest_message['entity']:
            for date in entity['dates']:
                response += f'({date}): {self.data.get(date, "")}\n'

        if tracker.slots["dates"] is None:
            slots = SlotSet('dates', entity['dates'])
        else:
            slots = SlotSet('dates', tracker.slots["dates"] + entity['dates'])

        dispatcher.utter_message(text=response)

        return [slots]
"""


# class ActionListAllDate(Action):
#
#     def name(self) -> Text:
#         return "action_list_all"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         dispatcher.utter_message(text='From actions.py')
#
#         return []

class ActionIdopontForm(Action):
    def __init__(self):
        with open('test_data.json', 'r') as f:
            self.data = json.load(f)

    def name(self) -> Text:
        return "action_idopont_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print(tracker.latest_message)
        print(tracker.slots)

        slots = []
        response = ""

        if not tracker.slots['date']:
            any_date, good_date = False, None
            for entity in tracker.latest_message['entities']:
                if entity['entity'] == 'dates':
                    any_date = True
                    for date in entity['value']:
                        if date in self.data:
                            good_date = date
                            break

            if not any_date:
                response += "Okés. Mikor lenne jó?"
                slots += [SlotSet('date', None)]
            else:
                if not good_date:
                    response += "Sajnos az a nap nem jó... Egy másik esetleg?"
                    slots += [SlotSet('date', None)]
                else:
                    response += "Tökéletes dátum."
                    slots += [SlotSet('date', good_date)]

        if tracker.get_slot("date") is not None and tracker.slots['time'] is None:
            any_time, good_time = False, None
            for entity in tracker.latest_message['entities']:
                if entity['entity'] == 'times':
                    any_time = True
                    for time in entity['value']:
                        if time in self.data[tracker.slots['date']]:
                            good_time = time
                            break

            if not any_time:
                response += "Hány órakor?"
                slots += [SlotSet('time', None)]
            else:
                if not good_time:
                    response += "Sajnos az az időpont nem jó... Egy másik időpont esetleg?"
                    slots += [SlotSet('time', None)]
                else:
                    response += "Tökéletes időpont."
                    slots += [SlotSet('time', good_time)]

        dispatcher.utter_message(text=response)

        print(slots)
        return slots
