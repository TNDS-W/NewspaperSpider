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

class Thesundaytimes(Spider):
    newspapername = '泰晤士星期天'
    newspaperlibraryid = '1045864910875000832'
    proxy = {"http": "http://127.0.0.1:8124", "https": "https://127.0.0.1:8124"}

    #时间处理
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

    # 路径处理
    def deal_href(self,article_id):
        pattern = '\'.*\''
        article_id = re.findall(pattern, article_id)
        article_id = article_id[0].replace("'", '')
        return article_id

    #获得时间和文章的id
    def get_article_id_and_publishtime(self):
        global driver
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')

        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(
            "https://login.thesundaytimes.co.uk/?gotoUrl=http://epaper.thesundaytimes.co.uk:80/epaper/pageview.aspx?cid=1163")
        # 窗口最大化
        driver.maximize_window()
        # 登陆
        driver.find_element_by_id('username').send_keys('13574827001@163.com')
        driver.find_element_by_id('password').send_keys('Yyy123456')
        driver.find_element_by_id('Submit').click()
        time.sleep(3)
        # 获取时间
        publishtime = driver.find_element_by_xpath("//span[@id='calendar_menu_title']").text

        # 跳转iframe
        driver.switch_to.frame('content_frame')

        time.sleep(2)

        # 文章
        arttitle = driver.find_elements_by_xpath(
            "//DIV[@id='pagepanel']/DIV[@class='layout_blocks']/DIV[@class='layout_block_title layout_block_inactive']")

        time.sleep(2)

        arttitle[len(arttitle) - 2].click()

        driver.switch_to.frame('content_window_frame_elm')

        time.sleep(2)
        btnforward = driver.find_elements_by_xpath(
            "//DIV[@id='artMain']/DIV/DIV[@class='art-storyorder']/A[@class='button-big button-big-back']")

        article_id = btnforward[1].get_attribute('href')

        article_id = self.deal_href(article_id)
        publishtime = self.EtoCtime(publishtime)

        driver.close()
        return publishtime, article_id

    # 频道和版面获取与处理
    def thetimes_page(self, publishtime):
        resp = requests.get(
            'https://r.prcdn.co/res/services/GetTOC.ashx?issue=1163' + publishtime + '00000000001001')

        pattern = re.compile(r"toc[A,P,S]{1}?\(.*\)")

        data = re.finditer(pattern, resp.text)

        page = ""
        page_channel = ""
        data_page = {}
        for pc in data:
            fb = pc.group()
            # print(fb)
            if "tocP" in fb:
                fb = self.del_page(fb)
                page = fb

            if "tocS" in fb:
                fb = self.del_channel(fb)
                page_channel = fb

            if "tocA" in fb:
                fb = self.del_title(fb)
                data_page[fb] = page + '#' + page_channel

        return data_page

    def del_page(self, data):
        pattern = (r"\(.*\)")

        m = re.findall(pattern, data)

        kh = m[0]
        kh = kh.replace("(", "")
        kh = kh.replace(")", "")
        return kh

    def del_channel(self, data):
        pattern = (r"\".*\"")

        m = re.findall(pattern, data)

        kh = m[0]
        kh = kh.replace('"', "")
        kh = kh.replace("'", "")
        return kh

    def del_title(self, data):
        pattern = (r',".*",')

        data = re.findall(pattern, data)

        kh = data[0]
        kh = kh.replace(',"', "")
        kh = kh.replace('",', "")

        return kh

    # requests 采集
    def requests_get_paper(self,publishtime, article_id):
        # 报纸集合
        neweparper = []

        publishtime = publishtime.replace("-", "")

        # 获取频道和版面
        data_page_channel = self.thetimes_page(publishtime)

        if data_page_channel:
            pass
        else:
            return neweparper

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
            "Cookie": 'lng=en; AProfile=ezvOOANR1K87wGz7SpLii84OgDovuRKEAgAAAhZRGw==; Profile=9BTXih2sYv8JUQ+K2tUYZmvouyKSxPwZpwY2q7REOYc8ODPUtwwEDJpHU/HyM9HH; PDAuth=DsJESOnPsFTDQ9ZttZLzt4ptPlaEFYPTBMJEYoPYh2I=; currentLng=en; psid=1024361965; __evo_thetimes={%22passthroughParams%22:{}%2C%22exitScreen%22:false%2C%22hot%22:true%2C%22autoSent%22:true}; login_event_fired=false; _ga=GA1.3.1809618322.1546565464; _ncg_id_=165a7c57adf-3e6cba18-c686-4ed6-97fc-0cb44910d66c; _ncg_g_id_=2da24b07-1cdf-4d83-8459-ae74609915d2; _ncg_sp_id.ff8a=f7eb5f5c-ab58-4f81-af5f-c73273e3ac89.1546565464.1.1546565466.1546565464.dd5a618f-b3d4-4690-baec-0047af28392c; __qca=P0-1200298675-1546565465547; __evo_thetimes_sid=m0TvrfUoylFPe2GT0ki4c0z6kkx7iFkr; __evo_thetimes_ip=60c36e8b11cd280ec460830315959d2d; __evo_thetimes_uid=197026437; OptanonAlertBoxClosed=2019-01-04T01:31:12.166Z; RT="sl=1&ss=1546565448927&tt=20417&obo=0&bcn=%2F%2F0dfab5ec.akstat.io%2F&sh=1546565469352%3D1%3A0%3A20417&dm=thetimes.co.uk&si=db0aa8d7-ffe5-43b0-bfd8-4fdebf654194&ld=1546565469353&nu=https%3A%2F%2Fwww.thetimes.co.uk%2Ftto%2Fpapers.do&cl=1546565470428&r=https%3A%2F%2Fwww.thetimes.co.uk%2F&ul=1546565470457&hd=1546565473538"; nukt_hc=1546565462508|||3; utag_main=v_id:016661de3a850002591e3c766cea03073001b06b00bd0$_sn:21$_ss:0$_st:1546567275193$_pn:2%3Bexp-session$ses_id:1546565462508%3Bexp-session$_gaprevpagename:homepage%3Bexp-1546569062764$_gaprevpagetype:homepage%3Bexp-1546569062765$_gaprevpagesection:homepage%3Bexp-1546569062766$_prevpage:barrier%20page%3Athe%20times%3A%3Aacquisition%20store%3A%3Athe%20times%20acquisition%20store%3Bexp-1546569075202; eupubconsent=BAAAAAAOZ0ynhAcABBENBr-AAAAht5_PXbnCJ4Th1P51NkQjACqACIACwAQAAsIAAEICAAgBCIEAQBIAgQAAAIZAQABwRAhAGgARQCiCsG-VOg99pN3ogAA; OptanonConsent=landingPath=NotLandingPage&datestamp=Fri+Jan+04+2019+09%3A31%3A15+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=3.6.25&EuOnly=false&groups=1%3A1%2C0_138456%3A1%2C0_138455%3A1%2C2%3A1%2C3%3A1%2C4%3A1%2C0_142811%3A1&AwaitingReconsent=false; nuk_customer_location=UK; iam_tgt=C%3DCN%3AA%3D1%3AG%3D2; livefyre_token=eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJuZXdzaW50IiwiZGlzcGxheV9uYW1lIjoic2h1IHllIiwidXNlcl9pZCI6IkFBQUEwMjEyNTYxNzAiLCJkb21haW4iOiJ0bmwuZnlyZS5jbyIsImV4cGlyZXMiOiIxNTYyMTE3NDg4LjUyMCJ9.hEPrK08ti-2jXX5EccRl5OmqIh45Soz-n2EHjKFr45Y; acs_tnl=tid%3D47aa8e9b-270e-46c2-9e5d-e220d4c2a402%26eid%3DAAAA021256170%26e%3D1%26a%3Dc2h1IHll%26u%3Db1b65fd1-3be6-4149-a4d3-300265294388%26t%3D1546565487%26h%3D72d0c83dd962cc8e6cf0a9f200e27232; ASP.NET_SessionId=rps4ultg3s2xn5rm5tl5ava1; _acnt=74813695; __utmc=1; __utmz=1.1546565506.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=1.1809618322.1546565464.1546820734.1546824514.5; s_pers=%20s_nr%3D1545363931564%7C1547955931564%3B%20s_visit%3D1%7C1546826388310%3B; s_sess=%20s_cc%3Dtrue%3B%20cmm%3D%257Bchannel%253A%2527Other%2520Websites%2527%252Ckeyword%253A%2527n/a%2527%252Cpartner%253A%2527Other%2520Websites%2527%252Creferrer%253A%2527http%253A//epaper.thetimes.co.uk/epaper/HomePageRedir.aspx%253Fdate%253D7.1.2019%2526width%253D1920%2527%252CcampaignId%253A%2527n/a%2527%257D%3B%20s_camp_dedupe%3DOther%2520Websites%3B%20s_sq%3D%3B; __utmb=1.12.10.1546824514'
        }

        count = 0

        # publishtime, article_id = self.get_article_id_and_publishtime()

        while True:
            url = "http://epaper.thesundaytimes.co.uk/epaper/showarticle.aspx?article=" + article_id + "&issue=1163" + publishtime + "00000000001001"

            #多次连接
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

            imageslist = "#".join(images)

            imagesdescriptionslist = "#".join(imagesdescriptions)

            titlelist = titlelist.strip().replace("\n", "")
            # 频道和版面
            if titlelist:
                title = title[0].strip()
                title = title.replace("\n", "")

                page_and_channel = data_page_channel[title]
                page_and_channel = page_and_channel.split("#")
                pagelist = page_and_channel[0]
                channellist = page_and_channel[1]
            # print(pagelist + "#" + channellist)

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


            if titlelist:
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

    def getpaper(self ,publishtime, article_id):
        return self.requests_get_paper(publishtime, article_id)

    # selenium 获得时间
    def selenium_get_pubtimes(self):
        global driver
        url = 'https://login.thesundaytimes.co.uk/?gotoUrl=http://epaper.thesundaytimes.co.uk:80/epaper/pageview.aspx?cid=1163'

        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        chrome_options.add_argument("--proxy-server=http://127.0.0.1:8124")

        driver = webdriver.Chrome(chrome_options=chrome_options)

        driver.get(url)

        # 窗口最大化
        driver.maximize_window()

        # 登陆
        driver.find_element_by_id('username').send_keys('13574827001@163.com')
        driver.find_element_by_id('password').send_keys('Yyy123456')
        driver.find_element_by_id('Submit').click()
        time.sleep(3)

        publishtime = driver.find_element_by_xpath("//span[@id='calendar_menu_title']").text

        # print(publishtime)
        # driver.close()
        return publishtime

    # selenium 采集
    def selenium_get_paper(self):
        # 报纸集合
        neweparper = []

        # 站点的电子报路径    泰晤士报
        # url = 'https://login.thesundaytimes.co.uk/?gotoUrl=http://epaper.thesundaytimes.co.uk:80/epaper/pageview.aspx?cid=1163'

        # chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('log-level=3')
        # chrome_options.add_argument("--proxy-server=http://127.0.0.1:8124")

        # 声明驱动
        # driver = webdriver.Chrome(chrome_options=chrome_options)

        # 声明等待
        wait = WebDriverWait(driver, 10)

        # 鼠标行动
        actions = ActionChains(driver)

        # 访问站点
        # driver.get(url)

        # # 窗口最大化
        # driver.maximize_window()
        #
        # # 登陆
        # driver.find_element_by_id('username').send_keys('13574827001@163.com')
        # driver.find_element_by_id('password').send_keys('Yyy123456')
        # driver.find_element_by_id('Submit').click()

        # 电子报纸首页
        # 跳转iframe
        driver.switch_to.frame('content_frame')
        while True:
            # 随意选择一篇
            wait.until(EC.presence_of_element_located((By.XPATH,
                                                       "//DIV[@id='pagepanel']/DIV[@class='layout_blocks']/DIV[@class='layout_block_title layout_block_inactive']")))
            arttitle = driver.find_elements_by_xpath(
                "//DIV[@id='pagepanel']/DIV[@class='layout_blocks']/DIV[@class='layout_block_title layout_block_inactive']")
            if arttitle:
                time.sleep(1)
                arttitle[len(arttitle) - 1].click()
                break
            else:
                driver.find_element_by_id("pagecurv_ru").click()

        time.sleep(1.5)
        driver.switch_to.frame('content_window_frame_elm')

        while True:
            try:
                driver.find_elements_by_xpath(
                    "//DIV[@id='artMain']/DIV/DIV[@class='art-storyorder']/A[@class='button-big button-big-back']")[1].click()
            except IndexError:
                break

        # 取内容
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

            # 取值
            try:
                wait.until(EC.presence_of_all_elements_located((By.XPATH,
                                                               "//DIV[@id='artMain']/DIV/DIV[@class='art-storyorder']/A[@class='button-big button-big-forward']")))
            except Ex.TimeoutException:
                pass
            try:
                title = driver.find_element_by_xpath("//DIV[@class='art-content']//H1")
            except Ex.NoSuchElementException:
                title = ''
            try:
                subtitle = driver.find_element_by_xpath("//DIV[@class='art-content']//H2")
            except Ex.NoSuchElementException:
                subtitle = ''
            try:
                author = driver.find_element_by_xpath("//UL[@class='art-meta']//LI[last()]")
            except Ex.NoSuchElementException:
                author = ''
            try:
                mainbody = driver.find_elements_by_xpath("//DIV[contains(@class,'clear')]/DIV/P")
            except Ex.NoSuchElementException:
                mainbody = ''
            try:
                images = driver.find_elements_by_xpath(
                    "//SPAN[@id='artObjectWrap']/A/IMG | //SPAN[@id='artObject2']/A/IMG")
            except Ex.NoSuchElementException:
                images = ''
            try:
                imagesdescriptions = driver.find_elements_by_xpath("//SPAN[@class='art-imagetext']")
            except Ex.NoSuchElementException:
                imagesdescriptions = ''

            # 打印，数据处理
            # 标题
            if title:
                titlelist = titlelist + title.text
                # print(titlelist)
            if subtitle:
                # 副标题
                try:
                    subtitlelist = subtitlelist + subtitle.text
                except Ex.StaleElementReferenceException:
                    subtitlelist = ''
                # print(subtitlelist)
            # 作者
            if author:
                try:
                    author = author.text
                    if author == 'The Times' or author == 'The Sunday Times':
                        authorlist = ''
                    else:
                        authorlist = authorlist + author
                except Ex.StaleElementReferenceException:
                    authorlist = ''
                # print(authorlist)
            # 正文
            if mainbody:
                try:
                    for mb in mainbody:
                        mainbodylist = mainbodylist + "<p>" + mb.text + "</p>"
                except Ex.StaleElementReferenceException:
                    mainbodylist = ''
                # print(mainbodylist)
            # 图片
            if images:
                try:
                    for im in images:
                        imageslist = imageslist + im.get_attribute('src') + "#"
                    imageslist = imageslist[:-1]
                except Ex.StaleElementReferenceException:
                    imageslist = ''
                # print(imageslist)
            # 图片描述
            if imagesdescriptions:
                try:
                    for imd in imagesdescriptions:
                        imagesdescriptionslist = imagesdescriptionslist + imd.text + "#"
                except Ex.StaleElementReferenceException:
                    imagesdescriptionslist = ''
                imagesdescriptionslist = imagesdescriptionslist[:-1]
                # print(imagesdescriptionslist)

            driver.switch_to.default_content()
            driver.switch_to.frame("content_frame")
            page = driver.find_element_by_xpath("//SPAN[@id='content_window_title']")
            channel = driver.find_element_by_xpath("//SPAN[@id='content_window_title']")

            # 版面
            page = page.text
            m = re.finditer('[0-9]+', page)
            pg = ''
            for mm in m:
                pg = mm.group(0)
            pagelist = pagelist + pg
            # print(pagelist)
            # 频道
            channel = channel.text
            n = re.finditer('(([A-Za-z]+\s)+|[A-Za-z]+)+', channel)
            cl = ''
            for nn in n:
                cl = nn.group()
            channellist = channellist + cl
            # print(channellist)

            driver.switch_to.frame("content_window_frame_elm")

            # #续版
            # while True:
            #     try:
            #         xb = driver.find_element_by_xpath("//a[@class='to']")
            #     except Ex.NoSuchElementException:
            #         break
            #     if "See page" in xb.text:
            #         xb.click()
            #
            #         time.sleep(2)
            #
            #         # 取值
            #         try:
            #             wait.until(EC.presence_of_all_elements_located((By.XPATH,
            #                                                             "//DIV[@id='artMain']/DIV/DIV[@class='art-storyorder']/A[@class='button-big button-big-forward']")))
            #         except Ex.TimeoutException:
            #             pass
            #         try:
            #             title = driver.find_element_by_xpath("//DIV[@class='art-content']//H1")
            #         except Ex.NoSuchElementException:
            #             title = ''
            #         try:
            #             subtitle = driver.find_element_by_xpath("//DIV[@class='art-content']//H2")
            #         except Ex.NoSuchElementException:
            #             subtitle = ''
            #         try:
            #             author = driver.find_element_by_xpath("//UL[@class='art-meta']//LI[last()]")
            #         except Ex.NoSuchElementException:
            #             author = ''
            #         try:
            #             mainbody = driver.find_elements_by_xpath("//DIV[contains(@class,'clear')]/DIV/P")
            #         except Ex.NoSuchElementException:
            #             mainbody = ''
            #         try:
            #             images = driver.find_elements_by_xpath(
            #                 "//SPAN[@id='artObjectWrap']/A/IMG | //SPAN[@id='artObject2']/A/IMG")
            #         except Ex.NoSuchElementException:
            #             images = ''
            #         try:
            #             imagesdescriptions = driver.find_elements_by_xpath("//SPAN[@class='art-imagetext']")
            #         except Ex.NoSuchElementException:
            #             imagesdescriptions = ''
            #
            #         # 打印，数据处理
            #         # 标题
            #         if title:
            #             titlelist = titlelist + '#' + title.text
            #             # print(titlelist)
            #         if subtitle:
            #             # 副标题
            #             try:
            #                 subtitlelist = subtitlelist + '#' + subtitle.text
            #             except Ex.StaleElementReferenceException:
            #                 subtitlelist = ''
            #             # print(subtitlelist)
            #         # 作者
            #         if author:
            #             try:
            #                 author = author.text
            #                 if author == 'The Times' or author == 'The Sunday Times':
            #                     authorlist = ''
            #                 else:
            #                     authorlist = authorlist + '#' + author
            #             except Ex.StaleElementReferenceException:
            #                 authorlist = ''
            #             # print(authorlist)
            #         # 正文
            #         if mainbody:
            #             try:
            #                 for mb in mainbody:
            #                     mainbodylist = mainbodylist + "<p>" + mb.text + "</p>"
            #             except Ex.StaleElementReferenceException:
            #                 mainbodylist = ''
            #             # print(mainbodylist)
            #         # 图片
            #         if images:
            #             try:
            #                 for im in images:
            #                     imageslist = imageslist + '#' + im.get_attribute('src') + "#"
            #                 imageslist = imageslist[:-1]
            #             except Ex.StaleElementReferenceException:
            #                 imageslist = ''
            #             # print(imageslist)
            #         # 图片描述
            #         if imagesdescriptions:
            #             try:
            #                 for imd in imagesdescriptions:
            #                     imagesdescriptionslist = imagesdescriptionslist + '#' + imd.text + "#"
            #             except Ex.StaleElementReferenceException:
            #                 imagesdescriptionslist = ''
            #             imagesdescriptionslist = imagesdescriptionslist[:-1]
            #             # print(imagesdescriptionslist)
            #
            #         driver.switch_to.default_content()
            #         driver.switch_to.frame("content_frame")
            #         page = driver.find_element_by_xpath("//SPAN[@id='content_window_title']")
            #         channel = driver.find_element_by_xpath("//SPAN[@id='content_window_title']")
            #
            #         # 版面
            #         page = page.text
            #         m = re.finditer('[0-9]+', page)
            #         pg = ''
            #         for mm in m:
            #             pg = mm.group(0)
            #         pagelist = pagelist + '#' + pg
            #         # print(pagelist)
            #         # 频道
            #         channel = channel.text
            #         n = re.finditer('(([A-Za-z]+\s)+|[A-Za-z]+)+', channel)
            #         cl = ''
            #         for nn in n:
            #             cl = nn.group()
            #         channellist = channellist + '#' + cl



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
            time.sleep(2)
            try:
                driver.find_elements_by_xpath(
                    "//DIV[@id='artMain']/DIV/DIV[@class='art-storyorder']/A[@class='button-big button-big-forward']")[1].click()
            except IndexError:
                break

        # 推出登陆
        driver.switch_to.default_content()
        driver.find_element_by_id('signin').click()
        driver.close()
        return neweparper

    def run(self):

        api = self.api

        # 获取token
        ret = api.gettoken()
        if not ret:
            return 0

        #获取时间
        print("获取时间")
        # requests
        try:
            publishtimes,article_id = self.get_article_id_and_publishtime()
        except Exception as e:
            driver.close()
            raise e
        # # selenium
        # publishtimes = self.selenium_get_pubtimes()

        # 从网页中获取发行日期
        publishedtime = publishtimes

        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)

        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败："+self.newspapername+"-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            # 数据加到数据库
            print("开始采集：" + self.newspapername)
            print("正在采集新闻")
            # 采集数据
            #requests
            newdata = self.getpaper(publishtimes,article_id)
            # selenium
            # newdata = self.selenium_get_paper()


            super().uploaddata(publishedtime, newdata, self.newspaperlibraryid, True)
            print("采集成功:"+self.newspapername+"-发行日期（" + publishedtime + "),文章数量（" + str(len(newdata)) + "）")
        return len(newdata)

    def supplement(self):

        api = self.api

        # 获取token
        ret = api.gettoken()
        if not ret:
            return 0

        #获取时间
        print("获取时间")
        # requests

        publishtimes,article_id = self.get_paper_date_and_id()

        # # selenium
        # publishtimes = self.selenium_get_pubtimes()

        # 从网页中获取发行日期
        publishedtime = publishtimes

        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)

        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败："+self.newspapername+"-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            # 数据加到数据库
            print("开始采集：" + self.newspapername)
            print("正在采集新闻")
            # 采集数据
            #requests
            newdata = self.getpaper(publishtimes,article_id)
            # selenium
            # newdata = self.selenium_get_paper()


            super().uploaddata(publishedtime, newdata, self.newspaperlibraryid, True)
            print("采集成功:"+self.newspapername+"-发行日期（" + publishedtime + "),文章数量（" + str(len(newdata)) + "）")
        return len(newdata)

    def get_paper_date_and_id(self):
        actricle_id = input("输入第一篇文章的文章id如（javascript:showArticle('31de1ba3-1105-408c-bd76-533f12e92a04',1) 是31de1ba3-1105-408c-bd76-533f12e92a04）")
        paper_pubdate = input("报纸的时间 如（2019-01-01）")

        return paper_pubdate,actricle_id


# if __name__ == '__main__':
#     art = Thesundaytimes().gatherpaper()
#     print(art['publishtime'])
#     print(len(art['newepaper']))