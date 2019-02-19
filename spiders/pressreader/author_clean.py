import re


class AuthorClean():

    def __init__(self, id, author):
        self.id = id
        self.author = author

    def cleaning(self):
        self.author = re.sub("^B[Yy]", "", self.author)
        self.author = re.sub("\s[aA][nN][dD]\s", "#", self.author)
        self.author = re.sub(", ", "#", self.author)
        self.author = re.sub(".*?\s[Bb]y\s", "", self.author)
        self.author = re.sub("\s[^\s]*?@.*", "", self.author)
        self.author = re.sub("\sis.*", "", self.author)
        self.author = re.sub("^[-]\s?", "", self.author)
        self.author = re.sub("\s[–]\s[Ww]ith\s", "#", self.author)
        self.author = re.sub("\s[^\s]*?\.com", "", self.author)
        if self.id == "5624":
            pass
        elif self.id == "1047" or self.id == "1058":
            # 华盛顿邮报
            self.author = self.author.replace('\xad', '').strip()
            self.author = re.sub('^[^\w\s]{0,1}(by|BY|By)\s', '', self.author)
            # self.author = re.sub('\s+AND\s+', ' # ', self.author)
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

        return self.author
