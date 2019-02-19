from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import selenium.common.exceptions as Ex
from spiders.basespider import Spider
import time
import requests
from lxml import etree
import re

class Sueddeutsche(Spider):
    newspapername = '南德意志报'
    newspaperlibraryid = "1060354570288365568"
    proxy = {"http": "http://127.0.0.1:8124", "https": "https://127.0.0.1:8124"}

    #获得时间
    def get_publishtimes(self):
        rsp = requests.get("https://epaper.sueddeutsche.de/Stadtausgabe",proxies=self.proxy) #,proxies=self.proxy
        result = rsp.content.decode('utf-8')
        html = etree.HTML(result)
        date = html.xpath("//div[@class='day__header']/text()")
        return str(date[1])

    #处理时间
    def deal_publishtime(self,publishtimes):

        #处理
        publishtimes = publishtimes.split(', ')
        publishtimes = publishtimes[1].replace('.','')
        publishtimes = publishtimes.split(' ')

        d_to_num = {
            "Januar": 1,
            "Februar": 2,
            "März": 3,
            "April": 4,
            "Mai": 5,
            "Juni": 6,
            "Juli": 7,
            "August": 8,
            "September": 9,
            "Oktober": 10,
            "November": 1,
            "Dezember": 12
        }

        publishtimes = "%s-%s-%s" %(publishtimes[2],str(d_to_num[publishtimes[1]]),publishtimes[0])
        return publishtimes

    #登陆
    def login_get_href(self):
        global driver

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        # chrome_options.add_argument("--proxy-server=http://127.0.0.1:8124")
        driver = webdriver.Chrome(chrome_options=chrome_options)

        url = "https://epaper.sueddeutsche.de/Stadtausgabe"

        # 声明等待
        wait = WebDriverWait(driver, 10)

        driver.get(url)

        driver.maximize_window()

        # 登陆
        driver.find_element_by_xpath(
            "//DIV[@class='primary-menu']/DIV[@class='primary-menu__column primary-menu__column--right']/A").click()

        driver.find_element_by_id('id_login').send_keys("13574827001@163.com")
        driver.find_element_by_id('id_password').send_keys("Yyy123456")
        driver.find_element_by_id('authentication-button').click()

        try:
            wait.until(EC.element_to_be_clickable((By.XPATH,"(//div[@class='day']/div[@class='row']//div[@class='issue__wrapper'])[1]")))
        except Ex.TimeoutException:
            driver.refresh()

        new_href = driver.find_element_by_xpath(
            "(//div[@class='day']/div[@class='row']//div[@class='issue__wrapper'])[1]/a[1]").get_attribute('href')

        # print(str(new_href))
        driver.close()

        new_href = str(new_href).split('/')
        new_href = new_href[len(new_href)-1]

        return str(new_href)

    #采集
    def getpaper(self,url):
        # 报纸集合
        neweparper = []
        #https://epaper.sueddeutsche.de/webreader-v3/urlproxy.php?url=https://sz.s4p-iapps.com/pdf/published/company/193/pdfplace/2593/files/766601/766601-media.json
        #https://epaper.sueddeutsche.de/webreader-v3/urlproxy.php?url=https://sz.s4p-iapps.com/pdf/published/company/193/pdfplace/2593/files/766771/766771-media.json

        url = "https://epaper.sueddeutsche.de/webreader-v3/urlproxy.php?url=https://sz.s4p-iapps.com/pdf/published/company/193/pdfplace/2593/files/" + url + "/" + url + "-media.json"
        # print(url)
        rsp = requests.get(url,proxies=self.proxy) #,proxies=self.proxy

        data = rsp.json()
        datalen = len(data)

        count = 0
        channel_change_page = 0
        page_new = 1
        for pagenum in range(datalen):
            if channel_change_page == 1:
                page_new += 1

            for aricle in data[str(pagenum+1)]:
                content = aricle['content']

                try:
                    title = content["title"]
                except KeyError:
                    continue
                try:
                    body = content["body"]
                except KeyError:
                    pass

                try:
                    pagetext = content["page"]
                except KeyError:
                    pass

                try:
                    channeltext = content["resort"]
                except KeyError:
                    pass

                #获取文本值
                # 内容集合
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

                #标题，副标题（有可能有）
                titletext = etree.HTML(title).xpath("//p/text()")

                #作者
                authortext = "#".join(etree.HTML(body).xpath("//p[@class='AUTOR_OBEN']//text()"))
                authortext = authortext.replace("und","#")

                #正文
                if body:
                    if authortext:
                        pattern = '<P CLASS="AUTOR_OBEN">.*</P>'
                        bodytext = re.sub(pattern,'',body)
                    else:
                        bodytext = body


                #打印 ，数据处理
                #标题，副标题（有可能有）
                if len(titletext) == 1:
                    titlelist = titletext[0]

                if len(titletext) == 2:
                    titlelist = titletext[0]
                    subtitlelist = titletext[1]

                #正文
                # for bd in bodytext:
                #     print(bd)
                bodytext = bodytext.replace("↵","")
                bodytext = bodytext.replace('<P CLASS="no_name"><SPAN CLASS="no_name" STYLE="font-family:SZoSansCond-Light;font-size:8.4pt;"> </SPAN></P>',"")
                pattern = r'<P CLASS="no_name">\s+</P>'
                bodytext = re.sub(pattern,"",bodytext)
                pattern = r'<P CLASS="no_name"><SPAN CLASS="no_name" STYLE="font-family:SZoText-Bold;font-weight:bold;">\s+</SPAN></P>'
                bodytext = re.sub(pattern,"", bodytext)
                mainbodylist = re.sub("<P>\s*</P>","",bodytext)


                # #版面
                # pagelist = str(pagenum + 1)
                # 频道 版面
                channellist = channeltext


                if channellist == 'München-Region-Bayern':
                    channel_change_page = 1

                if channel_change_page == 0:
                    pagelist = pagetext

                if channel_change_page == 1:
                    pagelist = "R" + str(page_new)

                #作者
                if authortext:
                    authorlist = authortext


                # 文章字典
                artpage = {'title': titlelist,
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
                if titlelist != "" and mainbodylist != "" :
                    neweparper.append(artpage)
                count = count + 1
                print(self.newspapername +"采集 ：" + str(count) + "篇")


        # selenium
        # # chrome_options = Options()
        # # chrome_options.add_argument('--headless')
        # # chrome_options.add_argument('--disable-gpu')
        # # chrome_options.add_argument('log-level=3') chrome_options=chrome_options
        # driver = webdriver.Chrome()
        #
        # url = "https://epaper.sueddeutsche.de/Stadtausgabe"
        #
        # # 声明等待
        # wait = WebDriverWait(driver, 10)
        #
        # driver.get(url)
        #
        # driver.maximize_window()
        #
        # # #获取发布时间
        # # try:
        # #     wait.until(EC.presence_of_element_located((By.XPATH,"//DIV[@class='day__header']")))
        # # except Ex.TimeoutException:
        # #     driver.refresh()
        # #
        # # publictimes = driver.find_elements_by_xpath("//DIV[@class='day__header']")[0].text
        #
        # #登陆
        # driver.find_element_by_xpath("//DIV[@class='primary-menu']/DIV[@class='primary-menu__column primary-menu__column--right']/A").click()
        #
        # driver.find_element_by_id('id_login').send_keys("13574827001@163.com")
        # driver.find_element_by_id('id_password').send_keys("Yyy123456")
        # driver.find_element_by_id('authentication-button').click()
        #
        # #选择报纸
        # try:
        #     wait.until(EC.element_to_be_clickable((By.XPATH,"(//div[@class='day']/div[@class='row']//div[@class='issue__wrapper'])[1]")))
        # except Ex.TimeoutException:
        #     driver.refresh()
        #
        # driver.find_element_by_xpath(
        #     "(//div[@class='day']/div[@class='row']//div[@class='issue__wrapper'])[1]").click()
        #
        # #进入电子报纸
        # count = 0
        # while True:
        #     # 获得 文章目录
        #     artpage = driver.find_elements_by_xpath("//DIV[contains(@class,'visible')]//DIV[@class='avBoxContainer ng-scope']/DIV")
        #
        #     time.sleep(1)
        #
        #     #遍历
        #     for ap in artpage:
        #
        #         time.sleep(2)
        #
        #         print(ap)
        #         #选择一篇文章
        #         ap.click()
        #
        #         # 内容集合
        #         titlelist = ''
        #         subtitlelist = ''
        #         authorlist = ''
        #         authorarealist = ''
        #         authordescriptionslist = ''
        #         pagelist = ''
        #         channellist = ''
        #         abstractlist = ''
        #         mainbodylist = ''
        #         imageslist = ''
        #         imagesdescriptionslist = ''
        #
        #         #获取内容
        #         try:
        #             title = driver.find_element_by_xpath("//div[@class='article-view-content']//span[@id='contentTitle']/h2/p")
        #         except Ex.NoSuchElementException:
        #             # 关闭
        #             driver.find_element_by_xpath("//DIV[@class='right-bar']/DIV[@class='close']").click()
        #             continue
        #
        #         try:
        #             subtitle = driver.find_element_by_xpath("//div[@class='article-view-content']//span[@id='contentTitle']/h3/p")
        #         except Ex.NoSuchElementException:
        #             subtitle = ''
        #
        #         try:
        #             author = driver.find_element_by_xpath("//div[@id='contentBody']/p[@class='AUTOR_OBEN']")
        #         except Ex.NoSuchElementException:
        #             author = ''
        #
        #         try:
        #             page = driver.find_element_by_xpath("//div[@id='container']//div[@class='page-number-indicator ng-binding']")
        #         except Ex.NoSuchElementException:
        #             pass
        #
        #         try:
        #             mainbody = driver.find_elements_by_xpath("//div[@id='contentBody']/p[@class='no_name']")
        #         except Ex.NoSuchElementException:
        #             pass
        #
        #         #数据处理 打印
        #         titlelist = title.text
        #         # print(titlelist)
        #
        #         if subtitle:
        #             subtitlelist = subtitlelist + subtitle.text
        #             # print(subtitlelist)
        #
        #         if author:
        #             authorlist = authorlist + author.text
        #             # print(authorlist)
        #
        #         page = page.text
        #         page = page.split(' ')[1]
        #         pagelist = page
        #         # print(pagelist)
        #
        #         for mb in mainbody:
        #             mainbodylist = mainbodylist + "<p>" + mb.text + "</p>"
        #         # print(mainbodylist)
        #
        #         # 文章字典
        #         artpage = {'title': titlelist,
        #                    'subTitle': subtitlelist,
        #                    'author': authorlist,
        #                    'authorArea': authorarealist,
        #                    'authorDescriptions': authordescriptionslist,
        #                    'page': pagelist,
        #                    'channel': channellist,
        #                    'abstract': abstractlist,
        #                    'mainBody': mainbodylist,
        #                    'images': imageslist,
        #                    'imageDescriptions': imagesdescriptionslist,
        #                    'cookies': '',
        #                    'referer': ''
        #                    }
        #
        #         neweparper.append(artpage)
        #         count = count + 1
        #         print("南德意志 采集：" + str(count) + "篇")
        #         #关闭
        #         driver.find_element_by_xpath("//DIV[@class='right-bar']/DIV[@class='close']").click()
        #
        #     try:
        #         driver.find_element_by_xpath("//DIV[@class='paginator-right ng-scope']/A[@class='paginator-element nextPage']/I").click()
        #     except Ex.NoSuchElementException:
        #         break

        return neweparper

    def run(self):
        api = self.api

        # 获取token
        ret = api.gettoken()
        if not ret:
            return 0

        # 从网页中获取发行日期
        print("获取时间")
        publishedtime = self.deal_publishtime(str(self.get_publishtimes()))

        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)

        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：" + self.newspapername + "-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            # 数据加到数据库
            print("开始采集：" + self.newspapername)
            print("正在采集新闻……")

            # 调用采集方法
            try:
                data = self.getpaper(url = self.login_get_href())
            except Exception as e:
                driver.close()
                raise e
            super().uploaddata(publishedtime, data, self.newspaperlibraryid, True)
            print("采集成功:" + self.newspapername + "-发行日期（" + publishedtime + "),文章数量（" + str(len(data)) + "）")
        return len(data)

    #补录
    def supplement(self):
        api = self.api

        # 获取token
        ret = api.gettoken()
        if not ret:
            return 0

        #id date
        paper_id,paper_date = self.get_input_paper_id()

        # 从网页中获取发行日期
        print("获取时间")
        publishedtime = paper_date

        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)

        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：" + self.newspapername + "-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            # 数据加到数据库
            print("开始采集：" + self.newspapername)
            print("正在采集新闻……")

            # 调用采集方法
            try:
                data = self.getpaper(paper_id)
            except Exception as e:
                driver.close()
                raise e
            super().uploaddata(publishedtime, data, self.newspaperlibraryid, True)
            print("采集成功:" + self.newspapername + "-发行日期（" + publishedtime + "),文章数量（" + str(len(data)) + "）")
        return len(data)

    def get_input_paper_id(self):
        paper_id = input("输入报纸id 如（href='/webreader/767015'的 767015）")
        date = input("输入报纸的时间 如（2019-01-01）")

        return paper_id,date

# if __name__ == '__main__':
#     # newe = Sueddeutsche()
#     # p = newe.get_publishtimes()
#     # print(p)
#     # p = newe.deal_publishtime(str(p))
#     # print(p)