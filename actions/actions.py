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
