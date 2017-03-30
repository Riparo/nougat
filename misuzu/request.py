from pprint import pprint
from urllib.parse import parse_qs, parse_qsl
import cgi
import json


class RequestParams(object):

    def __setattr__(self, key, value):
        super().__setattr__(key, value)


class Request:
    """

    """

    def __init__(self, url, headers, version, method, query, cookies=None):
        self.url = url
        self.version = version
        self.method = method
        self.headers = dict(headers)
        self.body = {}
        self.params = RequestParams()
        self.cookies = cookies or {}

        self.query = {}
        self.json = None

        self.__init_query(query)
        # self.__init_header(headers)
        self.__init__cookies()

    @property
    def content_type(self):
        return self.headers.get('CONTENT_TYPE', '').lower()

    def __init__cookies(self):
        """
        从 self.heanders 中读取 Cookies 并且格式化进入 self.cookies
        """
        cookies = self.headers.get("Cookie", None) or self.headers.get("cookie", None)
        if cookies:
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

    def init_body(self, body):
        """
        format body into different type
        :param body:
        :return:
        """
        # parse body as json
        if self.content_type == 'application/json':
            self.json = json.loads(body.decode())
            return

        if not self.content_type.startswith('multipart/'):
            pairs = parse_qsl(body.decode())
            for key, value in pairs:
                self.__set_body(key, value)
            return

        # TODO: from-data and file

    def __set_body(self, key, value):

        if key in self.body:
            if not isinstance(self.body[key], list):
                temp = list()
                temp.append(self.body[key])
                self.body[key] = temp
            self.body[key].append(value)

        else:
            self.body[key] = value

    def __get_msg(self, from_where, key, append=False):
        ret = None
        if from_where == 'cookie':
            return self.cookies.get(key, None)

        elif from_where == "query":
            ret = self.query.get(key, None)

        elif from_where == "form":
            ret = self.body.get(key, None)

        elif from_where == "header":
            return self.headers.get(key, None)

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
