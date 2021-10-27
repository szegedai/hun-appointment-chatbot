from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from actions.utils import get_timetable_in_discussion
from actions.action_blocks import ActionBlocks, RuleBlocks


class ActionTimeTableFiller(Action):

    def name(self) -> Text:
        return "action_fill_table"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        time_table = get_timetable_in_discussion(tracker)
        rule_blocks = RuleBlocks(tracker, time_table, dispatcher)
        action_blocks = ActionBlocks(tracker, time_table, dispatcher)

        if not rule_blocks.if_text_has_datetime():
            action_blocks.do_bot_suggest_next_range()

            return [SlotSet("time_table", time_table.toJSON())]

        if rule_blocks.if_exists_currently_discussed_range():

            if rule_blocks.if_text_further_specifies_currently_discussed():
                action_blocks.do_further_specify_currently_discussed()
            else:
                pass

            return [SlotSet("time_table", time_table.toJSON())]

        if rule_blocks.if_bot_is_free_in_overlap_and_appointment_is_set():
            action_blocks.do_bot_set_terminal_appointment()
        elif rule_blocks.if_bot_is_free_in_overlap():
            action_blocks.do_bot_set_non_terminal_appointment()

        time_table_modified = action_blocks.time_table

        return [SlotSet("time_table", time_table_modified.toJSON())]
