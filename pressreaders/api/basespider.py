from api.damsapi import DamsApi
import time,datetime



class Spider:
    # ret = api.checknewspaperexists(newsTypeId, publishedtime)

    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.api = DamsApi(username, password)


     #外部需要调用api可以调用这个函数
    def login(self):
        api = DamsApi(self.username,self.password)
        return api


    def uploaddata(self,publishedtime, datalist, newspaperlibraryid, requireAgent):
        if (not datalist) or datalist == []:
            print("内容为空,请检查代码")
            return
        # 先获取token
        ret = self.api.gettoken()
        if not ret:
            return

        # 根据报刊类型获取报刊数据
        libraryinfo = self.api.getnewspaperlibraryinfo(newspaperlibraryid)

        if (libraryinfo["success"]):
            libraryinfo = libraryinfo["result"]
        else:
            return

       # Newspaper数据
        newspaper = {
            'NewspaperLibraryId': newspaperlibraryid,
            'NewspaperName': libraryinfo["newspaperName"],
            'NewspaperCHSName': libraryinfo["newspaperCHSName"],
            'NewspaperType': libraryinfo["newspaperType"],
            'FileName': libraryinfo["newspaperCHSName"] + '-' + publishedtime,
            'FileRelativePath': '-',
            'PublishedTime': publishedtime,
            'Status': 1,
            'StorageTime': datetime.datetime.now(),
            'ReceiverId': self.api.userid,
            'ReceiverName': self.api.truename,
            'ReceiveTime': datetime.datetime.now()
        }
        newspaper = self.api.addnewspaper(newspaper)

        # 判断是否成功
        if (newspaper["success"]):
            newspaperId = newspaper["result"]["id"]
            print("开始储存数据")
            #循环插入文章
            for number in range(len(datalist)):
                if datalist[number]["images"] != "":
                    img = self.api.updateimg(datalist[number]["images"], newspaperId, requireAgent, cookies=datalist[number]["cookies"], referer=datalist[number]["referer"])
                    # img = self.api.downloadimg(datalist[number]["images"], requireAgent,publishedtime,libraryinfo["newspaperCHSName"], cookies=datalist[number]["cookies"], referer=datalist[number]["referer"])
                else:
                    img = {"result": ""}
                article = {
                    "newspaperId": newspaperId,
                    "title": datalist[number]["title"],
                    "subTitle": datalist[number]["subTitle"],
                    "author": datalist[number]["author"],
                    "authorArea": datalist[number]["authorArea"],
                    "authorDescriptions": datalist[number]["authorDescriptions"],
                    "abstract": datalist[number]["abstract"],  #摘要
                    "channel": datalist[number]["channel"],  #频道
                    "mainBody": datalist[number]["mainBody"],
                    "newspaperType": newspaper["result"]["newspaperType"],
                    "newspaperName": newspaper["result"]["newspaperName"],
                    "newspaperCHSName": newspaper["result"]["newspaperCHSName"],
                    "publishedTime": publishedtime,
                    "page": datalist[number]["page"],
                    "images": img["result"],  # #号分割
                    "imageDescriptions": datalist[number]["imageDescriptions"],
                    "fileRelativePath": "-",
                    "status": 0
                }
                self.api.addarticle(article)
                print("第"+str(number+1) +"篇存储成功")
                # 结束插入文章

        else:
            print(newspaper["error"]["message"])