import requests
from lxml import etree
import re
from api.damsapi import DamsApi
from spiders.basespider import Spider

# 作者：文振乾
# 时间：2018-12-6
# 用途：爬取求是周报

class Qiushi(Spider):

    newspaperlibraryid = "1045860779791745024"
    message = []         #保存爬取下来的所有数据

    def geturl(self,url):
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
            "Upgrade-Insecure-Requests": "1"
        }
        response = requests.get(url=url, headers=header)
        result = response.content.decode("utf-8")
        html = etree.HTML(result)
        urls = html.xpath('//div[@class="row"]//div[@class="booktitle"]/a/@href')[0]

        header1 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
            "Referer": url
        }
        i = 0
        while i<5:
            try:
                response1 = requests.get(url=urls, headers=header1)
                break
            except:
                i +=1
        result1 = response1.content.decode("utf-8")
        # print(result1)

        html1 = etree.HTML(result1)
        urls1 = html1.xpath('//div[@class="content"]//p//a/@href')[-1]
        page = ""
        header2 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
            "Referer" : urls
        }
        try:
            response2 = requests.get(url=urls1,headers=header2)
        except:
            response2 = requests.get(url=urls1,headers=header2)
        result2 = response2.content.decode("utf-8")
        # print(result2)
        html2 = etree.HTML(result2)
        block = html2.xpath('//div[@class="highlight"]/p')
        newsurl = {'':[]}
        Channel_list = ['']
        Channel = ''
        for i in block:
            try:
                Channel = i.xpath('font[@face="微软雅黑"]//text()')[0].replace("\u3000"," ")
                newsurl[Channel] = []
                Channel_list.append(Channel)
            except:
                if i.xpath('a/@href'):
                    newsurl[Channel].append(i.xpath('a/@href')[0])
                elif i.xpath('strong/a/@href'):
                    newsurl[Channel].append(i.xpath('strong/a/@href')[0])
        time = html2.xpath('//div[@class="headtitle"]//span/text()')[0]
        publishedtime = "-".join(re.findall("[0-9]{2,4}",time)[:3])
        # del newsurl[-1]
        # print(newsurl)
        return [newsurl,page,publishedtime,Channel_list]

    #解析页面
    def parsepage(self,newsurl,page,Channel_list):
        # print("开始解析")
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
        }
        newsurl[Channel_list[-1]].pop(-1)           #删掉最后一个"查看往期"的url
        a = 0
        for Channel in Channel_list:
            for url in newsurl[Channel]:
                # time.sleep(2)
                i = 0
                while i<10:
                    try:
                        response = requests.get(url=url,headers=header)
                        break
                    except:
                        i +=1
                result = response.content.decode("utf-8")
                html = etree.HTML(result)
                img = ""
                imgurl = ""
                imgdescrip = ""
                try:         # 有的有图片  有的没图片  图片url要拼接
                    img = html.xpath('//div[@class="content"]//div[@class="highlight"]//p//img//@src')
                    imgdescrip = html.xpath('//div[@class="content"]//div[@class="highlight"]/p/font/text()')
                    imgs = url.split("/")
                    imgs.pop(-1)
                    imgs.append("".join(img))
                    imgurl = "/".join(imgs)
                    # print(img)
                except:
                    pass
                finally:
                    title = "".join(html.xpath('//div[@class="row"]//div[@class="headtitle"]//h1/text()')).strip()
                    times = "".join(html.xpath('//div[@class="row"]//div[@class="headtitle"]//span/text()')).strip()
                    author = (html.xpath('//div[@class="row"]//div[@class="headtitle"]//text()')[-1].replace("\u3000"," ").split("：")[-1]).strip()
                    if len(author)>6:
                        author = author.replace("本刊记者 ","")
                        if len(author)>4:
                            author = '#'.join(author.split(" "))
                    cont = html.xpath('//div[@class="content"]//div[@class="highlight"]/p//text()')
                    cont.pop(-1)
                    content = []
                    subTitle = "".join(html.xpath('//div[@class="row"]//div[@class="headtitle"]//h2/text()')).strip()
                    if re.search('（.*?）',subTitle):
                        subTitle = ""
                    authorArea = ""
                    abstract = ""
                    channel = Channel
                    imageDescriptions = ""

                    authorDescriptions = ""
                    for x in cont:
                        if x.strip() != "":
                            if re.search('\s*（作者：.*?）',x):
                                authorDescriptions = "".join(re.findall('\s*（作者：(.*?)）',x))
                            x = "<p>" + x.strip() + "</p>"
                            content.append(x)
                    content = "".join(content)
                    if img == []:
                        imgurl = ""
                        self.message.append(
                            {"title": title, "subTitle": subTitle, "author": author, "authorArea": authorArea,
                             "authorDescriptions": authorDescriptions, "abstract": abstract,
                             "channel": channel, "mainBody": content, "page": page,
                             "images": imgurl, "imageDescriptions": imageDescriptions, "cookies": "",
                             "referer": ""})
                    else:
                        self.message.append({"title": title, "subTitle": subTitle, "author": author, "authorArea": authorArea,
                                             "authorDescriptions": authorDescriptions, "abstract": abstract,
                                             "channel": channel, "mainBody": content, "page": page,
                                             "images": imgurl, "imageDescriptions": imageDescriptions,"cookies":"","referer":""})
                        # print(title)
                    a += 1
                    print("第" + str(a) + "条采集成功")
            # print("爬取完成")



    def run(self):
        url = "http://www.qstheory.cn/qs/mulu.htm"
        api = self.api
        # 获取token信息
        ret = api.gettoken()
        if not ret:
            return 0
        # 从网页中获取发行日期
        publishedtime = self.geturl(url)[2]
        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：求是周报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            print("开始采集:求是周报")
            print("正在采集新闻……")
            result = self.geturl(url)
            self.parsepage(result[0],result[1],result[3])
            super().uploaddata(publishedtime,self.message,self.newspaperlibraryid,False)
            print("采集成功:求是周报-发行日期（" + publishedtime + "),文章数量（" + str(len(self.message)) + "）")
        return len(self.message)


