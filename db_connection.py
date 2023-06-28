# ~ import pymongo
import datetime
import json
from montydb.types.objectid import ObjectId
from montydb import set_storage, MontyClient


coll = None

def initDB(user):
    global coll
    # ~ client = pymongo.MongoClient('localhost', 27017)
    set_storage("db",  # dir path for database to live on disk, default is {cwd}
        storage="flatfile",     # storage name, default "flatfile"
        mongo_version="4.0",    # try matching behavior with this mongodb version
        use_bson=False)         # default None, and will import pymongo's bson if None or True
    client = MontyClient("db")
    coll = client[user]['messages']


def write(from_user, to_user, timestamp, content, status='sending'):
    db_json = {
        'from': from_user,
        'to': to_user,
        'timestamp': timestamp,
        'content': content,
        'status': status,
    }
    return coll.insert_one(db_json).inserted_id


def shortTimestamp(timestamp):
    date = datetime.datetime.fromisoformat(timestamp)
    date = date.replace(tzinfo=datetime.timezone.utc)
    return date.astimezone().strftime("%y-%m-%d %H:%M")


def read(username1, username2):
    mydoc1 = coll.find({'from': username1, 'to': username2})
    #coll.update_many(  {'from': username2, 'to': username1}, {'$set': {'status': 'received'}})
    mydoc2 = coll.find({'from': username2, 'to': username1})

    mydoc = []
    for x in mydoc2:
        mydoc.append(x)
    for x in mydoc1:
        mydoc.append(x)

    mydoc.sort(key=lambda x: x['timestamp'])
    for x in mydoc:
        print(f"[({x['status']}) {shortTimestamp(x['timestamp'])} {x['from']}]: {x['content']}")


def changeStatus(local_id, new_status):
    # ~ print('statusss')
    message_id = ObjectId(local_id)
    message = coll.find_one({'_id': message_id})
    if message['status'] == 'sending' or (message['status'] == 'sent' and new_status == 'received'):
        message = coll.update_one({'_id': message_id}, {'$set': {'status': new_status}})

