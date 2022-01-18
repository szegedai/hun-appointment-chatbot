from time_table import TimeTable, has_date_mention
from utils import get_human_friendly_range, load_responses, get_random_response, BOT_FREE_RANGE, USER_FREE_RANGE,\
    get_random_hour_from_timerange
from hun_date_parser.date_parser.interval_restriction import extract_datetime_within_interval, ExtractWithinRangeSuccess
from hun_date_parser import text2datetime
from datetime import datetime, timedelta
from datetimerange import DateTimeRange

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
            top_range = self.time_table.current_dtrl.top_range
            success_flag, user_date_mentions = extract_datetime_within_interval(top_range.start_datetime,
                                                                                top_range.end_datetime,
                                                                                self.text)
            return success_flag == ExtractWithinRangeSuccess.VALID_IN_RANGE

        return False

    def _get_user_bot_overlaps(self):
        user_date_mentions = text2datetime(self.text, expect_future_day=True)

        all_overlaps = []

        for date_intv in user_date_mentions:
            if date_intv['start_date'] and date_intv['end_date']:
                overlaps = self.time_table.query_timerange(date_intv['start_date'],
                                                           date_intv['end_date'],
                                                           BOT_FREE_RANGE)

                if overlaps:
                    overlap = overlaps[0]  # TODO: let's handle more overlaps...
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
        self.time_table.set_current_discussed(bot_free_dct)

    def do_bot_suggest_from_currently_discussed_range(self):
        currently_discussed = self.time_table.get_currently_discussed_range()
        random_hour = get_random_hour_from_timerange(currently_discussed)
        hf_start, hf_end = get_human_friendly_range(random_hour, include_date=True)
        response_template = get_random_response(RESPONSES, "bot_suggests_final")
        self.dispatcher.utter_message(text=response_template.format(hf_start))

        # bot_free_dct = {"start_date": random_hour.start_datetime, "end_date": random_hour.end_datetime}
        # self.time_table.set_current_discussed(bot_free_dct, BOT_FREE_RANGE)
        self.time_table.current_dtrl.step_in_ladder(random_hour)

    def do_bot_handle_bad_range(self):
        self.dispatcher.utter_message(get_random_response(RESPONSES, "bad_range"))

        requested_dates = text2datetime(self.text, expect_future_day=True)
        print(requested_dates)
        same_week = []
        week_num = []
        for requested_date in requested_dates:
            start_dt = requested_date['start_date']

            bot_free_list = self.time_table.sub_datetimes[BOT_FREE_RANGE]

            for bot_free_dtr in bot_free_list:
                if (start_dt.isocalendar()[0] == bot_free_dtr.start_datetime.isocalendar()[0] and
                        start_dt.isocalendar()[1] == bot_free_dtr.start_datetime.isocalendar()[1]):
                    same_week.append(bot_free_dtr)
                    week_num.append((start_dt.isocalendar()[0], start_dt.isocalendar()[1]))

        if not same_week:
            self.dispatcher.utter_message("Sajnos nincs más időpontom azon a héten... ")
        elif len(same_week) == 1:
            dtr = same_week[0]
            hf_start, hf_end = get_human_friendly_range(dtr, include_date=True)
            self.dispatcher.utter_message(f"Azon a héten csak egy napon lenne jó, {hf_start} és {hf_end} között. "
                                          f"Megfelel esetleg valamikor ezen belül?")
            self.time_table.set_current_discussed(dtr)
        else:
            hf_days = []
            hf_day_list = ['hétfőn', 'kedden', 'szerdán', 'csütörtökön', 'pénteken', 'szombaton', 'vasárnap']

            def get_start_and_end_date_from_calendar_week(year, calendar_week):
                monday = datetime.strptime(f'{year}-{calendar_week}-1', "%Y-%W-%w").date()
                return {'start_date': monday, 'end_date': monday + timedelta(days=6.9)}

            for dtr in same_week:
                hf_days.append(hf_day_list[dtr.start_datetime.weekday()])

            self.dispatcher.utter_message(f"Azon a héten több alkalom is megfelel, például {', '.join(hf_days[:-1])} és {hf_days[-1]}. "
                                          f"Megfelel esetleg valamikor ezek közül?")

            print(get_start_and_end_date_from_calendar_week(week_num[0][0], week_num[0][1]))

            self.time_table.set_current_discussed(get_start_and_end_date_from_calendar_week(week_num[0][0],
                                                                                            week_num[0][1]))

    def do_bot_suggest_alternative_range(self):
        within_currently_discussed_success = False
        if self.time_table.has_currently_discussed_range:
            within_currently_discussed_success = self.time_table.discard_currently_discussed_bottom_range()

        if not within_currently_discussed_success:
            next_free_bot_range = self.time_table.get_next_available_timerange(BOT_FREE_RANGE)
            bot_free_dct = {"start_date": next_free_bot_range.start_datetime,
                            "end_date": next_free_bot_range.end_datetime}
            self.time_table.set_current_discussed(bot_free_dct)
        else:
            currently_discussed = self.time_table.get_currently_discussed_range()
            next_free_bot_range = get_random_hour_from_timerange(currently_discussed)

        hf_start, hf_end = get_human_friendly_range(next_free_bot_range, include_date=True)
        response_template = get_random_response(RESPONSES, "bot_suggest_alternative")
        self.dispatcher.utter_message(text=response_template.format(hf_start, hf_end))

    def do_further_specify_currently_discussed(self):
        self.time_table.discuss_current(self.text)
        currently_discussed = self.time_table.get_currently_discussed_range()

        overlaps = self.time_table.query_timerange(currently_discussed.start_datetime,
                                                   currently_discussed.end_datetime,
                                                   BOT_FREE_RANGE)
        if not overlaps:
            # last discussed is not good for the bot, refuse and remove from currently discussed
            hf_start, _ = get_human_friendly_range(currently_discussed, include_date=True)
            self.dispatcher.utter_message(text="Sajnos az nem megfelelő. Esetleg máskor?")
            self.time_table.current_dtrl.ladder = self.time_table.current_dtrl.ladder[1:]
        elif len(overlaps) == 1:
            overlap = overlaps[0]
            self.time_table.current_dtrl.ladder = [overlap, *self.time_table.current_dtrl.ladder]
            hf_start, hf_end = get_human_friendly_range(overlap, include_date=False)
            if (overlap.end_datetime - overlap.start_datetime).seconds > APPOINTMENT_MAX_LEN:
                print("B1 1", (overlap.end_datetime - overlap.start_datetime).seconds)
                response_template = get_random_response(RESPONSES, "bot_free")
                self.dispatcher.utter_message(text=response_template.format(hf_start, hf_end))
            else:
                print("B1 2", (overlap.end_datetime - overlap.start_datetime).seconds)
                response_template = get_random_response(RESPONSES, "appointment_set") # ask "az jó lesz?"
                self.dispatcher.utter_message(text=response_template.format(hf_start))
        elif len(overlaps) > 1:
            hf_ranges = []
            for overlap in overlaps:
                hf_start, hf_end = get_human_friendly_range(overlap)
                hf_ranges.append(f"{hf_start}-tól {hf_end}-ig")

            self.dispatcher.utter_message(
                f"A kért időszakban több alkalom is megfelel, például {', '.join(hf_ranges[:-1])} és {hf_ranges[-1]}. "
                f"Megfelel esetleg valamikor ezek közül?")

    def do_confirm_currently_discussed_is_already_an_appointment(self):
        overlap = self.time_table.get_currently_discussed_range()
        start, end = overlap.start_datetime, overlap.end_datetime
        hf_start, hf_end = get_human_friendly_range(overlap, include_date=False)
        if (end - start).seconds <= APPOINTMENT_MAX_LEN:
            response_template = get_random_response(RESPONSES, "appointment_set")
            self.dispatcher.utter_message(text=response_template.format(hf_start))

    def do_bot_set_appointment(self):
        user_date_mentions = text2datetime(self.text, expect_future_day=True)
        bot_has_already_mentioned_date = False

        for date_intv in user_date_mentions:
            if date_intv['start_date'] and date_intv['end_date']:
                self.time_table.label_timerange(date_intv['start_date'],
                                                date_intv['end_date'],
                                                USER_FREE_RANGE)

                overlaps = self.time_table.query_timerange(date_intv['start_date'],
                                                           date_intv['end_date'],
                                                           BOT_FREE_RANGE)

                if len(overlaps) == 1:
                    overlap = overlaps[0]
                    start, end = overlap.start_datetime, overlap.end_datetime
                    hf_start, hf_end = get_human_friendly_range(overlap, include_date=True)
                    if (end - start).seconds <= APPOINTMENT_MAX_LEN:
                        response_template = get_random_response(RESPONSES, "appointment_set")
                        self.dispatcher.utter_message(text=response_template.format(hf_start))
                    else:
                        self.time_table.label_timerange(start, end, USER_FREE_RANGE)
                        self.time_table.set_current_discussed({"start_date": date_intv['start_date'], "end_date": date_intv['end_date']})
                        self.time_table.current_dtrl.ladder = [overlap, *self.time_table.current_dtrl.ladder]
                        if not bot_has_already_mentioned_date:
                            response_template = get_random_response(RESPONSES, "bot_free")
                            self.dispatcher.utter_message(text=response_template.format(hf_start, hf_end))
                            bot_has_already_mentioned_date = True
                        else:
                            response_template = get_random_response(RESPONSES, "bot_multiple_appointments")
                            self.dispatcher.utter_message(text=response_template.format(hf_start, hf_end))

                elif len(overlaps) > 1:
                    hf_days = []
                    for overlap in overlaps:
                        hf_start, _ = get_human_friendly_range(overlap, include_time=False)
                        hf_days.append(hf_start)

                    self.dispatcher.utter_message(
                        f"A kért időszakban több alkalom is megfelel, például {', '.join(hf_days[:-1])} és {hf_days[-1]}. "
                        f"Megfelel esetleg valamikor ezek közül?")

                    self.time_table.set_current_discussed({"start_date": date_intv['start_date'],
                                                           "end_date": date_intv['end_date']})
