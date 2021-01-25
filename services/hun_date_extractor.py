from typing import Any, Dict, Text
from datetime import timedelta

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
            date_matches = text2date(message_text)
            time_matches = text2time(message_text)
        except:
            return []

        if date_matches:
            dates = [{'start_date': d['start_date'].strftime('%Y-%m-%d'),
                      'end_date': (d['end_date'] + timedelta(days=1)).strftime('%Y-%m-%d')} for d in
                     date_matches]
        else:
            dates = []

        if time_matches:
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
