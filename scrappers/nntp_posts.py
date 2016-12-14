import requests ## Handling url requests
import MySQLdb ## mysql db connector
from bs4 import BeautifulSoup ## parser
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

    def dbCreateTable(self,table):
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        command = "CREATE TABLE %s.%s(msgID VARCHAR(100) PRIMARY KEY,OP VARCHAR(1),Board VARCHAR(100),ReplyNumber INT,ID VARCHAR(100),postID VARCHAR(100),Author VARCHAR(100),Tripcode VARCHAR(100),Data VARCHAR(100),Timex VARCHAR(100),Subject VARCHAR(100),Origin VARCHAR(100),Message VARCHAR(5000))" % (self.db_name,table)
        cur.execute(command)
        dbconnect.commit()
        dbconnect.close()

    def dbInsert(self,table,OP,Board,Origin,Author,Msgid,Data,Timex,Subject,Message,Tripcode,ReplyNumber,ID,postID):
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        command = "INSERT INTO %s (OP,Board,Origin,Author,msgID,Data,Timex,Subject,Message,Tripcode,ReplyNumber,ID,postID) VALUES (%r,%r,%r,%r,%r,%r,%r,%r,%r,%r,%r,%r,%r)" % (table,OP,Board,Origin,Author,Msgid,Data,Timex,Subject,Message,Tripcode,ReplyNumber,ID,postID)
        cur.execute(command)
        dbconnect.commit()
        dbconnect.close()

    def dbListBoards(self):
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        command = "SELECT * FROM boards"
        cur.execute(command)
        boards = cur.fetchall()
        dbconnect.close()
        boards_list = []
        for item in list(boards):
            boards_list.append(str(item).strip("(),'"))
        return boards_list

    def dbInsertBoard(self,board):
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        command = "INSERT INTO boards(board) VALUES (%r)" % board
        cur.execute(command)
        dbconnect.commit()
        dbconnect.close()

class Scrapper(object):
    def __init__(self):
        self.node = 'http://2hu-ch.org/'

    def ukko_scrapper(self):
        ukko_urls = []
        for n in range(11): ## Change to scrap thru more than 10 pages
            ukko_urls.append('ukko-%d.html' % n)
        req = requests.get(self.node + 'ukko.html')
        soup = BeautifulSoup(req.content,'html.parser')
        active_threads = []
        for page in ukko_urls: ## go thru all ukko pages
            req = requests.get(self.node + page)
            soup = BeautifulSoup(req.content,'html.parser')
            n = 0
            while n <= 9: ## retrive all 10 topics on the page and store em
                active_threads.append(soup.find_all('div',{"class":"thread"})[n]['id'])
                n+=1
        return active_threads

    def thread(self,urls):
        stats = []
        threads_new_count = 0
        threads_skipped_count = 0
        posts_new_count = 0
        posts_skipped_count = 0
        errors_count = 0

        for url in urls:
            try:                     ## Is thread alive?
                url = str(self.node + url.replace('_','-') + '.html')
                req = requests.get(url)
                soup = BeautifulSoup(req.content,'html.parser')

                is_op = 'Y'
                board = str(soup.find('div',{"class":"post op"})['data-newsgroup'])
                iD = str(soup.find('div',{'class':'post op'})['id'])
                try:  #In old posts there is no origin
                    origin = str(soup.find('div',{"class":"post op"})['data-origin'])
                except:
                    origin = "__NOTREADABLE__"
                author = str(soup.find('span',{"class":"name"}).text)
                msgid = str(soup.find('span',{"class":"msgid"}).text).strip('<>')
                raw_data = str(soup.find('time')['datetime'])
                data = raw_data.split('T')[0]
                table = data[0:7].replace("-","_")
                timex = raw_data.split('T')[1].split('-')[0]
                if "Z" in timex: # For some reason sometimes Z is added
                    timex = timex.strip("Z")
                subject = soup.find('span',{"class":"subject"}).text.encode('utf-8')
                try:
                    message = str(soup.find('div',{'class':'post_body'}).text.encode('ascii','ignore'))
                except:
                    message = '__NOTREADABLE__'
                postid = str(soup.find('a',{'class':'postno'}).text.strip('>'))
                replynumber = 0
                try:
                    tripcode = str(soup.find('span',{"class":"tripcode"}).text)
                except AttributeError: ## Tripcode is not obligatory, if none .text will raise NoneType
                    tripcode = ''

                try:
                    DBconnector().dbInsert(table,is_op,board,origin,author,msgid,data,timex,subject,message,tripcode,replynumber,iD,postid)
                    threads_new_count += 1
                except (MySQLdb.IntegrityError,MySQLdb.ProgrammingError): ## If record is already in the DB or the date is earlier than 01.2015
                    threads_skipped_count += 1

                try:
                    DBconnector().dbInsertBoard(board)
                except MySQLdb.IntegrityError:
                    pass

                try: ## If thread has any replies
                    for item in soup.find_all('div',{'class':'post reply'}):
                        replynumber += 1
                        is_op = 'N'
                        try:
                            origin = str(item.contents[1].find('img')['title'].replace('posted from ',''))
                        except:
                            origin = "__NOTREADABLE__"
                        author = str(item.find('span',{"class":"name"}).text)
                        msgid = str(item.find('span',{"class":"msgid"}).text.strip('<>'))
                        raw_data = str(item.find('time')['datetime'])
                        data = raw_data.split('T')[0]
                        table = data[0:7].replace("-","_")
                        timex = raw_data.split('T')[1].split('-')[0]
                        if "Z" in timex: # For some reason sometimes Z is added
                            timex = timex.strip("Z")
                        subject = item.find('span',{"class":"subject"}).text.encode('utf-8')
                        message = str(item.find('div',{'class':'post_body'}).text.encode('ascii','ignore'))
                        postid = str(item.find('a',{'class':'postno'}).text.strip('>'))
                        try:
                            tripcode = str(soup.find('span',{"class":"tripcode"}).text)
                        except AttributeError: ## Tripcode is not obligatory, if none .text will raise NoneType
                            tripcode = ''
                        try:
                            DBconnector().dbInsert(table,is_op,board,origin,author,msgid,data,timex,subject,message,tripcode,replynumber,iD,postid)
                            posts_new_count += 1
                        except (MySQLdb.IntegrityError,MySQLdb.ProgrammingError): ## If record is already in the DB or the date is earlier than 01.2015
                            posts_skipped_count += 1

                        try:
                            DBconnector().dbInsertBoard(board)
                        except MySQLdb.IntegrityError:
                            pass
                except:
                    pass
            except TypeError: ## Thread cant be scrapped :(
                errors_count += 1
        stats.append(threads_new_count)
        stats.append(threads_skipped_count)
        stats.append(posts_new_count)
        stats.append(posts_skipped_count)
        stats.append(errors_count)
        return stats

#=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=#

now_table = datetime.datetime.now()
table = "%d_%d" %(now_table.year,now_table.month)

try: #Create a new table for current month
    DBconnector().dbCreateTable(table)
    print "Created new table"
except MySQLdb.OperationalError: ## If table already exists
    print "All tables up to date"

active_threads = Scrapper().ukko_scrapper()
print "Threads loaded, processing..."

stats = Scrapper().thread(active_threads)

print('%i Errors loading threads') % stats[4]
print('==============')
print('Added %i new threads and skipped %i already existing') %(stats[0],stats[1])
print('Added %i new posts and skipped %i already existing') %(stats[2],stats[3])
