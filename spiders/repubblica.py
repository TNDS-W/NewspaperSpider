import requests,re,json,time,datetime
from spiders.basespider import Spider
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from spiders.basespider import Spider
from lxml import etree

# 作者：文振乾
# 时间：2018-12-27
# 用途：爬取共和国报

class Repubblica(Spider):
    message = []    # 存储所有信息
    newspaperlibraryid = "1060353518197538816"
    proxy = {"http": "http://127.0.0.1:8124", "https": "https://127.0.0.1:8124"}
    number = 1


    def log_in(self):
        global driver
        url = 'https://www.repubblica.it/social/sites/repubblica/nazionale/login.php?landing=true&forward=false&origin=&urlToken=repnzfree&backurl=https%3A%2F%2Fquotidiano.repubblica.it%2Fedicola%2Fmanager%3Fservice%3Dlogin.social'
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        options.add_argument('log-level=3')
        options.add_argument("--proxy-server=http://127.0.0.1:8124")
        driver = webdriver.Chrome(chrome_options=options)
        print("正在登陆：共和国报")
        driver.get(url)
        # 登陆网页
        WebDriverWait(driver,15).until(expected_conditions.presence_of_element_located((By.XPATH,'//input[@name="userid"]')))
        driver.find_element_by_xpath('//input[@name="userid"]').send_keys("13574827001@163.com")
        driver.find_element_by_xpath('//input[@name="userpw"]').send_keys("Yyy123456")
        time.sleep(0.2)
        driver.find_element_by_id("loginsubmit").click()
        time.sleep(3)
        result = driver.page_source
        html = etree.HTML(result)
        times = "".join(html.xpath('//a[@class="select-1"]/span/text()')).split(" ")[0]
        # print(times)
        publishedtime = times.split(".")[2] + "-" + times.split(".")[1] + "-" + times.split(".")[0]
        try:
            driver.find_element_by_xpath('//div[@class="blocco-1 nws_bkg"]/a').click()
        except:
            driver.refresh()
            time.sleep(5)
            driver.find_element_by_xpath('//div[@class="blocco-1 nws_bkg"]/a').click()
        time.sleep(2)
        cookies = driver.get_cookies()
        driver.close()

        cookie = []
        for x in cookies:
            cookie.append(x["name"] + "=" + x["value"])
        cookie = ";".join(cookie)
        if cookie == "":
            self.log_in()
        # print(cookie)
        print("登陆成功")
        return cookie,publishedtime

    def geturls(self,cookie,publishedtime):
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Cookie': cookie
        }
        url = 'http://quotidiano.repubblica.it/edizionerepubblica/scripts/get_timone.php?testata=REP&issue=' + "".join(publishedtime.split("-")) + '&edizione=nazionale'
        domain_name = 'http://quotidiano.repubblica.it/edizionerepubblica/pw/data/'
        try:
            response = requests.get(url, headers=header)
        except:
            response = requests.get(url, headers=header)
        result = response.text
        xml = re.findall('<xml><!\[CDATA\[(.*?.xml)]]></xml>', result)
        urls = []
        for x in xml:
            urls.append(domain_name + x)
        # print(urls)
        return urls

    #补录调用
    def supplement_geturl(self,cookie,publishedtime):

        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Cookie': cookie
        }
        url = 'http://quotidiano.repubblica.it/edizionerepubblica/scripts/get_timone.php?testata=REP&issue=' + "".join(
            publishedtime.split("-")) + '&edizione=nazionale'
        domain_name = 'http://quotidiano.repubblica.it/edizionerepubblica/pw/data/'
        try:
            response = requests.get(url, headers=header)
        except:
            response = requests.get(url, headers=header)
        result = response.text
        xml = re.findall('<xml><!\[CDATA\[(.*?.xml)]]></xml>', result)
        urls = []
        for x in xml:
            urls.append(domain_name + x)
        # print(urls)
        return urls

    def parsepage(self,urls,cookie):
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Cookie': cookie
        }
        for x in range(len(urls)):
            page = str(x + 1)
            try:
                response = requests.get(urls[x], headers=header, proxies=self.proxy)
            except:
                response = requests.get(urls[x], headers=header, proxies=self.proxy)
            result = response.content.decode("utf-8")
            article = re.findall('<Articolo.*?>([\d\D]+?)</Articolo>',result)
            for art in article:
                #标题
                title = "".join(re.findall("<Titolo[\d\D]*?<span>([\d\D]+?)</span>",art))
                if title == "":
                    continue
                #频道
                channel = "".join(re.findall('<Sezione\s.*?>\s*?<!\[CDATA\[(.*?)]]>',art))

                #副标题
                subTitle = "".join(re.findall('<Sottotitolo[\d\D]*?<span>([\d\D]+?)</span>',art))

                #作者
                author = "".join(re.findall('<Firma[\d\D]*?<span.*?>([\d\D]+?)</span>',art))
                if re.search(",$",author):
                    author = author.replace(",","")
                else:
                    author = author.replace(",","#")

                #正文
                content = re.findall('<Testo[\d\D]*?<span.*?>([\d\D]+?)]]>',art)
                mainbody = []
                for cont in content:
                    body = "<p>" + cont.replace("<span>","").replace("</span>","") + "</p>"
                    mainbody.append(body)
                mainbody = "".join(mainbody)
                self.message.append({"title": title, "subTitle": subTitle, "author": author, "authorArea": "",
                 "authorDescriptions": "", "abstract": "",
                 "channel": channel, "mainBody": mainbody, "page": page,
                 "images": '', "imageDescriptions": '', "cookies": "",
                 "referer": ""})
                print("第" + str(self.number) + "篇采集完成")
                self.number += 1
                # print((title,channel))

    def message_clean(self, messages):
        message = []

        for x in range(len(messages)):
            right = True
            for y in range(x, len(messages)):
                if x == y:
                    continue
                if messages[x]["title"] == messages[y]["title"]:
                    if messages[x]["mainBody"][0] == messages[y]["mainBody"][0]:
                        if messages[y]["page"] not in messages[x]["page"]:
                            messages[y]["page"] = messages[x]["page"] + "#" + messages[y]["page"]
                        if (messages[y]["channel"] not in messages[x]["channel"]) and (messages[x]["channel"] not in messages[y]["channel"]):
                            messages[y]["channel"] = messages[x]["channel"] + "#" + messages[y]["channel"]
                        # messages[y]["page"] = "".join(set(messages[y]["page"].split("#")))
                        right = False
                        break
            if right:
                message.append(messages[x])

        return message

    def run(self):
        self.message = []
        api = self.api
        # 获取token信息
        ret = api.gettoken()
        if not ret:
            return 0

        try:
            log = self.log_in()
        except Exception as e:
            driver.close()
            raise e
        # 从网页中获取发行日期
        publishedtime = log[1]
        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：共和国报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            print("开始采集:共和国报")
            print("正在采集新闻")
            try:
                urls = self.geturls(log[0],log[1])
                self.parsepage(urls,log[0])
            except Exception as e:
                self.message = []
                raise e
            messages = self.message_clean(self.message)
            for mess in range(len(messages)):
                messages[mess]["page"] = "#".join(list(set(messages[mess]["page"].split("#"))))
            # time.sleep(3)
            super().uploaddata(publishedtime, messages, self.newspaperlibraryid, True)
            print("采集成功:共和国报-发行日期（" + publishedtime + "),文章数量（" + str(len(messages)) + "）")
        return len(messages)

    #补录
    def supplement(self):
        api = self.api
        # 获取token信息
        ret = api.gettoken()
        if not ret:
            return 0

        try:
            log = self.log_in()
        except Exception as e:
            driver.close()
            raise e
        # 从网页中获取发行日期
        datenumber = input("请输入要补录的时间：")
        oneday = datetime.timedelta(days=1)
        publishedtime = datetime.datetime.strptime(datenumber,'%Y-%m-%d')
        for x in range(18):
            # 判断报纸是否存在
            ret = api.checknewspaperexists(self.newspaperlibraryid, str(publishedtime).split(" ")[0])
            # 如果为True,则说明已经存在
            if (ret["success"] and ret["result"]):
                print("采集失败：共和国报-发行日期已经存在，报纸日期（" + str(publishedtime).split(" ")[0] + ")")
                return 0
            else:
                print("开始采集:共和国报")
                print("正在采集新闻")
                urls = self.supplement_geturl(log[0], str(publishedtime).split(" ")[0])
                # time.sleep(3)
                self.parsepage(urls, log[0])
                messages = self.message_clean(self.message)
                for mess in range(len(messages)):
                    messages[mess]["page"] = "#".join(list(set(messages[mess]["page"].split("#"))))
                super().uploaddata(str(publishedtime).split(" ")[0], messages, self.newspaperlibraryid, True)
                print("采集成功:共和国报-发行日期（" + str(publishedtime).split(" ")[0] + "),文章数量（" + str(len(messages)) + "）")
                self.message = []
                publishedtime += oneday

        # publishedtime = input("请输入日期(2018-01-01)：")
        # # 判断报纸是否存在
        # ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # # 如果为True,则说明已经存在
        # if (ret["success"] and ret["result"]):
        #     print("采集失败：共和国报-发行日期已经存在，报纸日期（" + publishedtime + ")")
        #     return 0
        # else:
        #     print("开始采集:共和国报")
        #     print("正在采集新闻")
        #     urls = self.geturls(log[0], publishedtime)
        #     self.parsepage(urls, log[0])
        #     # time.sleep(3)
        #     super().uploaddata(publishedtime, self.message, self.newspaperlibraryid, True)
        #     print("采集成功:共和国报-发行日期（" + publishedtime + "),文章数量（" + str(len(self.message)) + "）")
        #     self.message = []
