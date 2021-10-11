import json
from typing import Any, Text, Dict, List

from datetime import datetime

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from actions.time_table import TimeTable

from hun_date_parser import text2datetime, datetime2text


def get_available_appointments():
    """
    Loads available appointment list.
    """
    now = datetime.now()  # Get the current date

    with open('test_data.json', 'r') as f:  # Opening test_data
        data = json.load(f)

    # Parsing the test_data into a dictionary
    res = []
    for day in data:
        parsed = {'start_date': datetime.fromisoformat(day['start_date']),
                  'end_date': datetime.fromisoformat(day['end_date'])}

        # Normalizing the data
        if parsed['end_date'] <= now:
            continue
        if parsed['start_date'] <= now:
            parsed['start_date'] = now
        res.append(parsed)

    return res


class ActionTimeTableFiller(Action):

    def name(self) -> Text:
        return "action_fill_table"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        time_table_repr = tracker.get_slot('time_table')

        if not time_table_repr:
            time_table = TimeTable(['user_free', 'bot_free'])
            for rec in get_available_appointments():
                time_table.label_timerange(rec['start_date'], rec['end_date'], 'bot_free')
        else:
            time_table = TimeTable.fromJSON(time_table_repr)

        user_date_mentions = text2datetime(tracker.latest_message['text'])
        if not user_date_mentions:
            pass
        else:
            for date_intv in user_date_mentions:
                if date_intv['start_date'] and date_intv['end_date']:
                    time_table.label_timerange(date_intv['start_date'],
                                               date_intv['end_date'],
                                               'user_free')

                    overlaps = time_table.query_timerange(date_intv['start_date'],
                                                          date_intv['end_date'],
                                                          'bot_free')

                    if overlaps:
                        for overlap in overlaps:
                            human_friendly_start = f"{datetime2text(overlap.start_datetime, 2)['dates'][-1]} " \
                                                   f"{datetime2text(overlap.start_datetime, 2)['times'][-1]}"
                            human_friendly_end = f"{datetime2text(overlap.end_datetime, 2)['dates'][-1]} " \
                                                 f"{datetime2text(overlap.end_datetime, 2)['times'][-1]}"

                            dispatcher.utter_message(text=f"Ráérek az általad kért időszakon belül "
                                                          f"{human_friendly_start} és {human_friendly_end} között.")
                    else:
                        dispatcher.utter_message(text="Sajos ekkor nem érek rá...")

        time_table.get_viz()

        return [SlotSet("time_table", time_table.toJSON())]
