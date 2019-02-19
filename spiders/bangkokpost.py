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

class Bangkokpost(Spider):
    # 报纸id
    newspapername = '曼谷邮报'
    newspaperlibraryid = '1049921042123849728'
    proxy = {"http": "http://127.0.0.1:8124", "https": "https://127.0.0.1:8124"}

    #获取时间
    def get_time(self):
        global driver
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')

        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get('http://bangkokpost.newspaperdirect.com/epaper/viewer.aspx')
        time.sleep(2)
        driver.switch_to.frame("content_frame")
        # 发布时间
        publishtime =  driver.find_element_by_xpath(
            "//div[@id='mainPanel']/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div[1]/div/a[2]").text

        # ISSUE_ID = driver.find_element_by_xpath("//table[@rules='none']//tr/td/a/@onclick").text

        # driver.close()
        return publishtime

    # 采集报纸
    def getnewepaper(self,url = 'http://bangkokpost.newspaperdirect.com/epaper/viewer.aspx'):
        # 报纸集合
        neweparper = []

        # 站点的电子报路径    曼谷邮报
        # url = 'http://bangkokpost.newspaperdirect.com/epaper/viewer.aspx'

        # chrome_options = Options()
        # # chrome_options.add_argument('--headless')
        # # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('log-level=3')
        # chrome_options.add_argument("--proxy-server=http://127.0.0.1:8124")
        # # 声明驱动
        #
        # driver = webdriver.Chrome(chrome_options=chrome_options)

        # 声明等待
        wait = WebDriverWait(driver, 10)

        # 鼠标行动
        actions = ActionChains(driver)

        # 访问站点
        driver.get(url)

        # 窗口最大化
        driver.maximize_window()

        #登陆
        driver.find_element_by_id('signin').click()
        time.sleep(2)
        driver.find_element_by_id('_ctl0__ctl0_MainContentPlaceHolder_MainPanel__ctl4_login__ctl0_UserName').send_keys(
            '13574827001@163.com')
        driver.find_element_by_id('_ctl0__ctl0_MainContentPlaceHolder_MainPanel__ctl4_login__ctl0_Password').send_keys(
            'Yyy123456')
        driver.find_element_by_id('login_existing_user_login_btn').click()

        #选择报纸

        try:
            wait.until(EC.presence_of_element_located((By.ID,"content_frame")))
        except EC.NoSuchFrameException:
            time.sleep(1)

        driver.switch_to.frame("content_frame")
        time.sleep(2)
        driver.find_element_by_xpath("//div[@id='mainPanel']/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div[1]/div/a[2]").click()

        # 电子报首页
        driver.switch_to.default_content()

        # 进入第一篇文章
        wait.until(EC.presence_of_element_located((By.XPATH,"//A[@id='toc_icon']/SPAN")))
        table = driver.find_element_by_xpath("//A[@id='toc_icon']/SPAN")
        actions.move_to_element(table).perform()
        time.sleep(2)
        actions.move_to_element(driver.find_element_by_xpath("//DIV[@id='toc_menubody']//TBODY/TR[1]")).perform()
        time.sleep(1)
        driver.find_element_by_xpath("//DIV[@id='toc_submenu_menubody']/DIV[2]/A").click()
        # actions.release()

        # 文章
        driver.switch_to.frame("content_frame")
        driver.switch_to.frame("content_window_frame_elm")
        nextbtn = driver.find_elements_by_xpath(
            "//DIV[@class='art-storyorder']/A[@class='button-big button-big-forward']")

        # 取文章内容
        count = 0
        while True:
            time.sleep(2)
            # 内容
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

            ##取值
            try:
                title = driver.find_element_by_xpath("//DIV[@id='artMain']/DIV/H1")
            except Ex.NoSuchElementException:
                title = ''
            # print(type(title))
            try:
                subtitle = driver.find_element_by_xpath("//DIV[@class='clear']/DIV/H2")
            except Ex.NoSuchElementException:
                subtitle = ''
            try:
                author = driver.find_element_by_xpath("//UL[@class='art-meta']/LI[4]")
            except Ex.NoSuchElementException:
                author = ''
            try:
                mainbody = driver.find_elements_by_xpath("//DIV[@class='clear']/DIV/P")
            except Ex.NoSuchElementException:
                pass
            try:
                images = driver.find_elements_by_xpath("//DIV[@class='clear']/DIV/SPAN//IMG")
            except Ex.NoSuchElementException:
                pass
            try:
                imagesdescriptions = driver.find_elements_by_xpath("//SPAN[@class='art-imagetext']")
            except Ex.NoSuchElementException:
                pass

            # 打印，数据处理
            # 标题
            if title:
                titlelist = titlelist + title.text
            # print(titlelist)
            # 副标题
            if subtitle:
                try:
                    subtitlelist = subtitlelist + subtitle.text
                except Ex.StaleElementReferenceException:
                    subtitlelist = ''
                # print(subtitlelist)
            # 作者
            if author:
                try:
                    authorlist = re.sub("^[Bb][Yy]","",authorlist + author.text)
                except Ex.StaleElementReferenceException:
                    authorlist = ''
                # print(authorlist)
            # 正文
            try:
                for mb in mainbody:
                    mainbodylist = mainbodylist + "<p>" + mb.text + "</p>"
            except Ex.StaleElementReferenceException:
                mainbodylist = ''
            # print(mainbodylist)
            # 图片
            try:
                for im in images:
                    imageslist = imageslist + im.get_attribute('src') + "#"
                imageslist = imageslist[:-1]
            except Ex.StaleElementReferenceException:
                imageslist = ''
            # print(imageslist)
            # 图片描述
            try:
                for imd in imagesdescriptions:
                    imagesdescriptionslist = imagesdescriptionslist + imd.text + "#"
                imagesdescriptionslist = imagesdescriptionslist[:-1]
            except Ex.StaleElementReferenceException:
                imagesdescriptionslist = ''
            # print(imagesdescriptionslist)

            driver.switch_to.default_content()
            driver.switch_to.frame("content_frame")
            page = driver.find_element_by_xpath("//SPAN[@id='content_window_title']")
            channel = driver.find_element_by_xpath("//SPAN[@id='content_window_title']")

            # 版面
            page = page.text
            pattern = r'[A-Z]+[0-9]+|[0-9]+'
            page = re.findall(pattern,page)
            page = "".join(page)
            pagelist = pagelist + page
            # print(pagelist)

            # 频道
            channel = channel.text
            pattern = r'[A-Z]+[0-9]+|[0-9]+'
            channel = re.sub(pattern,"" ,channel)
            channel = "".join(channel)

            channel = channel.replace(" | ","#")
            channel = channel.replace(" & ", "#")
            channel = channel.strip()

            channellist = channellist + channel
            # print(channellist)

            # 保存到文章字典
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
            count += 1
            print("采集了" + str(count) + "篇")

            driver.switch_to.frame("content_window_frame_elm")

            # 下一篇
            time.sleep(2)
            try:
                driver.find_elements_by_xpath(
                    "//DIV[@class='art-storyorder']/A[@class='button-big button-big-forward']")[1].click()
            except IndexError:
                break
        #推出登陆
        driver.switch_to.default_content()
        driver.find_element_by_id('signin').click()

        driver.close()

        return neweparper

    # 时间处理
    def EtoCtime(self, publishtimes):
        Etime = {
            "Jan": '01',
            "Feb": '02',
            "Mar": '03',
            "Apr": '04',
            "May": '05',
            "June": '06',
            "July": '07',
            "Aug": '08',
            "Sept": '09',
            "Oct": '10',
            "Nov": '11',
            "Dec": '12'
        }

        tp = publishtimes.split(" ")

        day = tp[0]

        if int(day) < 10:
            day = "0" + day

        publishtime = "%s-%s-%s" % (tp[2], Etime[tp[1]], day)
        return publishtime

        tp = publishtimes.split(" ")

        publishtime = "%s-%s-%s" % (tp[2], Etime[tp[1]], tp[0])
        return publishtime

    def run(self):
        print("开始采集：" + self.newspapername)
        api = self.api
        ret = api.gettoken()
        if not ret:
            return 0

        # 从网页中获取发行日期
        try:
            publishedtime = self.EtoCtime(self.get_time())
        except Exception as e:
            driver.close()
            raise e
        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败："+self.newspapername+"-发行日期已经存在，报纸日期（" + publishedtime + ")")
            driver.close()
            return 0
        else:
            # 数据加到数据库
            print("正在采集新闻……")
            try:
                newdata = self.getnewepaper()
            except Exception as e:
                driver.close()
                raise e
            super().uploaddata(publishedtime, newdata, self.newspaperlibraryid, True)
            print("采集成功:"+self.newspapername+"-发行日期（" + publishedtime + "),文章数量（" + str(len(newdata)) + "）")
            return len(newdata)

    #补录
    def supplement(self):
        print("开始采集：" + self.newspapername)
        api = self.api
        ret = api.gettoken()
        if not ret:
            return

        #选择补录的日期
        publishedtime,arcle_id = self.get_paper_date_and_id()

        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败："+self.newspapername+"-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return
        else:
            # 数据加到数据库
            print("正在采集新闻……")

            newdata = self.requests_get_paper(publishedtime,arcle_id)

            super().uploaddata(publishedtime, newdata, self.newspaperlibraryid, True)
            print("采集成功:"+self.newspapername+"-发行日期（" + publishedtime + "),文章数量（" + str(len(newdata)) + "）")

    # requests 采集
    def requests_get_paper(self, publishtime, article_id):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
            "Cookie": 'authreq2=798dfa10-e3cd-e811-93fd-0a94ef441a1f; currentLng=en; lng=en; AProfile=Q+aKOAM6PG8wRRzRTp3oOmPKt2Uf4AKwKgAABcVWGw==; Profile=UkcIea0xkPpaQTlXW6w0idlcQE93xhE8YveTV+xK7TcRCRWLuJboG76GJlnjjyho; PDAuth=zzNFyOuwhGF2hMbof6pTWwh3YsRp7y5pVdYXtWAiVTk=; psid=1024644870; homepage_settings_4=; _sp_id.ca34=c5c7e718f41ed842.1538963306.23.1543387716.1542760400; ASP.NET_SessionId=vdtjj1y1knd41whizujbmoz0; _acnt=75109971; __utma=1.392816917.1546911167.1546911167.1546911167.1; __utmc=1; __utmz=1.1546911167.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1;',
            "Proxy-Connection" : 'keep-alive'
        }

        count = 0
        # 报纸集合
        neweparper = []
        # publishtime, article_id = self.get_article_id_and_publishtime()
        publishtime = publishtime.replace("-", "")
        while True:
            url = "http://bangkokpost.newspaperdirect.com/epaper/showarticle.aspx?article=" + article_id + "&issue=1264" + publishtime + "00000000001001"
            # 多次连接
            count_get = 0
            while count_get < 4:
                resp = requests.get(url, headers=headers, proxies=self.proxy)
                if resp.status_code == 200:
                    break
                print("连接" + str(count_get) + "次")
                count_get += 1

            html = etree.HTML(resp.text)

            # 内容
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

            # 文章内容
            title = html.xpath("//div[@class='art-content']//h1/text()")
            subtitle = html.xpath("//div[@class='art-content']//h2/text()")
            author = html.xpath("//ul[@class='art-meta']//li[last()]/text()")
            mainbody = html.xpath("//div[contains(@class,'clear')]/div/p")
            images = html.xpath("//span[@id='artObjectWrap']/a/img/@src|//span[@id='artObject2']/a/img/@src")
            imagesdescriptions = html.xpath("//SPAN[@class='art-imagetext']//text()")

            # 数据处理
            titlelist = "".join(title)

            subtitlelist = "".join(subtitle)

            author = "".join(author)
            if author == 'The Times' or author == 'The Sunday Times':
                authorlist = ''
            else:
                authorlist = author

            for mb in mainbody:
                from_page = mb.xpath(".//text()")
                if from_page:
                    s = " ".join(from_page)
                    mainbodylist = mainbodylist + "<p>" + s + "</p>"
                else:
                    mainbodylist = mainbodylist + "<p>" + mb.text + "</p>"
            if len(re.findall('<p>',mainbodylist)) == 1 and len(mainbody) == 1:
                text = etree.tostring(mainbody[0]).decode('utf-8', 'ignore').replace('.','</p><p>')
                mainbodylist = re.sub('<p>\s*</p>','',text)

            imageslist = "#".join(images)

            imagesdescriptionslist = "#".join(imagesdescriptions)

            # 保存到文章字典
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

            # 计数
            count = count + 1
            print(self.newspapername + "采集：" + str(count) + "篇")
            # 下一篇文章路径
            try:
                href = html.xpath("(//a[@class='button-big button-big-forward'])[1]/@href")
                article_id = self.deal_href(href[0])
            except IndexError:
                break
        return neweparper

    # 路径处理
    def deal_href(self, article_id):
        pattern = '\'.*\''
        article_id = re.findall(pattern, article_id)
        article_id = article_id[0].replace("'", '')
        return article_id

    # #查找存在
    # def get_exist_paper(self):
    #     global driver
    #     chrome_options = Options()
    #     # chrome_options.add_argument('--headless')
    #     # chrome_options.add_argument('--disable-gpu')
    #     chrome_options.add_argument('log-level=3')
    #
    #     driver = webdriver.Chrome(chrome_options=chrome_options)
    #
    #     # driver.get('http://bangkokpost.newspaperdirect.com/epaper/viewer.aspx')
    #     #
    #     #
    #     # driver.maximize_window()
    #     # time.sleep(2)
    #     # driver.switch_to.frame("content_frame")
    #     #
    #     # # 发布时间
    #     # driver.find_element_by_xpath(
    #     #     "//div[@id='mainPanel']/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div[1]/div/a[2]").click()
    #     #
    #     # time.sleep(2)
    #     #
    #     # ActionChains(driver).move_to_element(driver.find_element_by_xpath("//a[@id='cal-button']")).perform()
    #     #
    #     # time.sleep(1)
    #     #
    #     # driver.find_element_by_id("cal-button").click()
    #     #
    #     # time.sleep(2)
    #     #
    #     # ISSUE_ID = driver.find_elements_by_xpath("//table[@rules='none']//tr/td/a/@onclick")
    #     #
    #     # exist_publishtimes = []
    #     #
    #     # for data in ISSUE_ID:
    #     #     exist_publishtimes.append(self.del_paper_date(data.text))
    #     #
    #     # # driver.close()
    #     # print(exist_publishtimes)
    #     # return exist_publishtimes
    #
    # #处理时间和id
    # def del_paper_date(self,issue_id):
    #     issue_id = re.findall(r'[0-9]+',issue_id)
    #
    #     issue_id = issue_id[0]
    #
    #     issue_id = issue_id[4:12]
    #
    #     year = issue_id[0:4]
    #     month = issue_id[4:6]
    #     day = issue_id[6:8]
    #
    #     date = "%s-%s-%s" % (year, month, day)
    #
    #     return date

    #输出日期，选择
    def get_paper_date_and_id(self):
        actricle_id = input("输入第一篇文章的文章id如（javascript:showArticle('f17f30bf-8a1f-457b-b05e-bc4542944e0e',1) 是f17f30bf-8a1f-457b-b05e-bc4542944e0e）")
        paper_pubdate = input("报纸的时间 如（2019-01-01）")

        return paper_pubdate,actricle_id

# if __name__ == '__main__':
#    ap =  Bangkokpost().get_time()
#    print(ap)
#    # for c in ap:
#    #     print(c)
