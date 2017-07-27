from retrying import retry
import requests
from bs4 import BeautifulSoup
import json
pausetime = 30000
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'}
feichangzun = 'http://www.variflight.com'
allUrl = "http://www.variflight.com/sitemap.html?AE71649A58c77="


# @retry(wait_fixed=pausetime)
# def getoneipaddress():
#     try:
#         r = requests.get('http://127.0.0.1:5010/get/')
#         proxy = BeautifulSoup(r.text, "lxml").get_text()
#         print(proxy)
#     except:
#         print("no more ip address please waite {} seconds".format(pausetime / 1000))
#         raise IOError("no more ip address please waite {} seconds")
#     return proxy
#
# r = requests.get('http://192.168.0.131:5010/delete/?proxy=123.163.68.119:808')
# proxy = BeautifulSoup(r.text, "lxml").get_text()
# print(proxy)

# ip = 'http://' + getoneipaddress()
# print(ip, type(ip))
# proxies = {
#     "http": ip
# }
# # http://192.168.0.131:5010/delete/?proxy=37.187.178.194:808

# # ConnectionRefusedError
anproxies ={
    "http": "http://179.187.182.243:8080",
    "https": "http://179.187.182.243:8080",
}
try:
    startHtml = requests.get('http://www.variflight.com/flight/fnum/3U5034.html?AE71649A58c77= ', headers=headers, proxies=anproxies)
    proxy = BeautifulSoup(startHtml.text, "lxml").get_text()
    print(proxy)
except:
    print("找到一个错误")

# Soup = BeautifulSoup(startHtml.text, 'lxml')
# print(Soup)
# """
# <html><body><p>{"msg":"IP blocked"}</p></body></html>
# {"msg":"IP blocked"}
# IP blocked <class 'str'>
# """


# def digui(n):
#     sum = 0
#     if n <= 0:
#         return 1
#     else:
#         return n * digui(n - 1)
#
#
# print(digui(5))