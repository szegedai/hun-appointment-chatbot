import json
from typing import Any, Text, Dict, List

from datetime import datetime

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType

from hun_date_parser import datetime2text, text2datetime
from datetimerange import DateTimeRange


def get_available_appointments():
    """
    Loads available appointment list.
    """
    now = datetime.now()

    with open('test_data.json', 'r') as f:
        data = json.load(f)

    res = []
    for day in data:
        parsed = {'start_date': datetime.fromisoformat(day['start_date']),
                  'end_date': datetime.fromisoformat(day['end_date'])}

        if parsed['end_date'] <= now:
            continue
        if parsed['start_date'] <= now:
            parsed['start_date'] = now

        res.append(parsed)

    return res


def get_date_text(dt):
    dt = datetime.combine(dt, datetime.min.time())
    candidates = datetime2text(dt, time_precision=2)

    return f"{candidates['dates'][0]}"


def get_time_text(dt, add_suffix=False):
    candidates = datetime2text(dt, time_precision=2)
    cand = candidates['times'][-1]
    if not cand.endswith('perccel') and add_suffix:
        if cand[-1].isdigit():
            cand += '-kor'
        else:
            cand += 'kor'

    return cand


def get_common_intervals(d_range_1, d_range_2):
    dtr1 = DateTimeRange(d_range_1['start_date'], d_range_1['end_date'])
    dtr2 = DateTimeRange(d_range_2['start_date'], d_range_2['end_date'])

    dtr_common = dtr1.intersection(dtr2)

    if dtr_common.start_datetime and dtr_common.end_datetime:
        return {'start_date': dtr_common.start_datetime, 'end_date': dtr_common.end_datetime}
    else:
        return None


def is_good_date(candidates, option):
    for c in candidates:
        if get_common_intervals(c, option):
            return get_common_intervals(c, option)

    return None


class ActionRemoveAppointment(Action):

    def name(self) -> Text:
        return "action_remove_appointment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SlotSet('date', None), SlotSet('time', None)]


class ActionRecommendDate(Action):
    def __init__(self):
        self.appointments = get_available_appointments()

    def name(self) -> Text:
        return "action_recommend_date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Recommends date...
        if tracker.get_slot('date') is None:
            if len(self.appointments) >= 2:
                response = f"Legközelebb {get_date_text(self.appointments[0]['start_date'])} és {get_date_text(self.appointments[1]['start_date'])} érek rá."
            elif self.appointments:
                response = f"Legközelebb {get_date_text(self.appointments[0]['start_date'])} érek rá."
            else:
                response = "Sajnos nincs szabad időpontom mostanában..."

        # Recommends times...
        else:
            set_date = datetime.strptime(tracker.get_slot('date'), '%Y-%m-%d')
            pos_times = [(a['start_date'], a['end_date']) for a in self.appointments if
                         a['start_date'].date() == set_date.date()]
            pos_times = [f'{get_time_text(beg)} és {get_time_text(end)} között' for beg, end in pos_times]

            if len(pos_times) > 1:
                pos_times_s = ", ".join(pos_times[:-1])
                pos_times_s += f' és {pos_times[-1]}'
            else:
                pos_times_s = f'{pos_times[0]}'

            response = f"{get_date_text(set_date)} ráérek {pos_times_s}.".capitalize()

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

        response = ""

        if tracker.get_slot('date') is None and tracker.get_slot('time') is None:
            any_date, good_date = False, False
            for entity in tracker.latest_message['entities']:
                if entity['entity'] == 'dates':
                    any_date = True
                    date_intervals = entity['value']
                    for e_date in date_intervals:
                        overlap = is_good_date(self.appointments, e_date)
                        if overlap and not good_date:
                            good_date = overlap['start_date'].date()
                            break

            if not any_date:
                response += "Okés. Mikor lenne jó?"
                dispatcher.utter_message(text=response)
                return []
            elif any_date:
                if not good_date:
                    response += "Sajnos nem érek rá akkor... Máskor esetleg?"
                    dispatcher.utter_message(text=response)
                    return []
                else:
                    response += f"Ráérek {get_date_text(good_date)}. Mikor lenne jó aznap?"
                    dispatcher.utter_message(text=response)
                    return [SlotSet('date', good_date.strftime('%Y-%m-%d'))]

        if tracker.get_slot("date") is not None:
            possible_date = datetime.strptime(tracker.get_slot('date'), '%Y-%m-%d')
            any_time, good_time = False, False
            for entity in tracker.latest_message['entities']:
                if entity['entity'] == 'times':
                    any_time = True
                    time_intervals = entity['value']
                    time_intervals = [{'start_date': datetime.combine(possible_date.date(),
                                                                      datetime.strptime(ti['start_date'],
                                                                                        '%H:%M').time()),
                                       'end_date': datetime.combine(possible_date.date(),
                                                                    datetime.strptime(ti['end_date'], '%H:%M').time())}
                                      for ti in time_intervals]
                    for e_time in time_intervals:
                        overlap = is_good_date(self.appointments, e_time)
                        if overlap and not good_time:
                            good_time = overlap['start_date'].time()
                            break

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
                    dispatcher.utter_message(template="utter_submit",
                                             date=get_date_text(
                                                 datetime.strptime(tracker.get_slot('date'), '%Y-%m-%d')),
                                             time=get_time_text(datetime.combine(datetime.min.date(), good_time),
                                                                add_suffix=True))

                    return [SlotSet('time', good_time.strftime('%M:%H'))]

        return []
