from spiders.basespider import Spider
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import datetime


# 作者 杜浩
# 时间 2018-12-06
# 用途 测试蜘蛛

class Newsweek(Spider):
    name = "美国新闻周刊"
    newspaperlibraryid = "1045930963550339072"

    def run(self):
        print("开始采集：" + self.name)
        api = self.api
        ret = api.gettoken()
        if not ret:
            return 0

        newDate = self.getNewDate()
        s_publishedtime = datetime.datetime.now().strftime('%Y-%m-%d')
        publishedtime = newDate["date"]
        if self.compare_time(publishedtime, s_publishedtime):
            print(self.name + "本期内容未更新完！")
            return 0
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        if (ret["success"] and ret["result"]):
            print("采集失败：" + self.name + "-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            print("正在采集新闻……")
            datalist = self.getNewArticles(newDate)
            super().uploaddata(publishedtime, datalist, self.newspaperlibraryid, True)
            print("采集成功：" + self.name + "-发行日期（" + publishedtime + "),文章数量（" + str(len(datalist)) + "）")
        return len(datalist)

    def supplement(self):
        print("开始补录采集：" + self.name)
        api = self.api
        ret = api.gettoken()
        if not ret:
            return 0

        date = input("请输入报刊发布日期（例：2018-11-09）:")
        newDateUrl = "https://www.newsweek.com/" + date.replace("-", "/") + "/issue.html"
        newDate = {"newDateUrl": newDateUrl, "date": date}
        s_publishedtime = datetime.datetime.now().strftime('%Y-%m-%d')
        publishedtime = newDate["date"]
        if self.compare_time(publishedtime, s_publishedtime):
            print(self.name + "本期内容未更新完！")
            return 0
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        if (ret["success"] and ret["result"]):
            print("补录采集失败：" + self.name + "-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            print("正在补录采集新闻……")
            datalist = self.getNewArticles(newDate)
            super().uploaddata(publishedtime, datalist, self.newspaperlibraryid, True)
            print("补录采集成功：" + self.name + "-发行日期（" + publishedtime + "),文章数量（" + str(len(datalist)) + "）")
        return len(datalist)

    # 获取最新期刊日期
    def getNewDate(self):
        # driver = webdriver.Chrome()

        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('log-level=3')
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get('https://www.newsweek.com/archive')
        newDateUrl = driver.find_element_by_xpath(
            "//ul[@class='magazine-archive-items row']/li[1]/date/a").get_attribute("href")
        date = str(newDateUrl).replace("https://www.newsweek.com/", "").replace("/issue.html", "").replace("/", "-")
        driver.close()
        return {"newDateUrl": newDateUrl, "date": date}

    # 获取最新期刊数据
    def getNewArticles(self, getNewDate):
        articleUrls = []
        retNewArticles = []
        driver = webdriver.Chrome()

        # chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('log-level=3')
        # driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(getNewDate["newDateUrl"])
        articleUrlList = driver.find_elements_by_xpath(
            "//div[@class='content']//article//h1/a|//div[@class='content']//article//h2/a|//div[@class='content']//article//h3/a|//div[@class='content']//article//h4/a")
        for articleUrl in articleUrlList:
            print(articleUrl.text+"/t"+articleUrl.get_attribute("href"))
            articleUrls.append(articleUrl.get_attribute("href"))

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
            driver.get(articleUrl)

            # 新闻标题
            title = driver.find_element_by_xpath("//header[@class='article-header']/h1").text
            print("-->采集第" + str(count + 1) + "篇文章<--")
            newArticle["title"] = title
            # print("新闻标题：" + title)

            # 新闻作者
            author = ""
            try:
                author = driver.find_element_by_xpath("//div[@class='byline']//span/a/span").text
            except Exception:
                pass
            newArticle["author"] = author
            # print("新闻作者：" + author)

            # 新闻频道
            channel = ""
            try:
                channel = driver.find_element_by_xpath("//div[@class='filed-under flex-xs flex-wrap ai-c']/a[1]").text
            except Exception:
                pass
            newArticle["channel"] = channel
            # print("新闻频道：" + channel)

            # 新闻正文
            mainBody = ""
            try:
                mainBodyListXpath = driver.find_elements_by_xpath("//div[contains(@class,'article-body')]/p")
            except Exception:
                pass
            else:
                for mainBodyXpath in mainBodyListXpath:
                    try:
                        img = mainBodyXpath.find_element_by_tag_name("span")
                        continue
                    except Exception:
                        pass
                    if mainBodyXpath.text != "":
                        mainBody += "<p>" + str(mainBodyXpath.text).replace("\n", "") + "</p>"
            newArticle["mainBody"] = mainBody
            # print("新闻正文：" + mainBody)

            # 新闻图片
            images = ""
            try:
                imagesListXpath = driver.find_elements_by_xpath(
                    "//figure//img|//div[contains(@class,'article-body')]/p//img")
            except Exception:
                pass
            else:
                for imagesXpath in imagesListXpath:
                    images += str(imagesXpath.get_attribute("src")) + "#"
            newArticle["images"] = images
            # print("新闻图片：" + images)

            # 图片描述
            imagesDescription = ""
            try:
                imagesDescriptionListXpath = driver.find_elements_by_xpath(
                    "//figcaption|//div[contains(@class,'article-body')]/p//span[@class='embed-image']")
            except Exception:
                pass
            else:
                for imagesDescriptionXpath in imagesDescriptionListXpath:
                    imagesDescription += str(imagesDescriptionXpath.text).replace("\n", "") + "#"
            newArticle["imageDescriptions"] = imagesDescription
            # print("新闻图片描述：" + imagesDescription)

            count += 1
            retNewArticles.append(newArticle)
        driver.close()
        print("一共采集" + str(count) + "篇文章")
        return retNewArticles

    def compare_time(self,time1, time2):
        s_time = time.mktime(time.strptime(time1, '%Y-%m-%d'))
        e_time = time.mktime(time.strptime(time2, '%Y-%m-%d'))
        return int(s_time) > int(e_time)

# if __name__ == '__main__':
#     # getDate=Newsweek("dh","123").getNewDate()
#     # Newsweek("dh","123").getNewArticles(getDate)
#     Newsweek("dh","123").supplement()
