import pymongo
import datetime
import json

#client = pymongo.MongoClient('mongodb://localhost:27017')
client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
db = client.testdata
coll = db.messages


def write(message):
    #print(message)
    coll.insert_one(message)
    #print(res)

def read( username1, username2):
    mydoc1 = coll.find({'from': username1})
    mydoc2 = coll.find({'from': username2})
    mydoc = []
    for x in mydoc2:
         mydoc.append(x)
    for x in mydoc1:
        mydoc.append(x)

    mydoc.sort(key=lambda x : x['timestamp'])
    for x in mydoc:
        print(  x['from'] + ' > '  +x['to']+ ' : ' + x['timestamp'] + '  :::: ' + x['content'])