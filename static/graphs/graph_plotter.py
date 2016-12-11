import MySQLdb
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

year = "2016"
month = "11"
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
