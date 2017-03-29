from pprint import pprint


class RequestParams(object):

    def __setattr__(self, key, value):
        super().__setattr__(key, value)


class Request:
    """

    """

    def __init__(self, url, headers, version, method, query, cookies=None):
        self.url = url
        self.headers = headers
        self.version = version
        self.method = method
        self.body = []
        self.params = RequestParams()
        self.cookies = cookies or {}

        self.query = {}

        self.__init_query(query)
        self.__init__cookies()

    def __init__cookies(self):
        """
        从 self.heanders 中读取 Cookies 并且格式化进入 self.cookies
        """
        cookies = self.headers.get(b"Cookie", b"").decode("utf-8")
        cookies = cookies.split("; ")
        for one_cookies in cookies:
            if one_cookies != "":
                one_cookies = one_cookies.split("=")
                self.cookies[one_cookies[0]] = "=".join(one_cookies[1:])

    def __init_query(self, query):
        """
        格式化 query 的内容
        :param query:
        :return:
        """
        if query:

            querys = query.decode("utf-8").split("&")
            for each_query in querys:
                query_path = each_query.split("=")
                if len(query_path) >= 2:
                    self.__set_query(query_path[0], "=".join(query_path[1:]))

    def __set_query(self, key, value):
        if key in self.query:
            if not isinstance(self.query[key], list):
                temp = list()
                temp.append(self.query[key])
                self.query[key] = temp
            self.query[key].append(value)

        else:
            self.query[key] = value

    def __get_msg(self, from_where, key, append=False):
        ret = None
        if from_where == 'cookies':
            return self.cookies.get(key, None)

        elif from_where == "query":
            ret = self.query.get(key, None)

        elif from_where == "body":
            pass

        elif from_where == "header":
            pass

        if isinstance(ret, list):
            return ret if append else ret[-1]

        return ret

    def generate_params(self, params):
        """
        格式化参数
        :param params:
        :return:
        """
        for param in params:
            for location in param.location:
                # pprint("{} {} {}", location, param.name, param.append)
                param_name = param.action or param.name
                param_content = self.__get_msg(location, param.name, param.append)
                self.params.__setattr__(param_name, param_content)
