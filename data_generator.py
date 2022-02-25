import datetime
from random import choice
import pandas as pd
import json

START_DATES = ["08:00", "09:00", "10:00", "11:00"]
END_DATES = ["13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"]


def get_bdates(start=datetime.datetime.now(), number_of_bdays=10):
    weekdays = pd.bdate_range(
        start, start+datetime.timedelta(days=number_of_bdays))
    added_days = number_of_bdays+1

    while len(weekdays) != number_of_bdays:
        weekdays = pd.bdate_range(start, start+datetime.timedelta(added_days))
        added_days += 1

    weekdays_list = [pd.to_datetime(weekday).date() for weekday in weekdays]
    return weekdays_list


def generate_dates(dates):
    return [{"start_date": f"{date}T{choice(START_DATES)}",
             "end_date": f"{date}T{choice(END_DATES)}"} for _, date in enumerate(dates)]


def main():
    weekdays = generate_dates(get_bdates(
        datetime.datetime.now()+datetime.timedelta(days=1), 13))
    with open('./action_server/test_data.json', 'w') as f:
        json.dump(weekdays, f, indent=4)


if __name__ == '__main__':
    main()
