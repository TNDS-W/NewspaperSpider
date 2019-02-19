import requests
from lxml import etree
import time, re, datetime
from api.damsapi import DamsApi
from spiders.basespider import Spider


# 作者：文振乾
# 时间：2018-12-7
# 用途：爬取中国经济时报

class Jjsb(Spider):
    newspaperlibraryid = "1045861073007149056"  # 报纸id
    url = "http://jjsb.cet.com.cn/"
    images = []
    message = []
    number = 0

    def geturl(self):
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
        }
        y = 0
        while y < 3:
            try:
                resp = requests.get(url=self.url, headers=header)
                break
            except:
                y += 1
        result = resp.content.decode("utf-8")
        html = etree.HTML(result)
        # 获取报纸最新日期的url
        newurl = self.url + html.xpath('//table[@id="footer1_dl_jqhg"]//a//@href')[0]
        publishedTime = html.xpath('//table[@id="footer1_dl_jqhg"]//a//text()')[0][1:-1]
        header1 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
            "Referer": self.url
        }
        i = 0
        while i < 3:
            try:
                resp1 = requests.get(url=newurl, headers=header1)
                break
            except:
                i += 1
        result1 = resp1.content.decode("utf-8")
        # print(result1)
        html1 = etree.HTML(result1)
        newurl1 = html1.xpath(
            '//td[@style="background-color:#ffffff; text-align:left; vertical-align: top;"]//a//@href')
        return [newurl1, publishedTime]

    def supplement_geturl(self):
        publishedTime = input("请输入要获取报纸的日期(例:2018-01-01):")
        newurl = input("请输入要补录日期的url(例:http://jjsb.cet.com.cn/szb_12791.html):")
        header1 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
            "Referer": self.url
        }
        i = 0
        while i < 3:
            try:
                resp1 = requests.get(url=newurl, headers=header1)
                break
            except:
                i += 1
        result1 = resp1.content.decode("utf-8")
        # print(result1)
        html1 = etree.HTML(result1)
        newurl1 = html1.xpath(
            '//td[@style="background-color:#ffffff; text-align:left; vertical-align: top;"]//a//@href')
        # print(newurl1, publishedTime)
        return [newurl1, publishedTime]

    def getnewsurl(self, newurl):
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
        }
        ajaxurl = "http://jjsb.cet.com.cn/ashx/tb_article.ashx"

        for x in newurl:
            newurl1 = self.url + x  # 版面导读A0,A1处完整的url
            pid = "".join(x).split("_")[1]  # post请求中的data参数
            oid = "".join(x).split("_")[2].replace(".html", "")  # post请求中的data参数
            # print(pid,oid)
            y = 0
            while y < 3:
                try:
                    resp = requests.get(url=newurl1, headers=header)
                    break
                except:
                    y += 1
            result = resp.content.decode("utf-8")
            html = etree.HTML(result)
            news_url = html.xpath(
                '//div[@style="width: 230px; text-align: left; margin-top: 10px; margin-right: 5px;"]//a//@href')
            news_number = len(news_url)  # 每个A系列板块的新闻个数
            # print(news_number)
            header1 = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
            }
            formdata = {
                "cmd": "disporder",
                "pid": pid,
                "oid": oid
            }
            time.sleep(0.5)
            i = 0
            while i < 3:
                try:
                    resp1 = requests.post(url=ajaxurl, headers=header1, data=formdata)
                    break
                except:
                    i += 1
            result1 = resp1.content.decode("utf-8")
            # print("开始")
            self.parseajax(result1, news_number, oid)
            time.sleep(0.5)
        # print("爬取完成，开始录入")

    # 解析ajax数据
    def parseajax(self, result, nes_number, oid):
        # print("开始解析")
        nowtime = "".join(re.findall('"publishDate":"(.*?)T', result)[0].split("-"))
        # print(result)
        for x in range(nes_number):
            print("-->采集第" + str(self.number + 1) + "篇文章<--")
            self.number += 1
            imgurl = []
            #标题
            leadtitle = re.findall('"leadTitle":"(.*?)"', result)[x].replace("\n", "")
            if leadtitle == "":
                title = leadtitle + re.findall('"title":"(.*?)"', result)[x].replace("\n", "")
            else:
                title = leadtitle + "#" + re.findall('"title":"(.*?)"', result)[x].replace("\n", "")
            if title == "":
                continue
            #作者
            authors = re.findall('"author":"(.*?)"', result)[x].strip()
            auth = re.findall('([^\s]+)',authors)
            if len(auth) <= 1:
                author = "".join(auth).replace("□","").replace(r"\n","")
            else:
                author = "#".join(auth).replace("□","").replace(r"\n","")

            #正文
            cont = re.findall('"content":"([\d\D]*?)","audited"', result)[x].split("\\n")
            if re.search("■", cont[0]):
                cont.pop(0)
            #副标题
            subTitle = re.findall('"title1":"(.*?)"', result)[x]
            authorArea = ""
            authorDescriptions = ""
            abstract = ""
            #频道
            channel = re.findall('"verName":"(.*?)"', result)[x]
            imageDescriptions = ""
            #图片
            try:
                img = re.findall('"images":"(.*?)"', result)[x].split(";")
                for x in range(len(img)):
                    imgs = self.url + "zgjjsb/" + nowtime + "/" + img[x]
                    imgurl.append(imgs)
            except:
                pass
            finally:
                content = []
                for y in cont:
                    if y:
                        y = "<p>" + y + "</p>"
                        content.append(y)
                content = "".join(content)
                if img == [""]:
                    imgurl = []
                    self.message.append(
                        {"title": title, "subTitle": subTitle, "author": author, "authorArea": authorArea,
                         "authorDescriptions": authorDescriptions, "abstract": abstract,
                         "channel": channel, "mainBody": content, "page": oid,
                         "images": "".join(imgurl), "imageDescriptions": imageDescriptions, "cookies": "",
                         "referer": ""})
                    # print(author,content)
                else:
                    self.message.append(
                        {"title": title, "subTitle": subTitle, "author": author, "authorArea": authorArea,
                         "authorDescriptions": authorDescriptions, "abstract": abstract,
                         "channel": channel, "mainBody": content, "page": oid,
                         "images": "#".join(imgurl), "imageDescriptions": imageDescriptions, "cookies": "",
                         "referer": ""})
                    # print(author,content)


    def run(self):
        api = self.api
        # 获取token
        ret = api.gettoken()
        if not ret:
            return 0
        # 从网页中获取发行日期
        print("开始采集:中国经济时报")
        publishedtime = self.geturl()[1]
        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：中国经济时报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            print("正在采集新闻……")
            a = self.geturl()
            self.getnewsurl(a[0])
            length = len(self.message)

            for x in range(length - 1):
                if self.message[x]["title"] == "":
                    self.message.pop(x)
            print("一共采集" + str(self.number) + "篇文章")
            super().uploaddata(a[1], self.message, self.newspaperlibraryid, False)
            print("采集成功:中国经济时报-发行日期（" + publishedtime + "),文章数量（" + str(len(self.message)) + "）")
        return len(self.message)

    #补录方法
    def supplement(self):
        api = self.api
        # 获取token
        ret = api.gettoken()
        if not ret:
            return 0
        # 从网页中获取发行日期
        print("开始采集:中国经济时报")
        a = self.supplement_geturl()
        publishedtime = a[1]

        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：中国经济时报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            print("正在采集新闻……")
            self.getnewsurl(a[0])
            length = len(self.message)
            for x in range(length - 1):
                if self.message[x]["title"] == "":
                    self.message.pop(x)
            print("一共采集" + str(self.number) + "篇文章")
            super().uploaddata(a[1], self.message, self.newspaperlibraryid, False)
            print("采集成功:中国经济时报-发行日期（" + publishedtime + "),文章数量（" + str(len(self.message)) + "）")
            self.message = []

