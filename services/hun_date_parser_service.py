from fuzzywuzzy import fuzz
from .lara import *


def mapper(msg):
    mapping = [('á', 'a'),
               ('é', 'e'),
               ('ő', 'o'),
               ('ö', 'o'),
               ('ó', 'o'),
               ('ú', 'u'),
               ('ű', 'u'),
               ('ü', 'u')]
    for a, b in mapping:
        msg = msg.replace(a, b)
    return msg


def fuzzy_match(a, b):
    return fuzz.ratio(mapper(a), mapper(b)) > 85


def get_cat(msg: str, cat: dict):
    for k, v in cat.items():
        for sub_v in v:
            if fuzzy_match(msg, sub_v):
                return k
    return -1


def l_in_l(l1, l2):
    _l2 = [mapper(e) for e in l2]
    for e1 in l1:
        if e1 in _l2:
            return True
    return False


def l_in_s(s, l2):
    _l2 = [mapper(e) for e in l2]
    for e1 in _l2:
        if e1 in s:
            return True
    return False


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead < 0:
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


def next_weekizer(d):
    this_sun = next_weekday(datetime.date.today(), 6)
    if d <= this_sun:
        return d + datetime.timedelta(days=7)
    else:
        return d


def days_between(d_min, d_max):
    n_days = (d_max - d_min).days
    days = []
    for i in range(n_days + 1):
        days.append(d_min + datetime.timedelta(i))

    return days


def parse_named_dates(msg: str):
    ths = ['a héten']
    nxt = ['jövő', 'következő', 'jövőhét', 'jövőhéten']
    nxt2 = ['két hét múlva', 'két hét múlvára', 'két hét múlvához', 'kéthét múlva']

    relative_days = {
        0: ['ma', 'mai', 'mához', 'mára'],
        1: ['holnap', 'holnapi', 'holnapra', 'holnaphoz'],
        2: ['holnapután', 'holnaputánra', 'holnaputáni', 'holnaputánhoz']
    }

    days = {
        0: ['hétfő', 'hétfőn', 'hétfőre', 'hétfőhöz'],
        1: ['kedd', 'kedden', 'keddre', 'keddhez'],
        2: ['szerda', 'szerdán', 'szerdára', 'szerdához'],
        3: ['csütörtök', 'csütörtökön', 'csütörtökre', 'csütörtökhöz'],
        4: ['péntek', 'pénteken', 'péntekre', 'péntekhez'],
        5: ['szombat', 'szombaton', 'szombatra', 'szombathoz'],
        6: ['vasárnap', 'vasárnapra', 'vasárnaphoz']
    }

    msg = mapper(msg)
    now = datetime.date.today()
    toks = tokenize(msg)

    is_ths = l_in_s(msg, ths)
    is_nxt = l_in_s(msg, nxt)
    is_2nxt = l_in_s(msg, nxt2)

    nth_days = []
    for a in toks:
        nth_day = get_cat(a, days)
        if nth_day != -1:
            nth_days.append(nth_day)

    res_d = [next_weekday(now, nth_day) for nth_day in nth_days]

    if is_nxt:
        res_d = [next_weekizer(d) for d in res_d]
    elif is_2nxt:
        res_d = [next_weekizer(d) + datetime.timedelta(days=7) for d in res_d]

    for a in toks:
        rel_day = get_cat(a, relative_days)
        if rel_day == 0:
            res_d.append(now)
        elif rel_day == 1:
            res_d.append(now + datetime.timedelta(days=1))
        elif rel_day == 2:
            res_d.append(now + datetime.timedelta(days=2))

    if res_d:
        return res_d
    elif is_ths:
        return days_between(now, next_weekday(now, 6))
    elif is_nxt:
        return days_between(next_weekizer(next_weekday(now, 0)),
                            next_weekizer(next_weekday(now, 6)))
    elif is_2nxt:
        return days_between(next_weekizer(next_weekday(now, 0) + datetime.timedelta(days=7)),
                            next_weekizer(next_weekday(now, 6) + datetime.timedelta(days=7)))
    else:
        return []


def parse_named_times(msg):
    day_parts = {
        0: ['reggel', 'reggelhez', 'reggelre'],
        1: ['délelőtt', 'délelőtthöz', 'délelőttre'],
        2: ['dél', 'délben'],
        3: ['délután'],
        4: ['este'],
        5: ['éjjel', 'éjszaka']
    }

    def get_hour(h):
        return f'{str(h).zfill(2)}:00'

    day_parts_time = {
        0: list(map(get_hour, range(6, 10))),
        1: list(map(get_hour, range(10, 12))),
        2: [get_hour(12)],
        3: list(map(get_hour, range(12, 18))),
        4: list(map(get_hour, range(18, 22))),
        5: list(map(get_hour, [23] + list(range(0, 6))))
    }

    toks = tokenize(msg)
    res_t = []

    for a in toks:
        rel_i = get_cat(a, day_parts)
        if rel_i != -1:
            res_t += day_parts_time[rel_i]

    return res_t


def get_datetimes(msg):
    info = Extract(msg)
    if info.dates():
        dates = info.dates()
    else:
        dates = [datetime.datetime.strftime(d, '%Y-%m-%d') for d in parse_named_dates(msg)]

    if info.times():
        times = info.times()
    else:
        times = parse_named_times(msg)

    return dates, times
