from spiders.basespider import Spider
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# 作者 杜浩
# 时间 2018-12-11
# 用途 测试蜘蛛

class Ft(Spider):
    info = [{"name": " 金融时报(亚洲版)", "newspaperlibraryid": "1033579987845775360",
             "hostUrl": "https://www.ft.com/todaysnewspaper/edition/asia", "data-href": "FTA/"},
            {"name": " 金融时报(中东版)", "newspaperlibraryid": "1046282995171852288",
             "hostUrl": "https://www.ft.com/todaysnewspaper/edition/middleeast", "data-href": "FTME/"},
            {"name": " 金融时报(欧洲版)", "newspaperlibraryid": "1046283135278383104",
             "hostUrl": "https://www.ft.com/todaysnewspaper/edition/europe", "data-href": "FTE/"},
            {"name": " 金融时报(英国版)", "newspaperlibraryid": "1046283412316356608",
             "hostUrl": "https://www.ft.com/todaysnewspaper/edition/uk", "data-href": "FTU/"},
            {"name": " 金融时报(美国版)", "newspaperlibraryid": "1082484087437918208",
             "hostUrl": "https://www.ft.com/todaysnewspaper/edition/us", "data-href": "FIT/"}]

    def run(self):
        print("开始采集：金融时报")
        api = self.api
        ret = api.gettoken()
        if not ret:
            return 0

        message = 0
        publishedtime = self.getDate()
        publishedtime = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        for i in range(0, 5):
            print("开始采集：" + self.info[i]["name"])
            if i > 0:
                driver.get(self.info[i]["hostUrl"])
            ret = api.checknewspaperexists(self.info[i]["newspaperlibraryid"], publishedtime)
            if (ret["success"] and ret["result"]):
                print("采集失败：" + self.info[i]["name"] + "-发行日期已经存在，报纸日期（" + publishedtime + ")")
                continue
            else:
                print("正在采集新闻……")
                try:
                    times_bl = publishedtime.replace("-", "/")
                    publishedtime_bl = self.info[i]["data-href"] + times_bl
                    datalist = self.getNewArticles(publishedtime_bl)
                except Exception as e:
                    driver.close()
                    raise e
                if datalist is 0:
                    print("采集失败：" + self.info[i]["name"] + "-发行日期不存在或者已过期！")
                    continue
                super().uploaddata(publishedtime, datalist, self.info[i]["newspaperlibraryid"], False)
                print("采集成功：" + self.info[i]["name"] + "-发行日期（" + publishedtime + "),文章数量（" + str(
                    len(datalist)) + "）")
            message += len(datalist)
        driver.close()
        return message

    def supplement(self):
        print("开始补录采集：金融时报")
        api = self.api
        ret = api.gettoken()
        if not ret:
            return 0

        message = 0
        publishedtime = input("请输入报刊发布日期（例：2018-11-09）:")
        d = self.getDate()
        for i in range(0, 5):
            print("开始补录采集：" + self.info[i]["name"])
            if i > 0:
                driver.get(self.info[i]["hostUrl"])
            ret = api.checknewspaperexists(self.info[i]["newspaperlibraryid"], publishedtime)
            if (ret["success"] and ret["result"]):
                print("补录采集失败：" + self.info[i]["name"] + "-发行日期已经存在，报纸日期（" + publishedtime + ")")
                continue
            else:
                print("正在补录采集新闻……")
                times_bl = publishedtime.replace("-", "/")
                publishedtime_bl = self.info[i]["data-href"] + times_bl
                datalist = self.getNewArticles(publishedtime_bl)
                if datalist is 0:
                    print("补录采集失败：" + self.info[i]["name"] + "-发行日期不存在或者已过期！")
                    continue
                super().uploaddata(publishedtime, datalist, self.info[i]["newspaperlibraryid"], False)
                print("补录采集成功：" + self.info[i]["name"] + "-发行日期（" + publishedtime + "),文章数量（" + str(
                    len(datalist)) + "）")
            message += len(datalist)
        driver.close()
        return message

    # 获取最新期刊日期
    def getDate(self):
        global driver
        global wait
        global chrome_options

        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')
        # chrome_options.add_argument("--proxy-server=http://127.0.0.1:8124")
        driver = webdriver.Chrome(chrome_options=chrome_options)

        wait = WebDriverWait(driver, 20)
        driver.get(self.info[0]["hostUrl"])
        cookieList = [{"name": "FTSession_s",
                       "value": "z1ljnUz2LED904QyvE8odyKpzwAAAWfoNioBw8I.MEYCIQC_7nTV5jYQZrOiUxxBCLgICraxXFNtDzXQvpCBMpPrXQIhALys2d-O7P2L8kkx95p26lem5DkU-Wfh5KU-IUxni1S4",
                       "domain": ".ft.com", 'path': '/', 'httpOnly': False, 'HostOnly': False, 'Secure': False},
                      {"name": "FTSession",
                       "value": "z1ljnUz2LED904QyvE8odyKpzwAAAWfoNioAw8I.MEQCIDllHR_uTKYjLHuQml_3HazpUe6oXfLkqYx6CBQteHq6AiBqhHtuyPY7dfdiLiiYx6exGRVYrZ-HFt4eO8MGsX2VmQ",
                       "domain": ".ft.com", 'path': '/', 'httpOnly': False, 'HostOnly': False, 'Secure': False},
                      {"name": "sc.ASP.NET_SESSIONID", "value": "undefined", "domain": "www.ft.com", 'path': '/',
                       'httpOnly': False, 'HostOnly': False, 'Secure': False},
                      {"name": "FTCookieConsentGDPR", "value": "true", "domain": ".ft.com", 'path': '/',
                       'httpOnly': False, 'HostOnly': False, 'Secure': False},
                      {"name": "__cfduid", "value": "deadb1f22314d1013ccd92a74fd2437fd1545784854",
                       "domain": ".brandmetrics.com", 'path': '/', 'httpOnly': False, 'HostOnly': False,
                       'Secure': False},
                      {"name": "spoor-id", "value": "cjq4gd5ob0000385t5b9m6qh3", "domain": ".ft.com", 'path': '/',
                       'httpOnly': False, 'HostOnly': False, 'Secure': False},
                      {"name": "S",
                       "value": "billing-ui-v3=ylSzIWE4OQSmNcSiR5QrCTXjZmWITYdH:billing-ui-v3-efe=ylSzIWE4OQSmNcSiR5QrCTXjZmWITYdH",
                       "domain": ".google.com", 'path': '/', 'httpOnly': False, 'HostOnly': False, 'Secure': False},
                      {"name": "FTLogin", "value": "beta", "domain": ".ft.com", 'path': '/', 'httpOnly': False,
                       'HostOnly': False, 'Secure': False},
                      {"name": "FTConsent",
                       "value": "behaviouraladsOnsite%3Aon%2CcookiesOnsite%3Aon%2CcookiesUseraccept%3Aoff%2CdemographicadsOnsite%3Aon%2CenhancementByemail%3Aon%2CenhancementByfax%3Aoff%2CenhancementByphonecall%3Aon%2CenhancementBypost%3Aon%2CenhancementBysms%3Aoff%2CmarketingByemail%3Aon%2CmarketingByfax%3Aoff%2CmarketingByphonecall%3Aon%2CmarketingBypost%3Aon%2CmarketingBysms%3Aoff%2CprogrammaticadsOnsite%3Aon%2CrecommendedcontentOnsite%3Aon",
                       "domain": ".ft.com", 'path': '/', 'httpOnly': False, 'HostOnly': False, 'Secure': False},
                      {"name": "_kuid_", "value": "MaGW982P", "domain": ".krxd.ne", 'path': '/', 'httpOnly': False,
                       'HostOnly': False, 'Secure': False},
                      {"name": "__gads",
                       "value": "ID=36ba3152be1a8a17:T=1545784813:S=ALNI_Mbrtw0HvQ_-RVcQ2tqjnIBVGG415A",
                       "domain": ".ft.com", 'path': '/', 'httpOnly': False, 'HostOnly': False, 'Secure': False},
                      {"name": "_csrf", "value": "DJ2dBibroe0UM7fma_ITP-nX", "domain": ".ft.com", 'path': '/',
                       'httpOnly': False, 'HostOnly': False, 'Secure': False},
                      {"name": "1751%5F0", "value": "C57639CE40F68C08827C237231AF380935CA6EE2AF439BA38F69CB522A7EE0EB",
                       "domain": ".ft.com", 'path': '/', 'httpOnly': False, 'HostOnly': False, 'Secure': False},
                      {"name": "IDE", "value": "AHWqTUkPt1mVrU3zTW1YcAFCmxAyhQI3hgT10OYAw2hVFgVBKaDu75uoLdBJ8SI6",
                       "domain": ".doubleclick.net", 'path': '/', 'httpOnly': False, 'HostOnly': False,
                       'Secure': False},
                      {"name": "FTAllocation", "value": "59639d4c-f62c-40fd-8432-bc4f287722a9", "domain": ".ft.com",
                       'path': '/', 'httpOnly': False, 'HostOnly': False, 'Secure': False},
                      {"name": "1P_JAR", "value": "2018-12-25-02", "domain": ".google.com", 'path': '/',
                       'httpOnly': False, 'HostOnly': False, 'Secure': False},
                      {"name": "sc.Status", "value": "2", "domain": "www.ft.com", 'path': '/', 'httpOnly': False,
                       'HostOnly': False, 'Secure': False},
                      {"name": "NID",
                       "value": "152=nffOS_oVjcyYzJekPgDows2-oA-Z5ApAgX19mJ3HVktG7CTGc-8DsCtbRLDCyWywg8-lBgzmuyXGzWcZbdBpxsWkxm7EYujB-2y_ufLUK6fjFHPXlQezYJOkiArYLvWwWWAftfuVZq3Ffi2IdoItzuIpV-aNOeOxb00aS6XUNRQ",
                       "domain": ".google.com", 'path': '/', 'httpOnly': False, 'HostOnly': False, 'Secure': False},
                      {"name": "o-typography-fonts-loaded", "value": "1", "domain": ".ft.com", 'path': '/',
                       'httpOnly': False, 'HostOnly': False, 'Secure': False},
                      {"name": "googtrans", "value": "/en/zh-CN", "domain": ".ft.com", 'path': '/', 'httpOnly': False,
                       'HostOnly': False, 'Secure': False},
                      {"name": "googtrans", "value": "/en/zh-CN", "domain": "www.ft.com", 'path': '/',
                       'httpOnly': False, 'HostOnly': False, 'Secure': False}]
        for cookie in cookieList:
            driver.add_cookie(cookie)
        driver.refresh()
        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//DIV[@class='tooltipster-box']//A[@class='odn-icon btn cancel']")))
            driver.find_element_by_xpath("//div[@class='tooltipster-box']//a[@class='odn-icon btn cancel']").click()
        except Exception as e:
            pass
        sleep(10)
        time = str(driver.find_element_by_xpath("//div[@id='toolbar']/div/div[1]/div[2]").text)
        times = time.split("/")
        publishedtime = times[2] + "-" + times[1] + "-" + times[0]
        # print(publishedtime)
        return publishedtime

    # 获取最新期刊数据
    def getNewArticles(self, isBul):
        retNewArticles = []
        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//DIV[@class='tooltipster-box']//A[@class='odn-icon btn cancel']")))
            driver.find_element_by_xpath("//div[@class='tooltipster-box']//a[@class='odn-icon btn cancel']").click()
        except Exception as e:
            pass

        driver.find_element_by_id("toolbarControl_viewOptions").click()
        sleep(1)
        driver.find_element_by_xpath('//*[@id="toolbarControl_viewOptions"]/div[1]/div/div[3]').click()

        # 是否补录
        if isBul != "":
            driver.find_element_by_xpath('//*[@id="toolbar"]/div/div[1]/div[2]').click()
            wait.until(EC.presence_of_element_located(
                (By.XPATH, '//DIV[@id="recentIssuesPopup_documentList"]/UL/LI[1]')))

            try:
                driver.find_element_by_xpath(
                    '//DIV[@id="recentIssuesPopup_documentList"]/ul/li[@data-href="' + isBul + '"]').click()
            except Exception as e:
                return 0

        wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="digestView_DigestTOC"]/UL/LI[1]/UL/LI/TABLE/TBODY/TR/TD[1]/DIV[1]/IMG')))
        sleep(4)
        driver.find_element_by_xpath(
            '//*[@id="digestView_DigestTOC"]/ul/li[1]/ul/li/table/tbody/tr/td[2]/ul/li[1]/table').click()
        sleep(2)
        count = 0
        while True:
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

            # 新闻标题
            title = ""
            try:
                title = driver.find_element_by_xpath(
                    '//*[@id="articleViewerPopup_articleViewer"]//h1[@class="headline"]').text
            except Exception:
                pass
            else:
                print("-->采集第" + str(count + 1) + "篇文章<--")
                title = str(title).replace("\n", "")
                newArticle["title"] = title
                # print("新闻标题：" + title)
            if title != "":
                # 新闻副标题
                subTitle = ""
                try:
                    subTitle = driver.find_element_by_xpath(
                        '//*[@id="articleViewerPopup_articleViewer"]//h2[@class="drop-head"]').text
                except Exception:
                    pass
                subTitle = str(subTitle).replace("\n", "")
                newArticle["subTitle"] = subTitle
                # print("新闻副标题：" + subTitle)

                # 新闻作者
                author = ""
                authorArea = ""
                try:
                    author = driver.find_element_by_xpath(
                        '//*[@id="articleViewerPopup_articleViewer"]//address[@class="ByLine"]/p').text
                except Exception:
                    pass
                author = author.replace(", ", "#") \
                    .replace(" AND ", "#") \
                    .replace(" and ", "#") \
                    .replace("BY ", "") \
                    .replace("By ", "") \
                    .replace("by ", "")
                if author.count("—") == 1:
                    ss = author.split("—")
                    author = ss[0].strip()
                    authorArea = ss[1].strip()
                elif author.count("—") > 1:
                    ss = author.split("—")
                    author = authorArea = ""
                    for i in range(len(ss)):
                        if i == 0:
                            author += ss[i]
                        elif i == len(ss) - 1:
                            authorArea += ss[i]
                        else:
                            cs = ss[i].split(" ")
                            banLen = 0
                            if len(cs) % 2 == 0:
                                banLen = len(cs) / 2
                            else:
                                banLen = (len(cs) - 1) / 2
                            author += "#"
                            for j in range(len(cs)):
                                if j < banLen:
                                    authorArea += cs[j] + " "
                                else:
                                    author += cs[j] + " "
                            authorArea += "#"
                    author = author.replace(" #", "#").replace("# ", "#").strip()
                    authorArea = authorArea.replace(" #", "#").replace("# ", "#").strip()
                newArticle["author"] = author
                # print("新闻作者：" + author)
                newArticle["authorArea"] = authorArea
                # print("新闻作者地区：" + authorArea)

                # 新闻频道
                channel = ""
                try:
                    channel = driver.find_element_by_xpath(
                        '//*[@id="articleViewerPopup_moreArticlesView"]/div[@class="more_section_name"]').text
                except Exception:
                    pass
                channel = channel.replace("MORE FROM ", "")
                newArticle["channel"] = channel
                # print("新闻频道：" + channel)

                # 新闻频道
                page = ""
                try:
                    page_date = driver.find_element_by_xpath(
                        '//*[@id="articleViewerPopup_articleViewer"]/div/div/div/div/span').get_attribute("data-json")
                    pages = eval(page_date)
                    page = pages["label"]
                except Exception:
                    pass
                newArticle["page"] = page
                # print("新闻版面：" + str(page))

                # 新闻正文
                mainBody = ""
                try:
                    mainBodyListXpath = driver.find_elements_by_xpath(
                        '//*[@id="articleViewerPopup_articleViewer"]//div[@class="Content"]/p')
                except Exception:
                    pass
                else:
                    for mainBodyXpath in mainBodyListXpath:
                        if mainBodyXpath.text != "":
                            mainBody += "<p>" + str(mainBodyXpath.text).replace("\n", "") + "</p>"
                newArticle["mainBody"] = mainBody
                # print("新闻正文：" + mainBody)

                # 新闻图片和图片描述
                images = ""
                try:
                    imagesListXpath = driver.find_elements_by_xpath(
                        '//*[@id="articleViewerPopup_articleViewer"]//div[contains(@class,"embed Picture")]/img')
                except Exception:
                    pass
                else:
                    for imagesXpath in imagesListXpath:
                        images += str(imagesXpath.get_attribute("src")) + "#"
                newArticle["images"] = images
                # print("新闻图片：" + images)

                imagesDescription = ""
                try:
                    imagesListXpath = driver.find_elements_by_xpath(
                        '//*[@id="articleViewerPopup_articleViewer"]//div[contains(@class,"embed Picture")]/img')
                except Exception:
                    pass
                else:
                    for i in range(0, len(imagesListXpath)):
                        try:
                            imagesDescriptionListXpath = driver.find_element_by_xpath(
                                '//*[@id="articleViewerPopup_articleViewer"]//div[contains(@class,"embed Picture")][' + str(
                                    i + 1) + ']/img/following-sibling::div[1]')
                            imagesDescription += str(imagesDescriptionListXpath.text + "#").replace("\n", "")
                        except Exception:
                            imagesDescription += "" + "#"
                newArticle["imageDescriptions"] = imagesDescription
                # print("新闻图片描述：" + imagesDescription)

                count += 1
                retNewArticles.append(newArticle)
            try:
                wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//DIV[@class="center-buttons-container"]/DIV[@id="next-article"]')))
                driver.find_element_by_xpath(
                    '//div[@class="center-buttons-container"]/div[@class="right_side_button odn-icon next-article"]').click()
                sleep(2)
            except Exception as e:
                break

        print("一共采集" + str(count) + "篇文章")
        return retNewArticles

# if __name__ == '__main__':
    # Ft("dh", "123").run()
#     Ft("dh", "123").supplement()
# Ft("dh", "123").getDate(0)
# Ft("dh", "123").getNewArticles()
