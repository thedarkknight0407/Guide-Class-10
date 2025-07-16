from flask import Flask, render_template, request, redirect, url_for, jsonify
from main import *

streak = streak_count()

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    

    return render_template('index.html',
                            streak=streak,
                            date=TODAY.strftime('%d/%m/%y'),
                            targets=tar, 
                            u_tests=upcoming_test(),
                            len = len,
                            tests=prev_test(),
                            progress=progress_showcase())


@app.route('/update', methods=['POST', "GET"])
def update():
    compchp = request.args.get('chapter')
    compsub = request.args.get('sub')
    return render_template('completed.html', streak=streak, date=TODAY.strftime('%d/%m/%y'), subject=compsub, chapter=compchp)

@app.route('/completetion', methods=['POST', 'GET'])
def completetion():
    global streak
    compsub = request.args.get('sub')
    compchp = request.args.get('chapter')


    tar.remove((compsub, compchp.lower()))

    target_complete(compsub)
    inc_streak()

    streak = streak_count()
    return redirect(url_for('index'))


@app.route('/addTest', methods=['POST', 'GET'])
def analytics():
   
    return render_template('add_test.html', streak=streak, date=TODAY.strftime('%d/%m/%y'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')