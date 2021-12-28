import threading
import requests
from fake_useragent import UserAgent
import json
import re
from requests.exceptions import HTTPError, Timeout, RequestException, ProxyError, ConnectTimeout
from concurrent.futures import ThreadPoolExecutor
import urllib3
import csv
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class spider_jd():
    """
    创建对象 输入指定的网站
    start_request方法进行评论爬取
    get_image方法获取图像的url
    get_name获取商品名称
    """

    def __init__(self, url):
        ua = UserAgent(use_cache_server=False).random
        self._url = url
        self.headers = {
            'Referer': 'https://www.baidu.com/',
            'User-Agent': ua
        }
        self.comment_api_url1 = 'https://sclub.jd.com/comment/productPageComments.action?callback=&productId=%s&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1'
        self.comment_api_url2 = 'https://sclub.jd.com/comment/productPageComments.action?callback=&productId=%s&score=0&sortType=5&page=%s&pageSize=10&isShadowSku=0&fold=1'
        self.csv_file = open('jd.csv', 'w+',newline='')
        fileNames = ['content']
        self.writer = csv.DictWriter(self.csv_file, fieldnames=fileNames)
        self.writer.writeheader()
        self.myLock = threading.Lock()


    def parse_url(self, url):
        try:
            response = requests.get(url, headers=self.headers, verify=False)
            if response.status_code == 200:
                return response.text
        except (HTTPError, Timeout, RequestException, ProxyError, ConnectTimeout) as err:
            print(err)
            return None

        return response

    def start_request(self):
        # 匹配id
        product_id = re.findall("\d+", self._url)[0]
        comment_url = self.comment_api_url1 % product_id
        response_text = self.parse_url(comment_url)
        json_data = json.loads(response_text)
        maxPage = int(json_data['maxPage'])
        print('能够获取的最大页码数量', maxPage)
        pool = ThreadPoolExecutor(10)
        for page in range(maxPage//100):
            comUrl = self.comment_api_url2 % (
                product_id, str(page))
            result = pool.submit(self.parse_url, comUrl)
            result.add_done_callback(self.parse_comments)
        pool.shutdown()

    def parse_comments(self, future):
        response_text = future.result()
        if response_text:
            comments = json.loads(response_text)['comments']

            for comment in comments:
                commentInfo = {}
                commentInfo['content'] = comment['content']
                self.save_db_to_csv(commentInfo)


    def save_db_to_csv(self, commentInfo):
        # 将数据写入csv文件
        self.myLock.acquire()
        self.writer.writerow(commentInfo)
        self.myLock.release()
        # with open('jd.csv', 'w') as csvfile:
        #     writer = csv.writer(csvfile)
        #     for i in range(1,len(commentInfo)):
        #         writer.writerow(commentInfo[i])
            # for item in commentInfo['content']:
            #     print(item)
            #     writer.writerow(item)

    def get_image(self):
        htmldata = requests.get(self._url, headers=self.headers, verify=False).text
        soup = BeautifulSoup(htmldata, "html.parser")
        img = soup.find('img', attrs={"id": "spec-img"})
        src = "http://"+img.get("data-origin").lstrip("//")
        return src

    def get_name(self):
        htmldata = requests.get(self._url, headers=self.headers, verify=False).text
        soup = BeautifulSoup(htmldata, "html.parser")
        name=soup.find('div',attrs={'class':'sku-name'}).get_text().strip()
        return name
#
# jd = spider_jd("https://item.jd.com/100010090645.html")
# jd.start_request()
    # print(jd.get_image())
    # print(jd.get_name())
