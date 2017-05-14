import httptools
import json
from urllib.parse import parse_qsl
from misuzu.httpstatus import STATUS_CODES
from misuzu.exceptions import HttpException


class Params(object):

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

    def __format_attr(self, attr_type, value):
        pass


class Context(object):

    def __init__(self, app, path, headers, ip, version, method):

        # base
        self.app = app

        self.path = path.decode()  # e.g. /hello?a=1

        path_parse = httptools.parse_url(path)
        self.url = path_parse.path  # e.g. /hello
        self.query_string = path_parse.query  # e.g. a=1

        self.__version = version  # http version
        self.method = method

        # request
        self.headers = dict(headers)
        self.cookies = {}

        self.ip = self.__init_ip(ip)
        self.req_body = {}

        self.query = None

        self.json = None

        # params
        self.params = Params()

        # response
        self.res = None
        self.status = None

        self.__init_query(self.query_string)
        self.__init__cookies()


    @property
    def type(self):
        """
        the content type for request
        """
        return self.headers.get('CONTENT_TYPE', '').lower()

    def set_cookies(self, value):
        # TODO set cookies
        pass

    def set_secret_cookies(self, value):
        # TODO set secret cookies
        pass

    def set(self, key, value):
        """
        set response header
        :param key: the key of header
        :param value: the value of header
        """

        # TODO set function for header
        pass

    def url_for(self, name, **kwargs):
        """
        get the url according to the section name and handler name
        :param name: a string like section_name.handler_name
        :return: the url string
        """
        # TODO url for function
        pass

    def redirect(self, url, forever=False):
        """
        redirect to another page
        :param url: the page need to go
        :param forever: return 302 status code if False , otherwise return 301 status code
        """
        # TODO redirect function
        pass

    def abort(self, status, body=None):
        """
        abort HTTPException
        :param status: http status code
        :param body: http body
        """
        raise HttpException(body, status)

    @property
    def output(self):
        """
        output the http payload
        """
        def body_bytes(body):
            body_type = type(body)
            if body_type is str:
                body = body.encode('utf-8')
            elif body_type is bytes:
                body = body
            else:
                body = b'Unable to interpret body'

            return body

        # TODO format the output
        body = body_bytes(self.res or STATUS_CODES.get(self.status, 'FAIL'))
        return b''.join([
            'HTTP/{} {} {}\r\n'.format(self.__version, self.status, STATUS_CODES.get(self.status, 'FAIL')).encode('latin-1'),
            'Content-Type: {}\r\n'.format(self.type).encode('latin-1'),
            'Content-Length: {}\r\n'.format(len(body)).encode('latin-1'),
            b'\r\n',
            body
        ])

    def __init_ip(self, ip):
        """
        set the right ip
        """
        if self.app.config['X-FORWARD-IP']:
            return self.headers.get("X-Forwarded-For", "").strip().split(",")
        else:
            return ip

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
        if self.type == 'application/json':
            self.json = json.loads(body.decode())
            return

        if not self.type.startswith('multipart/'):
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

    def generate_params(self, route):
        """
        格式化参数
        :param route:
        :return:
        """
        for param in route.params:

            if param.name in route.url_params_dict:
                self.params.__setattr__(param.name, route.url_params_dict[param.name])
                continue

            for location in param.location:
                # pprint("{} {} {}", location, param.name, param.append)
                param_name = param.action or param.name
                param_content = self.__get_msg(location, param.name, param.append) or param.default

                self.params.__setattr__(param_name, param_content)
