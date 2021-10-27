import json
from hun_date_parser import datetime2text
from datetime import datetime
from actions.time_table import TimeTable


def get_human_friendly_range(daterange):
    human_friendly_start = f"{datetime2text(daterange.start_datetime, 1)['dates'][-1]} " \
                           f"{datetime2text(daterange.start_datetime, 1)['times'][-1]}"
    human_friendly_end = f"{datetime2text(daterange.end_datetime, 1)['dates'][-1]} " \
                         f"{datetime2text(daterange.end_datetime, 1)['times'][-1]}"

    return human_friendly_start, human_friendly_end


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


def get_timetable_in_discussion(tracker):
    time_table_repr = tracker.get_slot('time_table')

    if not time_table_repr:
        time_table = TimeTable(['user_free', 'bot_free', 'last_offered'])
        for rec in get_available_appointments():
            time_table.label_timerange(rec['start_date'], rec['end_date'], 'bot_free')
    else:
        time_table = TimeTable.fromJSON(time_table_repr)

    return time_table
