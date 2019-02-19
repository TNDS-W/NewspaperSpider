from api.damsapi import DamsApi
from spiders.jjsb import Jjsb
from spiders.cbnweek import Cbnweek
from spiders.eeo import Eeo
from spiders.qiushi import Qiushi
from spiders.yicai import Yicai
from spiders.n21econmics import N21econmics
from spiders.lwdfweek import Lwfd_week
from spiders.newsweek import Newsweek
from spiders.zgxwweek import Zgxw_week
from spiders.faz import Faz
from spiders.japantimes import Japantimes
from spiders.nytimes import Nytimes
from spiders.smh import Smh
from spiders.thetimes import Thetimes
from spiders.nikkei import Nikkei
from spiders.pressreader.main import Pressreadermain
from spiders.thesundaytimes import Thesundaytimes
from spiders.scmp import SouthChina
from spiders.wsj import Wallstreet
from spiders.economist import Economist
from spiders.dailytimes import Dailytimes
from spiders.sueddeutsche import Sueddeutsche
from spiders.time import Time
from spiders.bostonglobe import Bostonglobe
from spiders.ft import Ft
from spiders.repubblica import Repubblica
from spiders.bangkokpost import Bangkokpost
from spiders.joins import JoongAng
from spiders.qiushi1 import Qiushi1
from spiders.lem import Lemonde
from spiders.usatoday import Usatoday
from spiders.theaustralian import Theaustralian
from spiders.rg import Rg
from spiders.thehindu import Thehindu
import schedule, os, datetime,threading
from spiders.fazSunday import FazSunday
from spiders.lwdfweek import Lwfd_week

spiderlist = [
    {"displayname": "求是", "classname": Qiushi1, "class": None},
    {"displayname": "中国经济时报", "classname": Jjsb, "class": None},
    {"displayname": "21世纪经济报道", "classname": N21econmics, "class": None},
    {"displayname": "经济观察报", "classname": Eeo, "class": None},
    {"displayname": "第一财经周刊", "classname": Cbnweek, "class": None},
    {"displayname": "日本时报", "classname": Japantimes, "class": None},
    {"displayname": "日本经济新闻(2份报刊)", "classname": Nikkei, "class": None},
    {"displayname": "纽约时报", "classname": Nytimes, "class": None},
    {"displayname": "法兰克福汇报", "classname": Faz, "class": None},
    {"displayname": "悉尼先驱晨报", "classname": Smh, "class": None},
    {"displayname": "泰晤星期日", "classname": Thesundaytimes, "class": None},
    {"displayname": "南华早报", "classname": SouthChina, "class": None},
    {"displayname": "华尔街时报", "classname": Wallstreet, "class": None},
    {"displayname": "经济学家", "classname": Economist, "class": None},
    {"displayname": "每日时报", "classname": Dailytimes, "class": None},
    {"displayname": "南德意志", "classname": Sueddeutsche, "class": None},
    {"displayname": "美国新闻周刊", "classname": Newsweek, "class": None},
    {"displayname": "时代周刊", "classname": Time, "class": None},
    {"displayname": "波士顿环球邮报", "classname": Bostonglobe, "class": None},
    {"displayname": "泰晤士报", "classname": Thetimes, "class": None},
    {"displayname": "第一财经日报", "classname": Yicai, "class": None},
    {"displayname": "曼谷邮报", "classname": Bangkokpost, "class": None},
    {"displayname": "金融时报(5份报刊)", "classname": Ft, "class": None},
    {"displayname": "共和国报", "classname": Repubblica, "class": None},
    {"displayname": "中央日报", "classname": JoongAng, "class": None},
    {"displayname": "法国世界报", "classname": Lemonde, "class": None},
    {"displayname": "今日美国", "classname": Usatoday, "class": None},
    {"displayname": "中国新闻周刊", "classname": Zgxw_week, "class": None},
    {"displayname": "法兰克福汇报(星期天)", "classname": FazSunday, "class": None},
    {"displayname": "澳大利亚人报", "classname": Theaustralian, "class": None},
    {"displayname": "俄罗斯报", "classname": Rg, "class": None},
    {"displayname": "教徒报", "classname": Thehindu, "class": None},
    # {"displayname": "瞭望周刊", "classname": Lwfd_week, "class": None},
    {"displayname": "下一页", "classname": Pressreadermain, "class": None}
]

#自动
def main():
    starttime = "爬虫开始执行，时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(starttime)
    username = "SpiderMan"
    password = "SpiderMan@2019"
    # username = "zyq"
    # password = "123456"

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

    for x in range(len(spiderlist)):
        a = spiderlist[x]["classname"](username, password)
        spiderlist[x]["class"] = "1"
        newspress = 1
        i = 0
        while i < 3:
            try:
                if spiderlist[x]["displayname"] == "下一页":
                    newspress = a.runpress()
                    newsnumber += newspress[-1]
                else:
                    sttime = "(" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ")" + "开始爬取:" + spiderlist[x]["displayname"]
                    news = a.run()
                    endtime = "(" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ")" + "爬取完成:" + spiderlist[x]["displayname"]
                    newsnumber += news
                print("-----" * 20)
                boolean = True
                break
            except Exception as e:
                print("爬取出错:" + spiderlist[x]["displayname"] + "报纸。错误原因：" + str(e))
                endtime = "(" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ")" + "爬取出错:" + spiderlist[x][
                    "displayname"] + "报纸。错误原因：" + str(e)
                print("-----" * 20)
                boolean = False
                i += 1
        if boolean:
            if news == 0 or newspress == 0:
                noNumber += 1
                nonewspaper.append(spiderlist[x]["displayname"])
            else:
                sucNumber += 1
                sucnewspaper.append(spiderlist[x]["displayname"])
        else:
            faiNumber += 1
            fainewspaper.append(spiderlist[x]["displayname"])
            # gLock.acquire()
            with open(os.getcwd() + r"\log\error-" + datetime.datetime.now().strftime('%Y-%m-%d') + r".txt", "a",
                      encoding="utf-8") as f:
                f.write(sttime + "\n")
                f.write(endtime + "\n")
            # gLock.release()

    finishtime = "全部报纸爬取完成,完成时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(finishtime)
    # gLock.acquire()

    with open(os.getcwd() + r"\log\record-" + datetime.datetime.now().strftime('%Y-%m-%d') + r".txt", "a+",
              encoding="utf-8") as F:
        # try:
        F.write(starttime + "\n")
        F.write(finishtime + "\n")
        F.write("录入成功篇数：" + str(sucNumber + newspress[0]) + "\n")
        F.write("录入成功报纸：" + "||".join(sucnewspaper) + "||" + newspress[3] + "\n")
        F.write("录入失败篇数：" + str(faiNumber + newspress[1]) + "\n")
        F.write("录入失败报纸：" + "||".join(fainewspaper) + "||" + newspress[4] + "\n")
        F.write("周报或未发布篇数：" + str(noNumber + newspress[2]) + "\n")
        F.write("周报或未发布报纸：" + "||".join(nonewspaper) + "||" + newspress[5] + "\n")
        F.write("总共采集报纸数：" + str(newsnumber) + "\n" + "\n")
        # except Exception as e:
        #     print(e)
    # gLock.release()

#多线程调用
def thread_main(a,b):
    gLock = threading.Lock()
    starttime = "爬虫开始执行，时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(starttime)
    username = "SpiderMan"
    password = "SpiderMan@2019"

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

    for x in range(a,b):
        a = spiderlist[x]["classname"](username, password)
        spiderlist[x]["class"] = "1"
        newspress = []
        i = 0
        while i < 3:
            try:
                if spiderlist[x]["displayname"] == "下一页":
                    newspress = a.runpress()
                    newsnumber += newspress[-1]
                else:
                    sttime = "(" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ")" + "开始爬取:" + \
                             spiderlist[x]["displayname"]
                    news = a.run()
                    endtime = "(" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ")" + "爬取完成:" + \
                              spiderlist[x]["displayname"]
                    newsnumber += news
                print("-----" * 20)
                boolean = True
                break
            except Exception as e:
                print("爬取出错:" + spiderlist[x]["displayname"] + "报纸。错误原因：" + str(e))
                endtime = "(" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ")" + "爬取出错:" + spiderlist[x][
                    "displayname"] + "报纸。错误原因：" + str(e)
                print("-----" * 20)
                boolean = False
                i += 1
        if not newspress:
            newspress = [0, 0, 0, "", "", "", 0]

        if boolean:
            if news == 0 or newspress == 0:
                noNumber += 1
                nonewspaper.append(spiderlist[x]["displayname"])
            else:
                sucNumber += 1
                sucnewspaper.append(spiderlist[x]["displayname"])
        else:
            faiNumber += 1
            fainewspaper.append(spiderlist[x]["displayname"])
            gLock.acquire()
            with open(os.getcwd() + r"\log\error-" + datetime.datetime.now().strftime('%Y-%m-%d') + r".txt", "a",
                      encoding="utf-8") as f:
                f.write(sttime + "\n")
                f.write(endtime + "\n")
            gLock.release()

    finishtime = "全部报纸爬取完成,完成时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(finishtime)
    gLock.acquire()

    with open(os.getcwd() + r"\log\record-" + datetime.datetime.now().strftime('%Y-%m-%d') + r".txt", "a+",
              encoding="utf-8") as F:
        try:
            F.write(starttime + "\n")
            F.write(finishtime + "\n")
            F.write("录入成功篇数：" + str(sucNumber + newspress[0]) + "\n")
            F.write("录入成功报纸：" + "||".join(sucnewspaper) + "||" + newspress[3] + "\n")
            F.write("录入失败篇数：" + str(faiNumber + newspress[1]) + "\n")
            F.write("录入失败报纸：" + "||".join(fainewspaper) + "||" + newspress[4] + "\n")
            F.write("周报或未发布篇数：" + str(noNumber + newspress[2]) + "\n")
            F.write("周报或未发布报纸：" + "||".join(nonewspaper) + "||" + newspress[5] + "\n")
            F.write("总共采集报纸数：" + str(newsnumber) + "\n" + "\n")
        except Exception as e:
            print(e)
    gLock.release()

# 人工
def run():
    username = "SpiderMan"
    password = "SpiderMan@2019"
    # username = "zyq"
    # password = "123456"
    supple = input("请选择是否补录(y/n)：")
    if supple == "n":
        print("爬虫开始执行，时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        while True:

            # 循环显示所有采集器
            for i in range(0, len(spiderlist)):
                print(str(i) + ":" + spiderlist[i]["displayname"])

            print("A:所有报纸")
            print("Q:退出")

            # 等待输入命令
            ret = input("请输入你要选择采集的报纸:")
            if (ret == "Q" or ret == "q"):
                break
            elif (ret == "A" or ret == "a"):  # 如果输入a 则全部爬取
                for x in range(len(spiderlist)):
                    a = spiderlist[x]["classname"](username, password)
                    spiderlist[x]["class"] = "1"
                    try:
                        if spiderlist[int(ret)]["displayname"] == "下一页":
                            a.runpress()
                        else:
                            a.run()
                        print("-----" * 20)
                    except Exception as e:
                        print("爬取出错:" + spiderlist[x]["displayname"] + "报纸。错误原因：" + str(e))
                        print("-----" * 20)
                    print("报纸爬取完成,完成时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            else:
                if (spiderlist[int(ret)]["class"] is None):
                    a = spiderlist[int(ret)]["classname"](username, password)
                    spiderlist[int(ret)]["class"] = "1"
                # try:
                if spiderlist[int(ret)]["displayname"] == "下一页":
                    a.ran()
                    print("报纸爬取完成,完成时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                # except Exception as e:
                #     print("爬取出错，请重新爬取该报纸。错误原因：" + str(e))
                else:
                    a.run()
                    print("报纸爬取完成,完成时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            print("====" * 30)

    elif supple == "y":
        print("爬虫开始执行，时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        while True:

            # 循环显示所有采集器
            for i in range(0, len(spiderlist)):
                print(str(i) + ":" + spiderlist[i]["displayname"])

            print("Q:退出")

            # 等待输入命令
            ret = input("请输入你要选择补录的报纸:")
            if (ret == "Q" or ret == "q"):
                break
            else:
                if (spiderlist[int(ret)]["class"] is None):
                    a = spiderlist[int(ret)]["classname"](username, password)
                    spiderlist[int(ret)]["class"] = "1"
                if spiderlist[int(ret)]["displayname"] == "下一页":
                    try:
                        a.run()
                        print("报纸爬取完成,完成时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    except Exception as e:
                        print("暂无补录或者爬取出错" + e)
                else:
                    try:
                        a.supplement()
                        print("报纸爬取完成,完成时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    except Exception as e:
                        print("暂无补录或者爬取出错" + e)


            print("====" * 30)

# 多线程实现
def thread_run():
    threads = []  # 线程池
    threads.append(threading.Thread(target=thread_main, args=(0, 14)))
    threads.append(threading.Thread(target=thread_main, args=(14, 31)))
    threads.append(threading.Thread(target=thread_main, args=(31, 31)))
    for x in threads:
        x.start()
    for y in threads:
        y.join()


if __name__ == '__main__':
    choice = input("请选择人工或自动采集（y(自动)/n(人工)）：")
    if choice == "y":
        thread_choice = input("是否使用多线程(y(使用)/n(不使用))")
        if thread_choice == "y":
            dates = input("是否直接运行(y(直接运行)/n(系统时间))：")
            if dates == "y":
                thread_run()
            elif dates == "n":
                print("系统将在：00:00 05:00 12:00 19:00 执行")
                schedule.every().day.at("00:00").do(thread_run)
                schedule.every().day.at("05:00").do(thread_run)
                schedule.every().day.at("12:00").do(thread_run)
                schedule.every().day.at("19:00").do(thread_run)

                while True:
                    schedule.run_pending()
            else:
                print("输入错误")
        elif thread_choice == "n":
            dates = input("是否直接运行(y(直接运行)/n(系统时间))：")
            if dates == "y":
                main()
            elif dates == "n":
                print("系统将在：00:00 05:00 12:00 19:00 执行")
                schedule.every().day.at("00:00").do(main)
                schedule.every().day.at("05:00").do(main)
                schedule.every().day.at("12:01").do(main)
                schedule.every().day.at("19:00").do(main)

                while True:
                    schedule.run_pending()
            else:
                print("输入错误")
        else:
            print("输入错误")

        # main()
    elif choice == "n":
        run()
    else:
        print("输入错误")
