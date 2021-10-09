import json
from typing import Any, Text, Dict, List

from datetime import datetime, timedelta

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType, FollowupAction

from hun_date_parser import datetime2text, text2datetime
from datetimerange import DateTimeRange


class ActionTimeTableFiller(Action):

    def name(self) -> Text:
        return "action_fill_table"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        time_table_repr = tracker.get_slot('time_table')

        time_table: TimeTable
        if not time_table_repr:
            time_table = TimeTable(['user_free'])
        else:
            time_table = TimeTable.fromJSON(time_table_repr)

        time_table.label_timerange_by_text(tracker.latest_message['text'], 'user_free')

        time_table.get_viz()

        return [SlotSet("time_table", time_table.toJSON())]