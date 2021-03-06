import requests
import pymysql
import datetime
import time
import os
import simplejson as json

crontable = []
outputs = []


def getdbconfig():
    with open('plugins/teamslackbot/dbconfig.conf') as data_file:
        dbconf = json.load(data_file)
        dbinfo = {}
        dbinfo['host'] = dbconf['Host']
        dbinfo['user'] = dbconf['User']
        dbinfo['passwd'] = dbconf['Password']
        dbinfo['dbname'] = dbconf['DB Name']
        dbinfo['slacktoken'] = dbconf['Slack Token']
        print(dbinfo['slacktoken'])
    return dbinfo

def getrealname(s):
    info = getdbconfig()
    r = requests.get(info['slacktoken'])
    user = s
    userdump = json.loads(r.content)
    for member in userdump['members']:
        if member['id'] == user:
            membername = member['real_name']
            return membername

def process_message(data):
     if data['text'].startswith("!imamaybe") or data['text'].startswith("!immaybe"):
        try:
            info = getdbconfig()
            db = pymysql.connect(info['host'], info['user'], info['passwd'], info['dbname'])
            cursor = db.cursor()
            uid = ""
            whosout = ""
            whosin = ""
            whosamaybe = ""
            username = str(data['user'])
            realname = getrealname(username)
            print(realname)
        except Exception as e:
            print(e)
        try:
            sql = "SELECT * FROM games WHERE datetime > '%d' ORDER BY datetime ASC" % (time.time())
            cursor.execute(sql)
            results = cursor.fetchall()
            results = results[0]
            uid = results[4]
            whosin = results[5]
            if whosin == None:
                whosin = ""
            whosout = results[8]
            if whosout == None:
                whosout = ""
            whosamaybe = results[9]
            if whosamaybe == None:
                whosamaybe = ""
            print(whosout)
        except Exception as e:
            print(e)
            outputs.append([data['channel'], "Something went wrong"])
            #quit()
        try:
            if realname in str(whosamaybe):
                outputs.append([data['channel'], '{} was already marked as maybe'.format(realname)])
            else:
                whosamaybe = whosamaybe+realname+"\n"
                sql = "UPDATE games SET whosamaybe = '%s' WHERE uid = '%s'" % (whosamaybe, uid)
                cursor.execute(sql)
                db.commit()
                outputs.append([data['channel'], '{} is a maybe :confused:'.format(realname)])
                
        except Exception as e:
            print(e)        
        try:
            if realname in str(whosin):
                replacename = str(realname+"\n")
                whosin = whosin.replace(replacename, "")
                sql = "UPDATE games SET whosin = '%s' WHERE uid = '%s'" % (whosin, uid)
                cursor.execute(sql)
                db.commit()

        except Exception as e:
            print(e)
        try:
            if realname in str(whosout):
                replacename = str(realname+"\n")
                whosout = whosout.replace(replacename, "")
                sql = "UPDATE games SET whosout = '%s' WHERE uid = '%s'" % (whosout, uid)
                cursor.execute(sql)
                db.commit()
        except Exception as e:
            print(e)
        db.close()
