from typing import Any, Dict, Text
from datetime import timedelta, date, time, datetime

from rasa.nlu.extractors.extractor import EntityExtractor
from rasa.shared.nlu.training_data.message import Message

from hun_date_parser import text2date, text2time


class HunDateExtractor(EntityExtractor):
    name = "HunDateExtractor"
    provides = ["entities"]
    requires = ["tokens"]

    def __init__(self, parameters: Dict[Text, Text]) -> None:
        super(HunDateExtractor, self).__init__(parameters)

        if parameters is None:
            raise AttributeError("No valid config given!")
        if not isinstance(parameters, dict):
            raise AttributeError(f"config has type {type(parameters)}")

    def process(self, message: Message, **kwargs: Any) -> None:
        extracted = self._match_entities(message)
        message.set("entities", message.get("entities", []) + extracted, add_to_output=True)

    def _match_entities(self, message: Message):
        message_text = message.get("text", "")
        try:
            date_matches = text2date(message_text, expect_future_day=True)
            time_matches = text2time(message_text, expect_future_day=True)
        except:
            return []

        date_matches_valid = []
        for d in date_matches:
            if d is not None:
                if d['start_date'] or d['end_date']:
                    if d['start_date'] is None:
                        d['start_date'] = date.today()
                    if d['end_date'] is None:
                        # hack for max date, as actual max date may result to an overflow
                        d['end_date'] = date(3000, 1, 1)
                    date_matches_valid.append(d)

        time_matches_valid = []
        for d in time_matches:
            if d is not None:
                if d['start_date'] or d['end_date']:
                    if d['start_date'] is None:
                        now = datetime.now().time()
                        d['start_date'] = time(now.hour, now.second)
                    if d['end_date'] is None:
                        max_time = time.max
                        d['end_date'] = time(max_time.hour, max_time.second)
                    time_matches_valid.append(d)

        if date_matches_valid:
            dates = [{'start_date': d['start_date'].strftime('%Y-%m-%d'),
                      'end_date': (d['end_date'] + timedelta(days=1)).strftime('%Y-%m-%d')} for d in
                     date_matches]
        else:
            dates = []

        if time_matches_valid:
            times = [{'start_date': d['start_date'].strftime('%H:%M'), 'end_date': d['end_date'].strftime('%H:%M')} for
                     d in time_matches]
        else:
            times = []

        res = []

        if dates:
            res += [{
                'entity': 'dates',
                'value': dates
            }]

        if times:
            res += [{
                'entity': 'times',
                'value': times
            }]

        return res
