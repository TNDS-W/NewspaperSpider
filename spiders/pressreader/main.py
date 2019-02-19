from spiders.basespider import Spider
import datetime,os
from spiders.pressreader.login import Login
from spiders.pressreader.pressreaderSpider import PressreaderSpider

# 作者：文振乾
# 时间：2018-12-13
# 用途：pressreader系列调度器

class Pressreadermain(Spider):
    pressreaderlist =[
                      {"displayname": "《瞭望》东方周刊", "paperId": "5624", "newspaperlibraryid": "1045861675632164864", "class": 'https://www.pressreader.com/china/oriental-outlook/'},
                      {"displayname": "华盛顿邮报", "paperId": "1047", "newspaperlibraryid": "1033578898694078464", "class": 'https://www.pressreader.com/usa/the-washington-post/'},
                      {"displayname": "华盛顿邮报(周日版)", "paperId": "1058", "newspaperlibraryid": "1033578898694078464", "class": 'https://www.pressreader.com/usa/the-washington-post-sunday/'},
                      {"displayname": "环球邮报", "paperId": "1893", "newspaperlibraryid": "1045865093163646976", "class": 'https://www.pressreader.com/canada/the-globe-and-mail-metro-ontario-edition/'},
                      {"displayname": "每日电讯报", "paperId": "1190", "newspaperlibraryid": "1052393687318790144", "class": 'https://www.pressreader.com/uk/the-daily-telegraph/'},
                      {"displayname": "每日电讯报(周日报)", "paperId": "1191", "newspaperlibraryid": "1062187599004696576", "class": 'https://www.pressreader.com/uk/the-sunday-telegraph/'},
                      {"displayname": "费加罗报", "paperId": "2526", "newspaperlibraryid": "1052399397175820288", "class": 'https://www.pressreader.com/france/le-figaro/'},
                      {"displayname": "马来西亚星报", "paperId": "1342", "newspaperlibraryid": "1056715269021368320", "class": 'https://www.pressreader.com/malaysia/the-star-malaysia/'},
                      {"displayname": "马尼拉公报", "paperId": "9f70", "newspaperlibraryid": "1055720173438238720", "class": 'https://www.pressreader.com/philippines/manila-bulletin/'},
                      {"displayname": "缅甸时报", "paperId": "9fak", "newspaperlibraryid": "1057893476043063296", "class": 'https://www.pressreader.com/myanmar/the-myanmar-times/'},
                      {"displayname": "菲律宾《星报》", "paperId": "1731", "newspaperlibraryid": "1059282635148230656", "class": 'https://www.pressreader.com/philippines/the-philippine-star/'},
                      {"displayname": "《ABC》报", "paperId": "2019", "newspaperlibraryid": "1059279325993369600", "class": 'https://www.pressreader.com/spain/abc/'},
                      {"displayname": "洛杉矶时报", "paperId": "1156", "newspaperlibraryid": "1033579506872352768", "class": 'https://www.pressreader.com/usa/los-angeles-times/'},
                      {"displayname": "《圣保罗报》", "paperId": "2011", "newspaperlibraryid": "1062165517546029056", "class": 'https://www.pressreader.com/brazil/folha-de-spaulo/'},
                      {"displayname": "《号角报》", "paperId": "2009", "newspaperlibraryid": "1062614516577075200", "class": 'https://www.pressreader.com/argentina/clarín/'},
                      {"displayname": "海峡时报", "paperId": "1105", "newspaperlibraryid": "1078890400258719744", "class": 'https://www.pressreader.com/singapore/the-straits-times/'},
                      {"displayname": "新海峡时报", "paperId": "9gqu", "newspaperlibraryid": "1078890509197377536", "class": 'https://www.pressreader.com/malaysia/new-straits-times/'},
                      {"displayname": "《教徒报》", "paperId": "1091", "newspaperlibraryid": "1059278542195392512", "class": 'https://www.pressreader.com/india/the-hindu/'},
                      # {"displayname": "第一财经周刊", "paperId": "5697", "newspaperlibraryid": "1045861372144910336", "class": None},
                      # {"displayname": "澳大利亚人报", "paperId": "1720", "newspaperlibraryid": "1045865018479869952", "class": 'https://www.pressreader.com/australia/the-australian/'},
                      {"displayname": "今日美国", "paperId": "1152", "newspaperlibraryid": "1049871921027481600", "class": 'https://www.pressreader.com/usa/usa-today-us-edition/'},
                      # {"displayname": "美国新闻周刊", "paperId": "9fc6", "newspaperlibraryid": "1045930963550339072", "class": 'https://www.pressreader.com/usa/newsweek/'},
                      # {"displayname": "中央日报", "paperId": "5531", "newspaperlibraryid": "1055631968592461824", "class": None},
                      # {"displayname": "曼谷邮报", "paperId": "1264", "newspaperlibraryid": "1049921042123849728", "class": "https://www.pressreader.com/thailand/bangkok-post/"},
    ]

    # 自动采集调用
    def runpress(self):
        # 读取info里的日期 检测是否需要运行登陆程序
        with open(os.getcwd()+"\spiders\pressreader\info.json","r") as f:
            info = eval(f.read())
        if str(info["date"]) == str(datetime.date.today()):
            pass
        else:
            Login().run()

        # 用于判断是否成功
        boolean = True
        # 成功篇数
        sucNumber = 0
        # 失败篇数
        faiNumber = 0
        # 不存在篇数
        noNumber = 0
        # 存储成功文章
        sucnewspaper = []
        # 存储失败文章
        fainewspaper = []
        # 存储不存在报纸
        nonewspaper = []
        # 存储总篇数
        newsnumber = 0

        #循环运行所有爬虫
        for x in range(len(self.pressreaderlist)):
            data = self.pressreaderlist[x]
            # i 用来表示循环次数
            i = 0
            while i<3:
                try:
                    news = PressreaderSpider(self.username,self.password,data["newspaperlibraryid"],data["paperId"],data["displayname"]).run()
                    boolean = True
                    newsnumber += news
                    print("=====" * 30)
                    break
                except Exception as e:
                    error = "("+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+")"+"爬取出错:"+data["displayname"]+"报纸。错误原因：" + str(e)
                    print(error)
                    #写入错误日志
                    with open(os.getcwd()+r"\log\error-" + datetime.datetime.now().strftime('%Y-%m-%d') + r".txt","a")as f:
                        f.write(error+"\n")
                    print("=====" * 30)
                    boolean = False
                    i += 1
            if boolean:
                if news == 0:
                    noNumber += 1
                    nonewspaper.append(data["displayname"])
                else:
                    sucNumber += 1
                    sucnewspaper.append(data["displayname"])
            else:
                faiNumber += 1
                fainewspaper.append(data["displayname"])

        return sucNumber, faiNumber, noNumber, "||".join(sucnewspaper), "||".join(fainewspaper), "||".join(nonewspaper), newsnumber


    # 人工采集调用
    def ran(self):
        with open(os.getcwd()+"\spiders\pressreader\info.json","r") as f:
            info = eval(f.read())
        if str(info["date"]) == str(datetime.date.today()):
            pass
        else:
            Login().run()

        while True:
            #循环显示所有采集器
            for i in range(0, len( self.pressreaderlist)):
                print(str(i) + ":" + self.pressreaderlist[i]["displayname"])

            print("A:所有报纸")
            print("Q:退出")

            #等待输入命令
            ret = input("请输入你要选择采集的报纸:")
            if (ret == "Q" or ret == "q"):
                break
            elif (ret == "A" or ret == "a"):  # 如果输入a 则全部爬取
                for x in range(len(self.pressreaderlist)):
                    data = self.pressreaderlist[x]
                    try:
                        PressreaderSpider(self.username,self.password,data["newspaperlibraryid"],data["paperId"],data["displayname"]).run()
                        print("=====" * 30)
                    except Exception as e:
                        print("爬取出错:"+data["displayname"]+"报纸。错误原因：" + str(e))
                        print("=====" * 30)

            else:
                data = self.pressreaderlist[int(ret)]
                # try:
                PressreaderSpider(self.username,self.password,data["newspaperlibraryid"],data["paperId"],data["displayname"]).run()
                # except Exception as e:
                #     print("爬取出错,错误原因：" + str(e))

            print("=====" * 30)

    # 补录调用
    def run(self):
        with open(os.getcwd()+"\spiders\pressreader\info.json","r") as f:
            info = eval(f.read())
        if str(info["date"]) == str(datetime.date.today()):
            pass
        else:
            Login().run()

        while True:
            #循环显示所有采集器
            for i in range(0, len( self.pressreaderlist)):
                print(str(i) + ":" + self.pressreaderlist[i]["displayname"])

            print("Q:退出")

            #等待输入命令
            ret = input("请输入你要选择补录的报纸:")
            if (ret == "Q" or ret == "q"):
                break
            else:
                data = self.pressreaderlist[int(ret)]
                try:
                    PressreaderSpider(self.username,self.password,data["newspaperlibraryid"],data["paperId"],data["displayname"]).supplement(data["class"])
                except Exception as e:
                    print("爬取出错,错误原因：" + str(e))

            print("=====" * 30)



# if __name__ == '__main__':
#     w = Pressreadermain("wzq","123456")
#     w.run()