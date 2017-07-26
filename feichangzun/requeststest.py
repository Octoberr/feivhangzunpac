from retrying import retry
import requests
from bs4 import BeautifulSoup
pausetime = 30000
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'}
feichangzun = 'http://www.variflight.com'
allUrl = "http://www.variflight.com/sitemap.html?AE71649A58c77="

# @retry(wait_fixed=pausetime)
# def getoneipaddress():
#     try:
#         r = requests.get('http://127.0.0.1:5000/get')
#         proxy = BeautifulSoup(r.text, "lxml").get_text()
#     except:
#         print("no more ip address please waite {} seconds".format(pausetime / 1000))
#         raise IOError("no more ip address please waite {} seconds")
#     return proxy
#
#
# ip = 'http://' + getoneipaddress()
# proxies = {
#     "http": ip,
#     "https": ip
# }
# print(proxies)
startHtml = requests.get('http://www.goubanjia.com/free/gngn/index.shtml', headers=headers)
Soup = BeautifulSoup(startHtml.text, 'lxml')
a = Soup.find('div', id='list')
b = a.find_all('tr')
for element in b:
    text = element.find('td', class_='ip')
    if text is not None:
        print(text.get_text())

