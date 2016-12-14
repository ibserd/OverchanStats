import MySQLdb,datetime
import matplotlib.pyplot as plt

class DbConnector(): # Used for stats.html
    def __init__(self):
        credentials = []
        with open('../../login.txt') as login:
            for line in login.readlines():
                credentials.append(line.strip('\n"'))

        self.db_name = credentials[1]
        self.host = credentials[0]
        self.user = credentials[2]
        self.passwd = credentials[3]

    def dbGetPosts(self,year,month): #Used within stats
        db = MySQLdb.connect(self.host,self.user,self.passwd,self.db_name)
        cur = db.cursor()
        data = year + "-" + month + "-%"
        command = "SELECT * FROM posts WHERE Data LIKE %r" % data
        cur.execute(command)
        tables = cur.fetchall()
        db.close()

        return tables

    def dbGetTables(self):
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        command = "SHOW TABLES;"
        cur.execute(command)
        tables = cur.fetchall()
        dbconnect.close()
        tables_list = []
        for item in tables:
            item = str(item).strip("()',")
            tables_list.append(item)

        return tables_list

    def dbGetMonthPosts(self,table):
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        command = "SELECT * FROM %s" % table
        cur.execute(command)
        posts = cur.rowcount
        dbconnect.close()
        return posts

class Plotter(object):
    def daily(self):
        now= datetime.datetime.now()
        year = str(now.year)
        month = str(now.month)

        days = []
        posts = []
        posts_tulpe = DbConnector().dbGetPosts(year,month)
        for item in posts_tulpe:
            days.append(int(item[0][-2:]))
            posts.append(int(item[1]))

        plt.figure()
        plt.plot(days,posts,label="Global")
        plt.ylabel("Posts per day")
        plt.xlabel("Day of the month")
        title = "%s-%s Global posts per day" %(year,month)
        plt.title(title)
        plt.legend(loc="upper left")
        filename = "%s-%s_GlobalGraph.png" %(year,month)
        plt.savefig(filename)

    def monthly(self):
        tables = DbConnector().dbGetTables()[-13:-3]
        month=[]
        posts=[]

        for table in tables:
            month.append(int(table[-2:]))
            posts.append(int(DbConnector().dbGetMonthPosts(table)))

        plt.figure()
        plt.plot(month,posts,label="Global monthly")
        plt.ylabel("Posts per month")
        plt.xlabel("Month")
        title = "Global posts per month"
        plt.title(title)
        plt.legend(loc="upper left")
        filename = "Monthly_GlobalGraph.png"
        plt.savefig(filename)

Plotter().daily()
Plotter().monthly()
