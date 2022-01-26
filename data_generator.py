#!/usr/bin/python3

import datetime
import pandas as pd
import json

def get_bdates(start = datetime.datetime.now(), number_of_bdays=10):
  weekdays = pd.bdate_range(start, start+datetime.timedelta(days=number_of_bdays))
  added_days = number_of_bdays+1

  while len(weekdays) != number_of_bdays:
    weekdays = pd.bdate_range(start, start+datetime.timedelta(added_days))
    added_days += 1

  wdays = []
  for weekday in weekdays:
    wdays += [pd.to_datetime(weekday).date()]
  return wdays

def generate_dates(dates):
  return [
    {"start_date": f"{dates[0]}T14:00", "end_date": f"{dates[0]}T16:00"},

    {"start_date": f"{dates[1]}T12:00", "end_date": f"{dates[1]}T13:00"},
    {"start_date": f"{dates[1]}T16:00", "end_date": f"{dates[1]}T18:00"},

    {"start_date": f"{dates[2]}T12:00", "end_date": f"{dates[2]}T18:00"},

    {"start_date": f"{dates[3]}T08:00", "end_date": f"{dates[3]}T12:00"},

    {"start_date": f"{dates[4]}T07:30", "end_date": f"{dates[4]}T16:00"},

    {"start_date": f"{dates[5]}T09:00", "end_date": f"{dates[5]}T12:00"},
    {"start_date": f"{dates[5]}T14:00", "end_date": f"{dates[5]}T17:00"},

    {"start_date": f"{dates[6]}T12:45", "end_date": f"{dates[6]}T17:30"},

    {"start_date": f"{dates[7]}T12:00", "end_date": f"{dates[7]}T18:00"},

    {"start_date": f"{dates[8]}T07:45", "end_date": f"{dates[8]}T12:15"},
    {"start_date": f"{dates[8]}T13:15", "end_date": f"{dates[8]}T16:15"},

    {"start_date": f"{dates[9]}T12:00", "end_date": f"{dates[9]}T18:00"},

    {"start_date": f"{dates[10]}T14:00", "end_date": f"{dates[10]}T21:00"},

    {"start_date": f"{dates[11]}T14:00", "end_date": f"{dates[11]}T17:00"},

    {"start_date": f"{dates[12]}T09:25", "end_date": f"{dates[12]}T15:45"}
  ]

def main():
  weekdays = generate_dates(get_bdates(datetime.datetime.now()+datetime.timedelta(days=1), 13))
  with open('./action_server/test_data.json', 'w') as f:
    json.dump(weekdays, f, indent=4)


if __name__ == '__main__':
  main()