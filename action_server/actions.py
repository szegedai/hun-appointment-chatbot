import json
from typing import Any, Text, Dict, List

from datetime import datetime, timedelta

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType, FollowupAction

from hun_date_parser import datetime2text, text2datetime
from datetimerange import DateTimeRange


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


def get_date_text(dt):
    """
    Converting dates into text.
    """

    dt = datetime.combine(dt, datetime.min.time())
    candidates = datetime2text(dt, time_precision=2)

    return f"{candidates['dates'][0]}"


def get_time_text(dt, add_suffix=False):
    """
    Converting datetime to text.
    """

    candidates = datetime2text(dt, time_precision=2)
    cand = candidates['times'][-1]
    if not cand.endswith('perccel') and add_suffix:
        if cand[-1].isdigit():
            cand += '-kor'
        else:
            cand += 'kor'

    return cand


def get_common_intervals(d_range_1, d_range_2):
    """
    Get the interval of start_date and end_date.
    """

    dtr1 = DateTimeRange(d_range_1['start_date'], d_range_1['end_date'])
    dtr2 = DateTimeRange(d_range_2['start_date'], d_range_2['end_date'])

    dtr_common = dtr1.intersection(dtr2)

    if dtr_common.start_datetime and dtr_common.end_datetime:
        return {'start_date': dtr_common.start_datetime, 'end_date': dtr_common.end_datetime}
    else:
        return None


def is_good_date(candidates, option, all_options=False):
    """
    Checks the intervals.
    """

    all_overlaps = []
    for c in candidates:
        if get_common_intervals(c, option):
            if not all_options:
                common_interval = get_common_intervals(c, option)
                common_interval['end_date'] += timedelta(minutes=1)  # TODO: find proper solution instead of hotfix
                return common_interval
            else:
                common_interval = get_common_intervals(c, option)
                common_interval['end_date'] += timedelta(minutes=1)  # TODO: find proper solution instead of hotfix
                all_overlaps.append(common_interval)

    if all_overlaps and all_options:
        return all_overlaps

    return None


def is_multiple_days(candidates):
    """
    If the days is bigger than 1 return true, else false.
    """

    days = []
    for d in candidates:
        days.append(d['start_date'].date())

    if len(set(days)) > 1:
        return True
    else:
        return False


def rec_date(appointments):
    next_dates = [get_date_text(d['start_date']) for d in appointments]

    if next_dates:
        unique_next_dates = list(dict.fromkeys(next_dates))
        if len(unique_next_dates) >= 2:
            response = f"A Főnök úr legközelebb {unique_next_dates[0]} és {unique_next_dates[1]} ér rá."
        else:
            response = f"A Főnök úr legközelebb {unique_next_dates[0]} ér rá."
    else:
        response = "A Főnök úrnak sajnos nincs szabad időpontja mostanában..."

    return response


def rec_time(date, appointments):
    set_date = datetime.strptime(date, '%Y-%m-%d')
    pos_times = [(a['start_date'], a['end_date']) for a in appointments if
                 a['start_date'].date() == set_date.date()]
    pos_times = [f'{get_time_text(beg)} és {get_time_text(end)} között' for beg, end in pos_times]

    if len(pos_times) > 1:
        pos_times_s = ", ".join(pos_times[:-1])
        pos_times_s += f' és {pos_times[-1]}'
        response = f"{get_date_text(set_date)} ráér {pos_times_s}.".capitalize()
    elif len(pos_times) == 0:
        response = f"A Főnök úrnak{get_date_text(set_date).capitalize()}sajnos nincs szabad időpontja."
    else:
        pos_times_s = f'{pos_times[0]}'
        response = f"A Főnök úr {get_date_text(set_date)} ráér {pos_times_s}.".capitalize()

    return response


class ActionRemoveAppointment(Action):

    def name(self) -> Text:
        return "action_remove_appointment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Removes the appointment, clearing the slots
        """
        return [SlotSet('date', None), SlotSet('time', None)]


class ActionRecommendDate(Action):
    def __init__(self):
        self.appointments = get_available_appointments()

    def name(self) -> Text:
        return "action_recommend_date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Recommends time on specific date
        if tracker.latest_message['entities']:
            dates = [e for entity in tracker.latest_message['entities']
                     for e in entity['value'] if entity['entity'] == 'dates']
            response = ''
            possible_dates = []
            for date in dates:
                response += rec_time(date['start_date'], self.appointments)
                possible_dates.append(date['start_date'])
            dispatcher.utter_message(response)

            return [SlotSet('possible_dates', possible_dates)]

        # Recommends date, if the date slot is empty looks for a next available date
        if tracker.get_slot('date') is None:
            response = rec_date(self.appointments)

        # Recommends times, if the date slot has a value
        # and the time slot is empty looks for a next available time interval
        else:
            response = rec_time(tracker.get_slot('date'), self.appointments)

        dispatcher.utter_message(text=response)
        return []


class FActionRecommendDate(Action):
    def __init__(self):
        self.appointments = get_available_appointments()

    def name(self) -> Text:
        return "followup_action_recommend_date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Recommends date...
        if tracker.get_slot('date') is None:
            response = rec_date(self.appointments)

        # Recommends times...
        else:
            response = rec_time(tracker.get_slot('date'), self.appointments)

        dispatcher.utter_message(text=response)
        return []


class ActionIdopontForm(Action):
    def __init__(self):
        self.appointments = get_available_appointments()

    def name(self) -> Text:
        return "validate_idopont_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[EventType]:

        slots = {}

        if tracker.get_slot('date') is None and tracker.get_slot('time') is None:
            any_date, good_date = False, False
            for entity in tracker.latest_message['entities']:
                if entity['entity'] == 'dates':
                    any_date = True
                    date_intervals = entity['value']
                    for e_date in date_intervals:
                        overlaps = is_good_date(self.appointments, e_date, all_options=True)
                        if overlaps and not good_date:

                            # If specified interval is longer then a day, suggest narrowing it...
                            if is_multiple_days(overlaps):
                                cands = sorted([d['start_date'] for d in overlaps])
                                cands = list(dict.fromkeys([cand.date() for cand in cands]).keys())
                                cands_s = f'{get_date_text(cands[0])} és {get_date_text(cands[1])}'
                                dispatcher.utter_message(
                                    text=f"A legközelebbi két nap amikor a Főnök úr ráér a kért időszakban {cands_s} lesz.")
                                return []
                            else:
                                good_date = overlaps[0]['start_date'].date()
                                break

                elif entity['entity'] == 'times' and tracker.get_slot('possible_dates') is not None:
                    for date in tracker.get_slot('possible_dates'):
                        for appointment in self.appointments:
                            if date in appointment['start_date'].strftime("%Y-%m-%d"):
                                good_date = datetime.strptime(date, "%Y-%m-%d").date()
                                any_date = True
                                break

            # Checking the value of any_date and good_date variables, and with that give back the right sentence
            if not any_date:
                dispatcher.utter_message(text="Okés. Mikor lenne jó?")
                return []

            if not good_date:
                dispatcher.utter_message(text="A Főnök úr sajnos nem ér rá akkor... Máskor esetleg?")
                return [FollowupAction("followup_action_recommend_date")]

            if good_date:
                slots['date'] = SlotSet('date', good_date.strftime('%Y-%m-%d'))

        if tracker.get_slot("date") or slots:
            if tracker.get_slot('date'):
                possible_date = datetime.strptime(tracker.get_slot('date'), '%Y-%m-%d').date()
            else:
                possible_date = good_date

            any_time, good_time = False, False
            for entity in tracker.latest_message['entities']:
                if entity['entity'] == 'times':
                    any_time = True
                    time_intervals = entity['value']
                    time_intervals = [{'start_date': datetime.combine(possible_date,
                                                                      datetime.strptime(ti['start_date'],
                                                                                        '%H:%M').time()),
                                       'end_date': datetime.combine(possible_date,
                                                                    datetime.strptime(ti['end_date'], '%H:%M').time())}
                                      for ti in time_intervals]
                    for e_time in time_intervals:
                        overlap = is_good_date(self.appointments, e_time, True)
                        if overlap and not good_time:

                            # If specified interval is longer then an hour, suggest narrowing it...
                            if (overlap[-1]['end_date'] - overlap[0]['start_date']).seconds > 3600:
                                intervals = [f"{get_time_text(overl['start_date'])} és"
                                             f" {get_time_text(overl['end_date'])}" for overl in overlap]
                                if len(intervals) > 1:
                                    resp = ', '.join(intervals[:-1])
                                    resp += f" és {intervals[-1]}"
                                else:
                                    resp = f"{intervals[0]}"

                                dispatcher.utter_message(
                                    text=f"A Főnök úr {resp.capitalize()} között ráér. Mikor legyen pontosan?")
                                return []
                            else:
                                good_time = overlap[0]['start_date'].time()
                                break

            if not any_time and not slots:
                dispatcher.utter_message(text="Nem értettem, ne haragudj. Hány órakor találkoznál?")
                return []

            if not good_time and not slots:
                dispatcher.utter_message(text=f"A Főnök úr sajnos nem ér rá ekkor... Egy másik időpont esetleg?")
                return [FollowupAction("followup_action_recommend_date")]

            if good_time:
                slots['time'] = SlotSet('time', good_time.strftime('%H:%M'))

        if slots:
            if 'time' in list(slots.keys()):
                if 'date' in list(slots.keys()):
                    date = good_date
                else:
                    date = datetime.strptime(tracker.get_slot('date'), '%Y-%m-%d')

                dispatcher.utter_message(template="utter_submit",
                                         date=get_date_text(date),
                                         time=get_time_text(datetime.combine(datetime.min.date(), good_time),
                                                            add_suffix=True))

            elif 'date' in list(slots.keys()):
                dispatcher.utter_message(text=f"A Főnök úr ráér {get_date_text(good_date)}. Mikor lenne jó aznap?")

            return list(slots.values())
        else:
            return []
