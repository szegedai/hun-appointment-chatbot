from actions.time_table import TimeTable, has_date_mention
from actions.utils import get_human_friendly_range
from hun_date_parser.date_parser.interval_restriction import extract_datetime_within_interval, ExtractWithinRangeSuccess
from hun_date_parser import text2datetime

APPOINTMENT_MAX_LEN = 7200
BOT_FREE_RANGE = "bot_free"
USER_FREE_RANGE = "user_free"


class RuleBlocks:

    def __init__(self, tracker, time_table: TimeTable, dispatcher):
        self.tracker = tracker
        self.text = tracker.latest_message['text']
        self.time_table = time_table
        self.dispatcher = dispatcher

    def if_text_has_datetime(self):
        return has_date_mention(self.text)

    def if_exists_currently_discussed_range(self):
        return self.time_table.has_currently_discussed_range

    def if_current_range_appropriate_appointment(self):
        if self.time_table.has_currently_discussed_range:
            dtr = self.time_table.get_currently_discussed_range()
            start, end = dtr.start_datetime, dtr.end_datetime
            return (end - start).seconds < APPOINTMENT_MAX_LEN

        return False

    def if_text_further_specifies_currently_discussed(self):
        if self.time_table.has_currently_discussed_range:
            last_offered_range = self.time_table.get_currently_discussed_range()
            success_flag, user_date_mentions = extract_datetime_within_interval(last_offered_range.start_datetime,
                                                                                last_offered_range.end_datetime,
                                                                                self.text)
            return success_flag == ExtractWithinRangeSuccess.VALID_IN_RANGE

        return False

    def if_text_in_currently_discussed_top_range(self):
        if self.time_table.has_currently_discussed_range:
            top_range = self.time_table.current_dtrl["ladder"].top_range
            success_flag, user_date_mentions = extract_datetime_within_interval(top_range.start_datetime,
                                                                                top_range.end_datetime,
                                                                                self.text)
            return success_flag == ExtractWithinRangeSuccess.VALID_IN_RANGE

        return False

    def if_bot_is_free_in_overlap_and_appointment_is_set(self):
        user_date_mentions = text2datetime(self.text)

        for date_intv in user_date_mentions:
            if date_intv['start_date'] and date_intv['end_date']:
                overlaps = self.time_table.query_timerange(date_intv['start_date'],
                                                           date_intv['end_date'],
                                                           BOT_FREE_RANGE)

                if overlaps:
                    overlap = overlaps[0]  # TODO: let's handle more overlaps...
                    start, end = overlap.start_datetime, overlap.end_datetime
                    if (end - start).seconds < APPOINTMENT_MAX_LEN:
                        return True

        return False

    def if_bot_is_free_in_overlap(self):
        user_date_mentions = text2datetime(self.text)

        for date_intv in user_date_mentions:
            if date_intv['start_date'] and date_intv['end_date']:
                overlaps = self.time_table.query_timerange(date_intv['start_date'],
                                                           date_intv['end_date'],
                                                           BOT_FREE_RANGE)

                if overlaps:
                    return True

        return False


class ActionBlocks:
    # ToDo outsource dispatcher messages into domain.yml

    def __init__(self, tracker, time_table: TimeTable, dispatcher):
        self.tracker = tracker
        self.text = tracker.latest_message['text']
        self.time_table = time_table
        self.dispatcher = dispatcher

    def do_bot_suggest_range(self):
        next_free_bot_range = self.time_table.get_first_range_for_label(BOT_FREE_RANGE)
        hf_start, hf_end = get_human_friendly_range(next_free_bot_range)
        self.dispatcher.utter_message(text=f"Esetleg {hf_start} és {hf_end} között valamikor?")

        bot_free_dct = {"start_date": next_free_bot_range.start_datetime, "end_date": next_free_bot_range.end_datetime}
        self.time_table.set_current_discussed(bot_free_dct, BOT_FREE_RANGE)
        # self.time_table.get_next_available_timerange()

    def do_bot_suggest_next_range(self):
        next_free_bot_range = self.time_table.get_next_available_timerange(BOT_FREE_RANGE)
        print(f'kovi bot range:{next_free_bot_range}')
        hf_start, hf_end = get_human_friendly_range(next_free_bot_range)
        self.dispatcher.utter_message(text=f"Akkor {hf_start} és {hf_end} között valamikor?")

        bot_free_dct = {"start_date": next_free_bot_range.start_datetime, "end_date": next_free_bot_range.end_datetime}
        self.time_table.set_current_discussed(bot_free_dct, BOT_FREE_RANGE)

    def do_further_specify_currently_discussed(self):
        self.time_table.discuss_current(self.text)
        currently_discussed = self.time_table.get_currently_discussed_range()
        hf_start, hf_end = get_human_friendly_range(currently_discussed)

        if (currently_discussed.end_datetime - currently_discussed.start_datetime).seconds > APPOINTMENT_MAX_LEN:
            print("B1 1", (currently_discussed.end_datetime - currently_discussed.start_datetime).seconds)
            self.dispatcher.utter_message(text=f"Ráérek az általad kért időszakon belül "
                                               f"{hf_start} és {hf_end} között. "
                                               f"Mit szólsz hozzá?")
        else:
            print("B1 2", (currently_discussed.end_datetime - currently_discussed.start_datetime).seconds)
            self.dispatcher.utter_message(text=f"Ráérek az általad kért időszakon belül "
                                               f"{hf_start} és {hf_end} között. "
                                               f"Találkozzunk az irodámban.")

    def do_bot_set_non_terminal_appointment(self):
        """
        this function could be merged with do_bot_set_terminal_appointment function as the only difference is 1 if
        branch which would be the else branch if merged
        """
        user_date_mentions = text2datetime(self.text)

        for date_intv in user_date_mentions:
            if date_intv['start_date'] and date_intv['end_date']:
                self.time_table.label_timerange(date_intv['start_date'],
                                                date_intv['end_date'],
                                                USER_FREE_RANGE)

                overlaps = self.time_table.query_timerange(date_intv['start_date'],
                                                           date_intv['end_date'],
                                                           BOT_FREE_RANGE)

                if overlaps:
                    overlap = overlaps[0]  # TODO: let's handle more overlaps...
                    start, end = overlap.start_datetime, overlap.end_datetime
                    hf_start, hf_end = get_human_friendly_range(overlap)
                    if (end - start).seconds > APPOINTMENT_MAX_LEN:
                        self.time_table.set_current_discussed({"start_date": start, "end_date": end}, USER_FREE_RANGE)
                        self.dispatcher.utter_message(text=f"Ráérek az általad kért időszakon belül "
                                                           f"{hf_start} és {hf_end} között. "
                                                           f"Mit szólsz hozzá?")

    def do_bot_set_terminal_appointment(self):

        user_date_mentions = text2datetime(self.text)

        for date_intv in user_date_mentions:
            if date_intv['start_date'] and date_intv['end_date']:
                self.time_table.label_timerange(date_intv['start_date'],
                                                date_intv['end_date'],
                                                USER_FREE_RANGE)

                overlaps = self.time_table.query_timerange(date_intv['start_date'],
                                                           date_intv['end_date'],
                                                           BOT_FREE_RANGE)

                if overlaps:
                    overlap = overlaps[0]  # TODO: let's handle more overlaps...
                    start, end = overlap.start_datetime, overlap.end_datetime
                    hf_start, hf_end = get_human_friendly_range(overlap)
                    if (end - start).seconds <= APPOINTMENT_MAX_LEN:
                        self.dispatcher.utter_message(text=f"Ráérek az általad kért időszakon belül "
                                                           f"{hf_start} és {hf_end} között. "
                                                           f"Találkozzunk az irodámban.")
