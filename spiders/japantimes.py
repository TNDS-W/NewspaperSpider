from spiders.basespider import Spider
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
import datetime


# 作者 杜浩
# 时间 2018-12-06
# 用途 测试蜘蛛

class Japantimes(Spider):
    name = " 日本时报"
    newspaperlibraryid = "1049098569526542336"

    def run(self):
        print("开始采集：" + self.name)
        api = self.api
        ret = api.gettoken()
        if not ret:
            return 0

        newDate = self.getDate()
        publishedtime = newDate
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        if (ret["success"] and ret["result"]):
            print("采集失败：" + self.name + "-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            print("正在采集新闻……")
            datalist = self.getNewArticles(newDate)
            if len(datalist) < 1:
                print("采集失败：" + self.name + "-发行日期（" + publishedtime + "),没有发布新闻！")
            else:
                super().uploaddata(publishedtime, datalist, self.newspaperlibraryid, True)
                print("采集成功：" + self.name + "-发行日期（" + publishedtime + "),文章数量（" + str(len(datalist)) + "）")
        return len(datalist)

    def supplement(self):
        print("开始补录采集：" + self.name)
        api = self.api
        ret = api.gettoken()
        if not ret:
            return 0

        newDate = input("请输入报刊发布日期（例：2018-11-09）:")
        publishedtime = newDate
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        if (ret["success"] and ret["result"]):
            print("补录采集失败：" + self.name + "-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            print("正在补录采集新闻……")
            datalist = self.getNewArticles(newDate)
            if len(datalist) < 1:
                print("补录采集失败：" + self.name + "-发行日期（" + publishedtime + "),没有发布新闻！")
            else:
                super().uploaddata(publishedtime, datalist, self.newspaperlibraryid, True)
                print("补录采集成功：" + self.name + "-发行日期（" + publishedtime + "),文章数量（" + str(len(datalist)) + "）")
        return len(datalist)

    # 获取最新期刊日期
    def getDate(self):
        publishedtime = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        return publishedtime

    # 获取最新期刊数据
    def getNewArticles(self, getNewDate):
        articleUrls = []
        retNewArticles = []
        # driver = webdriver.Chrome()

        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        # chrome_options.add_argument("--proxy-server=http://127.0.0.1:8124")
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get("https://www.japantimes.co.jp/" + getNewDate.replace("-", "/"))
        driver.find_element_by_xpath("//ul[@id='user_account_header']/li[2]/a").click()
        sleep(2)
        driver.find_element_by_id("inp_mla").send_keys("13574827001@163.com")
        driver.find_element_by_id("inp_ups").send_keys("Yyy123456")
        driver.find_element_by_id("btnSubmit").click()
        sleep(3)
        articleUrlList = driver.find_elements_by_xpath("//div[@class='archive_block single_block']/article//h1/a")
        for articleUrl in articleUrlList:
            articleUrls.append(articleUrl.get_attribute("href"))
            # print(articleUrl.text + "：" + articleUrl.get_attribute("href"))
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
            i = 0
            while i < 3:
                try:
                    title = driver.find_element_by_xpath("//div[@class='padding_block']//h1").text
                    break
                except Exception as e:
                    driver.refresh()
                    sleep(2)
                    i += 1
            print("-->采集第" + str(count + 1) + "篇文章<--")
            newArticle["title"] = title
            # print("新闻标题：" + title)

            # 新闻作者
            author = ""
            try:
                authorXpaths = driver.find_elements_by_xpath(
                    "//div[@class='padding_block']//h5|//div[@class='padding_block']//p[@class='credit']")
            except Exception:
                pass
            else:
                for authorXpath in authorXpaths:
                    author += authorXpath.text + " "

            newArticle["author"] = author.replace("BY ", "").replace(" AND ", "#").replace(", ", "#")
            # print("新闻作者：" + author)

            # 新闻频道
            channel = ""
            try:
                channel_P = driver.find_element_by_xpath("//div[@class='page_title col_6 col_gutter']/hgroup/h2/a").text
                channel = str(
                    channel_P + "#" + driver.find_element_by_xpath("//div[@class='padding_block']//h3").text).replace(
                    " / ", "#")
            except Exception:
                pass
            newArticle["channel"] = channel
            # print("新闻频道：" + channel)

            # 新闻正文
            mainBody = ""
            try:
                mainBodyListXpath = driver.find_elements_by_xpath("//div[@id='jtarticle']/p")
            except Exception:
                pass
            else:
                for mainBodyXpath in mainBodyListXpath:
                    if mainBodyXpath.text != "":
                        mainBody += "<p>" + str(mainBodyXpath.text).replace("\n", "") + "</p>"
            newArticle["mainBody"] = mainBody
            # print("新闻正文：" + mainBody)

            # 新闻图片
            images = ""
            try:
                imagesListXpath = driver.find_elements_by_xpath(
                    "//div[@class='gallery single_block']/figure/img|//div[@class='attachments']/a/img")
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
                    "//div[@class='gallery single_block']/figure/figcaption|//div[@class='attachments']/a/img")
            except Exception:
                pass
            else:
                for imagesDescriptionXpath in imagesDescriptionListXpath:
                    if imagesDescriptionXpath.tag_name == "img":
                        imagesDescription += str(imagesDescriptionXpath.get_attribute("alt")).replace("\n", "") + "#"
                    else:
                        imagesDescription += str(imagesDescriptionXpath.text).replace("\n", "") + "#"
            newArticle["imageDescriptions"] = imagesDescription
            # print("新闻图片描述：" + imagesDescription)

            count += 1
            retNewArticles.append(newArticle)
        driver.close()
        print("一共采集" + str(count) + "篇文章")
        return retNewArticles

# if __name__ == '__main__':
#     publishedtime = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
#     print(publishedtime)
#     getDate = Japantimes("dh", "123").getDate()
#     Japantimes("dh", "123").getNewArticles(getDate)
#     Japantimes("dh","123").supplement()
