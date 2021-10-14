import json
from typing import Any, Text, Dict, List

from datetime import datetime

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from actions.time_table import TimeTable

from hun_date_parser import text2datetime, datetime2text
from hun_date_parser.date_parser.interval_restriction import extract_datetime_within_interval


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


def get_human_friendly_range(daterange):
    human_friendly_start = f"{datetime2text(daterange.start_datetime, 2)['dates'][-1]} " \
                           f"{datetime2text(daterange.start_datetime, 2)['times'][-1]}"
    human_friendly_end = f"{datetime2text(daterange.end_datetime, 2)['dates'][-1]} " \
                         f"{datetime2text(daterange.end_datetime, 2)['times'][-1]}"

    return human_friendly_start, human_friendly_end


def bot_suggest_next(time_table, dispatcher):
    next_free_bot_range = time_table.get_first_range_for_label("bot_free")
    hf_start, hf_end = get_human_friendly_range(next_free_bot_range)
    dispatcher.utter_message(text=f"Esetleg {hf_start} és {hf_end} között valamikor?")

    time_table.flush_label("last_offered")
    time_table.label_timerange(next_free_bot_range.start_datetime,
                               next_free_bot_range.end_datetime,
                               "last_offered")

    return time_table


def is_appointment_length(start, end):
    return (start - end).seconds < 7200


class ActionTimeTableFiller(Action):

    def name(self) -> Text:
        return "action_fill_table"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        time_table_repr = tracker.get_slot('time_table')

        if not time_table_repr:
            time_table = TimeTable(['user_free', 'bot_free', 'last_offered'])
            for rec in get_available_appointments():
                time_table.label_timerange(rec['start_date'], rec['end_date'], 'bot_free')
        else:
            time_table = TimeTable.fromJSON(time_table_repr)

        if time_table.get_label("last_offered"):
            last_offered_range = time_table.get_label("last_offered")[0]
            success_flag, user_date_mentions = extract_datetime_within_interval(last_offered_range.start_datetime,
                                                                                last_offered_range.end_datetime,
                                                                                tracker.latest_message['text'])
            if success_flag.value != "valid_in_range":
                time_table.flush_label("last_offered")
        else:
            user_date_mentions = text2datetime(tracker.latest_message['text'])

        if not user_date_mentions:
            time_table = bot_suggest_next(time_table, dispatcher)
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
                        overlap = overlaps[0]  # TODO: let's handle more overlaps...

                        hf_start, hf_end = get_human_friendly_range(overlap)

                        if is_appointment_length(overlap.start_datetime, overlap.end_datetime):
                            dispatcher.utter_message(text=f"Ráérek az általad kért időszakon belül "
                                                          f"{hf_start} és {hf_end} között. "
                                                          f"Találkozzunk az irodámban.")
                        else:
                            dispatcher.utter_message(text=f"Ráérek az általad kért időszakon belül "
                                                          f"{hf_start} és {hf_end} között. "
                                                          f"Mit szólsz hozzá?")

                        time_table.label_timerange(overlap.start_datetime, overlap.end_datetime, 'last_offered')
                    else:
                        dispatcher.utter_message(text="Sajos ekkor nem érek rá...")
                        time_table = bot_suggest_next(time_table, dispatcher)

        time_table.get_viz()

        return [SlotSet("time_table", time_table.toJSON())]
