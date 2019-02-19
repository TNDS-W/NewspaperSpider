import re


class AuthorClean():
    # {"displayname": "《瞭望》东方周刊", "paperId": "5624", "newspaperlibraryid": "1045861675632164864",
    #  "class": 'https://www.pressreader.com/china/oriental-outlook/'},
    # {"displayname": "华盛顿邮报", "paperId": "1047", "newspaperlibraryid": "1033578898694078464",
    #  "class": 'https://www.pressreader.com/usa/the-washington-post/'},
    # {"displayname": "环球邮报", "paperId": "1893", "newspaperlibraryid": "1045865093163646976",
    #  "class": 'https://www.pressreader.com/canada/the-globe-and-mail-metro-ontario-edition/'},
    # {"displayname": "每日电讯报", "paperId": "1190", "newspaperlibraryid": "1052393687318790144",
    #  "class": 'https://www.pressreader.com/uk/the-daily-telegraph/'},
    # {"displayname": "每日电讯报(周日报)", "paperId": "1191", "newspaperlibraryid": "1062187599004696576",
    #  "class": 'https://www.pressreader.com/uk/the-sunday-telegraph/'},
    # {"displayname": "费加罗报", "paperId": "2526", "newspaperlibraryid": "1052399397175820288",
    #  "class": 'https://www.pressreader.com/france/le-figaro/'},
    # {"displayname": "马来西亚星报", "paperId": "1342", "newspaperlibraryid": "1056715269021368320",
    #  "class": 'https://www.pressreader.com/malaysia/the-star-malaysia/'},
    # {"displayname": "马尼拉公报", "paperId": "9f70", "newspaperlibraryid": "1055720173438238720",
    #  "class": 'https://www.pressreader.com/philippines/manila-bulletin/'},
    # {"displayname": "缅甸时报", "paperId": "9fak", "newspaperlibraryid": "1057893476043063296",
    #  "class": 'https://www.pressreader.com/myanmar/the-myanmar-times/'},
    # {"displayname": "菲律宾《星报》", "paperId": "1731", "newspaperlibraryid": "1059282635148230656",
    #  "class": 'https://www.pressreader.com/philippines/the-philippine-star/'},
    # {"displayname": "《ABC》报", "paperId": "2019", "newspaperlibraryid": "1059279325993369600",
    #  "class": 'https://www.pressreader.com/spain/abc/'},
    # {"displayname": "洛杉矶时报", "paperId": "1156", "newspaperlibraryid": "1033579506872352768",
    #  "class": 'https://www.pressreader.com/usa/los-angeles-times/'},
    # {"displayname": "《教徒报》", "paperId": "1091", "newspaperlibraryid": "1059278542195392512",
    #  "class": 'https://www.pressreader.com/india/the-hindu/'},
    # {"displayname": "《圣保罗报》", "paperId": "2011", "newspaperlibraryid": "1062165517546029056",
    #  "class": 'https://www.pressreader.com/brazil/folha-de-spaulo/'},
    # {"displayname": "《号角报》", "paperId": "2009", "newspaperlibraryid": "1062614516577075200",
    #  "class": 'https://www.pressreader.com/argentina/clarín/'},
    # {"displayname": "海峡时报", "paperId": "1105", "newspaperlibraryid": "1078890400258719744",
    #  "class": 'https://www.pressreader.com/singapore/the-straits-times/'},
    # {"displayname": "新海峡时报", "paperId": "9gqu", "newspaperlibraryid": "1078890509197377536",
    #  "class": 'https://www.pressreader.com/malaysia/new-straits-times/'}

    def __init__(self, id, author):
        self.id = id
        self.author = author

    def cleaning(self):
        self.author = re.sub("^B[Yy]", "", self.author)
        self.author = re.sub("[aA][nN][dD]", "#", self.author)
        self.author = re.sub(", ", "#", self.author)
        self.author = re.sub(".*?[Bb]y", "", self.author)
        self.author = re.sub("\s[^\s]*?@.*", "", self.author)
        self.author = re.sub("\sis.*", "", self.author)
        self.author = re.sub("^[-]\s?", "", self.author)
        self.author = re.sub("^[–]\s", "", self.author)
        self.author = re.sub("\s[–]\s[Ww]ith\s", "#", self.author)
        self.author = re.sub("\s[^\s]*?\.com", "", self.author)
        if self.id == "5624":
            pass
        elif self.id == "1047" or self.id == "1058":
            # 华盛顿邮报
            self.author = self.author.replace('\xad', '').strip()
            self.author = re.sub('^[^\w\s]{0,1}(by|BY|By)\s', '', self.author)
            self.author = re.sub('\s+AND\s+', ' # ', self.author)
            self.author = re.sub(',\s*', ' # ', self.author).split()
            new = []
            for i in self.author:
                if i == '#':
                    new.append('#')
                if i.isupper() and len(i) > 1:
                    new.append(i)
            self.author = []
            for i in ' '.join(new).split('#'):
                if i.strip():
                    self.author.append(i.strip())
            self.author = '#'.join(self.author)
            while True:
                self.author = re.sub('#\s*$', '', self.author)
                if not re.search('#\s*$', self.author):
                    break
        elif self.id == "1190" or self.id == "1191":
            self.author = re.sub("[aA][nN][dD]", "#", self.author)
            self.author = re.sub(".*?[Bb]y", "", self.author)
            self.author = re.sub("\s[^\s]*?@.*", "", self.author)

        return self.author
