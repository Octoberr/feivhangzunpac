import requests
from bs4 import BeautifulSoup
from time import sleep
from retrying import retry
import json
import re
import pymongo
import datetime

from feichangzun import config


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'}
feichangzun = 'http://www.variflight.com'
allUrl = "http://www.variflight.com/sitemap.html?AE71649A58c77="
pausetime = 30000


class HANDL:
    def __init__(self, flight, flightlink):
        self.flight = flight
        self.flightlink = flightlink


class FCZPAC:
    @retry(wait_fixed=pausetime)
    def getoneipaddress(self):
        try:
            r = requests.get('http://127.0.0.1:5000/get')
            proxy = BeautifulSoup(r.text, "lxml").get_text()
            ip = 'http://' + proxy
            proxies = {
                "http": ip,
                "https": ip
            }
            print(proxies)
        except:
            print("no more ip address please waite {} seconds".format(pausetime/1000))
            raise IOError("no more ip address please waite.")
        return proxies

    def getquerydate(self, aircarfNo):
        client = pymongo.MongoClient(host=config.mongo_config['host'], port=config.mongo_config['port'])
        db = client.swmdb
        eagleyedates = db.runtest
        cursor = eagleyedates.find({"Info.fno": aircarfNo}, {"Info.Date": 1}).sort("Info.Date", -1).limit(1)
        for el in cursor:
            havedate = datetime.datetime.strptime(el["Info"]['Date'], "%Y-%m-%dT%H:%M:%S").date()
            return havedate

    def insertintomongo(self, flightdata):
        client = pymongo.MongoClient(host=config.mongo_config['host'], port=config.mongo_config['port'])
        db = client.swmdb
        eagleyedates = db.runtest
        eagleyedates.insert(flightdata)
        print(datetime.datetime.now(), 'insert mongodb success')

    @retry
    def getchuanghanglist(self):
        # ips = self.getoneipaddress()
        # 发送请求
        startHtml = requests.get(allUrl, headers=headers)
        sleep(1)
        Soup = BeautifulSoup(startHtml.text, 'lxml')
        allA = Soup.find('div', class_='f_content').find_all('a')
        flight = []
        flightlink = []
        for i in range(1, len(allA)):
            if '3U' in allA[i].get_text():
                flight.append(allA[i].get_text())
                flightlink.append(allA[i].get('href'))
        return HANDL(flight, flightlink)

    @retry
    def getListData(self, flightlink, flightstr):
        # ips = self.getoneipaddress()
        today = datetime.datetime.now().date()
        allflightLink = []
        for i in range(len(flightlink)):
            flightlist = []
            alreadydate = self.getquerydate(flightstr[i])
            print("查询结果", alreadydate)
            if alreadydate is not None:
                looptimes = (today + datetime.timedelta(days=7) - alreadydate).days
                tmpurl = (feichangzun + flightlink[i]).split('=')[0]
                for n in range(1, looptimes+1):
                    querydate = alreadydate + datetime.timedelta(days=n)
                    url = tmpurl + '&fdate={}'.format(querydate.strftime("%Y%m%d"))
                    # 发送请求
                    listHtml = requests.get(url, headers=headers)
                    sleep(1)
                    listSoup = BeautifulSoup(listHtml.text, 'lxml')
                    listUrl = listSoup.find('div', class_='fly_list')
                    if listUrl is not None:
                        listhref = listUrl.find('div', class_='li_box').find_all('a')
                        for link in listhref:
                            if '/schedule' in link.get('href'):
                                print('find a schedule link')
                                flightlist.append(link.get('href'))
                    else:
                        break
                    allflightLink.append(flightlist)
            elif alreadydate is None:
                # print("当查询结果为空的时候")
                tmpurl2 = (feichangzun + flightlink[i]).split('=')[0]
                # print("空link", tmpurl2)
                for n in range(1, 7):
                    querydate2 = today + datetime.timedelta(days=n)
                    url2 = tmpurl2 + '&fdate={}'.format(querydate2.strftime("%Y%m%d"))
                    # print("空查询link", url2)
                    # 发送请求
                    listHtml2 = requests.get(url2, headers=headers)
                    sleep(1)
                    listSoup2 = BeautifulSoup(listHtml2.text, 'lxml')
                    listUrl2 = listSoup2.find('div', class_='fly_list')
                    if listUrl2 is not None:
                        listhref2 = listUrl2.find('div', class_='li_box').find_all('a')
                        for link2 in listhref2:
                            if '/schedule' in link2.get('href'):
                                print('当查询为空时find a schedule link')
                                flightlist.append(link2.get('href'))
                    else:
                        break
                    allflightLink.append(flightlist)
        return allflightLink                  # [[一个航班],[]]

    @retry
    def getaflightinfo(self, aflight):     # 传进来一个航班的[link],获取到这个航班的信息
        # ips = self.getoneipaddress()
        flightinfolist = []
        for el in aflight:
            flightinfo = {}
            url = feichangzun + el
            # 发送请求
            listHtml = requests.get(url, headers=headers)
            sleep(1)
            listSoup = BeautifulSoup(listHtml.text, 'lxml')
            qfcity = listSoup.find('div', class_='cir_l curr').get_text().strip()
            ddcity = listSoup.find('div', class_='cir_r').get_text().strip()
            code = el.split('/')[2].split('-')
            qfcitycode = code[0]
            ddcitycode = code[1]
            fno = code[2].split('.')[0]
            city = listSoup.find_all('div', class_='fly_mian')
            qfsimple = city[0].find('h2').get('title').split(qfcity)[1]
            if 'T' in qfsimple:
                qfTerminal = 'T' + qfsimple.split('T')[1]
            else:
                qfTerminal = ""
            qf = qfcity + " " + qfsimple
            ddsimple = city[len(city)-1].find('h2').get('title').split(ddcity)[1]
            if 'T' in ddsimple:
                ddTerminal = 'T' + ddsimple.split('T')[1]
            else:
                ddTerminal = ""
            dd = ddcity + " " + ddsimple
            qftimestr = city[0].find('span', class_='date').get_text().strip()
            qfdate = re.compile('\d{4}[-/]\d{2}[-/]\d{2}').findall(qftimestr)
            qftime = qfdate[0] + "T" + re.compile('\d{2}[:/]\d{2}').findall(qftimestr)[0]
            ddtimestr = city[len(city)-1].find('span', class_='date').get_text().strip()
            dddate = re.compile('\d{4}[-/]\d{2}[-/]\d{2}').findall(ddtimestr)
            ddtime = dddate[0] + "T" + re.compile('\d{2}[:/]\d{2}').findall(ddtimestr)[0]
            state = listSoup.find('div', class_='reg').get_text()
            if state == '计划':
                stateid = 1
            else:
                stateid = 0
            flightinfo['qf'] = qf
            flightinfo['qf_city'] = qfcity
            flightinfo['qf_citycode'] = qfcitycode
            flightinfo['qf_simple'] = qfsimple
            flightinfo['dd'] = dd
            flightinfo['dd_simple'] = ddsimple
            flightinfo['dd_city'] = ddcity
            flightinfo['dd_citycode'] = ddcitycode
            flightinfo['qfTerminal'] = qfTerminal
            flightinfo['ddTerminal'] = ddTerminal
            flightinfo['jhqftime_full'] = qftime
            flightinfo['sjqftime_full'] = None
            flightinfo['jhddtime_full'] = ddtime
            flightinfo['sjddtime_full'] = None
            flightinfo['State'] = state
            flightinfo['stateid'] = stateid
            flightinfo['djk'] = '--'
            flightinfo['zjgt'] = '--'
            flightinfo['xlzp'] = '--'
            flightinfo['date'] = qfdate[0]
            flightinfo['fno'] = fno
            print('get a schedule from a schedule list')
            flightinfolist.append(flightinfo)
        return flightinfolist

    def start(self):
        flightdata = self.getchuanghanglist()
        flightlink = flightdata.flightlink
        flightstr = flightdata.flight
        listLink = self.getListData(flightlink, flightstr)
        for flight in listLink:
            flightdic = {}
            info = {}
            flightinfo = self.getaflightinfo(flight)
            if len(flightinfo) == 1:
                init = 0
                info['from'] = flightinfo[init]['qf']
                info['to'] = flightinfo[init]['dd']
                info['from_simple'] = flightinfo[init]['qf_simple']
                info['to_simple'] = flightinfo[init]['dd_simple']
                info['FromTerminal'] = flightinfo[init]['qfTerminal']
                info['ToTerminal'] = flightinfo[init]['ddTerminal']
                info['from_city'] = flightinfo[init]['qf_city']
                info['to_city'] = flightinfo[init]['dd_city']
                info['from_code'] = flightinfo[init]['qf_citycode']
                info['to_code'] = flightinfo[init]['dd_citycode']
                info['fno'] = flightinfo[init]['fno']
                info['Company'] = '3U'
                info['Date'] = flightinfo[init]['date']+"T00:00:00"
                info['zql'] = ""
            else:
                init = 1
                info['from'] = flightinfo[init]['qf']
                info['to'] = flightinfo[init]['dd']
                info['from_simple'] = flightinfo[init]['qf_simple']
                info['to_simple'] = flightinfo[init]['dd_simple']
                info['FromTerminal'] = flightinfo[init]['qfTerminal']
                info['ToTerminal'] = flightinfo[init]['ddTerminal']
                info['from_city'] = flightinfo[init]['qf_city']
                info['to_city'] = flightinfo[init]['dd_city']
                info['from_code'] = flightinfo[init]['qf_citycode']
                info['to_code'] = flightinfo[init]['dd_citycode']
                info['fno'] = flightinfo[init]['fno']
                info['Company'] = '3U'
                info['Date'] = flightinfo[init]['date']+"T00:00:00"
                info['zql'] = ""
            flightdic['Info'] = info
            flightdic['List'] = flightinfo
        # jsondatar = json.dumps(flightdic, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        # with open('flight.json', 'w') as outfile:
        #     json.dump(flightdic, outfile)
            self.insertintomongo(flightdic)

if __name__ == '__main__':
    fp = FCZPAC()
    fp.start()
    # flightdata = fp.getchuanghanglist()
    # flightlink = flightdata.flightlink
    # fp.getListData(flightlink)
    # fp.getaflightinfo(['/schedule/SZX-CTU-3U3033.html?AE71649A58c77='])