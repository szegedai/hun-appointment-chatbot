# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import json
from typing import Any, Text, Dict, List
from datetime import datetime, date, time

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType

from services.datetime2text import date2text, time2text


class ActionRemoveAppointment(Action):

    def name(self) -> Text:
        return "action_remove_appointment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [SlotSet('date', None), SlotSet('time', None)]


class ActionRecommendDate(Action):
    def __init__(self):
        with open('test_data.json', 'r') as f:
            self.data = json.load(f)

    def name(self) -> Text:
        return "action_recommend_date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if tracker.get_slot('date') is None:
            free_dates = list(self.data.keys())
            if len(free_dates) >= 2:
                response = f"Legközelebb {date2text(free_dates[0])} és {date2text(free_dates[1])} érek rá."
            elif len(free_dates) == 1:
                response = f"Legközelebb {date2text(free_dates[0])} érek rá."
            else:
                response = "Sajnos nincs szabad időpontom mostanában..."
        else:
            possible_date = tracker.get_slot('date')
            pos_times = self.data[possible_date]
            if len(pos_times) > 1:
                pos_times_s = ", ".join(list(map(time2text, pos_times[:-1])))
                pos_times_s += f' és {time2text(pos_times[-1])}'
            else:
                pos_times_s = f'{time2text(pos_times[0])}'

            response = f"{date2text(possible_date)} ráérek {pos_times_s}.".capitalize()

        dispatcher.utter_message(text=response)
        return []


class ActionIdopontForm(Action):
    def __init__(self):
        with open('test_data.json', 'r') as f:
            self.data = json.load(f)

    def name(self) -> Text:
        return "validate_idopont_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[EventType]:

        response = ""

        if tracker.get_slot('date') is None and tracker.get_slot('time') is None:
            any_date, good_date = False, False
            for entity in tracker.latest_message['entities']:
                if entity['entity'] == 'dates':
                    any_date = True
                    for e_date in entity['value']:
                        if e_date in self.data.keys() and not good_date:
                            good_date = e_date
                            break

            #nincs datum
            if not any_date:
                response += "Okés. Mikor lenne jó?"
                dispatcher.utter_message(text=response)
                return []
            else:
                #van datum de nincs listaban
                if not good_date:
                    response += "Sajnos nem érek rá akkor... Egy másik esetleg?"
                    dispatcher.utter_message(text=response)
                    return []
                #jo datum
                else:
                    response += f"Ráérek {date2text(good_date)}. Mikor lenne jó aznap?"
                    dispatcher.utter_message(text=response)
                    return [SlotSet('date', good_date)]

        if tracker.get_slot("date") is not None:
            possible_date = tracker.get_slot('date')
            any_time, good_time = False, False
            for entity in tracker.latest_message['entities']:
                if entity['entity'] == 'times':
                    any_time = True
                    for e_time in entity['value']:
                        if e_time in self.data[possible_date] and not good_time:
                            good_time = e_time
                            break
            #nincs idő
            if not any_time:
                response += "Nem értettem, ne haragudj. Hány órakor találkozzunk?"
                dispatcher.utter_message(text=response)
                return []

            else:
                if not good_time:
                    response += f"Sajnos nem érek rá ekkor... Egy másik időpont esetleg?"
                    dispatcher.utter_message(text=response)
                    return []
                else:
                    # konszenzus
                    dispatcher.utter_message(template="utter_submit",
                                             date=date2text(tracker.get_slot('date')),
                                             time=time2text(good_time))

                    return [SlotSet('time', good_time)]


            # resetting previously set appointment


        return []
