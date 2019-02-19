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


class Thetimes(Spider):
    newspapername = '泰晤士报'
    newspaperlibraryid = '1033581158333415424'
    proxy = {"http": "http://127.0.0.1:8124", "https": "https://127.0.0.1:8124"}

    # 路径处理
    def deal_href(self, article_id):
        pattern = '\'.*\''
        article_id = re.findall(pattern, article_id)
        article_id = article_id[0].replace("'", '')
        return article_id

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

    #频道和版面获取与处理
    def thetimes_page(self,publishtime,class_id):
        resp = requests.get('https://r.prcdn.co/res/services/GetTOC.ashx?issue=1148'+ publishtime +'000000' + class_id +'001001')

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

    def del_page(self,data):
        pattern = (r"\(.*\)")

        m = re.findall(pattern, data)

        kh = m[0]
        kh = kh.replace("(", "")
        kh = kh.replace(")", "")
        return kh

    def del_channel(self,data):
        pattern = (r"\".*\"")

        m = re.findall(pattern, data)

        kh = m[0]
        kh = kh.replace('"', "")
        kh = kh.replace("'", "")
        return kh

    def del_title(self,data):
        pattern = (r',".*",')

        data = re.findall(pattern, data)

        kh = data[0]
        kh = kh.replace(',"', "")
        kh = kh.replace('",', "")

        return kh

    # 获得时间和文章的id
    def get_article_id_and_publishtime(self):
        global driver
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        chrome_options.add_argument('log-level=3')

        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(
            "https://login.thetimes.co.uk/?gotoUrl=http://epaper.thetimes.co.uk:80/epaper/viewer.aspx")
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
        time.sleep(2)
        driver.switch_to.frame('content_frame')


        # 文章
        arttitle = driver.find_elements_by_xpath(
            "//DIV[@id='pagepanel']/DIV[@class='layout_blocks']/DIV[@class='layout_block_title layout_block_inactive']")

        time.sleep(5)
        arttitle[len(arttitle) - 2].click()

        driver.switch_to.frame('content_window_frame_elm')

        WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.XPATH,"//DIV[@id='artMain']/DIV/DIV[@class='art-storyorder']/A[@class='button-big button-big-back']")))
        btnforward = driver.find_elements_by_xpath(
            "//DIV[@id='artMain']/DIV/DIV[@class='art-storyorder']/A[@class='button-big button-big-back']")

        article_id = btnforward[1].get_attribute('href')

        driver.close()

        article_id = self.deal_href(article_id)
        publishtime = self.EtoCtime(publishtime)

        return publishtime, article_id

    #requests 采集
    def requests_get_paper(self,publishtime, article_id, class_id):
        # 报纸集合
        neweparper = []

        publishtime = publishtime.replace("-", "")

        #获取频道和版面
        data_page_channel = self.thetimes_page(publishtime,class_id)

        # print(data_page_channel)

        if data_page_channel != {}:
            pass
        else:
            return neweparper

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
            "Cookie": 'lng=en; currentLng=en; AProfile=4UKOOAMi2VF1ONX2Sbd2L/JMb4uquRKEAgAArdZdGw==; Profile=Ee2jKXMOXplQqvT+d8KV92okhuwowF32DyG444CvN78VHnhLAMithPxsu1O1QcjM; PDAuth=NkxK/98FRUfhlG0DW9MluQaHLaUOQG1zqx2o4klDgic=; psid=1026297459; __evo_thetimes={%22passthroughParams%22:{}%2C%22exitScreen%22:false%2C%22hot%22:true%2C%22autoSent%22:true}; ASP.NET_SessionId=vrmhdqv0duiq0uwcqaojozle; _acnt=74813695; nuk_customer_location_hint=UK; login_event_fired=false; _ncg_id_=165a7c57adf-3e6cba18-c686-4ed6-97fc-0cb44910d66c; _ga=GA1.3.151612638.1547372888; _gid=GA1.3.1170315381.1547372888; _ncg_g_id_=2da24b07-1cdf-4d83-8459-ae74609915d2; eupubconsent=BOaVniTOaVniTAcABBENCB-AAAAjV5_PXbnCJ4Th1P51NkQjICqACIACwAQAAsIAAEICAAgBCIEAQBIAgQAAAIZAQABwRAhAGgARQDiCsG-VOgd_5t__3ziXNogA; _ncg_sp_ses.ff8a=*; OptanonConsent=landingPath=https%3A%2F%2Fwww.thetimes.co.uk%2F&datestamp=Mon+Jan+14+2019+08%3A33%3A32+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=4.3.1&EU=false&firstPageView=false; _ncg_sp_id.ff8a=81ed03db-1630-4dd5-9c56-5cb16cd2182d.1547372888.2.1547426013.1547372888.4fc5e7b5-2196-400d-9d04-7601118afa3f; __qca=P0-352857335-1547426013897; nukt_hc=1547426011658|||3; utag_main=v_id:016661de3a850002591e3c766cea03073001b06b00bd0$_sn:31$_ss:1$_st:1547427817630$_pn:1%3Bexp-session$ses_id:1547426011658%3Bexp-session$_gaprevpagename:homepage%3Bexp-1547429611764$_gaprevpagetype:homepage%3Bexp-1547429611765$_gaprevpagesection:homepage%3Bexp-1547429611765$_prevpage:homepage%3A%3Ahomepage%3A%3Ahomepage%3Bexp-1547429611774; ak_bmsc=A8D70DE8CC9D89AACC9A7E3FC361C0F117DF9635DE770000D8D83B5C3AFC5A43~plIh52sRBEwE0JufV3ogRgMRrspQ31IH7pxfThCOzqcdhbfPzMZyaPG8vkRGK1x1i14/J6zpGxp9cl+YyLInykrrO4aZy4dkfVBQ5X0rN1JMgt/erdCTlHXNgHGdiaTcIV1F9AUAZUE2fNe1uO9YgkZwYEdIDhSLsYFjstO+I5Qt/4rr8CrQaIOrjVATX4AzUejScp+u5+jigcjoiVBFXhvseDAwdNNNz1nBbnIGmfoNc7LJZv+r+wFdw1RQmKlJVt; bm_sv=5CEF75318AA36940BB3E7C3A3C7D9B0E~7xAIdNQ+2gmrRVKp4FzIQUYmshCGX0mxRfpi5TfLCHzcLbtu5q78+PuoRBlrjbulx06PA1cdwptiOI0uD+5iDNLZSyiI+6L/7zXmUz++TAuFLiYfL3csGnmhAt4BOeBKQEMqOvOp2d2dRc+WcmMbMbqWHwKxOFc0yp3O0nrhr7g=; RT="sl=1&ss=1547426010642&tt=0&obo=1&sh=1547426017635%3D1%3A1%3A0&dm=thetimes.co.uk&si=fe388af8-2511-4852-a6d7-7c8389a2f0ef&bcn=%2F%2F17d98a5d.akstat.io%2F&nu=https%3A%2F%2Fwww.thetimes.co.uk%2Ftto%2Fpapers.do&cl=1547426017622&ld=1547426017636&r=https%3A%2F%2Fwww.thetimes.co.uk%2F&ul=1547426017638&hd=1547426023161"; __utmt=1; __utma=1.151612638.1547372888.1547426027.1547426027.1; __utmc=1; __utmz=1.1547426027.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); s_sess=%20cmm%3D%257Bchannel%253A%2527Other%2520Websites%2527%252Ckeyword%253A%2527n/a%2527%252Cpartner%253A%2527Other%2520Websites%2527%252Creferrer%253A%2527http%253A//epaper.thetimes.co.uk/epaper/pageview.aspx%253Fissue%253D11482019011200000000001001%2527%252CcampaignId%253A%2527n/a%2527%257D%3B%20s_camp_dedupe%3DOther%2520Websites%3B%20s_cc%3Dtrue%3B%20s_sq%3D%3B; __utmb=1.30.10.1547426027; s_pers=%20s_nr%3D1545363931564%7C1547955931564%3B%20s_visit%3D1%7C1547428338375%3B'
        }
        count = 0
        # publishtime, article_id = self.get_article_id_and_publishtime()
        # url = "http://epaper.thesundaytimes.co.uk/epaper/showarticle.aspx?article=" + article_id + "&issue=11632018122300000000001001"
        while True:
            url = "http://epaper.thetimes.co.uk/epaper/showarticle.aspx?article=" + article_id + "&issue=1148" + publishtime + "000000"+ class_id +"001001"

            # 多次连接
            count_get = 0
            while True:
                try:
                    resp = requests.get(url, headers=headers, proxies=self.proxy)
                    break
                except:
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
            imagesdescriptions = html.xpath("//span[@class='art-imagetext']//text()")

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
            titlelist = titlelist.strip().replace("\n","")
            #频道和版面
            if titlelist:
                title = title[0].strip()
                title = title.replace("\n","")

                page_and_channel = data_page_channel[title]
                page_and_channel = page_and_channel.split("#")
                pagelist = page_and_channel[0]
                channellist = page_and_channel[1]
            # print(pagelist + "#" +channellist)

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
            href = html.xpath("(//a[@class='button-big button-big-forward'])[1]/@href")
            try:
                article_id = self.deal_href(href[0])
            except IndexError:
                break
        return neweparper

    # 采集
    def getpaper(self, publishtime, article_id,class_id):
        return self.requests_get_paper(publishtime, article_id,class_id)
        # return self.selenium_get_paper()

    # selenium 获得时间
    def selenium_get_pubtimes(self):
        global driver
        url = 'http://epaper.thetimes.co.uk/epaper/viewer.aspx'
        driver = webdriver.Chrome()

        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.maximize_window()
        driver.get(url)
        driver.find_element_by_id('username').send_keys('13574827001@163.com')
        driver.find_element_by_id('password').send_keys('Yyy123456')
        driver.find_element_by_id('Submit').click()
        driver.refresh()
        publishtime = driver.find_element_by_xpath("//SPAN[@id='calendar_menu_title']").text
        # driver.close()
        return publishtime

    # selenium 采集报纸
    def selenium_get_paper(self):
        # 报纸集合
        neweparper = []

        # 站点的电子报路径    泰晤士报
        # url = 'http://epaper.thetimes.co.uk/epaper/viewer.aspx'
        # driver = webdriver.Chrome()

        # chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('log-level=3')
        # driver = webdriver.Chrome(chrome_options=chrome_options)
        # driver = webdriver.Chrome()
        # driver.maximize_window()
        # 声明等待
        wait = WebDriverWait(driver, 10)
        # 鼠标行动
        actions = ActionChains(driver)
        # 访问站点
        # driver.get(url)
        # driver.find_element_by_id('username').send_keys('13574827001@163.com')
        # driver.find_element_by_id('password').send_keys('Yyy123456')
        # driver.find_element_by_id('Submit').click()

        # 电子报纸首页
        # 发布时间
        # publishtime = driver.find_element_by_xpath("//SPAN[@id='calendar_menu_title']").text
        # 跳转iframe
        driver.switch_to.frame('content_frame')
        # 随意选择一篇
        wait.until(EC.presence_of_element_located((By.XPATH,
                                                   "//DIV[@id='pagepanel']/DIV[@class='layout_blocks']/DIV[@class='layout_block_title layout_block_inactive']")))
        arttitle = driver.find_elements_by_xpath(
            "//DIV[@id='pagepanel']/DIV[@class='layout_blocks']/DIV[@class='layout_block_title layout_block_inactive']")

        arttitle[len(arttitle) - 1].click()

        time.sleep(2)
        driver.switch_to.frame('content_window_frame_elm')
        time.sleep(2)
        # previous = driver.find_elements_by_xpath(
        #     "//DIV[@id='artMain']/DIV/DIV[@class='art-storyorder']/A[@class='button-big button-big-back']")
        # nextbnt = driver.find_elements_by_xpath(
        #     "//DIV[@id='artMain']/DIV/DIV[@class='art-storyorder']/A[@class='button-big button-big-forward']")

        # 取内容
        y = 0
        while True:
            time.sleep(3)
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

            proxy_error_count = 0
            if title:
                while True:
                    if proxy_error_count > 5:
                        break
                    driver.refresh()
                    proxy_error_count += 1
                    print("刷新" + str(proxy_error_count) + "次")

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
            print("-->采集第" + str(y + 1) + "篇文章<--")

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

            y += 1
            driver.switch_to.frame("content_window_frame_elm")
            try:
                try:
                    wait.until(EC.element_to_be_clickable((By.XPATH, "(//DIV[@id='artMain']/DIV/DIV[@class='art-storyorder']/A[@class='button-big button-big-forward'])[2]")))
                    driver.find_elements_by_xpath(
                        "//DIV[@id='artMain']/DIV/DIV[@class='art-storyorder']/A[@class='button-big button-big-forward']")[
                        1].click()
                    time.sleep(2)
                except Ex.TimeoutException:
                    pass
            except IndexError:
                break

        # 推出登陆
        driver.switch_to.default_content()
        driver.find_element_by_id('signin').click()
        print("一共采集" + str(y) + "篇文章")
        driver.close()
        return neweparper

    def run(self):
        print("开始采集：泰晤士报")
        api = self.api
        ret = api.gettoken()
        if not ret:
            return 0

        print("获取时间")
        # 从网页中获取发行日期
        try:
            publishedtime,article = self.get_article_id_and_publishtime()
            # publishedtime = self.selenium_get_pubtimes()
            # publishedtime = '2019-01-20'
        except Exception as e:
            driver.close()
            raise e
        # print(publishedtime,article)

        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：泰晤士报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            # 数据加到数据库
            print("正在采集新闻……")
            # try:
            #     newdata = self.selenium_get_paper()
            # except Exception as e:
            #     driver.close()
            #     raise e

            class_id = '00'
            while True:
                newdata = self.getpaper(publishedtime,article,class_id)
                if len(newdata) > 1:
                    break
                else:
                    class_id = '51'
            super().uploaddata(publishedtime, newdata, self.newspaperlibraryid, True)
            print("采集成功:泰晤士报-发行日期（" + publishedtime + "),文章数量（" + str(len(newdata)) + "）")
        return len(newdata)

    def supplement(self):
        print("开始采集：泰晤士报")
        api = self.api
        ret = api.gettoken()
        if not ret:
            return 0

        print("获取时间")
        # 从网页中获取发行日期

        publishedtime,article= self.get_paper_date_and_id()

        # print(publishedtime,article)

        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：泰晤士报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            # 数据加到数据库
            print("正在采集新闻……")
            class_id = '00'

            while True:

                newdata = self.getpaper(publishedtime,article,class_id)

                if len(newdata) > 1:
                    break
                else:
                    class_id = '51'
            super().uploaddata(publishedtime, newdata, self.newspaperlibraryid, True)
            print("采集成功:泰晤士报-发行日期（" + publishedtime + "),文章数量（" + str(len(newdata)) + "）")
        return len(newdata)

    def get_paper_date_and_id(self):
        actricle_id = input("输入第一篇文章的文章id如（javascript:showArticle('31de1ba3-1105-408c-bd76-533f12e92a04',1) 是31de1ba3-1105-408c-bd76-533f12e92a04）")
        paper_pubdate = input("报纸的时间 如（2019-01-01）")

        return paper_pubdate,actricle_id

# if __name__ == '__main__':
#     Thetimes().getpubtimes()
