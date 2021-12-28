# 实现从网上把商品的信息抓取到数据库中 https://detail.tmall.com/item.htm?spm=a220m.1000858.1000725.36.2c075c9c1EEmce&id=631431632923&skuId=4688860675362&areaId=510100&user_id=1714128138&cat_id=50024400&is_b=1&rn=2ec5e038cc311e68a3608a8f815ea0e7
# https://detail.tmall.com/item.htm?spm=a220m.1000858.1000725.36.2c075c9c1EEmce
# &id=631431632923&skuId=4688860675362&areaId=510100&user_id=1714128138&cat_id=50024400
# &is_b=1&rn=2ec5e038cc311e68a3608a8f815ea0e7

import requests
from bs4 import BeautifulSoup as bs
import json
import csv
import re
import time
import pymysql


COMMENT_PAGE_URL = []
# 定义需要的字段
nickname = []
userId = []
auctionSku = []
rateContent = []
rateDate = []


def get_url(num):
    urlFront = 'https://rate.tmall.com/list_detail_rate.htm?itemId=631431632923&spuId=1902784688&sellerId=1714128138&order=3&currentPage='
    urlRear = '&append=0&content=1&tagId=&posi=&picture=&groupId=&ua=098%23E1hvTpvavaOvU9CkvvvvvjiWPLdysjYRP2dyzj1VPmPv6jrWRLSO1jlEnLSh6jlRRsuvvpvZz%2FYqNrE4zYMzrpLGchS5BnGCzWmvvpvWz%2FNlc2X4zYMznP5wdvhvmpvhX98YSpstPF9CvvpvvvvvdvhvmpvUXQRMSQ1aUL9CvvpvvvvvdvhvmpvUhI8ZDvsGZ8QCvvyvmHQEyEvWrh4%2BvpvEvvFQkLQG2E93dvhvmpvWiO5V19CiAUOCvvpvCvvvi9hvCvvv9UUgvpvhvvvvvv9CvhQUqNyvCsnlYU3thBODN%2BBlYE7rV361iNLWgCuOfCuYiXVvVE6Fp%2B0x9WowjLEc6acEKBmAVADlYExreCIaWXxr1nmK5kx%2FAj7QD46wKvhv8vvvvvCvpvvvvvmmvhCvmhvvvUUvphvUpQvv99CvpvkkvvmmvhCvm88UvpvVmvvC9j3Uuvhvmvvv92QgGn0HvvhvC9vhvvCvpvgCvvLMMQvvdvhvmpvUrU83Ipvy14QCvvyvmjp2qRQW24JvvpvWz%2FYQ5vHwzYMzm5Fw9vhv2nMSGt1ZcnMNYtbqz8QCvvyvC2A2m9IWgJ%2F%2BvpvEvvog95B62Pxp9vhvHnM5ax1o7rMNYYWHMHSozAqNCnsCRvhvCvvvvvmvvpvWz%2FaRNVC4zYMz2Pqw9vhv2nM5El1U7rMNY1o7zv%3D%3D&needFold=0&_ksTS=1616934351620_3055&callback=jsonp3056'
    for i in range(0, num):
        COMMENT_PAGE_URL.append(urlFront + str(1 + i) + urlRear)


# 获取评论、昵称、评论时间等数据
def GetInfo(num):
    # 循环获取每一页评论
    headers = {
        'cookie': 't=908445326e0c780061006635d5fb5ab6; _tb_token_=eb3b78830b148; cookie2=172476e18b3c2ea207d76b437076951b; cna=Pa3gGGFszFICAbaWpBsvSXHJ; xlly_s=1; dnk=tb4425496033; tracknick=tb4425496033; lid=tb4425496033; lgc=tb4425496033; login=true; _m_h5_tk=f730be234d4ceadf1ee7e621310ad21e_1616939937510; _m_h5_tk_enc=1ae9af14b3974ec6657ce6677d15c9bf; sm4=510100; uc1=cookie15=UtASsssmOIJ0bQ%3D%3D&cookie14=Uoe1hM118Syj9Q%3D%3D&cookie16=UIHiLt3xCS3yM2h4eKHS9lpEOw%3D%3D&pas=0&existShop=false&cookie21=VT5L2FSpczFp; uc3=nk2=F5RBwfH8m48kg2RD&vt3=F8dCuAtUKHH9BP55yEQ%3D&id2=UUphy%2FZybznDgQD12g%3D%3D&lg2=VFC%2FuZ9ayeYq2g%3D%3D; _l_g_=Ug%3D%3D; uc4=id4=0%40U2grEJGNHKhr6d0BoN8rT0JUv5KvKl5a&nk4=0%40FY4KpC4lbzn8m3Y7jIzCfZYQasBRXoY%3D; unb=2201480757263; cookie1=VWfFHBXtxklwndzh8yC6eZ28y4gvX%2FtfgqTlJ%2FRgkJA%3D; cookie17=UUphy%2FZybznDgQD12g%3D%3D; _nk_=tb4425496033; sgcookie=E100IhWKh8VFx4rRZ2g0Wh%2FOGubXCRuX9xSp0Rj6iF4kB6ScTeJy4RmWBDCulGtCJMklXHJNtVrfY%2FClyR8f4JcNEg%3D%3D; sg=337; csg=023016c3; enc=PiULqNK51oNfMEH07RiL%2BpY1SreNrtDVSa%2BsPhNS%2FLttaES1NzOzGKKDqqaJJRthJwuPX6wSFBiTlPCtXQmgHpW54sc9xdgIDHPH%2FysVfaM%3D; isg=BNLShERQ5g1NmBrxhiKDm2MUI5i049Z99xeCK5wuYAcRr3qphHHajHqJHguTmE4V; tfstk=cDBOBRf1ay4Mvu-d41FncmMNaxvAalM9kcTrHlK-D9fjr5DEKsxRETCWZ5t-WpEd.; l=eBM_uzA7jzSbH7YaBO5w-urza77O3CdfcOFzaNbMiIncC6v1G49tIUKQDjLtzLtRJ8XVTzYB4sz4jMwtiFF88yYfoTB7K9cdvdLDhFLC.',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'referer': 'https://detail.tmall.com/item.htm?spm=a220m.1000858.1000725.36.2c075c9c1EEmce&id=631431632923&skuId=4688860675362&areaId=510100&user_id=1714128138&cat_id=50024400&is_b=1&rn=2ec5e038cc311e68a3608a8f815ea0e7',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9'
    }
    for i in range(num):
        # 头文件，没有头文件会返回错误的js
        params={
            'itemId': '631431632923',
            'spuId': '1902784688',
            'sellerId': '1714128138',
            'currentPage': i,
            'callback': 'jsonp3056'
        }
        # 解析JS文件内容
        content= requests.get(COMMENT_PAGE_URL[i], params,headers=headers).text[12:-1]
        comment = re.findall('rateContent":"(.*?)"', content)
        nk=re.findall('displayUserNick":"(.*?)"',content)
        #Id=re.compile('id:"(\d*?)"',re.S)
        #userId.extend(re.findall(Id,content))
        Id=re.findall(r'id":"(\d+)"',content)
        rateDate.extend(re.findall('"rateDate":"(.*?)"', content))
        #Id=re.findall(r'\"id\"\:\"[\d\.]*?\"', content)
        #print(Id)
        rateContent.extend(comment)
        nickname.extend(nk)
        userId.extend(Id)
        print(len(userId))#此处数字还未爬取成功
       # auctionSku.extend(re.findall('"auctionSku":"(.*?)"', content))#商品类型，可以作为附加的功能
        print(rateDate)
        save_data()
    # 将数据写入TEXT文件中
    for i in list(range(0, len(rateContent))):
        text = rateContent[i] + '-->' + nickname[i] + '-->' + rateDate[i] + '\n'
        with open(r"Content.txt", 'a+', encoding='UTF-8') as file:
            file.write(text + ' ')
            print(i + 1, ":写入成功")


def save_data():
    db = pymysql.connect(
        host="localhost",
        user="root",
        passwd="20010316",
        database="nlp_test")
    cursor = db.cursor()  # 创建一个游标对象
    # 插入对象
     # sql="INSERT INTO comment(comment_id,goods_id,user_id,user_nk,content,comment_time) VALUES(%d,%d,%d,%s,%s,%s)"%(i+1,1,nickname[i],ratecontent[i],ratedate[i])
    #SQL="""INSERT INTO goods_item(goods_id,goods_name) VALUES(1,'红米手机')"""
    for every in range(0, len(rateContent)):
        comment_id=every+1
        goods_id=1
        user_nk=nickname[every]
        content=rateContent[every]
        comment_time=rateDate[every]
        value=(comment_id,goods_id,user_nk,content,comment_time)
        try:
            sql = "INSERT INTO comment(comment_id,goods_id,user_nk,content,comment_time) VALUES(%s,%s,%s,%s,%s)"
            cursor.execute(sql,value)
            db.commit()
            print("successful!")
        except:
            db.rollback()
    db.close()
    # sql="INSERT INTO comment(comment_id,goods_id,user_id,user_nk,content,comment_time) VALUES(%d,%d,%d,%s,%s,%s)"%(i+1,1,nickname[i],ratecontent[i],ratedate[i])
    #sql = "SELECT * FROM admin"




