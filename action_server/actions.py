from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from utils import get_timetable_in_discussion, load_responses, get_random_response
from action_blocks import ActionBlocks, RuleBlocks

RESPONSES = load_responses()


class ActionRemoveAppointment(Action):

    def name(self) -> Text:
        return "action_remove_appointment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("torles")
        """
        Removes the appointment, clearing the slot
        """
        return [SlotSet('time_table', None)]


class ActionRecommendOtherDate(Action):
    def name(self) -> Text:
        return "recommend_other_date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        time_table = get_timetable_in_discussion(tracker)
        rule_blocks = RuleBlocks(tracker, time_table, dispatcher)
        action_blocks = ActionBlocks(tracker, time_table, dispatcher)

        if not rule_blocks.if_text_has_datetime():
            action_blocks.do_bot_suggest_alternative_range()
        elif rule_blocks.if_bot_is_free_in_overlap():
            action_blocks.do_bot_set_appointment()
        elif rule_blocks.if_text_in_currently_discussed_top_range():
            action_blocks.do_further_specify_currently_discussed()
        else:
            action_blocks.do_bot_handle_bad_range()

        time_table_modified = action_blocks.time_table
        return [SlotSet("time_table", time_table_modified.toJSON())]


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
            dispatcher.utter_message(get_random_response(RESPONSES, "accept_appointment_intent"))
            action_blocks.do_bot_suggest_range()

            return [SlotSet("time_table", time_table.toJSON())]

        currently_discussed_remains = False
        if rule_blocks.if_exists_currently_discussed_range():
            print("B")

            if rule_blocks.if_text_further_specifies_currently_discussed():
                print("B1")
                currently_discussed_remains = True
                action_blocks.do_further_specify_currently_discussed()

                return [SlotSet("time_table", time_table.toJSON())]
            elif rule_blocks.if_text_in_currently_discussed_top_range():
                print("B2")
                currently_discussed_remains = True
                action_blocks.do_further_specify_currently_discussed()

                return [SlotSet("time_table", time_table.toJSON())]

        if not currently_discussed_remains and rule_blocks.if_bot_is_free_in_overlap():
            print("C2")
            action_blocks.do_bot_set_appointment()

        if not currently_discussed_remains and not rule_blocks.if_bot_is_free_in_overlap():
            action_blocks.do_bot_handle_bad_range()

        time_table_modified = action_blocks.time_table
        # time_table_modified.get_viz()

        return [SlotSet("time_table", time_table_modified.toJSON())]


class ActionUserAffirmed(Action):

    def name(self) -> Text:
        return "action_user_affirmed"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        time_table = get_timetable_in_discussion(tracker)
        rule_blocks = RuleBlocks(tracker, time_table, dispatcher)
        action_blocks = ActionBlocks(tracker, time_table, dispatcher)

        if rule_blocks.if_exists_currently_discussed_range():

            if not rule_blocks.if_text_has_datetime():
                if rule_blocks.if_currently_discussed_already_an_appointment():
                    action_blocks.do_confirm_currently_discussed_is_already_an_appointment()
                else:
                    action_blocks.do_bot_suggest_from_currently_discussed_range()

                return [SlotSet("time_table", time_table.toJSON())]
            elif rule_blocks.if_text_further_specifies_currently_discussed():
                print("B1")
                action_blocks.do_further_specify_currently_discussed()

                return [SlotSet("time_table", time_table.toJSON())]
            elif rule_blocks.if_text_in_currently_discussed_top_range():
                print("B2")
                action_blocks.do_further_specify_currently_discussed()

                return [SlotSet("time_table", time_table.toJSON())]

        else:
            dispatcher.utter_message(get_random_response(RESPONSES, "not_understood"))

        time_table_modified = action_blocks.time_table
        # time_table_modified.get_viz()

        print("TERMINAL")
        return [SlotSet("time_table", time_table_modified.toJSON())]


class ActionRecommendAppointment(Action):

    def name(self) -> Text:
        return "action_recommend_appointment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        time_table = get_timetable_in_discussion(tracker)
        rule_blocks = RuleBlocks(tracker, time_table, dispatcher)
        action_blocks = ActionBlocks(tracker, time_table, dispatcher)

        if not rule_blocks.if_text_has_datetime():
            action_blocks.do_bot_suggest_range()
            return [SlotSet("time_table", time_table.toJSON())]
        else:
            return [SlotSet("time_table", time_table.toJSON()), FollowupAction("action_user_affirmed")]


class ActionRemoveRange(Action):

    def name(self) -> Text:
        return "action_remove_range"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[str, Any]]:

        time_table = get_timetable_in_discussion(tracker)
        #print(time_table)
        time_table.label_user_not_free_range()
        return [SlotSet("time_table", time_table.toJSON())]
