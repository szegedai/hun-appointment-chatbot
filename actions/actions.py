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
from rasa_sdk.events import SlotSet, EventType

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
            domain: Dict[Text, Any]) -> List[EventType]:

        print('pre action', tracker.slots)

        slots = []
        response = ""

        if tracker.get_slot('date') is None:
            any_date, good_date = False, []
            for entity in tracker.latest_message['entities']:
                if entity['entity'] == 'dates':
                    any_date = True
                    for date in entity['value']:
                        if date in self.data.keys():
                            good_date += [date]
                            break
            #nincs datum
            if not any_date:
                print("NINCS DATUM")
                response += "Okés. Mikor lenne jó?"
                dispatcher.utter_message(text=response)
                return [SlotSet('requested_slot', 'date')]
            else:
                #van datum de nincs listaban
                if len(good_date) == 0:
                    print("VAN DATUM DE NINCS LISTABAN")
                    response += "Sajnos az a nap nem jó... Egy másik esetleg?"
                    dispatcher.utter_message(text=response)
                    #return [SlotSet('requested_slot', 'date')]
                #jo datum
                else:
                    print("JO DATUM")
                    response += "Rendben. Hány órakor lenne jó?"
                    dispatcher.utter_message(text=response)
                    return [SlotSet('date', good_date)]

        if tracker.get_slot("date") is not None:
            print("DATUM BEALLITVA")
            any_time, good_time = False, []
            for entity in tracker.latest_message['entities']:
                if entity['entity'] == 'times':
                    any_time = True
                    for time in entity['value']:
                        print(time, "TIME")
                        print(tracker.get_slot('date'), "SLOTBAN")
                        for possible_date in tracker.get_slot('date'):
                            if time in self.data[possible_date]:
                                good_time += [time]
                                break
            #nincs idő
            if not any_time:
                print("NINCS IDŐPONT")
                print(tracker.get_slot('date'))
                return [SlotSet('requested_slot', 'time')]

            else:
                if not good_time:
                    print("VAN IDŐPONT DE NINCS LISTÁBAN")
                    response += "Sajnos az az időpont nem jó... Egy másik időpont esetleg?"
                    dispatcher.utter_message(text=response)
                    #return [SlotSet('requested_slot', 'time')]
                else:
                    print("VAN IDŐPONT ÉS JÓ IS")
                    response += "Tökéletes időpont."
                    dispatcher.utter_message(text=response)
                    return [SlotSet('time', good_time), SlotSet('requested_slot', None)]

        return [SlotSet('requested_slot', None)]

class ActionSubmitForm(Action):
    def name(self) -> Text:
        return "submit_idopont_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(template="utter_submit",
                                 date=tracker.get_slot('date'),
                                 time=tracker.get_slot('time'))
        return []