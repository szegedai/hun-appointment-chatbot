from time_table import TimeTable, has_date_mention
from utils import get_human_friendly_range, load_responses, get_random_response, BOT_FREE_RANGE, USER_FREE_RANGE, \
    get_random_hour_from_timerange
from hun_date_parser.date_parser.interval_restriction import extract_datetime_within_interval, ExtractWithinRangeSuccess
from hun_date_parser import text2datetime

APPOINTMENT_MAX_LEN = 3700
RESPONSES = load_responses()


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

    def _get_user_bot_overlaps(self):
        user_date_mentions = text2datetime(self.text)

        print("user date mentions:")
        for index in user_date_mentions:
            print(index)

        all_overlaps = []

        print(f'length:{len(user_date_mentions)}')

        for i, date_intv in enumerate(user_date_mentions):

            print(f'index:{i}')

            if date_intv['start_date'] and date_intv['end_date']:
                overlaps = self.time_table.query_timerange(date_intv['start_date'],
                                                           date_intv['end_date'],
                                                           BOT_FREE_RANGE)

                if overlaps:
                    overlap = overlaps[0]  # TODO: let's handle more overlaps...
                    for i, olap in enumerate(overlaps):
                        print(f'No.{i}, overlap:{olap}')

                    all_overlaps.append(overlap)

        return all_overlaps

    def if_bot_is_free_in_overlap_and_appointment_is_set(self):
        overlaps = self._get_user_bot_overlaps()

        for overlap in overlaps:
            start, end = overlap.start_datetime, overlap.end_datetime
            if (end - start).seconds < APPOINTMENT_MAX_LEN:
                return True

        return False

    def if_currently_discussed_already_an_appointment(self):
        overlap = self.time_table.get_currently_discussed_range()

        start, end = overlap.start_datetime, overlap.end_datetime
        if (end - start).seconds < APPOINTMENT_MAX_LEN:
            return True

        return False

    def if_bot_is_free_in_overlap(self):
        overlaps = self._get_user_bot_overlaps()

        return bool(overlaps)


class ActionBlocks:
    # ToDo outsource dispatcher messages into domain.yml

    def __init__(self, tracker, time_table: TimeTable, dispatcher):
        self.tracker = tracker
        self.text = tracker.latest_message['text']
        self.time_table = time_table
        self.dispatcher = dispatcher

    def do_bot_suggest_range(self):
        next_free_bot_range = self.time_table.get_first_range_for_label(BOT_FREE_RANGE)
        hf_start, hf_end = get_human_friendly_range(next_free_bot_range, include_date=True)
        response_template = get_random_response(RESPONSES, "bot_suggest")
        self.dispatcher.utter_message(text=response_template.format(hf_start, hf_end))

        bot_free_dct = {"start_date": next_free_bot_range.start_datetime, "end_date": next_free_bot_range.end_datetime}
        self.time_table.set_current_discussed(bot_free_dct, BOT_FREE_RANGE)

    def do_bot_suggest_from_currently_discussed_range(self):
        currently_discussed = self.time_table.get_currently_discussed_range()
        random_hour = get_random_hour_from_timerange(currently_discussed)
        hf_start, hf_end = get_human_friendly_range(random_hour, include_date=True)
        response_template = get_random_response(RESPONSES, "bot_suggests_final")
        self.dispatcher.utter_message(text=response_template.format(hf_start))

        # bot_free_dct = {"start_date": random_hour.start_datetime, "end_date": random_hour.end_datetime}
        # self.time_table.set_current_discussed(bot_free_dct, BOT_FREE_RANGE)
        self.time_table.current_dtrl['ladder'].step_in_ladder(random_hour)

    def do_bot_suggest_alternative_range(self):
        within_currently_discussed_success = False
        if self.time_table.has_currently_discussed_range:
            within_currently_discussed_success = self.time_table.discard_currently_discussed_bottom_range()

        if not within_currently_discussed_success:
            next_free_bot_range = self.time_table.get_next_available_timerange(BOT_FREE_RANGE)
            bot_free_dct = {"start_date": next_free_bot_range.start_datetime,
                            "end_date": next_free_bot_range.end_datetime}
            self.time_table.set_current_discussed(bot_free_dct, BOT_FREE_RANGE)
        else:
            currently_discussed = self.time_table.get_currently_discussed_range()
            next_free_bot_range = get_random_hour_from_timerange(currently_discussed)

        hf_start, hf_end = get_human_friendly_range(next_free_bot_range, include_date=True)
        response_template = get_random_response(RESPONSES, "bot_suggest_alternative")
        self.dispatcher.utter_message(text=response_template.format(hf_start, hf_end))

    def do_further_specify_currently_discussed(self):
        self.time_table.discuss_current(self.text)
        currently_discussed = self.time_table.get_currently_discussed_range()
        hf_start, hf_end = get_human_friendly_range(currently_discussed, include_date=False)

        if (currently_discussed.end_datetime - currently_discussed.start_datetime).seconds > APPOINTMENT_MAX_LEN:
            print("B1 1", (currently_discussed.end_datetime - currently_discussed.start_datetime).seconds)
            response_template = get_random_response(RESPONSES, "bot_free")
            self.dispatcher.utter_message(text=response_template.format(hf_start, hf_end))
        else:
            print("B1 2", (currently_discussed.end_datetime - currently_discussed.start_datetime).seconds)
            response_template = get_random_response(RESPONSES, "appointment_set")
            self.dispatcher.utter_message(text=response_template.format(hf_start))

    def do_confirm_currently_discussed_is_already_an_appointment(self):
        overlap = self.time_table.get_currently_discussed_range()
        start, end = overlap.start_datetime, overlap.end_datetime
        hf_start, hf_end = get_human_friendly_range(overlap, include_date=False)
        if (end - start).seconds <= APPOINTMENT_MAX_LEN:
            response_template = get_random_response(RESPONSES, "appointment_set")
            self.dispatcher.utter_message(text=response_template.format(hf_start))

    def do_bot_set_appointment(self):
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
                    hf_start, hf_end = get_human_friendly_range(overlap, include_date=True)
                    if (end - start).seconds <= APPOINTMENT_MAX_LEN:
                        response_template = get_random_response(RESPONSES, "appointment_set")
                        self.dispatcher.utter_message(text=response_template.format(hf_start))
                    else:
                        self.time_table.label_timerange(start, end, USER_FREE_RANGE)
                        self.time_table.set_current_discussed({"start_date": start, "end_date": end}, USER_FREE_RANGE)
                        response_template = get_random_response(RESPONSES, "bot_free")
                        self.dispatcher.utter_message(text=response_template.format(hf_start, hf_end))

        return None
