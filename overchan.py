from flask import Flask,render_template

import MySQLdb,time,re,operator
from datetime import *

app = Flask(__name__)

class DbConnector(): # Used for stats.html
    def __init__(self):
        credentials = []
        with open('login.txt') as login:
            for line in login.readlines():
                credentials.append(line.strip('\n"'))

        self.db_name = credentials[1]
        self.host = credentials[0]
        self.user = credentials[2]
        self.passwd = credentials[3]

    def dbConnector(self):
        db = MySQLdb.connect(self.host,self.user,self.passwd,self.db_name)
        return db

    def dbGetOrigin(self,data,board):
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        origin = {"i2p":0,"clearnet":0,"tor":0}
        for index in origin:
            command = "SELECT * FROM %s WHERE Origin = %r AND Data LIKE %r;" % (board,index,data)
            cur.execute(command)
            origin[index] = cur.rowcount
        dbconnect.close()
        return origin

    def dbGetSage(self,data,board):
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        command = "SELECT * FROM %s WHERE Subject = 'sage' AND Data LIKE %r;" % (board,data)
        cur.execute(command)
        sage_count = cur.rowcount
        dbconnect.close()
        return sage_count

    def dbGetSubject(self,data,board):
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        command = "SELECT * FROM %s WHERE Subject != 'sage' AND Subject !='None' AND Data LIKE %r;" % (board,data)
        cur.execute(command)
        non_empty_subject = cur.rowcount
        dbconnect.close()
        return non_empty_subject

    def dbGetName(self,data,board):
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        command = "SELECT * FROM %s WHERE Author != 'Anonymous' AND Data LIKE %r;" % (board,data)
        cur.execute(command)
        non_empty_name = cur.rowcount
        dbconnect.close()
        return non_empty_name

    def dbGetTime(self,data,board):
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        timez = {"00":0,"01":0,"02":0,"03":0,"04":0,"05":0,"06":0,"07":0,"08":0,"09":0,"10":0,"11":0,"12":0,"13":0,"14":0,"15":0,"16":0,"17":0,"18":0,"19":0,"20":0,"21":0,"22":0,"23":0}
        for item in timez:
            hour = "\'%s:__:__\'" % item
            command = "SELECT * FROM %s WHERE Timex LIKE %s AND Data LIKE %r;" % (board,hour,data)
            cur.execute(command)
            hour_count = cur.rowcount
            timez[item] = hour_count
        dbconnect.close()
        return timez

    def dbGetDate(self,data,board):
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        datez = {"01":0,"02":0,"03":0,"04":0,"05":0,"06":0,"07":0,"08":0,"09":0,"10":0,"11":0,"12":0,"13":0,"14":0,"15":0,"16":0,"17":0,"18":0,"19":0,"20":0,"21":0,"22":0,"23":0,"24":0,"25":0,"26":0,"27":0,"28":0,"29":0,"30":0,"31":0}
        for item in datez:
            data = "%s-%s-%s" % (str(data.split("-")[0]),str(data.split("-")[1]),item)
            command = "SELECT * FROM %s WHERE Data LIKE %r;" % (board,data)
            cur.execute(command)
            datez_count = cur.rowcount
            datez[item] = datez_count
        dbconnect.close()
        return datez

    def dbGetNode(self,data,board):
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        command = "SELECT msgID FROM %s WHERE Data LIKE %r;" % (board,data)
        cur.execute(command)
        nodess = list(cur.fetchall())
        dbconnect.close()

        nodes = {}
        for item in nodess:
            node = str(item).strip("',()").split("@")[1]
            if node not in nodes:
                nodes[node] = 1
            else:
                nodes[node] += 1
        return nodes


def uptime(uptime): #Used within index(status page)
    nodes = {"node1":0,"node2":0,"node3":0,"node4":0,"node5":0,"node6":0,"node7":0,"node8":0,"node9":0,"node10":0}
    time = 0
    while time < len(uptime): #how many records for selected range
        node = 1
        while node <= len(nodes): #Total of nodes, <= bc starting from 1
            if uptime[time][node] == "OK":
                nodes["node"+str(node)] += 1
            node += 1
        time += 1

    for key,value in nodes.items():
        if nodes[key] == len(uptime):
            nodes[key] = 100
        else:
            nodes[key] = "%.2f" %round((float(value)/len(uptime) * 100),2)
    return nodes

def boardList(): #Used within stats
    db = DbConnector().dbConnector()
    cur = db.cursor()
    cur.execute("show tables;")
    tables = cur.fetchall()
    db.close()
    boards = ['Global']
    boards_blacklist=['ctl','overchan_porn','posts','status']
    for board in tables:
        board = str(board).strip(",()'")
        if board not in boards_blacklist:
            boards.append(board)

    regex = re.compile('overchan_test*')
    filtered_out = [string for string in boards if re.match(regex, string)]
    for filtered in filtered_out:
        boards = filter(lambda a: a != filtered, boards)

    return boards

def monthsRecorded():
    months = ['november','december']
    return months

@app.route('/')
def index():
    db = DbConnector().dbConnector()
    cur = db.cursor()
    ##Start Last Update query
    cur.execute("SELECT * FROM status ORDER BY Data DESC")
    last_update = cur.fetchone()
    date_last = last_update[0] #TBU for days elapsed since start
    ## Returned to flask
    now = str(last_update[0]).split(" ") #List of date,time of the last status check
    last_update = list(last_update[1:]) #List of the last status check results
    ##Start total checks and first entry query
    cur.execute("SELECT * FROM status ORDER BY Data ASC")
    first_update = cur.fetchone()
    date_first = first_update[0] #TBU for days elapsed since start
    ##Returned to flask
    first_update = str(first_update[0]).split(" ") ##List of the first status check date and time
    checks = cur.rowcount #Int no of performed checks
    days_since_start = (date_last.date() - date_first.date()).days #Int no of days since start
    ##How much time passed since last update
    time_last = date_last
    time_now = datetime.now()
    diff = time_now - time_last
    ##Retrned to flask
    time_since_last_update = str(diff)[2:4]

    ##Uptime queries start here
    ##Today
    today_date = "'"+now[0] + " %'"
    command = "SELECT * FROM status WHERE Data LIKE %s ;" % today_date
    cur.execute(command)
    uptime_today = cur.fetchall()
    ##Returned to flask
    today = uptime(uptime_today)
    ##Month
    month_date = "'"+now[0][0:8] + "%'"
    command = "SELECT * FROM status WHERE Data LIKE %s ;" % month_date
    cur.execute(command)
    uptime_month = cur.fetchall()
    ##Returned to flask
    month = uptime(uptime_month)
    ##ALL
    command = "SELECT * FROM status"
    cur.execute(command)
    uptime_all = cur.fetchall()
    ##Returned to flask
    alltime = uptime(uptime_all)

    db.close() #done with db.

    return render_template('index.html',last_update=last_update,now=now,today=today,month=month,alltime=alltime,first_update=first_update,checks=checks,days_since_start=days_since_start,time_since_last_update=time_since_last_update)

@app.route('/stats')
def stats():
    boards = boardList()
    months = monthsRecorded()
    return render_template('stats.html',boards=boards,months = months)

@app.route('/stats/<board>/<month>')
def stats_board_month(board,month):
    boards = boardList()
    months = monthsRecorded()
    months_int = {"january":1,"february":2,"march":3,"april":4,"may":5,"june":6,"july":7,"august":8,"september":9,"october":10,"november":11,"december":12}

    ##Declared for methods
    board = board.replace(".","_")
    month_int = months_int[month]

    ##Im gonna rewrite it in a year
    if month_int == 11 or month_int == 12:
        data = '2016-' + str(month_int) + '-%'
    else:
        data = '2017-' + str(month_int) + '-%'

    ##Returned to Flask (stats_board_month.html)
    origin = DbConnector().dbGetOrigin(data,board)
    sages = DbConnector().dbGetSage(data,board)
    subjects = DbConnector().dbGetSubject(data,board)
    names = DbConnector().dbGetName(data,board)
    timez = DbConnector().dbGetTime(data,board)
    datez = DbConnector().dbGetDate(data,board)
    nodes = DbConnector().dbGetNode(data,board)

    ##Check if user was playing with url :)
    if board in boards and month in months:
        return render_template('stats_board_month.html',board=board,month=month,boards=boards,months=months,origin=origin,sages=sages,subjects=subjects,names=names,timez=timez,datez=datez,nodes=nodes)
    else:
        return render_template('not_found.html',name = board)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/<name>')
def no_such_page(name):
    return render_template('not_found.html',name = name)

if __name__ == "__main__":
   app.run()
