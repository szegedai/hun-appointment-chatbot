import json
from typing import Any, Text, Dict, List

from datetime import datetime

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from actions.time_table import TimeTable


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

        time_table.label_timerange_by_text(tracker.latest_message['text'], 'user_free')

        time_table.get_viz()

        return [SlotSet("time_table", time_table.toJSON())]
