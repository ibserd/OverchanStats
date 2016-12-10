## Scraps DB to present archived data

import MySQLdb
import operator
import requests

class dbConnector(object):
    def __init__(self):
        self.db_name =
        self.host =
        self.user =
        self.passwd =

    def dbGetTables(self):
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        command = "SHOW TABLES;"
        cur.execute(command)
        tables = cur.fetchall()
        dbconnect.close()
        return tables

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
            #print command
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
            #print command
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
        nodes = list(cur.fetchall())
        dbconnect.close()
        return nodes



tables_count = dbConnector().dbGetTables()
print "Total boards this month: ",len(tables_count)
active = 0
for item in tables_count:
    item = str(item).strip('(),\'')
    data = '2016-11-%'  ##modify
    try:
        origin_count = dbConnector().dbGetOrigin(data,item)
        if origin_count["clearnet"] != 0 or origin_count["i2p"] != 0 or origin_count["tor"] != 0:
            print item.replace('_','.')
            print "clearnet: ",origin_count["clearnet"],"i2p: ",origin_count["i2p"],"tor: ",origin_count["tor"]
            active += 1

            sage = dbConnector().dbGetSage(data,item)
            print "sage: ", sage

            non_empty_subject = dbConnector().dbGetSubject(data,item)
            print "subject non empty nor saged: ", non_empty_subject

            non_empty_name = dbConnector().dbGetName(data,item)
            print "namefags: ", non_empty_name

            timez = dbConnector().dbGetTime(data,item)
            for key,value in timez.iteritems():
                if value !=0:
                    print "Hour: ",key,"Posts: ",value
            #print timez

            datez = dbConnector().dbGetDate(data,item)
            for key,value in datez.iteritems():
                if value !=0:
                    print "Day: ",key,"Posts: ",value
            #print datez

            nodess = dbConnector().dbGetNode(data,item)
            nodes = {}
            for item in nodess:
                node = str(item).strip("',()").split("@")[1]
                if node not in nodes:
                    nodes[node] = 1
                else:
                    nodes[node] += 1
            total = 0
            for item in nodes.items():
                total += item[1]

            for item in sorted(nodes.items(), key=operator.itemgetter(1),reverse=True):
                print("%s:%i (%i%s)") %(item[0],item[1],(item[1]*100/total),"%")

            print '\n'
        else:
            pass

    except MySQLdb.ProgrammingError:
        pass
print "Active boards this month: ", active
