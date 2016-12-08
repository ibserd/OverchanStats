import requests
import MySQLdb

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

    def createColumns(self,node):
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        command = "ALTER TABLE status ADD %s VARCHAR(10); " % (node)
        cur.execute(command)
        dbconnect.commit()
        dbconnect.close()

    def getColumns(self):
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        command = "SHOW COLUMNS FROM status;"
        cur.execute(command)
        result = cur.fetchall()
        dbconnect.close()
        cleaned =[]
        for item in result:
            cleaned.append(item[0])

        columns = ",".join(cleaned)

        return columns

    def insertValues(self,*args):
        columns = self.getColumns()
        values =  ",".join(args[0:len(args)])
        dbconnect = MySQLdb.connect(host=self.host,db=self.db_name,user=self.user,passwd=self.passwd)
        cur = dbconnect.cursor()
        command = "INSERT INTO status(%s) VALUES (now(),%s) ; " % (columns,values)
        cur.execute(command)
        dbconnect.commit()
        dbconnect.close()


nodes = ["https://2hu-ch.org","http://nsfl.ga","http://gchan.xyz","http://ucavviu7wl6azuw7.onion","http://oniichanylo2tsi4.onion","http://ev7fnjzjdbtu3miq.onion","http://f2bksxtwzmst2dhx.onion","http://yqfbo7ghmwzotrml.onion","http://emvykufthqjgudpldo7tj26j57z4q2b6at6vmrfo6jxnvozmultq.b32.i2p","http://g7c54d4b7yva4ktpbaabqeu2yx6axalh4gevb44afpbwm23xuuya.b32.i2p"]

def getStatus(nodes):
    node_status = {}
    for node in nodes:
        try:
            cleared_node = "".join(node.split("//")[1:]).replace(".","_").replace("-","_")
            DBconnector().createColumns(cleared_node)
        except MySQLdb.OperationalError:
            pass

        if node.split(".")[1] == "onion":
            proxy = {"http":"socks5://localhost:9050"}
            try:
                req = requests.head(node,proxies=proxy)
                if req.status_code == 200:
                    node_status[node] = "'OK'"
                else:
                    node_status[node] = "'FAIL'"
            except requests.ConnectionError:
                node_status[node] = "'DEAD'"

        elif node.split(".")[-1] == "i2p":
            proxy = {"http":"http://localhost:4444"}
            try:
                req = requests.head(node,proxies=proxy)
                if req.status_code == 200:
                    node_status[node] = "'OK'"
                else:
                    node_status[node] = "'FAIL'"
            except requests.ConnectionError:
                node_status[node] = "'DEAD'"
        else:
            try:
                req = requests.head(node)
                if req.status_code == 200:
                    node_status[node] = "'OK'"
                else:
                    node_status[node] = "'FAIL'"
            except requests.ConnectionError:
                node_status[node] = "'DEAD'"

    DBconnector().insertValues(node_status["https://2hu-ch.org"],node_status["http://nsfl.ga"],node_status["http://gchan.xyz"],node_status["http://ucavviu7wl6azuw7.onion"],node_status["http://oniichanylo2tsi4.onion"],node_status["http://ev7fnjzjdbtu3miq.onion"],node_status["http://f2bksxtwzmst2dhx.onion"],node_status["http://yqfbo7ghmwzotrml.onion"],node_status["http://emvykufthqjgudpldo7tj26j57z4q2b6at6vmrfo6jxnvozmultq.b32.i2p"],node_status["http://g7c54d4b7yva4ktpbaabqeu2yx6axalh4gevb44afpbwm23xuuya.b32.i2p"])


if __name__ == "__main__":
    getStatus(nodes)
