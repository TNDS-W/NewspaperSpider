import requests,time,re,datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from lxml import etree
from spiders.basespider import Spider

class Economist(Spider):
    newspaperlibraryid = "1049469261988233216"
    url = 'https://www.economist.com'
    message = []
    proxy = {"https":"https://127.0.0.1:8124","http":"http://127.0.0.1:8124"}
    months = {
        "Jan": "01",
        'Feb': "02",
        'Mar': "03",
        'Apr': "04",
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Aug': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': "12"
    }

    # 登陆
    def log_in(self):
        global driver
        options = Options()
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        options.add_argument('log-level=3')
        options.add_argument("--proxy-server=http://127.0.0.1:8124")
        driver = webdriver.Chrome(chrome_options=options)
        print("正在登陆")
        driver.get(self.url)
        driver.set_page_load_timeout(100)
        WebDriverWait(driver,5).until(EC.visibility_of_element_located((By.XPATH,'//div[@class="navigation__user-menu"]//a[@target="_blank"]'))).click()
        # driver.find_element_by_xpath('//div[@class="navigation__user-menu"]//a[@target="_blank"]').click()
        time.sleep(0.5)
        driver.find_element_by_xpath('//li[@class="navigation__user-menu-linklist-item"]/button[@type="submit"]').click()
        # 进入登陆界面
        driver.find_elements_by_class_name('css-1iyl08k')[0].send_keys("13574827001@163.com")
        driver.find_elements_by_class_name('css-1iyl08k')[1].send_keys("Yyy123456")
        time.sleep(0.5)
        driver.find_element_by_id('submit-login').click()
        cookies = driver.get_cookies()
        cookie = []
        for x in cookies:
            cookie.append(x["name"] + "=" + x["value"])
        cookie = "; ".join(cookie)
        # print(cookie)
        driver.close()
        print('登陆成功')
        return cookie

    #获取最新一期的所有新闻
    def getnews(self,cookie):
        year = datetime.datetime.now().year
        periodicalurl = "https://www.economist.com/printedition/covers?print_region=76975&date_filter%5Bvalue%5D%5Byear%5D=" + str(year)
        header = {
            'cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
        }
        try:
            response = requests.get(url=periodicalurl, headers=header, proxies=self.proxy)
        except:
            response = requests.get(url=periodicalurl, headers=header, proxies=self.proxy)

        result = response.content.decode("utf-8")
        html = etree.HTML(result)
        #获取发行日期
        try:
            times = html.xpath('//div[@class="center cover-creation"]/span[@class="date-display-single"]/text()')[0]
        except IndexError:
            year = int(year) - 1
            periodicalurl = "https://www.economist.com/printedition/covers?print_region=76975&date_filter%5Bvalue%5D%5Byear%5D=" + str(year)
            header = {
                'cookie': cookie,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
            }
            try:
                response = requests.get(url=periodicalurl, headers=header, proxies=self.proxy)
            except:
                response = requests.get(url=periodicalurl, headers=header, proxies=self.proxy)

            result = response.content.decode("utf-8")
            html = etree.HTML(result)
            times = html.xpath('//div[@class="center cover-creation"]/span[@class="date-display-single"]/text()')[0]

        year = times.split(" ")[2]
        month = self.months[times.split(" ")[0]]
        day = "".join(re.findall("([0-9]{,2})",times.split(" ")[1]))
        if len(day) == 1:
            day = "0" + day
        publishedTime = "-".join([year,month,day])

        newspaperurl = self.url + html.xpath('//div[@class="print-cover-image"]/a/@href')[0]
        try:
            response1 = requests.get(url=newspaperurl, headers=header, proxies=self.proxy)
        except:
            response1 = requests.get(url=newspaperurl, headers=header, proxies=self.proxy)

        result1 = response1.content.decode("utf-8")
        html1 = etree.HTML(result1)
        news = html1.xpath('//ul[@class="list"]/li/a[@itemprop="url"]/@href')
        newsurls = []
        for x in range(len(news)):
            urls = self.url + news[x]
            newsurls.append(urls)
        # print(newsurls)
        return newsurls,publishedTime

    def supplement_getnews(self,cookie):
        header = {
            'cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
        }
        date = input("请输入要补录的新闻日期(例:2018-01-01):")
        newspaperurl = input("请输入要补录的报纸url(例:https://www.economist.com/printedition/2018-12-08):")
        try:
            response1 = requests.get(url=newspaperurl, headers=header, proxies=self.proxy)
        except:
            response1 = requests.get(url=newspaperurl, headers=header, proxies=self.proxy)

        result1 = response1.content.decode("utf-8")
        html1 = etree.HTML(result1)
        news = html1.xpath('//ul[@class="list"]/li/a[@itemprop="url"]/@href')
        newsurls = []
        for x in range(len(news)):
            urls = self.url + news[x]
            newsurls.append(urls)
        # print(newsurls)
        return newsurls, date

    #解析页面
    def parsepage(self,newsurls,cookie):
        header = {
            'cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        }
        for x in range(len(newsurls)):

            time.sleep(1)
            imageDescriptions = [""]
            mainbody = []
            i = 0
            while i<5:
                try:
                    response = requests.get(url=newsurls[x], headers=header, proxies=self.proxy)
                    break
                except:
                    i += 1
            result = response.content.decode("utf-8")
            html = etree.HTML(result)
            print("第" + str(x+1) + '篇采集完成')
            #标题
            titles = html.xpath('//h1[@class="flytitle-and-title__body"]/span/text()')
            if len(titles) == 1:
                title = "".join(titles)
            else:
                titles[0],titles[1] = titles[1],titles[0]
                title = "#".join(titles)

            #部分文章没有副标题
            try:
                subTitle = "".join(html.xpath('//p[@class="blog-post__rubric"]/text()'))
            except:
                subTitle = ""

            #作者
            author = ""
            #作者描述
            authorDescriptions = ""
            authorArea = ""
            abstract = ""
            #频道
            channel = html.xpath('//h3[@class="blog-post__section"]/span//text()')[3].replace("| ","")
            #正文
            div_number = html.xpath('//div[@class="blog-post__text"]/p|//div[@class="blog-post__text"]/h2')
            for x in range(len(div_number)):
                content = "".join(html.xpath('(//div[@class="blog-post__text"]/p|//div[@class="blog-post__text"]/h2)['+str(x+1)+']//text()'))
                if content != "":
                    content = "<p>" + content + "</p>"
                    mainbody.append(content)
            try:
                fotter = " ".join(html.xpath('//footer[@itemprop="publication"]//text()'))
                fotter = "<p>" + fotter + "</p>"
                mainbody.append(fotter)
            except:
                pass
            mainbody = "".join(mainbody)
            #图片
            imgs = html.xpath('//div[@class="blog-post__inner"]/div/img/@src|//figure/div/img/@src')
            if len(imgs) <= 1 :
                imgurl = "".join(imgs)
            else:
                imgurl = "#".join(imgs)
            image = html.xpath("//figure")
            for y in range(len(image)):
                try:
                    descriptions = "".join(html.xpath("(//figure)["+str(y)+"]/figcaption//text()"))
                except:
                    descriptions = ""
                imageDescriptions.append(descriptions)

            self.message.append(
                {"title": title, "subTitle": subTitle, "author": author, "authorArea": authorArea,
                 "authorDescriptions": authorDescriptions, "abstract": abstract,
                 "channel": channel, "mainBody": mainbody, "page": "",
                 "images": imgurl, "imageDescriptions": imageDescriptions, "cookies": "",
                 "referer": ""})



    def run(self):
        api = self.api
        # 获取token信息
        ret = api.gettoken()
        if not ret:
            return 0

        try:
            cookies = self.log_in()
        except Exception as e:
            driver.close()
            raise e
        getnew = self.getnews(cookies)
        # 从网页中获取发行日期
        publishedtime = getnew[1]
        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：经济学家-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            print("开始采集:经济学家")
            print("正在采集新闻")
            self.parsepage(getnew[0],cookies)
            super().uploaddata(publishedtime, self.message, self.newspaperlibraryid, True)
            print("采集成功:经济学家-发行日期（" + publishedtime + "),文章数量（" + str(len(self.message)) + "）")
        return len(self.message)

    # 补录
    def supplement(self):
        api = self.api
        # 获取token信息
        ret = api.gettoken()
        if not ret:
            return 0

        try:
            cookies = self.log_in()
        except Exception as e:
            driver.close()
            raise e
        getnew = self.supplement_getnews(cookies)
        # 从网页中获取发行日期
        publishedtime = getnew[1]
        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：经济学家-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            print("开始采集:经济学家")
            print("正在采集新闻")
            self.parsepage(getnew[0], cookies)
            super().uploaddata(publishedtime, self.message, self.newspaperlibraryid, True)
            print("采集成功:经济学家-发行日期（" + publishedtime + "),文章数量（" + str(len(self.message)) + "）")
            self.message = []