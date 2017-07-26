import pymongo
import datetime
from feichangzun import config

# def days_between(d1, d2):
#     d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
#     d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
#     return abs((d2 - d1).days)
datetimes = datetime.datetime.now().date()
str = "2017-07-28T11:05:22"
dateTime = datetime.datetime.strptime(str, "%Y-%m-%dT%H:%M:%S").date()
startDate = datetimes + datetime.timedelta(days=5)
# i = days_between(startDate, datetimes)
i = (dateTime - datetimes).days
print(datetimes)
print(startDate)
print(i, type(i))

def getquerydata(aircarfNo):
    print(aircarfNo, type(aircarfNo))
    client = pymongo.MongoClient(host=config.mongo_config['host'], port=config.mongo_config['port'])
    db = client.swmdb
    eagleyedates = db.runtest
    # cursor = eagleyedates.find({"Info": {"fno": aircarfNo}}, {"Date": 1, "_id": 0}).sort(["Date", -1]).limit(1)
    # cursor = eagleyedates.find({"Info.fno": aircarfNo}, {"Info.Date": 1, "_id": 0}).sort(["Info.Date", -1]).limit(1)
    cursor = eagleyedates.find({"Info.fno": aircarfNo}).sort("Info.Date", -1).limit(1)
    for el in cursor:
        havedate = datetime.datetime.strptime(el["Info"]['Date'], "%Y-%m-%dT%H:%M:%S").date()
        return havedate

querdate = getquerydata('3U20031')
print(querdate)