import re
import time
import random
import requests
import pandas as pd
from retrying import retry
from selenium import webdriver
from bs4 import BeautifulSoup
import pymysql
import urllib

# 请求头池
user_agent = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; "
    ".NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR "
    "2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR "
    "3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; "
    ".NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR "
    "3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 ("
    "Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 "
    "Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 "
    "Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 "
    "LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR "
    "3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 "
    "LBBROWSER",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR "
    "3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR "
    "3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR "
    "3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 "
    "Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 "
    "Safari/537.36",
]

# @retry(stop_max_attempt_number=8)
def getHtml(url):
    try:
        random_user_agent = random.choice(user_agent)  # 从user_agent池中随机生成headers
        response = requests.get(url, headers={'user-agent': random_user_agent})
        response.encoding = 'utf-8'
        if response.status_code == 200:
            html = response.content.decode()
            return html
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)


# 第一步，先把简介信息采集下来，形成一个数据库 先做这个--
baseUrl = "http://www.birder.cn"
# driver = webdriver.Firefox()

# 数据库信息
DataBase  = "bird"
Sqlusername = "remoteroot"
Sqlpw = "123456"
port = 3306

# 连接数据库
connection = pymysql.connect(user=Sqlusername, password=Sqlpw,
                             database=DataBase, charset="utf8", port=port, db='python')

def getRecord(url):

    html = getHtml(url)
    #
    # 存在去重问题 虽然在不同时间但是需要 进行查重 所以仍然需要对数据表设定一个主键【时间戳 -- 后面可以转化成只保留日期的字段】
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        info = soup.find_all('div', attrs={'class': 'info_t'})
        id = soup.find('div', attrs={'class': 'info'}).text.strip()

        detail = {}

        detail['id'] = "".join(list(filter(str.isdigit, id)))
        print(detail['id'])
        # content = content[:shiId-2] # 需要验证是否会有问题
        time = info[0].string.strip()
        detail['date'] = time[time.find("：")+1:time.find(" ")]
        print(detail['date'])
        # 省、市、区
        location = info[-1].string.strip()
        detail['location'] = location[location.find("：")+1:]

        detail = Transfer(detail)

        if detail['province'] is None:
            print(detail['location'])

        AllRecord = [] # 或者不存下来而是去

        recordList = soup.find_all('div',attrs={'class':'show_bird'})
        for item in recordList:
            oneRecord = {}
            text = item.text.strip().split(' ')
            oneRecord['name'] = text[1].strip()
            oneRecord['number'] = int(text[0])
            oneRecord = dict(oneRecord,**detail)
            AllRecord.append(oneRecord)

        # for record in AllRecord:
        #     save_data(record)
            # print(record)


def read_key(key_path):
    with open(key_path, 'r', encoding='utf-8') as f:
        key = f.read()
    return key

def Transfer(detail):
    address = detail['location']
    key = read_key('user-key.txt')
    index_url = f'https://restapi.amap.com/v3/geocode/geo?address={address}&output=XML&key={key}'
    result = getHtml(index_url)
    soup = BeautifulSoup(result, 'lxml')
    # 省份
    province = soup.find('province')
    detail['province'] = province.text if province else None
    # 城市
    city = soup.find('city')
    detail['city'] = city.text if province else None
    # 区
    district = soup.find('district')
    detail['district'] = district.text if province else None
    return detail

index = 0
def save_data(record):
    global index
    index += 1
    try:
        # 检查连接是否断开，如果断开就进行重连
        connection.ping(reconnect=True)
        cursor1 = connection.cursor()
        sql = 'insert into birdrecord_new(recordID,name,location,province,city,district,date,number) ' \
              'values(%s,%s,%s,%s,%s,%s,%s,%s)'
        cursor1.execute(sql, (record['id'],record['name'], record['location'], record['province'],record['city'],record['district'],record['date'],record['number']))
        # 提交事务
        connection.commit()
        # print("%d记录保存成功\n" % (index))

    except Exception as e:
        print("操作出现错误：{}".format(e))
        # 回滚所有更改
        connection.rollback()

    cursor1.close()
    connection.close()

recordUrl = "http://www.birder.cn/recordcenter.html"
introUrl = "http://www.birder.cn/species/Tragopan-melanocephalus"

def Crawl():
    pageNum = 2156
    # 目前爬完了2155没有爬到2156
    EnableCrawl = True
    while EnableCrawl:
        url = "http://www.birder.cn/recordcenter.html?keyword=&NowAreaCode0=&NowAreaCode1=&NowAreaCode2=&NowAreaCode=&address=&stardate=&enddate=&user_id=0&page=%d"%(pageNum)
        # 对每一页进行判断 进入下一个主页面
        html = getHtml(url)
        if html:
            soup = BeautifulSoup(html,'html.parser')
            trList = soup.find_all('tr')
            aLink = []
            for tr in trList:
                a = tr.find('a')
                if a is not None:
                    aLink.append(baseUrl + a['href'])

            for link in aLink:
                getRecord(link)
            print("page:%d 爬取完成\n"%(pageNum))
        # 处理翻页问题
        pageNext = soup.find('a', attrs={'class', 'link'})
        if pageNext is not None:
            pageNum += 1
        else:
            EnableCrawl = False
        # if pageNum == 5:
        # EnableCrawl = False
        # pageNum+=1
Crawl()
# getRecord('')

