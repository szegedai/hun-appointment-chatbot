from datetime import datetime, date, time

days = [
    ['hétfő', 'hétfőn'],
    ['kedd', 'kedden'],
    ['szerda', 'szerdán'],
    ['csütörtök', 'csütörtökön'],
    ['péntek', 'pénteken'],
    ['szombat', 'szombaton'],
    ['vasárnap']
]

hours_cust = {
    0: 'éjfélkor',
    1: 'hajnali egykor',
    2: 'hajnali kettőkor',
    3: 'hajnali háromkor',
    4: 'hajnali négykor',
    5: 'hajnali ötkor',
    6: 'reggel hatkor',
    7: 'reggel hétkor',
    8: 'reggel 8-kor',
    9: 'reggel 9-kor',
    10: 'délelőtt 10-kor',
    11: 'délelőtt 11-kor',
    12: 'délben',
    13: 'délután 1-kor',
    14: 'délután 2-kor',
    15: 'délután 3-kor',
    16: 'délután 4-kor',
    17: 'délután 5-kor',
    18: 'este 6-kor',
    19: 'este 7-kor',
    20: 'este 8-kor',
    21: 'este 9-kor',
    22: 'este 10-kor',
    23: 'este 11-kor',
}


def date2text(d):
    if type(d) == str:
        d = date.fromisoformat(d)

    now = date.today()
    is_day_of = lambda d: days[d.weekday()][-1]
    resp = ''

    day_diff = (d - now).days
    till_next_week = 7 - now.weekday() - 1

    if day_diff == 0:
        resp += 'ma'
    elif day_diff == 1:
        resp += 'holnap'
    elif day_diff < till_next_week:
        resp += 'ezen a héten ' + is_day_of(d)
    elif day_diff > till_next_week:
        resp += 'jövőhét ' + is_day_of(d)
    elif day_diff > till_next_week + 7 and till_next_week + 14 < day_diff:
        resp += 'két hét múlva ' + is_day_of(d)
    else:
        resp += f'ekkor: {d.year}-{d.month}-{d.day}', + is_day_of(d)

    return resp


def time2text(t):
    if type(t) == str:
        t = time.fromisoformat(t)

    return hours_cust[t.hour]
