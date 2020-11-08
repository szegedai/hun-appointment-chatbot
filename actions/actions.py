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


class ActionListSpecificDate(Action):
    def __init__(self):
        with open('test_data.json', 'r') as f:
            self.data = json.load(f)


    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(tracker.latest_message)
        response = ''
        for entity in tracker.latest_message['entities']:
            if entity['value']:
                response += f'Elérhető időpontok ({entity["value"]}): {self.data[entity["value"]][0]}'

        dispatcher.utter_message(text=response)

        return []

class ActionListAllDate(Action):

    def name(self) -> Text:
        return "action_list_all"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(tracker.latest_message['entities'][0]['value'])
        print(tracker.latest_message['entities'])
        dispatcher.utter_message(text='From actions.py')

        return []
