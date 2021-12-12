from typing import List
import pandas as pd
import json
import altair as alt
from hun_date_parser import text2datetime
from hun_date_parser.date_parser.interval_restriction import extract_datetime_within_interval
from datetimerange import DateTimeRange
from copy import deepcopy
from enum import Enum


class RequestFeedback(Enum):
    REQUEST_OK = "REQUEST_OK"
    REQUEST_SKIPPED = "REQUEST_SKIPPED"


def has_date_mention(text):
    res = text2datetime(text)
    return bool(res)


class TimeTable:
    """
    Time interval state representation
    """

    def __init__(self, labels: List[str]):
        """
        :param
        """
        self.labels = labels
        self.sub_datetimes = {l: [] for l in labels}
        self.current_dtrl = {'label': None, 'ladder': None}
        self.has_currently_discussed_range = False

    def _house_keeping(self):
        for label in self.labels:
            for i, dtr_i in enumerate(self.sub_datetimes[label]):
                for j, dtr_j in enumerate(self.sub_datetimes[label]):
                    if i < j and dtr_i.is_intersection(dtr_j):
                        self.sub_datetimes[label][i] = self.sub_datetimes[label][i].encompass(
                            self.sub_datetimes[label][j])
                        del self.sub_datetimes[label][j]
                        self._house_keeping()
                        break

    def label_timerange(self, start, end, label):
        new_dtr = DateTimeRange(start, end)

        encompassed = False
        for i in range(len(self.sub_datetimes[label])):
            if self.sub_datetimes[label][i].is_intersection(new_dtr):
                encompassed = True
                self.sub_datetimes[label][i] = self.sub_datetimes[label][i].encompass(new_dtr)

        if not encompassed:
            self.sub_datetimes[label].append(new_dtr)

        self._house_keeping()

    def query_timerange(self, start, end, label):
        queried_dtr = DateTimeRange(start, end)
        result = []

        for dtr in self.sub_datetimes[label]:
            if queried_dtr.is_intersection(dtr):
                result.append(queried_dtr.intersection(dtr))

        return result

    def label_timerange_by_text(self, text, label):
        res_l = text2datetime(text)

        for tval in res_l:
            if tval['start_date'] and tval['end_date']:
                self.label_timerange(tval['start_date'], tval['end_date'], label)

    def flush_label(self, label):
        self.sub_datetimes[label] = []

    def get_label(self, label):
        return self.sub_datetimes[label]

    def get_first_range_for_label(self, label):
        if not self.sub_datetimes[label]:
            return None

        min_dtr = self.sub_datetimes[label][0]
        for dtrange in self.sub_datetimes[label][1:]:
            if dtrange.start_datetime < min_dtr.start_datetime:
                min_dtr = dtrange

        return min_dtr

    def get_next_available_timerange(self, label):
        current = self.get_currently_discussed_range()
        for dtrange in self.sub_datetimes[label]:
            if current.start_datetime < dtrange.start_datetime:
                current = dtrange
                break

        return current

    def set_current_discussed(self, top_range_dct, label):
        top_range = DateTimeRange(top_range_dct['start_date'], top_range_dct['end_date'])
        dtrl = DateRangeLadder(top_range)
        self.current_dtrl = {'label': label, 'ladder': dtrl}
        self.has_currently_discussed_range = True

    def discuss_current(self, query_text):
        if not self.current_dtrl['ladder'] or not has_date_mention(query_text):
            return RequestFeedback.REQUEST_SKIPPED

        self.current_dtrl['ladder'].step_in_ladder_with_text(query_text)
        if not self.current_dtrl['ladder'].has_range():
            self.has_currently_discussed_range = False

        return RequestFeedback.REQUEST_OK

    def get_currently_discussed_range(self):
        if self.has_currently_discussed_range:
            print("LADDER", self.current_dtrl['ladder'])
            return self.current_dtrl['ladder'].get_bottom_step()
        else:
            return RequestFeedback.REQUEST_SKIPPED

    def remove_currently_discussed(self):
        self.current_dtrl = {'label': None, 'ladder': None}
        self.has_currently_discussed_range = False

    def get_viz(self):
        res = []

        for label, ti_list in self.sub_datetimes.items():
            for dtr in ti_list:
                res.append([label, dtr.start_datetime, dtr.end_datetime])

        df_timetable = pd.DataFrame(res, columns=['label', 'from', 'to'])

        alt.renderers.enable('default')
        timeline_chart = alt.Chart(df_timetable).mark_bar().encode(
            x='from',
            x2='to',
            y='label',
            tooltip=[alt.Tooltip('from', format='%Y-%m-%d %H:%M'), alt.Tooltip('to', format='%Y-%m-%d %H:%M')],
            color=alt.Color('label', scale=alt.Scale(scheme='dark2'))
        ).properties(
            width=1200,
            height=200
        )

        ladder_res = []
        if self.current_dtrl["ladder"]:
            for i, dtr in enumerate(self.current_dtrl["ladder"].ladder):
                    res.append([i, dtr.start_datetime, dtr.end_datetime])

        df_ladder_timetable = pd.DataFrame(ladder_res, columns=['label', 'from', 'to'])

        ladder_chart = alt.Chart(df_ladder_timetable).mark_bar().encode(
            x='from',
            x2='to',
            y='label'
        ).properties(
            width=1200,
            height=200
        )
        alt.vconcat(timeline_chart, ladder_chart).save('chart_from_chatbot.html')

    def toJSON(self):
        dct = deepcopy(self.__dict__)

        serializable_sub_datetimes = {lb: [] for lb in self.labels}
        for k, intv_list in self.sub_datetimes.items():
            for intv in intv_list:
                serializable_sub_datetimes[k].append((intv.start_datetime.strftime('%Y-%m-%d %H:%M'),
                                                      intv.end_datetime.strftime('%Y-%m-%d %H:%M')))

        dct["sub_datetimes"] = serializable_sub_datetimes

        if self.current_dtrl["ladder"]:
            ladder = self.current_dtrl["ladder"].toJSON()
        else:
            ladder = ''
        dct["current_dtrl"] = [self.current_dtrl["label"], ladder]

        return json.dumps(dct)

    @staticmethod
    def fromJSON(json_str):
        dct = json.loads(json_str)
        tt = TimeTable(dct['labels'])

        parsed_sub_datetimes = {lb: [] for lb in dct['labels']}
        for k, intv_list in dct['sub_datetimes'].items():
            for sd, ed in intv_list:
                parsed_sub_datetimes[k].append(DateTimeRange(sd, ed))

        tt.sub_datetimes = parsed_sub_datetimes

        ladder_r = dct["current_dtrl"][1]
        if ladder_r:
            tt.current_dtrl = {
                "label": dct["current_dtrl"][0],
                "ladder": DateRangeLadder.fromJSON(ladder_r)
            }
        else:
            tt.current_dtrl = {'label': None, 'ladder': None}
        tt.has_currently_discussed_range = dct["has_currently_discussed_range"]

        return tt


class DateRangeLadder:

    def __init__(self, top_range):
        self.top_range = top_range
        self.ladder = [top_range]  # [smaller --> greater]

    def step_in_ladder(self, daterange):
        inserted = False
        for i in range(len(self.ladder)):
            intersection = self.ladder[i].intersection(daterange)
            if intersection.start_datetime and intersection.end_datetime:
                self.ladder = [intersection, *self.ladder[i:]]
                inserted = True

        if not inserted:
            self.ladder = []

    def step_in_ladder_with_text(self, query):
        if not has_date_mention(query):
            return None

        inserted = False
        for i in range(len(self.ladder)):
            current = self.ladder[i]
            success_flag, user_date_mentions = extract_datetime_within_interval(current.start_datetime,
                                                                                current.end_datetime,
                                                                                query,
                                                                                expect_future_day=True)
            dt_mention = user_date_mentions[0]
            mention_dtr = DateTimeRange(dt_mention['start_date'],
                                        dt_mention['end_date'])
            intersection = self.ladder[i].intersection(mention_dtr)

            if intersection.start_datetime and intersection.end_datetime:
                self.ladder = [intersection, *self.ladder[i:]]
                inserted = True

        if not inserted:
            self.ladder = []

    def get_bottom_step(self):
        if self.has_range():
            print(f'bottom step{self.ladder[0]}')
            return self.ladder[0]
        else:
            return None

    def has_range(self):
        return bool(self.ladder)

    def toJSON(self):
        dct = {}
        dct['top_range'] = (self.top_range.start_datetime.strftime('%Y-%m-%d %H:%M'),
                            self.top_range.end_datetime.strftime('%Y-%m-%d %H:%M'))

        ladder_s = []
        for dtr in self.ladder:
            ladder_s.append((dtr.start_datetime.strftime('%Y-%m-%d %H:%M'),
                             dtr.end_datetime.strftime('%Y-%m-%d %H:%M')))

        dct["ladder"] = ladder_s

        return json.dumps(dct)

    @staticmethod
    def fromJSON(json_str):
        dct = json.loads(json_str)
        top_dtr_tup = dct['top_range']
        drl = DateRangeLadder(DateTimeRange(top_dtr_tup[0], top_dtr_tup[1]))

        ladder = []
        for dtr_dct in dct['ladder']:
            ladder.append(DateTimeRange(dtr_dct[0], dtr_dct[1]))

        drl.ladder = ladder

        return drl
