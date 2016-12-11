import MySQLdb
year = "2016"
db = MySQLdb.connect(host=,user=,passwd=,db=)
cur = db.cursor()
for item in range(1,11):
    if item < 10:
        item = "0" + str(item)
    table = "%s_%s" % (year,item)
    for item2 in range(1,32):
        if item2 < 10:
            item2 = "0" + str(item2)

        data = "%s-%s-%s" %(year,item,item2)
        command = "SELECT * FROM %s WHERE Data LIKE %r" %(table,data)
        cur.execute(command)
        posts = cur.rowcount
        if posts == 0:
            pass
        else:
            command = "INSERT INTO posts(Data,Posts) VALUES(%r,%r)" % (data,posts)
            cur.execute(command)
            cur.commit()

db.close()
