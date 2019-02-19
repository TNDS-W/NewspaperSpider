import requests,json
import re
from spiders.basespider import Spider

class Thehindu(Spider):

    message = []
    newspaperlibraryid = "1059278542195392512"
    proxy = {"http": "127.0.0.1:8124", "https": "127.0.0.1:8124"}

    def getpublishedTime(self):
        header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            # "referer": "https: // www.thehindu.com /"
        }
        try:
            response = requests.get("https://www.thehindu.com/todays-paper/", headers=header, proxies=self.proxy)
        except:
            response = requests.get("https://www.thehindu.com/todays-paper/", headers=header, proxies=self.proxy)
        result = response.text
        dates = "".join(re.findall('var maxDate = "(.*?)";',result)).split(",")
        months = {
            "January": "01",
            'February': "02",
            'March': "03",
            'April': "04",
            'May': '05',
            'June': '06',
            'July': '07',
            'August': '08',
            'September': '09',
            'October': '10',
            'November': '11',
            'December': "12"
        }
        year = dates[-1].strip()
        month = months[dates[0].split(" ")[0]]
        day = dates[0].split(" ")[1]
        publishedTime = year + "-" + month + "-" + day

        return publishedTime


    def getpageurl(self,publishedTime):
        basemessage = []
        header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "referer": "https: // www.thehindu.com /"
        }
        times = publishedTime.split("-")
        times.reverse()    # reverse必须单独操作，否则返回None
        url = "https://epaper.thehindu.com/Home/GetAllpages?editionid=1&editiondate=" + "%2F".join(times)
        i = 0
        while i < 4:
            try:
                response = requests.get(url, headers=header, proxies=self.proxy)
                break
            except:
                i += 1
        result = json.loads(response.text)
        for x in range(len(result)):
            page = result[x]["PageNo"]
            channel = result[x]["NewsProPageTitle"]
            pageId = result[x]["PageId"]
            basemessage.append({"page": page, "channel": channel, "pageId": pageId})

        return basemessage

    def getnewsurl(self,basemessage):
        newsurl = []
        header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            # "referer": "https: // www.thehindu.com /"
        }
        for x in range(len(basemessage)):
            i = 0
            while i < 4:
                try:
                    response = requests.get('https://epaper.thehindu.com/Home/getingRectangleObject?pageid=' + str(basemessage[x]["pageId"]), headers=header, proxies=self.proxy)
                    break
                except:
                    i += 1
            result = json.loads(response.text)
            for y in result:
                objectId = "https://epaper.thehindu.com/Home/getstorydetail?Storyid=" + str(y["ObjectId"])
                page = basemessage[x]["page"]
                channel = basemessage[x]["channel"]
                newsurl.append({"page":page, "channel":channel, "url":objectId})

        return newsurl

    def parsepage(self,newsurl):
        numbers = 0
        header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            # "referer": "https: // www.thehindu.com /"
        }
        for x in newsurl:
            i = 0
            while i < 4:
                try:
                    response = requests.get(x["url"], headers=header, proxies=self.proxy)
                    break
                except:
                    i += 1

            result = json.loads(response.text)
            if result == []:
                continue
            try:
                title = result[0]["Headlines"][0]
            except:
                continue

            try:
                subTitle = result[0]["Headlines"][1]
            except:
                subTitle = ""

            author = result[4].replace(", ","#")

            authorArea = result[5]

            authorDescriptions = ""

            abstract = ""

            channel = x["channel"]

            mainbody = re.sub("<p></p>","",result[0]["Body"])

            pagename = x["page"]

            imgurl = "#".join(map(lambda y:y["fullpathlinkpic"],result[1])).replace("\\","/")
            print(imgurl)
            imageDescriptions = "#".join(map(lambda z:z["caption"],result[1]))

            self.message.append({"title": title, "subTitle": subTitle, "author": author, "authorArea": authorArea,
               "authorDescriptions": authorDescriptions, "abstract": abstract,
               "channel": channel, "mainBody": mainbody, "page": pagename,
               "images": imgurl, "imageDescriptions": imageDescriptions, "cookies": "",
               "referer": ""})
            print("第" + str(numbers) + "篇爬取完成")
            numbers += 1

    def run(self):
        self.message = []
        api = self.api
        # 获取token
        ret = api.gettoken()
        if not ret:
            return 0
        # 从网页中获取发行日期
        print("开始采集:教徒报")
        publishedtime = self.getpublishedTime()
        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("采集失败：教徒报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            print("正在采集新闻……")
            pageurl = self.getpageurl(publishedtime)
            newsurl = self.getnewsurl(pageurl)
            self.parsepage(newsurl)
            super().uploaddata(publishedtime, self.message, self.newspaperlibraryid, False)
            print("采集成功:教徒报-发行日期（" + publishedtime + "),文章数量（" + str(len(self.message)) + "）")
        return len(self.message)


    def supplement(self):
        api = self.api
        # 获取token
        ret = api.gettoken()
        if not ret:
            return 0
        # 从网页中获取发行日期
        print("开始补录:教徒报")
        publishedtime = input("请输入补录的日期(2018-01-01):")
        # 判断报纸是否存在
        ret = api.checknewspaperexists(self.newspaperlibraryid, publishedtime)
        # 如果为True,则说明已经存在
        if (ret["success"] and ret["result"]):
            print("补录失败：教徒报-发行日期已经存在，报纸日期（" + publishedtime + ")")
            return 0
        else:
            print("正在采集新闻……")
            pageurl = self.getpageurl(publishedtime)
            newsurl = self.getnewsurl(pageurl)
            self.parsepage(newsurl)
            super().uploaddata(publishedtime, self.message, self.newspaperlibraryid, False)
            print("补录成功:教徒报-发行日期（" + publishedtime + "),文章数量（" + str(len(self.message)) + "）")
        self.message = []
