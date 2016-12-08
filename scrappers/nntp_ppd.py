import MySQLdb

import requests
from bs4 import BeautifulSoup

import datetime


class DBconnector(object):
    def __init__(self):
        credentials = []
        with open('login.txt') as login:
            for line in login.readlines():
                credentials.append(line.strip('\n"'))
        self.db_name = credentials[1]
        self.host = credentials[0]
        self.user = credentials[2]
        self.passwd = credentials[3]
        self.table = "posts"
        self.year = datetime.date.today().year

    def dbInsert(self,data,posts):
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        data = str(self.year) + "-" + data
        command = "INSERT INTO %s (Data,Posts) VALUES (%r,%i);" % (self.table,data,posts)
        cur.execute(command)
        dbconnect.commit()
        dbconnect.close()

node = 'http://oniichanylo2tsi4.onion/index.html'
proxy = {"http":"socks5://localhost:9050"}
req = requests.get(node,proxies=proxy)

if req.status_code != requests.codes.ok:
    print('Connection Error')
    quit()

soup = BeautifulSoup(req.content,'html.parser')
table = soup.find_all('table',{'id':'posts_graph'})
for item in table:
    n = 3
    new = 0
    skipped = 0
    while n <= 27:
        try:
            DBconnector().dbInsert(str(item.find_all('td')[n].text),int(item.find_all('td')[n+1].text))
            n += 3
            new += 1
        except MySQLdb.IntegrityError:
            n += 3
            skipped += 1
    print ('All done! Added: %d records and skipped %d!') %(new,skipped)
