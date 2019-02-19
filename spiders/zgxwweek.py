from spiders.basespider import Spider
from selenium import webdriver
from time import sleep
import urllib.request
from selenium.webdriver.chrome.options import Options
import requests
import datetime
import os

# 作者 杜浩
# 时间 2018-12-06
# 用途 测试蜘蛛

class Zgxw_week(Spider):
    name = "中国新闻周刊"
    newspaperlibraryid = "1045862119234338816"

    def requests_get_issue(slef,year):
        data = {
            'magazineguid': '9015A0E8-ECA9-4560-9C5E-317420AEE8F5',
            'year': year,
            'page': '1',
            'pagesize': '12',
            'type': 'GetMagaListByYear'
        }
        resp = requests.post('http://www.qikan.com.cn/Handle/MagazineProcess.ashx', data=data,timeout=20)
        issue = resp.json()
        numberissue = issue['pages']
        year = issue['records'][0]['Year']

        return numberissue, year

    def get_local_issue(slef):
        f = open(os.getcwd()+r'\spiders\newchina.txt', 'r')

        date = f.read()

        date = date.split(' : ')

        year = date[0]

        f.close()

        return date[1], year

    def get_inter_issue(slef,numberissue,year):
        f = open(os.getcwd()+r'\spiders\newchina.txt', 'w')

        # numberissue, year = slef.requests_get_issue(year)

        f.write(str(year) + " : " + str(numberissue))

        f.close()

    def compare_year_issue(slef):
        num, year = slef.get_local_issue()

        num1, year1 = slef.requests_get_issue(year)

        boolean = False

        if int(year) == year1:
            if int(num) == num1:
                boolean = True

        result = {
            'issue': str(num1),
            'year' : str(year1),
            'boolean' : boolean
        }

        return result

    def run(self):
        print("开始采集："+self.name)
        api = self.api

        # 获取token
        ret = api.gettoken()
        if not ret:
            return 0

        # 从网页中获取发行日期
        # newDate = self.getNewDate()
        # publishedtime = newDate["date"]
        result = self.compare_year_issue()
        publishedtime = datetime.datetime.now().strftime('%Y-%m-%d')

        # 判断报纸是否存在
        if result['boolean'] == False:
            # print("不存在")
            ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        else:
            print("采集失败："+self.name+"-发行日期已经存在，报纸年期（" + str(result['year'])+" "+ str(result['issue']) + ")")
            return 0

        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败："+self.name+"-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            print("正在采集新闻……")
            datalist = self.getNewArticles(result)
            super().uploaddata(publishedtime,datalist,self.newspaperlibraryid,False)

            if len(datalist) < 1:
                print("采集成功：" + self.name + "-发行日期（" + publishedtime + "),文章数量（" + str(len(datalist)) + "）")
                print("不修改最新数据的的限定，如果报纸真为零片文章，请人为修改为本次采集最新数据限定如（2018 : 47）即年和期数")
            else:
                print("采集成功："+self.name+"-发行日期（" + publishedtime + "),文章数量（" + str(len(datalist)) + "）")
                self.get_inter_issue(result['issue'],result['year'])
        return len(datalist)

    def supplement(self):
        print("开始补录采集："+self.name)
        api = self.api

        # 获取token
        ret = api.gettoken()
        if not ret:
            return 0

        # 从网页中获取发行日期
        newDate = self.getNewDate()
        publishedtime = newDate["date"]
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)

        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("补录采集失败："+self.name+"-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            print("正在补录采集新闻……")
            datalist = self.getNewArticles(newDate)
            super().uploaddata(publishedtime,datalist,self.newspaperlibraryid,False)
            print("补录采集成功："+self.name+"-发行日期（" + publishedtime + "),文章数量（" + str(len(datalist)) + "）")
        return len(datalist)

    # 获取最新期刊日期
    def getNewDate(self):
        year = input("请输入报刊年份（例：2018）:")
        qiShu = input("请输入报刊期数（例：44）:")
        date = input("请输入报刊发布日期（例：2018-11-09）:")
        result={"year":year,"issue":qiShu,"date":date}
        return result

    # 获取最新期刊数据
    def getNewArticles(self,getNewDate):
        articleUrls = []
        retNewArticles = []
        # driver = webdriver.Chrome()
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get('http://www.qikan.com.cn/account/mymagazines.html')
        driver.set_window_size(1100, 1080)
        driver.find_element_by_id("ContentPlaceHolder1_txtLoginname").send_keys("13574827001@163.com")
        sleep(1)
        driver.find_element_by_id("ContentPlaceHolder1_txtPwd").send_keys("Yyy123456")
        driver.find_element_by_name("ctl00$ContentPlaceHolder1$btnLogin").click()
        #print("登录成功")
        urlStr = "http://www.qikan.com.cn/magdetails/9015A0E8-ECA9-4560-9C5E-317420AEE8F5/" + getNewDate["year"] + "/" + getNewDate["issue"] + ".html"
        driver.get(urlStr)
        # driver.find_element_by_id("wenbenbuy").click()
        articleUrlList = driver.find_elements_by_xpath("//div[@class='catalog2']//a")
        for articleUrl in articleUrlList:
            channelAndUrl = {"channel": "", "url": ""}
            channelAndUrl["url"] = articleUrl.get_attribute("href")
            channelAndUrl["channel"] = str(articleUrl.text).split("丨")[0]
            # print(channelAndUrl)
            articleUrls.append(channelAndUrl)

        count = 0
        for articleUrl in articleUrls:
            newArticle = {
                "title": "",
                "subTitle": "",
                "author": "",
                "authorArea": "",
                "authorDescriptions": "",
                "abstract": "",
                "channel": "",
                "mainBody": "",
                "page": "",
                "images": "",
                "imageDescriptions": "",
                "cookies": driver.get_cookies(),
                "referer": driver.current_url
            }
            driver.get(articleUrl["url"])

            # 新闻标题
            title = driver.find_element_by_xpath("//div[@class='article']/h1").text
            print("-->采集第" + str(count+1) + "篇文章<--")
            newArticle["title"] = title

            # 新闻作者
            author = ""
            try:
                authorXpath = driver.find_element_by_xpath("//div[@class='article']/span/img")
            except Exception:
                pass
            else:
                author = str(authorXpath.get_attribute("src")).replace("http://www.qikan.com.cn/verificationcode/",
                                                                       "").replace(".html", "")
                author = urllib.request.unquote(author).replace("作者+", "").replace("+", "#").replace('　', "#")
            newArticle["author"] = author
            # print("新闻作者：" + author)

            # 新闻频道
            channel = ""
            if articleUrl["channel"] != "":
                channel = articleUrl["channel"]
            newArticle["channel"] = channel
            # print("新闻频道：" + channel)

            # 新闻正文
            mainBody = ""
            try:
                mainBodyNext = driver.find_element_by_xpath(
                    "//div[@class='article']/div[@class='art-pre']/a[@class='surplus']")
            except Exception:
                pass
            else:
                mainBodyNext.click()
                sleep(2)
            mainBodyListXpath = driver.find_elements_by_xpath("//div[@class='article']/div[@class='textWrap']/*")
            for mainBodyXpath in mainBodyListXpath:
                if mainBodyXpath.tag_name == "p" or mainBodyXpath.tag_name == "h3":
                    if mainBodyXpath.text != "":
                        mainBody += "<p>" + mainBodyXpath.text + "</p>"
            newArticle["mainBody"] = mainBody
            #print("新闻正文：" + mainBody)

            # 新闻图片
            images = ""
            try:
                imagesListXpath = driver.find_elements_by_xpath("//div[@class='article']/div[@class='textWrap']//img")
            except Exception:
                pass
            else:
                for imagesXpath in imagesListXpath:
                    imagespath = str(imagesXpath.get_attribute("src"))
                    images += imagespath + "#"
            newArticle["images"] = images
            #print("新闻图片链接：" + images)

            # 图片描述
            imagesDescription = ""
            try:
                imagesDescriptionListXpath = driver.find_elements_by_xpath(
                    "//div[@class='article']/div[@class='textWrap']//figcaption")
            except Exception:
                pass
            else:
                for imagesDescriptionXpath in imagesDescriptionListXpath:
                    imagesDescription += imagesDescriptionXpath.text + "#"
            newArticle["imageDescriptions"] = imagesDescription
            #print("新闻图片描述：" + imagesDescription)
            retNewArticles.append(newArticle)
            count += 1

        print("一共采集" + str(count) + "篇文章")
        driver.close()
        return retNewArticles




# if __name__ == '__main__':
#     Zgxw_week("dh","123").supplement()