import json, os
from datetime import *
import random


SUB = ['Maths', 'Physics', 'Chemistry', 'Maths', 'Economics', 'History', 'Geography', 'Civics']
TODAY = date.today()


def extract(filename):
    with open(f'data/{filename}.json', "r") as f:
        return json.load(f)

def dump_data(data, filename):
    with open(f"data/{filename}.json", 'w') as f:
        json.dump(data, f)
    return True

def check_today():
    data = extract('streak')

    return data[str(TODAY)]

# STREAK
def streak_count():
    streak_data = extract('streak')
    streak_c = 0
    for day, value in streak_data.items():
        if date(int(day[:4]), int(day[5:7]), int(day[8:])) <=  TODAY:
            if value:
                streak_c += 1
            else:
                streak_c = 0
    return streak_c

def inc_streak():
    if not tar:
        streak_data = extract('streak')
        if str(TODAY) in streak_data:
            streak_data[str(TODAY)] = True

            dump_data(streak_data, 'streak')
            return True

# TARGETS
def today_subjects():
    tt = extract('time_table')
    return tt[str(TODAY.strftime('%A')).lower()]

def target_show():

    if not check_today():

        plan = extract('plan')

        targets = []

        for sub in today_subjects():
            targets.append((sub, plan[sub][0][0]))

        return targets

    return [[None, 'No Targets Available']]
def target_complete(sub):
    plan = extract('plan')

    target = plan[sub].pop(0)

    completed = extract('completed')

    completed[sub].append(target)

    dump_data(completed, 'completed')
    dump_data(plan, 'plan')

# TEST
def upcoming_test():
    import math

    books = {
    "maths": ["NCERT", "RD Sharma", "Question Bank", "Exemplar"],
    "physics": ["NCERT","Question Bank", "Lakhmir Singh"],
    "chemistry": ["NCERT", "Question Bank", "Lakhmir Singh"],
    "biology": ["NCERT", "Question Bank", "Lakhmir Singh"],
    "history": ["NCERT", "Question Bank"],
    "civics": ["NCERT", "Question Bank"],
    "geography": ["NCERT", "Question Bank"],
    "economics": ["NCERT", "Question Bank"]
    }
    #[['int', 'topic', 'qno', 'book']]

    multiplier = {
  "maths": 1000,
  "physics": 300,
  "chemistry": 300,
  "biology": 200,
  "history": 200,
  "civics": 200,
  "geography": 200,
  "economics": 200
}
    

    tests = []
    sno = 1
    completed = extract('completed')



    for key in completed:
        a = []
        topicList = ""
        qC = 0
        if completed[key]:
            for topic in completed[key]:
                topicList += topic[0] + ", "
                qC += topic[1]
            a = ([f"{sno}.", key, topicList, str(math.floor(qC*multiplier[key])), random.choice(books[key]), next_weekday(6)])
            sno += 1

        tests.append(a)

        print(tests) 
    return tests

def prev_test():
    data = extract("tests")

    rv = []

    for key in data:
        for iter in data[key]:
            l = []    
            l.extend([key.title(), iter[0], iter[1]])
            rv.append(l)

    return rv

def next_weekday(target_weekday):
    """
    Get the date of the next target_weekday (0=Monday, 6=Sunday).
    """
    today = datetime.today()
    days_ahead = target_weekday - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return (today + timedelta(days=days_ahead)).strftime('%d/%m/%y')


# PROGRESS SECTION
def progress_showcase():
    pdata = extract('plan')
    cdata = extract('completed')

    rv = []
    
    tc = 0
    tp = 0

    for key in pdata:
        if cdata[key]:
            rv.append((len(cdata[key])/len(pdata[key]))*100)
        else:
            rv.append(0)

        tc += len(cdata[key])
        tp += len(pdata[key])

    rv.insert(0, (tc/tp)*100)
    return rv


# def temp():
#     from datetime import datetime, timedelta

#     start_date = datetime.today()
#     end_date = datetime(2025, 11, 16)

#     current_date = start_date
#     while current_date <= end_date:
#         print(current_date.date())  # or .strftime('%Y-%m-%d')
#         current_date += timedelta(days=1)


# temp()

# def temp():
#     d = {'maths': [1,2,3,4], 'science': [3,4,'k,',8]}
#     for i in d:
#         print(i)
# temp()


tar = target_show()
print(tar)
