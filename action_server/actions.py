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
        #the user wants another date (if doesnt mention specifically, the bot will recommend)

        if not rule_blocks.text_has_datetime():
            print("RO1")
            #if there are is initialised timetable, recommend date at random
            if tracker.get_slot('time_table') == None:
                action_blocks.do_bot_suggest_range()
            else:    
                action_blocks.do_bot_suggest_alternative_range()
        elif rule_blocks.bot_is_free_in_overlap():
            print("RO2")
            action_blocks.do_bot_set_appointment()
        elif rule_blocks.text_in_currently_discussed_top_range():
            print("RO3")
            action_blocks.do_further_specify_currently_discussed()
        else:
            print("RO4")
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

        #user did not request a specific time, so bot suggests 
        if not rule_blocks.text_has_datetime():
            print("A")
            dispatcher.utter_message(get_random_response(RESPONSES, "accept_appointment_intent"))
            action_blocks.do_bot_suggest_range()

            return [SlotSet("time_table", time_table.toJSON())]

        currently_discussed_remains = False
        #a time frame is being discussed
        if rule_blocks.exists_currently_discussed_range():
            print("B")

            #the timeframe is getting smaller
            if rule_blocks.text_further_specifies_currently_discussed():
                print("B1")
                currently_discussed_remains = True
                action_blocks.do_further_specify_currently_discussed()

                return [SlotSet("time_table", time_table.toJSON())]
            elif rule_blocks.text_in_currently_discussed_top_range():
                print("B2")
                currently_discussed_remains = True
                action_blocks.do_further_specify_currently_discussed()

                return [SlotSet("time_table", time_table.toJSON())]

        #currently discussed range has changed, but it is good for the bot
        if not currently_discussed_remains and rule_blocks.bot_is_free_in_overlap():
            print("C2")
            action_blocks.do_bot_set_appointment()

        #currently discussed range has changed, but it is not good for the bot
        if not currently_discussed_remains and not rule_blocks.bot_is_free_in_overlap():
            print("C3")
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

        #user agreed that the the appointment will be good within the currently discussed range
        if rule_blocks.exists_currently_discussed_range():

            #bat didn't specify further
            if not rule_blocks.text_has_datetime():
                print("K0")
                if rule_blocks.currently_discussed_already_an_appointment():
                    print("K0-1")
                    action_blocks.do_confirm_currently_discussed_is_already_an_appointment()
                else:
                    #bot suggests an appointment from the already mentioned interval
                    print("K0-2")
                    action_blocks.do_bot_suggest_from_currently_discussed_range()

                return [SlotSet("time_table", time_table.toJSON())]
            elif rule_blocks.text_further_specifies_currently_discussed():
                print("K1")
                action_blocks.do_further_specify_currently_discussed()

                return [SlotSet("time_table", time_table.toJSON())]
            elif rule_blocks.text_in_currently_discussed_top_range():
                print("K2")
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

        #user is flexible, bot will recommend appointment

        if not rule_blocks.text_has_datetime():
            print("R1")
            action_blocks.do_bot_suggest_range()
            return [SlotSet("time_table", time_table.toJSON())]
        else:
            print("R2")
            return [SlotSet("time_table", time_table.toJSON()), FollowupAction("action_user_affirmed")]
