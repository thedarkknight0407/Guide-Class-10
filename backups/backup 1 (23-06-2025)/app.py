from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime
import math
import time

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')
WEEK_FILE = os.path.join(os.path.dirname(__file__), 'week.json')
DAYS_FILE = os.path.join(os.path.dirname(__file__), 'days.json')
SUBJECTS = ['Maths 1', 'Stats 1', 'Computational Thinking']
WEEKS = 12
FINAL_DEADLINE = datetime(2025, 8, 31)
TODAYS_DATE = datetime.today().date()


def load_week_data():
    if os.path.exists(WEEK_FILE):
        with open(WEEK_FILE, 'r') as f:
            return json.load(f)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {subject: {str(week): {'total': 0, 'completed': 0} for week in range(1, WEEKS+1)} for subject in SUBJECTS}

def load_completion_status_data():
    if os.path.exists(DAYS_FILE):
        with open (DAYS_FILE, 'r') as f:
            d =  json.load(f)
            todays_date = TODAYS_DATE
            if d["days"][str(todays_date)] == "Yes":
                return True, d
            
            else:
                return False, d

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)
    

#Checking if today tasks are done?
def date_adder():
    with open(DAYS_FILE, "r") as f:
        try:
            pre_data = json.load(f)

        except json.decoder.JSONDecodeError as e:
            print("Empty File, setting up base!")
            pre_data = {"days": {}}

        except Exception as e:
            print("An error occured:", e)
    today_date = TODAYS_DATE
    if str(today_date) in pre_data['days'].keys():
        pass

    else:
        with open(DAYS_FILE, 'w+') as f:
            pre_data["days"][str(today_date)] = "No"
            json.dump(pre_data, f)
        



date_adder()
data = load_data()
week_data = load_week_data()

# setting current week
def set_active_week():
    global active_week
    active_week = []
    for i in range(1, WEEKS + 1):
        week_begin_date = str(week_data["Foundation"][str(i)]['begin'])
        week_end_date = str(week_data["Foundation"][str(i)]['deadline'])
        if datetime.today() >= datetime(2025, int(week_begin_date[2:4]), int(week_begin_date[0:2])) and datetime.today() <= datetime(2025, int(week_end_date[2:4]), int(week_end_date[0:2])):
            active_week.append(i)

set_active_week()




@app.route('/', methods=['POST', 'GET'])
def index():
    global todo
    completion_status, day_data = load_completion_status_data()
    total_tasks = sum(data[subject][str(week)]['total'] for subject in SUBJECTS for week in range(1, WEEKS+1))
    completed_tasks = sum(data[subject][str(week)]['completed'] for subject in SUBJECTS for week in range(1, WEEKS+1))
    progress_percent = [('overall',int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0),]
    current_week = active_week[0]

    if request.method == 'POST':
        current_week = request.form.get('week-progress')


    # Progress perncent calculation per subject
    for subject in SUBJECTS:
        t_tasks = data[subject][str(current_week)]['total']
        c_tasks = data[subject][str(current_week)]['completed']
        progress_percent.append((subject, int((c_tasks/t_tasks)*100) if t_tasks > 0 else 0))
    
    t_tasks = 0
    c_tasks = 0

    for subject in SUBJECTS:
        t_tasks += data[subject][str(current_week)]['total']
        c_tasks += data[subject][str(current_week)]['completed']
    remaining_tasks = t_tasks - c_tasks
    progress_width = "width: " + str(progress_percent) + "%"

    days_left = (datetime(2025, int(str(week_data["Foundation"][str(current_week)]['deadline'])[2:4]), int(str(week_data["Foundation"][str(current_week)]['deadline'])[0:2]), 23, 59) - datetime.now()).days - 1
    daily_target = math.ceil(remaining_tasks / days_left)

    subject_targets = {}
    for subject in SUBJECTS:
        subject_total_remaining = sum(data[subject][str(week)]['total'] - data[subject][str(week)]['completed'] for week in range(1, WEEKS+1))
        target = (subject_total_remaining // days_left) if days_left > 0 else subject_total_remaining
        subject_targets[subject] = target




    #creating the todo
    todo = []
    todoprogress = progress_percent.copy()
    todoprogress.sort(key=lambda x :x[1])
    
    for t in todoprogress:
        if t[1] >= 100 or t[0] == 'overall':
            todoprogress.remove(t)
    
    # finding number of target persubject to complete
    def each_sub_target(n): #n = number of subjects (left)
        est = daily_target // n
        et = daily_target - est * n
        return [est, et]
    
    # To catch up on lacking subject
    if daily_target % len(SUBJECTS) != 0:
        extra_target = daily_target - each_sub_target(len(SUBJECTS))[0] * len(SUBJECTS)

    # number of left targets
    left_targets = [] #[(sub, remaining targets), (sub, remaining targets), (sub, remaining targets)...]
    for sub in SUBJECTS:
        # (subject, total - completed)
        l_t = data[sub][str(current_week)]['total'] - data[sub][str(current_week)]['completed']
        left_targets.append((sub, l_t))
    
    left_targets.sort(key= lambda x: x[1], reverse=True)


    print("REMAINING TARGETS:", left_targets)
    if not completion_status:   
        for sub, remain in left_targets:
            if remain < each_sub_target(len(left_targets))[0]:
                for i in range(remain):
                    todo.append(sub)
                
                left_targets.remove((sub, remain))
                daily_target -= remain

            
            else:
                for i in range(each_sub_target(len(left_targets))[0]):
                    todo.append(sub)

        if each_sub_target(len(left_targets))[1]:
            for target in range(each_sub_target(len(left_targets))[1]):
                todo.append(left_targets[target][0])

    
    
 
    print("PROGRESS PERCENTAGE:", progress_percent)


    #The function for updateing the todo-list
    def alldone():
        if request.form.get('todo-chk') == 'done':
            for sub in SUBJECTS:
                a = todo.count(sub)
                data[sub][str(active_week[0])]['completed'] += a

            print("HERE")
            with open(DAYS_FILE, 'w') as f:
                day_data['days'][str(TODAYS_DATE)] = "Yes"
                json.dump(day_data, f)
            save_data(data)
            

    return render_template('index.html',
                           data=data,
                           subjects=SUBJECTS,
                           weeks=active_week,
                           current_week=current_week,
                           total=t_tasks,
                           completed=c_tasks,
                           remaining=remaining_tasks,
                           target=len(todo),
                           progress=progress_percent,
                           subject_targets=subject_targets,
                           progress_width = progress_width,
                           todo = sorted(todo),
                           len=len,
                           alldone=alldone,
                           remaining_days = days_left)


@app.route('/update', methods=['POST'])
def update():
    subject = request.form['subject']
    week = request.form['week']
    total = int(request.form.get('total', 0))
    completed = int(request.form.get('completed', 0))
    data[subject][week]['total'] = total
    data[subject][week]['completed'] = completed
    save_data(data)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)