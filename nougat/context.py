import httptools
import json
from yarl import URL
from urllib.parse import parse_qsl
from nougat.httpstatus import STATUS_CODES
from nougat.exceptions import HttpException


class Params(object):

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

    def __format_attr(self, attr_type, value):
        pass


class Context(object):

    def __init__(self, app, path, headers, ip, version, method):

        # base
        self.app = app
        self.url = URL(path.decode())

        self.__version = version  # http version
        self.method = method

        # request
        self.headers = dict(headers)
        self.cookies = {}

        self.ip = self.__init_ip(ip)
        self.req_body = {}

        self.query = self.url.query

        self.json = None

        # params
        self.params = Params()

        # response
        self.res_header = {}
        self.type = "text/plain"
        self.res = None
        self.status = 200

        self.__init__cookies()

    @property
    def content_type(self):
        """
        the content type for request
        """
        return self.headers.get('CONTENT_TYPE', '').lower()

    def set_cookies(self, name, value, expires=None, domain=None, path=None, secure=False, http_only=False, same_site=None):
        """
        
        :param name: cookies name
        :param value: cookies value
        :param expires: number of seconds until the cookie expires
        :param domain: specifies those hosts to which the cookie will be sent
        :param path: indicates a URL path that must exist in the requested resource before sending the Cookie header
        :param secure: a secure cookie will only be sent to the server when a request is made using SSL and the HTTPS protocol 
        :param http_only: 
        :param same_site: 
        :return: 
        """

        header_value = "{}={}".format(name, value)

        if expires:
            header_value = "{}; Max-Age={}".format(header_value, expires)
        if domain:
            header_value = "{}; Domain={}".format(header_value, domain)
        if path:
            header_value = "{}; Path={}".format(header_value, path)
        if secure:
            header_value = "{}; Secure".format(header_value)
        if http_only:
            header_value = "{}; HttpOnly".format(header_value)
        if same_site:
            header_value = "{}; SameSite={}".format(header_value, same_site)

        self.set("Set-Cookie", header_value)

    def set(self, key, value):
        """
        set response header
        :param key: the key of header
        :param value: the value of header
        """

        self.res_header[key] = value

    def url_for(self, name, **kwargs):
        """
        get the url according to the section name and handler name
        :param name: a string like section_name.handler_name
        :return: the url string
        """
        # TODO url for function
        _name_split = name.split(".")

        if len(_name_split) != 2:
            raise Exception()  # TODO new exception

        section_name, handler_name = _name_split
        section = self.app.sections.get(section_name, None)

        if not section:
            raise Exception()  # TODO ne exception

        route = section.get_route_by_name(handler_name)

        return route.url(**kwargs)

    def redirect(self, url):
        """
        redirect to another page
        :param url: the page need to go
        """
        self.set("Location", url)
        self.abort(302)

    def abort(self, status, body=None):
        """
        abort HTTPException
        :param status: http status code
        :param body: http body
        """
        raise HttpException(body, status)

    def __build_response_headers(self):
        """
        generator response headers
        :return: 
        """
        headers = []
        for key, value in self.res_header.items():
            headers.append("{}: {}\r\n".format(key, value).encode('utf-8'))

        return headers

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

        payload = []

        # HTTP STATUS
        payload.append('HTTP/{} {} {}\r\n'.format(self.__version, self.status, STATUS_CODES.get(self.status, 'FAIL')).encode('latin-1'))

        # CONTENT TYPE AND LENGTH
        payload.append('Content-Type: {}\r\n'.format(self.type).encode('latin-1'))
        payload.append('Content-Length: {}\r\n'.format(len(body)).encode('latin-1'))

        # HEADERS OF LOCATION OR COOKIES
        payload.extend(self.__build_response_headers())

        # RESPONSE BODY
        payload.append(b'\r\n')
        payload.append(body)

        return b''.join(payload)

    def __init_ip(self, ip):
        """
        set the right ip
        """
        if self.app.config.get("X-FORWARD-IP", False):
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
