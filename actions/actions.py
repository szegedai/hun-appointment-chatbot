from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from utils import get_timetable_in_discussion
from action_blocks import ActionBlocks, RuleBlocks


class ActionRemoveAppointment(Action):

    def name(self) -> Text:
        return "action_remove_appointment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Removes the appointment, clearing the slots
        """
        return [SlotSet('time_table', None)]


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
            print("A")
            action_blocks.do_bot_suggest_next_range()

            return [SlotSet("time_table", time_table.toJSON())]

        if rule_blocks.if_exists_currently_discussed_range():

            if rule_blocks.if_text_further_specifies_currently_discussed():
                print("B1")
                action_blocks.do_further_specify_currently_discussed()

                return [SlotSet("time_table", time_table.toJSON())]
            elif rule_blocks.if_text_in_currently_discussed_top_range():
                print("B2")
                action_blocks.do_further_specify_currently_discussed()

                return [SlotSet("time_table", time_table.toJSON())]

        elif rule_blocks.if_bot_is_free_in_overlap():
            print("C2")
            action_blocks.do_bot_set_appointment()

        else:
            dispatcher.utter_message("Sajnos nem megfelelő a kért időpont...")

        time_table_modified = action_blocks.time_table

        print("TERMINAL")
        return [SlotSet("time_table", time_table_modified.toJSON())]
