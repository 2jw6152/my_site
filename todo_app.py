from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import requests
import re

app = Flask(__name__, template_folder='')
app.jinja_env.globals['datetime'] = datetime
app.jinja_env.globals['timedelta'] = timedelta

todos = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        date = request.form['date']
        task = request.form['task']
        if date in todos and todos[date]:
            todos[date].append({'task': task, 'done': False})
        else:
            todos[date] = [{'task': task, 'done': False}]
        return redirect(url_for('index'))

    today = datetime.now().date()
    dates = [today + timedelta(days=i) for i in range(8)]

    for date in todos.keys():
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        if date_obj not in dates:
            dates.append(date_obj)

    # Get meal information
    now = datetime.now()
    today = str(now.strftime('%Y%m%d'))
    mealnum1 = '1'
    mealnum2 = '2'
    mealnum3 = '3'
    url1 = 'https://open.neis.go.kr/hub/mealServiceDietInfo?KEY=46343e32dd8c482a8ee0043126d3f95a&Type=json&pIndex=1&pSize=30&ATPT_OFCDC_SC_CODE=B10&SD_SCHUL_CODE=7010084&MMEAL_SC_CODE='+mealnum1+'&MLSV_YMD='
    url2 = 'https://open.neis.go.kr/hub/mealServiceDietInfo?KEY=46343e32dd8c482a8ee0043126d3f95a&Type=json&pIndex=1&pSize=30&ATPT_OFCDC_SC_CODE=B10&SD_SCHUL_CODE=7010084&MMEAL_SC_CODE='+mealnum2+'&MLSV_YMD='
    url3 = 'https://open.neis.go.kr/hub/mealServiceDietInfo?KEY=46343e32dd8c482a8ee0043126d3f95a&Type=json&pIndex=1&pSize=30&ATPT_OFCDC_SC_CODE=B10&SD_SCHUL_CODE=7010084&MMEAL_SC_CODE='+mealnum3+'&MLSV_YMD='

    url = url1 + today
    response = requests.get(url)
    contents = response.text

    def rep(str):
        nonlocal contents
        contents = contents.replace(str, '')

    def convert():
        nonlocal contents
        rep('"mealServiceDietInfo":[{"head":[{"list_total_count":1},{"RESULT":{"CODE":"INFO-000","MESSAGE":"정상 처리되었습니다."}}]},{"row":[{"ATPT_OFCDC_SC_CODE":"B10","ATPT_OFCDC_SC_NM":"서울특별시교육청","SD_SCHUL_CODE":"7010084","SCHUL_NM":"서울과학고등학교","MMEAL_SC_CODE":')
        rep(',"MMEAL_SC_NM":"')
        rep('","MLSV_YMD":"')
        rep('","MLSV_FGR":"')
        rep('","DDISH_NM":"')
        rep('"1"조식')
        rep('"2"중식')
        rep('"3"석식')
        rep('{')
        rep('}')
        pattern = r'"ORPLC_INFO":.*'
        contents = re.sub(pattern, '', contents)
        pattern2 = r'\d+|\(.*?\)'
        contents = re.sub(pattern2, '', contents)
        contents = contents.replace('<br/>', '\n')
        rep('",')
        rep('*')
        rep('-')

    convert()
    breakfast = contents

    url = url2 + today
    response = requests.get(url)
    contents = response.text
    convert()
    lunch = contents

    url = url3 + today
    response = requests.get(url)
    contents = response.text
    convert()
    dinner = contents

    # Add meal information to the template rendering
    return render_template('index.html', dates=dates, todos=todos, breakfast=breakfast, lunch=lunch, dinner=dinner)

if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=7777)
