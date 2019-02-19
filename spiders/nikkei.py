from spiders.basespider import Spider
from selenium import webdriver
from time import sleep
import urllib.request
from selenium.webdriver.chrome.options import Options
import datetime


# 作者 杜浩
# 时间 2018-12-11
# 用途 测试蜘蛛

class Nikkei(Spider):
    info = [{"name": " 日本经济新闻(早刊)", "newspaperlibraryid": "1049098479718105088"},
            {"name": " 日本经济新闻(夕刊)", "newspaperlibraryid": "1049972782936358912"}]

    def run(self):
        print("开始采集：日报经济新闻")
        newsnumber = 0
        api = self.api
        ret = api.gettoken()
        if not ret:
            return 0
        for i in range(0, 2):
            print("开始采集：" + self.info[i]["name"])
            publishedtime = self.getDate()
            ret = api.checknewspaperexists(self.info[i]["newspaperlibraryid"], publishedtime)
            if (ret["success"] and ret["result"]):
                print("采集失败：" + self.info[i]["name"] + "-发行日期已经存在，报纸日期（" + publishedtime + ")")
                continue
            else:
                print("正在采集新闻……")
                datalist = self.getNewArticles(publishedtime, str(i + 1))
                if datalist["ret"]:
                    super().uploaddata(publishedtime, datalist["retNewArticles"], self.info[i]["newspaperlibraryid"],
                                       True)
                    print("采集成功：" + self.info[i]["name"] + "-发行日期（" + publishedtime + "),文章数量（" + str(
                        len(datalist["retNewArticles"])) + "）")
                    newsnumber += len(datalist["retNewArticles"])
                else:
                    print("采集失败：" + self.info[i]["name"] + "/" + publishedtime + ",请检查该期报刊是否存在，稍后重新采集！")
        return newsnumber

    def supplement(self):
        print("开始补录采集：日报经济新闻")
        newsnumber = 0
        api = self.api
        ret = api.gettoken()
        if not ret:
            return 0
        publishedtime = input("请输入报刊发布日期（例：2018-11-09）:")
        for i in range(0, 2):
            print("开始补录采集：" + self.info[i]["name"])
            ret = api.checknewspaperexists(self.info[i]["newspaperlibraryid"], publishedtime)
            if (ret["success"] and ret["result"]):
                print("补录采集失败：" + self.info[i]["name"] + "-发行日期已经存在，报纸日期（" + publishedtime + ")")
                continue
            else:
                print("正在补录采集新闻……")
                datalist = self.getNewArticles(publishedtime, str(i + 1))
                if datalist["ret"]:
                    super().uploaddata(publishedtime, datalist["retNewArticles"], self.info[i]["newspaperlibraryid"],
                                       True)
                    print("补录采集成功：" + self.info[i]["name"] + "-发行日期（" + publishedtime + "),文章数量（" + str(
                        len(datalist["retNewArticles"])) + "）")
                    newsnumber += len(datalist["retNewArticles"])
                else:
                    print("补录采集失败：" + self.info[i]["name"] + "/" + publishedtime + ",请检查该期报刊是否存在，稍后重新采集！")
        return newsnumber

    # 获取最新期刊日期
    def getDate(self):
        publishedtime = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        return publishedtime

    # 获取最新期刊数据
    def getNewArticles(self, getNewDate, tyep):
        articleUrls = []
        retNewArticles = []
        driver = webdriver.Chrome()

        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        # # chrome_options.add_argument("--proxy-server=http://127.0.0.1:8124")
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get("https://www.nikkei.com/paper")
        sleep(5)
        driver.find_element_by_id("LA7010Form01:LA7010Email").send_keys("13574827001@163.com")
        sleep(1)
        driver.find_element_by_id("LA7010Form01:LA7010Password").send_keys("Yyy123456")
        driver.find_element_by_class_name("btnM1").click()
        sleep(3)
        driver.get('https://www.nikkei.com/paper/morning/?b=' + getNewDate.replace("-", "") + '&d=0')
        try:
            driver.find_element_by_xpath("//*[@id='INDEX_MENU']/div[3]/ul/li[" + tyep + "]/a").click()
        except:
            try:
                driver.find_element_by_xpath("//*[@id='JSID_UserMenu']/a").click()
                driver.find_element_by_xpath("//*[@id='JSID_l-miH02_H02c_userMenu']/div/div/div/div/div/a").click()
            except:
                pass
            driver.close()
            return {"ret": False}

        articleUrlList = driver.find_elements_by_xpath("//*[@class='cmn-article_title']//a")
        for articleUrl in articleUrlList:
            if articleUrl.get_attribute("href") != "javascript:void(0)":
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
            try:
                title = driver.find_element_by_xpath("//div[@class='cmn-section cmn-indent']/h1").text
            except:
                continue
            else:
                print("-->采集第" + str(count + 1) + "篇文章<--")
                title = str(title).replace("\n", "")
                newArticle["title"] = title
                # print("新闻标题：" + title)

            # 新闻作者
            author = ""
            try:
                author = driver.find_element_by_xpath(
                    "//div[@id='CONTENTS_MAIN']/div[@class='cmn-section cmn-indent']/div[@class='cmn-article_text JSID_key_fonttxt m-streamer_medium'][last()]/p").text
                author = str(author)
                if author[0] == "（" and author[-1] == "）":
                    author = author
                elif author.count("（編集委員　") == 1:
                    author = (author.split("（編集委員　"))[1]
                else:
                    author = ""
                if "=" in author:
                    author = author.split("=", 1)[-1]
                author = author.replace("（", "") \
                    .replace("）", "") \
                    .replace("、", "#") \
                    .replace("編集委員　", "")
            except Exception:
                pass
            newArticle["author"] = author
            # print("新闻作者：" + author)

            # 新闻频道
            channel = ""
            try:
                channel = driver.find_element_by_xpath("//div[@class='cmn-result_headline cmn-clearfix']/h3").text
            except Exception:
                pass
            newArticle["channel"] = channel
            # print("新闻频道：" + channel)

            # 新闻正文
            mainBody = ""
            try:
                mainBodyListXpath = driver.find_elements_by_xpath(
                    "//div[@id='CONTENTS_MAIN']/div[@class='cmn-section cmn-indent']/div/p")
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
            # 图片描述
            imagesDescription = ""
            try:
                imagesListXpath = driver.find_elements_by_xpath("//div[@class='cmn-section cmn-indent']//img")
            except Exception:
                pass
            else:
                for imagesXpath in imagesListXpath:
                    images += str(imagesXpath.get_attribute("src")) + "#"
                    imagesDescription += str(imagesXpath.get_attribute("alt") + "#").replace("\n", "")
            newArticle["images"] = images
            # print("新闻图片：" + images)
            newArticle["imageDescriptions"] = imagesDescription
            # print("新闻图片描述：" + imagesDescription)

            count += 1
            retNewArticles.append(newArticle)
        print("一共采集" + str(count) + "篇文章")
        driver.find_element_by_xpath("//*[@id='JSID_UserMenu']/a").click()
        driver.find_element_by_xpath("//*[@id='JSID_l-miH02_H02c_userMenu']/div/div/div/div/div/a").click()
        driver.close()
        return {"ret": True, "retNewArticles": retNewArticles}

# if __name__ == '__main__':
#     Nikkei("dh", "123").supplement()
# print(Nikkei("dh", "123").info[0])
# for i in range(0, 2):
#     print("开始采集=：" + Nikkei("dh", "123").info[i]["name"])
