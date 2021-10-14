from typing import List

import pandas as pd
import json
import altair as alt
from hun_date_parser import text2datetime
from datetimerange import DateTimeRange
from copy import deepcopy


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

    def get_viz(self):
        res = []

        for label, ti_list in self.sub_datetimes.items():
            for dtr in ti_list:
                res.append([label, dtr.start_datetime, dtr.end_datetime])

        df_timetable = pd.DataFrame(res, columns=['label', 'from', 'to'])

        alt.renderers.enable('default')
        alt.Chart(df_timetable).mark_bar().encode(
            x='from',
            x2='to',
            y='label',
            tooltip=[alt.Tooltip('from', format='%Y-%m-%d %H:%M'), alt.Tooltip('to', format='%Y-%m-%d %H:%M')],
            color=alt.Color('label', scale=alt.Scale(scheme='dark2'))
        ).properties(
            width=1200,
            height=200
        ).save('chart_from_chatbot.html')

    def toJSON(self):
        dct = deepcopy(self.__dict__)

        serializable_sub_datetimes = {lb: [] for lb in self.labels}
        for k, intv_list in self.sub_datetimes.items():
            for intv in intv_list:
                serializable_sub_datetimes[k].append((intv.start_datetime.strftime('%Y-%m-%d %H:%M'),
                                                      intv.end_datetime.strftime('%Y-%m-%d %H:%M')))

        dct["sub_datetimes"] = serializable_sub_datetimes

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

        return tt
