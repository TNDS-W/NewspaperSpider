from pressreaders.api.basespider import Spider
import datetime, os
# from pressreader.login import Login
from pressreaders.pressreader.pressreaderSpider import PressreaderSpider
from pressreaders.pressreader.login import Login


# 作者：文振乾
# 时间：2018-12-13
# 用途：pressreader系列调度器

class Pressreadermain(Spider):
    pressreaderlist = [
        {"displayname": "纽约日报", "paperId": "1024", "newspaperlibraryid": "1090130141155164160",
         "class": 'https://www.pressreader.com/usa/new-york-daily-news/'},
        {"displayname": "德国每日镜报", "paperId": "3035", "newspaperlibraryid": "1090130309858459648",
         "class": 'https://www.pressreader.com/germany/der-tagesspiegel/'},
        {"displayname": "多伦多明星报", "paperId": "1038", "newspaperlibraryid": "1090130367114903552",
         "class": 'https://www.pressreader.com/canada/toronto-star/'},
        {"displayname": "墨西哥改革报", "paperId": "34kt", "newspaperlibraryid": "1090130448421486592",
         "class": 'https://www.pressreader.com/mexico/reforma/'},
        {"displayname": "意大利晚邮报", "paperId": "3501", "newspaperlibraryid": "1090130697185656832",
         "class": 'https://www.pressreader.com/italy/corriere-della-sera/'},
        {"displayname": "挪威日报", "paperId": "3222", "newspaperlibraryid": "1090130788017504256",
         "class": 'https://www.pressreader.com/norway/dagbladet/'},
        {"displayname": "奥塔哥每日时报", "paperId": "9hym", "newspaperlibraryid": "1090131745434501120",
         "class": 'https://www.pressreader.com/new-zealand/otago-daily-times/'},
        {"displayname": "今日法国", "paperId": "2505", "newspaperlibraryid": "1090132463809724416",
         "class": 'https://www.pressreader.com/france/aujourdhui-en-france/'},
        {"displayname": "瑞典日报", "paperId": "3233", "newspaperlibraryid": "1090133203005472768",
         "class": 'https://www.pressreader.com/sweden/svenska-dagbladet/'},
        {"displayname": "西班牙国家报", "paperId": "2317", "newspaperlibraryid": "1090133439702630400",
         "class": 'https://www.pressreader.com/spain/el-pais/'},
        {"displayname": "中国日报", "paperId": "7650", "newspaperlibraryid": "1090132420407066624",
         "class": 'https://www.pressreader.com/china/china-daily/'},
        {"displayname": "纽约邮报", "paperId": "1245", "newspaperlibraryid": "1090139897999654912",
         "class": 'https://www.pressreader.com/usa/new-york-post/'},
        {"displayname": "卫报", "paperId": "1545", "newspaperlibraryid": "1090143178004103168",
         "class": 'https://www.pressreader.com/uk/the-guardian/'},
        {"displayname": "国家邮报", "paperId": "1006", "newspaperlibraryid": "1090144387544907776",
         "class": 'https://www.pressreader.com/canada/national-post-latest-edition/'},
        {"displayname": "每日快报", "paperId": "1043", "newspaperlibraryid": "1090154536305164288",
         "class": 'https://www.pressreader.com/uk/daily-express/'},
        {"displayname": "独立报", "paperId": "1029", "newspaperlibraryid": "1090157145317441536",
         "class": 'https://www.pressreader.com/uk/the-independent-1029/'},
        {"displayname": "每日星报", "paperId": "1069", "newspaperlibraryid": "1090157708776046592",
         "class": 'https://www.pressreader.com/uk/daily-star/'},
        {"displayname": "温哥华太阳报", "paperId": "1000", "newspaperlibraryid": "1090158629392220160",
         "class": 'https://www.pressreader.com/canada/vancouver-sun/'},
        {"displayname": "印度时报(孟买版)", "paperId": "1066", "newspaperlibraryid": "1090160261551095808",
         "class": 'https://www.pressreader.com/india/the-times-of-india-mumbai-edition/'},
        {"displayname": "印度时报(新德里版)", "paperId": "1011", "newspaperlibraryid": "1095578885577244672",
         "class": 'https://www.pressreader.com/india/the-times-of-india-new-delhi-edition/'},
        {"displayname": "商务旅行者", "paperId": "9350", "newspaperlibraryid": "1095580098343469056",
         "class": 'https://www.pressreader.com/international/business-traveller/'},
        {"displayname": "西澳洲报", "paperId": "9a63", "newspaperlibraryid": "1095580968774795264",
         "class": 'https://www.pressreader.com/australia/the-west-australian/'},
        {"displayname": "费城询问报", "paperId": "1014", "newspaperlibraryid": "1095581637229412352",
         "class": 'https://www.pressreader.com/usa/the-philadelphia-inquirer/'},
        {"displayname": "卡尔加里先驱报", "paperId": "1032", "newspaperlibraryid": "1095582165413920768",
         "class": 'https://www.pressreader.com/canada/calgary-herald/'},
        {"displayname": "渥太华公民报", "paperId": "1131", "newspaperlibraryid": "1095583437999308800",
         "class": 'https://www.pressreader.com/canada/ottawa-citizen/'},
        {"displayname": "先驱太阳报", "paperId": "1835", "newspaperlibraryid": "1095583878707412992",
         "class": 'https://www.pressreader.com/australia/herald-sun/'},
        {"displayname": "先锋报", "paperId": "2065", "newspaperlibraryid": "1095585084301377536",
         "class": 'https://www.pressreader.com/spain/la-vanguardia/'},
        {"displayname": "阿斯报", "paperId": "2099", "newspaperlibraryid": "1095585505845706752",
         "class": 'https://www.pressreader.com/spain/as/'},
        {"displayname": "英国每日镜报", "paperId": "1039", "newspaperlibraryid": "1095585982645796864",
         "class": 'https://www.pressreader.com/uk/daily-mirror/'},
        {"displayname": "罗盘报", "paperId": "4133", "newspaperlibraryid": "1095847648822296576",
         "class": 'https://www.pressreader.com/indonesia/kompas/'},
        {"displayname": "殖民者时报", "paperId": "1213", "newspaperlibraryid": "1095848126230560768",
         "class": 'https://www.pressreader.com/canada/times-colonist/'},
        {"displayname": "温莎星报", "paperId": "1187", "newspaperlibraryid": "1095849748088225792",
         "class": 'https://www.pressreader.com/canada/windsor-star/'},
        {"displayname": "埃德蒙顿日报", "paperId": "1035", "newspaperlibraryid": "1095850869359902720",
         "class": 'https://www.pressreader.com/canada/edmonton-journal/'},
        {"displayname": "爱尔兰时报", "paperId": "1095", "newspaperlibraryid": "1095851715757867008",
         "class": 'https://www.pressreader.com/ireland/the-irish-times/'},
        {"displayname": "底特律新闻报", "paperId": "1454", "newspaperlibraryid": "1095853331517014016",
         "class": 'https://www.pressreader.com/usa/the-detroit-news/'},
        {"displayname": "怀卡托时报", "paperId": "1482", "newspaperlibraryid": "1095853953406468096",
         "class": 'https://www.pressreader.com/new-zealand/waikato-times/'},
        {"displayname": "魁北克太阳报", "paperId": "2624", "newspaperlibraryid": "1095855368967290880",
         "class": 'https://www.pressreader.com/canada/le-soleil/'},
        {"displayname": "莱茵邮报", "paperId": "3012", "newspaperlibraryid": "1095856087510286336",
         "class": 'https://www.pressreader.com/germany/rheinische-post/'},
        {"displayname": "耶路撒冷邮报", "paperId": "1007", "newspaperlibraryid": "1095856720778887168",
         "class": 'https://www.pressreader.com/israel/jerusalem-post/'},
        {"displayname": "国家报（阿根廷）", "paperId": "2260", "newspaperlibraryid": "1095858135890919424",
         "class": 'https://www.pressreader.com/argentina/la-nacion/'},
        {"displayname": "伦敦自由报", "paperId": " 6228", "newspaperlibraryid": "1096292314030014464",
         "class": 'https://www.pressreader.com/canada/the-london-free-press/'},
        {"displayname": "水牛城新闻报", "paperId": "1733", "newspaperlibraryid": "1096293760779681792",
         "class": 'https://www.pressreader.com/usa/the-buffalo-news/'},
        {"displayname": "休斯敦纪事报（星期天）", "paperId": "1210", "newspaperlibraryid": "1096294648021778432",
         "class": 'https://www.pressreader.com/usa/houston-chronicle-sunday/'},
        {"displayname": "休斯敦纪事报", "paperId": "1084", "newspaperlibraryid": "1096295009612726272",
         "class": 'https://www.pressreader.com/usa/houston-chronicle/'},
        {"displayname": "苏格兰人报", "paperId": "1159", "newspaperlibraryid": "1096295736837931008",
         "class": 'https://www.pressreader.com/uk/the-scotsman/'},
        {"displayname": "肯特阿什福德地区快报", "paperId": "1467", "newspaperlibraryid": "1096296681567158272",
         "class": 'https://www.pressreader.com/uk/kentish-express-ashford-district/'},
        {"displayname": "奥地利新闻报", "paperId": "3013", "newspaperlibraryid": "1096297494607822848",
         "class": 'https://www.pressreader.com/austria/die-presse/'},
        {"displayname": "回响报", "paperId": "3055", "newspaperlibraryid": "1096297998184349696",
         "class": 'https://www.pressreader.com/south-africa/beeld/'},
        {"displayname": "阿尔伯克基日报", "paperId": "1369", "newspaperlibraryid": "1096298398715215872",
         "class": 'https://www.pressreader.com/usa/albuquerque-journal/'},
        {"displayname": "中国日报（香港版）", "paperId": "1287", "newspaperlibraryid": "1096300015149645824",
         "class": 'https://www.pressreader.com/china/china-daily-hong-kong/'},
        {"displayname": "今日青年先锋报", "paperId": "0501", "newspaperlibraryid": "1097333091464118273",
         "class": 'https://www.pressreader.com/czech-republic/mf-dnes/'},
        {"displayname": "新德意志报", "paperId": "3605", "newspaperlibraryid": "1097333491957235712",
         "class": 'https://www.pressreader.com/germany/neues-deutschland/'},
        {"displayname": "坦帕湾时报", "paperId": "7089", "newspaperlibraryid": "1097334774042722304",
         "class": 'https://www.pressreader.com/usa/tampa-bay-times/'},
        {"displayname": "特鲁罗每日新闻报", "paperId": "1934", "newspaperlibraryid": "1097335416949833728",
         "class": 'https://www.pressreader.com/canada/truro-daily-news/'},
        {"displayname": "东方日报", "paperId": "5503", "newspaperlibraryid": "1097336081554079744",
         "class": 'https://www.pressreader.com/malaysia/oriental-daily-news/'},
        {"displayname": "华盛顿时报周刊", "paperId": "1002", "newspaperlibraryid": "1097339158805872640",
         "class": 'https://www.pressreader.com/usa/the-washington-times-weekly/'},
        {"displayname": "华盛顿时报", "paperId": "1062", "newspaperlibraryid": "1097338981072240640",
         "class": 'https://www.pressreader.com/usa/the-washington-times-daily/'},
        {"displayname": "商界(菲律宾报纸)", "paperId": "9gcz", "newspaperlibraryid": "1097340598899179520",
         "class": 'https://www.pressreader.com/philippines/business-world/'},
        {"displayname": "阿塞新闻", "paperId": "1354", "newspaperlibraryid": "1097341574074859520",
         "class": 'https://www.pressreader.com/azerbaijan/azer-news/'},
        {"displayname": "约克郡邮报", "paperId": "7402", "newspaperlibraryid": "1097342294119415808",
         "class": 'https://www.pressreader.com/uk/yorkshire-post/'},
    ]

    # 自动采集调用
    def runpress(self):
        # 读取info里的日期 检测是否需要运行登陆程序
        with open(os.getcwd() + "\spiders\pressreader\info.json", "r") as f:
            info = eval(f.read())
        if str(info["date"]) == str(datetime.date.today()):
            pass
        else:
            log = Login()
            log.main(self.pressreaderlist)  # 调用登陆方法

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

        # 循环运行所有爬虫
        for x in range(len(self.pressreaderlist)):
            data = self.pressreaderlist[x]
            # i 用来表示循环次数
            i = 0
            while i < 3:
                try:
                    news = PressreaderSpider(self.username, self.password, data["newspaperlibraryid"], data["paperId"],
                                             data["displayname"]).run()
                    boolean = True
                    newsnumber += news
                    print("=====" * 30)
                    break
                except Exception as e:
                    error = "(" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ")" + "爬取出错:" + data[
                        "displayname"] + "报纸。错误原因：" + str(e)
                    print(error)
                    # 写入错误日志
                    with open(os.getcwd() + r"\log\error-" + datetime.datetime.now().strftime('%Y-%m-%d') + r".txt",
                              "a")as f:
                        f.write(error + "\n")
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

        return sucNumber, faiNumber, noNumber, "||".join(sucnewspaper), "||".join(fainewspaper), "||".join(
            nonewspaper), newsnumber

    # 人工采集调用
    def ran(self):
        with open(os.getcwd() + "\info.json", "r") as f:
            info = eval(f.read())
        if str(info["date"]) == str(datetime.date.today()):
            pass
        else:
            log = Login()
            log.main(self.pressreaderlist)  # 调用登陆方法

        while True:
            # 循环显示所有采集器
            for i in range(0, len(self.pressreaderlist)):
                print(str(i) + ":" + self.pressreaderlist[i]["displayname"])

            print("A:所有报纸")
            print("Q:退出")

            # 等待输入命令
            ret = input("请输入你要选择采集的报纸:")
            if (ret == "Q" or ret == "q"):
                break
            elif (ret == "A" or ret == "a"):  # 如果输入a 则全部爬取
                for x in range(len(self.pressreaderlist)):
                    data = self.pressreaderlist[x]
                    try:
                        PressreaderSpider(self.username, self.password, data["newspaperlibraryid"], data["paperId"],
                                          data["displayname"]).run()
                        print("=====" * 30)
                    except Exception as e:
                        print("爬取出错:" + data["displayname"] + "报纸。错误原因：" + str(e))
                        print("=====" * 30)

            else:
                data = self.pressreaderlist[int(ret)]
                # try:
                PressreaderSpider(self.username, self.password, data["newspaperlibraryid"], data["paperId"],
                                  data["displayname"]).run()
                # except Exception as e:
                #     print("爬取出错,错误原因：" + str(e))

            print("=====" * 30)

    # 补录调用
    def run(self):
        with open(os.getcwd() + "\info.json", "r") as f:
            info = eval(f.read())
        if str(info["date"]) == str(datetime.date.today()):
            pass
        else:
            getattr(self, 'main')

        while True:
            # 循环显示所有采集器
            for i in range(0, len(self.pressreaderlist)):
                print(str(i) + ":" + self.pressreaderlist[i]["displayname"])

            print("Q:退出")

            # 等待输入命令
            ret = input("请输入你要选择补录的报纸:")
            if (ret == "Q" or ret == "q"):
                break
            else:
                data = self.pressreaderlist[int(ret)]
                try:
                    PressreaderSpider(self.username, self.password, data["newspaperlibraryid"], data["paperId"],
                                      data["displayname"]).supplement(data["class"])
                except Exception as e:
                    print("爬取出错,错误原因：" + str(e))

            print("=====" * 30)


if __name__ == '__main__':
    w = Pressreadermain("wzq", "123456")
    choice = input("补录否？（y/n）")
    if choice == "y":
        w.run()
    else:
        w.ran()
