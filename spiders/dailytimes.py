from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import selenium.common.exceptions as Ex
import time
from spiders.basespider import Spider
import requests
from lxml import etree
import re
from selenium.webdriver.chrome.options import Options

class Dailytimes(Spider):
    newspapername = '每日时报'
    newspaperlibraryid = "1062233195828740096"
    proxy = {"https": "https://127.0.0.1:8124"}

    #获得频道和发布时间 （requests）
    def get_time_and_channel(self,url='https://dailytimes.com.pk/e-paper/'):
        try:
            response = requests.get(url,proxies=self.proxy)
        except:
            response = requests.get(url,proxies=self.proxy)
        result = response.content.decode('UTF-8')
        html = etree.HTML(result)
        channel = html.xpath("//ul[@class='epaper-nav']/li/text()")
        publictimes = html.xpath("//input[@id='date']/@value")
        return channel,publictimes

    #处理时间
    def dealpublictime(self,publictimes):
        #20-12-2018
        publictimes = publictimes.split('-')

        publictime = "%s-%s-%s" %(publictimes[2],publictimes[1],publictimes[0])

        return publictime

    #selenium 获得报纸id
    def get_paper_id(self):
        global driver

        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        chrome_options.add_argument("--proxy-server=http://127.0.0.1:8124")

        driver = webdriver.Chrome(chrome_options=chrome_options)

        driver.get("https://dailytimes.com.pk/e-paper/")

        driver.maximize_window()

        paper_id = driver.find_element_by_xpath("//img[@class='maphilighted']").get_attribute("src")

        driver.close()
        #处理
        paper_id = paper_id.split("/")
        paper_id = paper_id[len(paper_id)-2]

        return paper_id

    #采集
    def getpaper(self,url,channel):
        # 报纸集合
        neweparper = []
        count = 0
        #获取文章链接
        # channel,publictimes = self.get_time_and_channel()
        # pagename = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "B1", "B2", "B3", "B4", "C1", "C2", "C3", "C4", "C5", "C7", "C8"]
        for i in range(len(channel)):
            # 多次连接
            count_get_href = 0
            while count_get_href < 7:
                try:
                    response = requests.get(
                        "https://dailytimes.com.pk/assets/uploads/epaper/" + url + "/a" + str(i + 1) + ".html",proxies=self.proxy
                        ) # proxies=self.proxy
                except:
                    pass

                if response.status_code == 200:
                    break
                print("连接" + str(count_get_href) + "次")
                count_get_href += 1
                if count_get_href == 7:
                    raise Exception("请求失败！！！ 循环6次版面未请求成功")


            result = response.content.decode("UTF-8")

            #文章链接
            html = etree.HTML(result)
            artpage_href = html.xpath("//map/area/@href")

            for ah in artpage_href:
                #requests
                try:
                    #去空
                    if not ah:
                        continue

                    #去图片
                    if ".jpg" in ah:
                        continue

                    headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"}

                    # 多次连接
                    count_get = 0
                    while count_get < 7:

                        requests_except = 0
                        while requests_except < 7:
                            try:
                                pagecontenrt = requests.get(ah,headers=headers,proxies=self.proxy) # proxies=self.proxy
                                break
                            except:
                                print("请求错误" + str(requests_except) + "次")
                                requests_except += 1
                                if count_get_href == 7:
                                    raise Exception("请求失败！！！ 循环6次新闻未请求成功")

                        if pagecontenrt.status_code == 200:
                            break
                        print("连接" + str(count_get) + "次")
                        count_get += 1
                        if count_get_href == 7:
                            raise Exception("请求失败！！！ 循环6次新闻未请求成功")

                    page_result = pagecontenrt.content.decode("UTF-8")
                    html = etree.HTML(page_result)

                    # 获取文章内容
                    titlelist = ''
                    subtitlelist = ''
                    authorlist = ''
                    authorarealist = ''
                    authordescriptionslist = ''
                    pagelist = ''
                    channellist = ''
                    abstractlist = ''
                    mainbodylist = ''
                    imageslist = ''
                    imagesdescriptionslist = ''

                    # 标题
                    title = html.xpath("//div[@class='post-header']//h1/text()")
                    subtitle = html.xpath("//div[@class='post-header']//p[@class='post-shoulder']/text()")
                    author = html.xpath("//div[@class='post-header']//p[@class='author-links']/a/text()")
                    mainbody = html.xpath(
                        "//div[@class='entry-content']/p|//div[@class='site-inner']//div[@class='entry-content']/blockquote/p")
                    images = html.xpath(
                        "//div[@class='site-inner']//figure/img/@src|//div[@class='site-inner']//div[@class='entry-content']/p/img/@src")
                    imagedescription = html.xpath("//div[@class='site-inner']//figure/figcaption/text()")
                    chnnel = channel[i]
                    # pagelist = pagename[i]

                    # 打印 数据处理
                    # print(title[0].text)
                    if not title:
                        continue
                    titlelist = title[0]
                    # print(titlelist)
                    for st in subtitle:
                        # print(st.text)
                        subtitlelist = subtitlelist + st
                    # print(subtitlelist)
                    for ar in author:
                        # print(ar.text)
                        authorlist = authorlist + ar
                    # print(authorlist)
                    for mb in mainbody:
                        if mb.text:
                            mainbodylist = mainbodylist + "<p>" + mb.text + "</p>"
                        else:
                            strong = mb.xpath(".//text()")
                            if strong:
                                st = "".join(strong)
                                mainbodylist = mainbodylist + "<p>" + st + "</p>"
                            else:
                                em = mb.xpath("./*//text()")
                                if em:
                                    s = "".join(em)
                                    s = "<p>" + s + "</p>"
                                    mainbodylist = mainbodylist + s
                        # mainbodylist = mainbodylist + "<p>" + mb + "</p>"
                    # print(mainbodylist)
                    for im in images:
                        # print(im)
                        imageslist = imageslist + im + '#'
                        imageslist = imageslist[:-1]
                    # print(imageslist)
                    for imd in imagedescription:
                        # print(imd)
                        imagesdescriptionslist = imagesdescriptionslist + imd + '#'
                        imagesdescriptionslist = imagesdescriptionslist[:-1]
                    # print(imagesdescriptionslist)
                    # print(chnnel)
                    channellist = chnnel
                    # print(channellist)
                    # print("##################################################################")
                    # 保存到字典
                    artpage = {
                        'title': titlelist,
                        'subTitle': subtitlelist,
                        'author': authorlist,
                        'authorArea': authorarealist,
                        'authorDescriptions': authordescriptionslist,
                        'page': pagelist,
                        'channel': channellist,
                        'abstract': abstractlist,
                        'mainBody': mainbodylist,
                        'images': imageslist,
                        'imageDescriptions': imagesdescriptionslist,
                        'cookies': '',
                        'referer': ''
                    }
                    neweparper.append(artpage)
                    count = count + 1
                    print("每日时报 采集：" + str(count) + "篇")
                except Exception:
                    raise Exception
               # # selenium使用
               # # 获得驱动
               # driver = self.chrome_driver()
               #
               # while True:
               #     try:
               #         driver.get(ah)
               #         break
               #     except Exception:
               #         driver.refresh()
               #
               # driver.maximize_window()
               #
               # #文章采集
               # # 获取文章内容
               # titlelist = ''
               # subtitlelist = ''
               # authorlist = ''
               # authorarealist = ''
               # authordescriptionslist = ''
               # pagelist = ''
               # channellist = ''
               # abstractlist = ''
               # mainbodylist = ''
               # imageslist = ''
               # imagesdescriptionslist = ''
               #
               # try:
               #      title = driver.find_element_by_xpath("//DIV[@class='post-header']//H1")
               # except Ex.NoSuchElementException:
               #     driver.close()
               #     continue
               # try:
               #      subtitle = driver.find_element_by_xpath("//DIV[@class='post-header']//P[@class='post-shoulder']")
               # except Ex.NoSuchElementException:
               #     pass
               # try:
               #      author = driver.find_element_by_xpath("//DIV[@class='post-header']//P[@class='author-links']")
               # except Ex.NoSuchElementException:
               #     pass
               # try:
               #      mainbody = driver.find_elements_by_xpath("//DIV[@class='entry-content']/P|//DIV[@class='site-inner']//DIV[@class='entry-content']/BLOCKQUOTE/P")
               # except Ex.NoSuchElementException:
               #     pass
               # try:
               #      images = driver.find_elements_by_xpath(
               #     "//DIV[@class='site-inner']//FIGURE/IMG|//DIV[@class='site-inner']//DIV[@class='entry-content']/P/IMG")
               # except Ex.NoSuchElementException:
               #     pass
               # try:
               #      imagedescription = driver.find_elements_by_xpath("//DIV[@class='site-inner']//FIGURE/FIGCAPTION")
               # except Ex.NoSuchElementException:
               #     pass
               # chnnel = channel[i]
               #
               #  #打印 数据处理
               #
               # #
               # titlelist = title.text
               #
               # subtitlelist = subtitlelist + subtitle.text
               #
               # authorlist = authorlist + author.text
               #
               # for mb in mainbody:
               #     mainbodylist = mainbodylist + "<p>" + mb.text + "</p>"
               #
               # for im in images:
               #     imageslist = imageslist + im.get_attribute("src") + "#"
               # imageslist = imageslist[:-1]
               #
               # for imd in imagedescription:
               #     imagesdescriptionslist = imagesdescriptionslist + imd.text + "#"
               # imagesdescriptionslist = imagesdescriptionslist[:-1]
               #
               # channellist = chnnel
               #
               # # 保存到字典
               # artpage = {
               #     'title': titlelist,
               #     'subTitle': subtitlelist,
               #     'author': authorlist,
               #     'authorArea': authorarealist,
               #     'authorDescriptions': authordescriptionslist,
               #     'page': pagelist,
               #     'channel': channellist,
               #     'abstract': abstractlist,
               #     'mainBody': mainbodylist,
               #     'images': imageslist,
               #     'imageDescriptions': imagesdescriptionslist,
               #     'cookies': '',
               #     'referer': ''
               # }
               #
               # neweparper.append(artpage)
               # count = count + 1
               # print("每日时报 采集：" + str(count) + "篇")
               #
               # #关闭
               # driver.close()

        return neweparper

    def mainbody_clean(self,messages):
        message = []
        messages = list(reversed(messages))
        for x in range(len(messages)):
            right = True
            for y in range(x, len(messages)):
                if x == y:
                    continue
                if messages[x]["title"] == messages[y]["title"]:
                    if messages[x]["mainBody"][0] == messages[y]["mainBody"][0]:
                        right = False
                        break
            if right:
                message.append(messages[x])

        message = list(reversed(message))

        return message


    def run(self):

        api = self.api

        #获取token
        ret = api.gettoken()
        if not ret:
            return 0

        channel,publictimes = self.get_time_and_channel()

        # 从网页中获取发行日期
        print("获取时间")
        publishedtime = self.dealpublictime(str(publictimes[0]))

        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)

        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：" + self.newspapername + "-发行日期已经存在，报纸日期（"+publishedtime+")")
            return 0
        else:
            #数据加到数据库
            print("开始采集：" + self.newspapername)
            print("正在采集新闻……")

            try:
                datas = self.getpaper(self.get_paper_id(),channel)
            except Exception as e:
                driver.close()
                raise e

            data = self.mainbody_clean(datas)
            super().uploaddata(publishedtime,data,self.newspaperlibraryid,True)
            print("采集成功:" + self.newspapername + "-发行日期（"+publishedtime+"),文章数量（"+str(len(data))+"）")
        return len(data)

    #补录
    def supplement(self):

        api = self.api

        #获取token
        ret = api.gettoken()
        if not ret:
            return 0

        paper_id,publictimes,paper_date = self.get_input_id_and_date()

        channel, publictimess = self.get_time_and_channel("https://dailytimes.com.pk/e-paper/" + paper_date + "/")

        # 从网页中获取发行日期
        print("获取时间")
        publishedtime = publictimes

        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)

        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：" + self.newspapername + "-发行日期已经存在，报纸日期（"+publishedtime+")")
            return 0
        else:
            #数据加到数据库
            print("开始采集：" + self.newspapername)
            print("正在采集新闻……")

            datas = self.getpaper(paper_id,channel)
            data = self.mainbody_clean(datas)

            super().uploaddata(publishedtime,data,self.newspaperlibraryid,True)
            print("采集成功:" + self.newspapername + "-发行日期（"+publishedtime+"),文章数量（"+str(len(data))+"）")
        return len(data)

    def get_input_id_and_date(self):

        paper_id = input("输入报纸id 如（https://dailytimes.com.pk/assets/uploads/epaper/341510/a14.html 如:341510）")
        date = input("输入报纸的时间 如（2019-01-01）")

        paper_date = date.split("-")

        paper_date = "%s-%s-%s" %(paper_date[2],paper_date[1],paper_date[0])

        return paper_id,date,paper_date

# if __name__ == '__main__':
#     new = Dailytimes()
#     print(type(new.get_paper_id()))
#     print(new.get_paper_id())
#     c,p = new.get_time_and_channel()
#     p = new.dealpublictime(str(p[0]))
#     print(p)
#     # new = Dailytimes().getpaper()
#     # for nw in new:
#     #     print(nw)

