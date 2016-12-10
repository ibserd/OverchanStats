### Overchan Scrapper. Uses 2hu.ch by default and stores posts in MySQL DB.
### First it goes to 2hu.ch/board.html and scraps all exisiting boards. It takes
### this data and for every board creates a MySQL table. Then it goes though ukko
### pages and grabs thread urls. It's 10 pages by default, ukko on oniichan can
### go back to 100 pages. With urls, it goes to every thread and using BS pass the
### content to DB.

import requests ## Handling url requests
import MySQLdb ## mysql db connector
from bs4 import BeautifulSoup ## parser

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

    def dbCreateTable(self,board_name):
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        command = "CREATE TABLE %s.%s(msgID VARCHAR(100) PRIMARY KEY,OP VARCHAR(1),Board VARCHAR(100),ReplyNumber INT,ID VARCHAR(100),postID VARCHAR(100),Author VARCHAR(100),Tripcode VARCHAR(100),Data VARCHAR(100),Timex VARCHAR(100),Subject VARCHAR(100),Origin VARCHAR(100),Message VARCHAR(5000))" % (self.db_name,board_name)
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

def board_list():
    boards_url = 'http://2hu-ch.org/boards.html'
    req = requests.get(boards_url)
    soup = BeautifulSoup(req.content,'html.parser')
    boards = []
    for item in soup.find_all('td'):
        try:
            boards.append(str(item.find('a').text))
        except AttributeError:
            pass
    return boards

def ukko_scrapper():
    ukko_urls = []
    for n in range(11): ## Change to scrap thru more than 10 pages
        ukko_urls.append('ukko-%d.html' % n)
    req = requests.get('http://2hu-ch.org/ukko.html')
    soup = BeautifulSoup(req.content,'html.parser')
    active_threads = []
    for page in ukko_urls: ## go thru all ukko pages
        req = requests.get('http://2hu-ch.org/%s' % page)
        soup = BeautifulSoup(req.content,'html.parser')
        n = 0
        while n <= 9: ## retrive all 10 topics on the page and store em
            active_threads.append(soup.find_all('div',{"class":"thread"})[n]['id'])
            n+=1
    return active_threads

def thread(urls):
    stats = []
    threads_new_count = 0
    threads_skipped_count = 0
    posts_new_count = 0
    posts_skipped_count = 0
    errors_count = 0

    for url in urls:
        try:                     ## Is thread alive? Not banned and propagated
            url = str('http://2hu-ch.org/' + url.replace('_','-') + '.html')
            req = requests.get(url)
            soup = BeautifulSoup(req.content,'html.parser')

            is_op = 'Y'
            board = str(soup.find('div',{"class":"post op"})['data-newsgroup'])
            iD = str(soup.find('div',{'class':'post op'})['id'])
            try:
                origin = str(soup.find('div',{"class":"post op"})['data-origin'])
            except:
                origin = "__NOTREADABLE__"
                print url
                print "origin fucked, check it"
            author = str(soup.find('span',{"class":"name"}).text)
            msgid = str(soup.find('span',{"class":"msgid"}).text).strip('<>')
            raw_data = str(soup.find('time')['datetime'])
            data = raw_data.split('T')[0]
            timex = raw_data.split('T')[1].split('-')[0]
            if "Z" in timex: # For some reason sometimes Z is added
                timex = timex.strip("Z")
            subject = str(soup.find('span',{"class":"subject"}).text)
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
                DBconnector().dbInsert(board.replace('.','_'),is_op,board,origin,author,msgid,data,timex,subject,message,tripcode,replynumber,iD,postid)
                threads_new_count += 1
            except MySQLdb.IntegrityError: ## If record is already in the DB
                threads_skipped_count += 1

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
                    timex = raw_data.split('T')[1].split('-')[0]
                    if "Z" in timex: # For some reason sometimes Z is added
                        timex = timex.strip("Z")
                    subject = str(item.find('span',{"class":"subject"}).text)
                    message = str(item.find('div',{'class':'post_body'}).text.encode('ascii','ignore'))
                    postid = str(item.find('a',{'class':'postno'}).text.strip('>'))
                    try:
                        tripcode = str(soup.find('span',{"class":"tripcode"}).text)
                    except AttributeError: ## Tripcode is not obligatory, if none .text will raise NoneType
                        tripcode = ''
                    try:
                        DBconnector().dbInsert(board.replace('.','_'),is_op,board,origin,author,msgid,data,timex,subject,message,tripcode,replynumber,iD,postid)
                        posts_new_count += 1
                    except MySQLdb.IntegrityError: ## If record is already in the DB
                        posts_skipped_count += 1
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

############# ACTUAL SCRIPT ###############

board_list = board_list() ## Get the list of all boards.

for item in board_list:
    try: #Create a new table for each board
        DBconnector().dbCreateTable(item.replace('.','_')) ## Mysql doesnt like dots in names
    except MySQLdb.OperationalError: ## If table already exists.
        pass

print ('Done with tables, moving to threads')

active_threads = ukko_scrapper() ## Get threads from ukko
print ('Threads loaded!\n Processing...')

stats = thread(active_threads)

print('%i Errors loading threads') % stats[4]
print('==============')
print('Added %i new threads and skipped %i already existing') %(stats[0],stats[1])
print('Added %i new posts and skipped %i already existing') %(stats[2],stats[3])
