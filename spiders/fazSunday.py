from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import selenium.common.exceptions as Ex
from spiders.basespider import Spider
import time
import re
from selenium.webdriver.chrome.options import Options
import requests
from lxml import etree

class FazSunday(Spider):
    newspapername = "法兰克福汇报(星期天)"
    newspaperlibraryid = '1055718503497072640'
    proxy = {"http": "http://127.0.0.1:8124", "https": "https://127.0.0.1:8124"}

    #获得时间
    def get_times(self):
        resp = requests.get('http://epaper.faz.net/',proxies=self.proxy)
        html = etree.HTML(resp.text)
        new_href = html.xpath("//div[@class='row newspapers-row']/div[5]//a[@class='btn dropdown-toggle']/text()")
        return str(new_href[0])

    # 时间处理
    def timedate(self, timesdata):
        it = re.finditer('[0-9]+', timesdata)
        datalist = []
        for datet in it:
            datalist.append(datet.group())
        timestring = "%s-%s-%s" % (datalist[2], datalist[1], datalist[0])
        return timestring

    # 登陆
    def login_get_href(self):
        global driver
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        # chrome_options.add_argument("--proxy-server=http://127.0.0.1:8124")
        driver = webdriver.Chrome(chrome_options=chrome_options)

        url = "http://epaper.faz.net/"

        # 声明等待
        wait = WebDriverWait(driver, 10)

        # 鼠标行动
        actions = ActionChains(driver)

        driver.get(url)

        driver.maximize_window()

        # 登陆
        actions.move_to_element(
            driver.find_element_by_xpath("//ul/li[1]/button[@class='btn btn-link']")).click().perform()
        # driver.find_element_by_xpath("//ul/li[1]/button[@class='btn btn-link']").click()
        actions.release()
        time.sleep(2)

        driver.find_element_by_xpath("//input[@name='loginName']").send_keys("lizhuoqun")
        driver.find_element_by_xpath("//input[@name='password']").send_keys("Yyy123456")
        driver.find_element_by_xpath("//input[@class='form-submit-btn']").click()

        try:
            wait.until(EC.element_to_be_clickable(
                (By.XPATH, "(//div[@class='day']/div[@class='row']//div[@class='issue__wrapper'])[1]")))
        except Ex.TimeoutException:
            driver.refresh()
        count = 0
        while count < 4 :
            try:
                new_href = driver.find_element_by_xpath(
                    "//div[@class='row newspapers-row']/div[5]//div[@class='newspaper-cover-inner']/a").get_attribute('href')
                break
            except Ex.NoSuchElementException:
                driver.refresh()
                count += 1

        # print(str(new_href))
        driver.close()

        if new_href:
            new_href = str(new_href).split('/')
            new_href = new_href[len(new_href) - 1]

        return new_href

    # requests 采集 包的数据完整 但版面有些不对
    def requests_get_paper(self,url):
        # 报纸集合
        neweparper = []

        url = "https://faz.s4p-iapps.com/pdf/published/company/137/pdfplace/1171/files/" + url + "/" + url + "-media.json"

        resp = requests.get(url, proxies=self.proxy)

        data = resp.json()

        datalen = len(data)

        count = 0
        for pagenum in range(datalen):

            if data[str(pagenum + 1)] is None:
                continue

            for art in data[str(pagenum + 1)]:
                # 文章
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

                title = art['hauptzeile']
                subtitle = art['unterzeile']
                abstract = art['teaser']
                channel = art['rubrik']
                mainbody = art['text']
                if art['vorspann'] != "":
                    if art['vorspann'] != art['teaser']:
                        mainbody = mainbody + "<p>" + art['vorspann'] + "</p>"

                page = art['page']

                titlelist = titlelist + title
                if not titlelist:
                    continue
                abstractlist = abstractlist + abstract
                if 'Von' in subtitle:
                    authorlist = authorlist + subtitle
                else:
                    subtitlelist = subtitlelist + subtitle
                # subtitlelist = subtitle
                # authorlist = author
                channellist = channellist + channel
                pagelist = pagelist + str(page)
                mainbodylist = mainbodylist + mainbody

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
                neweparper.append(artpage)
                count = count + 1
                print(self.newspapername + "采集 ：" + str(count) + "篇")
        return neweparper

    # selenium 采集 拿不到版面
    def faznewpaper(slef):
        # 报纸集合
        neweparper = []

        # 站点的电子报路径    法兰克福汇报
        url = 'http://epaper.faz.net/'

        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        chrome_options.add_argument("--proxy-server=http://127.0.0.1:8124")
        driver = webdriver.Chrome(chrome_options=chrome_options)

        # 声明等待
        wait = WebDriverWait(driver, 10)

        # 鼠标行动
        actions = ActionChains(driver)

        # 窗口最大化
        driver.maximize_window()

        # 访问站点
        driver.get(url)

        # 登陆
        actions.move_to_element(
            driver.find_element_by_xpath("//ul/li[1]/button[@class='btn btn-link']")).click().perform()
        # driver.find_element_by_xpath("//ul/li[1]/button[@class='btn btn-link']").click()
        actions.release()
        time.sleep(2)

        driver.find_element_by_xpath("//input[@name='loginName']").send_keys("lizhuoqun")
        driver.find_element_by_xpath("//input[@name='password']").send_keys("Yyy123456")
        driver.find_element_by_xpath("//input[@class='form-submit-btn']").click()

        # 进入电子报
        # driver.minimize_window()
        time.sleep(2)
        while True:
            try:
                driver.find_element_by_xpath("//DIV[@class='row newspapers-row']/DIV[1]//DIV[@class='newspaper-cover-inner']/A").click()
                break
            except Ex.NoSuchFrameException:
                driver.refresh()
        while True:
            try:
                wait.until(EC.element_to_be_clickable((By.XPATH, "//A[@class='paginator-element nextPage']")))
                nextbtn = driver.find_element_by_xpath("//A[@class='paginator-element nextPage']")
                break
            except Ex.TimeoutException:
                driver.refresh()

        count = 0
        while (nextbtn != None):
            time.sleep(3)
            # 文章列表
            artpage = driver.find_elements_by_xpath("//DIV[@class='availableBox ng-scope']/DIV[@class='avBoxContainer ng-scope']/DIV")

            # 获取文章
            for ap in artpage:
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

                #图片
                # nowtime = time.strftime("%Y%m%d.%H.%M.%D")
                # driver.get_screenshot_as_file("D:\\work\\图片\\新建文件夹\\faz\\%s.png" % nowtime)

                # 进入文章
                try:
                    ap.click()
                except Exception:
                    continue

                    # 采集文章内容
                try:
                    title = driver.find_element_by_id("avHauptzeile")
                except Ex.NoSuchElementException:
                    title = ''
                # try:
                #     subtitle = driver.find_elements_by_id("avUnterzeile")
                # except Ex.NoSuchElementException:
                #     subtitle=''
                try:
                    author = driver.find_element_by_id("avAutorzeile")
                except Ex.NoSuchElementException:
                    author=''
                try:
                    channel = driver.find_element_by_id("avIssueTitle")
                except Ex.NoSuchElementException:
                    channel = ''
                try:
                    subtitle = driver.find_elements_by_xpath("//*[@id='avTeaser']")
                except Ex.NoSuchElementException:
                    subtitle = ''
                try:
                    mainbody = driver.find_elements_by_xpath("//*[@id='avText']/p")
                except Ex.NoSuchElementException:
                    mainbody = ''

                print("-->采集第" + str(count + 1) + "篇文章<--")

                # if not title.text:
                #     # 关闭文章框
                #     driver.find_element_by_xpath("//DIV[@class='close']").click()
                #     continue

                # 内容保存到集合
                if title:
                    titlelist = titlelist + (title.text)
                    if titlelist == "":
                        continue

                if subtitle:
                    for st in subtitle:
                        subtitlelist = subtitlelist + st.text

                # if abstracts:
                #     for ab in abstracts:
                #         abstractlist = abstractlist + ab.text


                if channel:
                    channel = channel.text
                    channel = channel.split('- ')
                    channellist = channel[1]
                    authorlist = authorlist + author.text

                if subtitlelist:
                    if mainbody:
                        for mb in mainbody[:-1]:
                            mainbodylist = mainbodylist + ("<p>" + mb.text + "</p>")


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
                            'cookies' : '',
                            'referer' : ''
                           }

                try:
                    # 关闭文章框
                    driver.find_element_by_xpath("//DIV[@class='close']").click()
                except Exception:
                    pass

                neweparper.append(artpage)
                count += 1
            try:
                driver.find_element_by_xpath("//A[@class='paginator-element nextPage']").click()
            except Ex.NoSuchElementException:
                break
        print("一共采集" + str(count) + "篇文章")
        driver.close()
        return neweparper

    def run(self):
        api = self.api

        # 获取token
        ret = api.gettoken()
        if not ret:
            return 0

        # 从网页中获取发行日期
        publishedtime = self.timedate(self.get_times())

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
                data = self.requests_get_paper(self.login_get_href())
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

        paper_id,paper_date = self.get_input_paper_id()

        # 从网页中获取发行日期
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
                data = self.requests_get_paper(paper_id)
            except Exception as e:
                driver.close()
                raise e

            super().uploaddata(publishedtime, data, self.newspaperlibraryid, True)
            print("采集成功:" + self.newspapername + "-发行日期（" + publishedtime + "),文章数量（" + str(len(data)) + "）")
        return len(data)

    def get_input_paper_id(self):
        paper_id = input("输入报纸id 如（href='/webreader/454273'的 454273）")
        date = input("输入报纸的时间 如（2019-01-01）")

        return paper_id,date