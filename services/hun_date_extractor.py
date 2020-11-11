from typing import Any, Dict, Text

from rasa.nlu.extractors.extractor import EntityExtractor
from rasa.shared.nlu.training_data.message import Message

from services.hun_date_parser_service import *


class HunDateExtractor(EntityExtractor):
    """
    This is a custom date extractor based partially on https://github.com/sedthh/lara-hungarian-nlp.
    """
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
        """
        Process an incoming message by determining the most similar (or matching) names.
        """
        extracted = self._match_entities(message)
        message.set("entities", message.get("entities", []) + extracted, add_to_output=True)

    def _match_entities(self, message: Message):
        """
        Perform fuzzy matching on each token of the message.
        A token contains its text, its offset, its end and optionally additional data.
        """
        message_text = message.get("text", "")
        dates, times = get_datetimes(message_text)

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
