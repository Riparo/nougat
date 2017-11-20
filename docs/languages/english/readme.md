# Nougat
Nougat is an asynchronous web framework based on Python3.6, which focus on enhancing the experience of asynchronous web developing

At the beginning, the main point of Nougat is changing the way of writing Restful API by dividing the definition of parameters and the logic of controller

Another point is that Nougat can provide an automatic generator for API document, which has a lots templates
 
However, with the development of Nougat, it was separated into two parts - the basic framework with Router and Middleware and the Restful Extension, which can let itself more popular and be highly extendable.

## Installation
Nougat relays on Python3.6 and DOES NOT support the elder version, which is hosted at Pypi. So you can install stable version through:
```bash
pip3 install nougat
```
#### Develop Version
if you wanna test the new feature of Nougat, you can install it from Github:
<p class="warning">
  In Develop Verson it would has some unknown bugs and unstable factors, SO PLEASE CHOOSE IT DELIBERATELY!
</p>

```bash
pip3 install git@github.com:Kilerd/nougat.git@develop
```

### Minimal Usage
```python
from nougat import Nougat, Routing, get

app = Nougat()

class MainRouting(Routing):

    @get('/')
    async def index(self):
        return 'Hello world'

app.route(MainRouting)

app.run(debug=True)
```

### Get Started
from the above sample, we can see something important:
 - `Nougat` the entrance of entire framework, controlling all middlewares, guarders and router. At the same time, it also is used to start the server.
 - `Routing` used to define some route, which is similar as `Blueprint`

after creating the instance of `Nougat`, the routing would be activated only after registering to Nougat application. `app.route(MainRouting)` means registering `MainRouting` to `app`. notices that the parameter is class propotype, not the class instance.
`app.run(debug=True)` is used to start server with debug mode.

#### the steps of using Nougat
 1. Create`Nougat`instance
 2. Write Routes and group them into `Routing`
 3. Write some middlewares
 4. Register middlewares to `Nougat`
 5. Register routings to `Nougat`
 6. Start the server

### Nougat Class

the most import class in Nougat is `Nougat`. it controlls almost everythings: middlewares, routes and guardrs etc, and starts or stops the server
```python
app = Nougat()
```
#### Register middlewares to `Nougat`
`app.use()` is used to register middleware, the detail of middleware, please read the middleware part
```python
async def middleware(context, next):

    await next()

app.use(middleware)
```
#### Register routings to `Nougat`
```python

class OneRouting(Routing):
    pass

app.route(OneRouting)
```

#### Start Server
```python
app.run(debug=True)
```
### Configuration
Nougat class instance has an attribute `config` to manage the configurations.
#### Load the config from Python object

`app.config` has function `load_from_object(object_name)`, it can load all the object attributes which is upper word.
```python
class DefaultConfig:
    UPPER_WORD = 1
    normal = 2

app.config.load_from_object(DefaultConfig)
```
in this sample, `UPPER_WORD` could be loaded to `app.config`, but not the `normal`.

#### Access config
Class `app.config` is an object and also a dictionary, so you can access config in two ways:
 - object way: `app.config.UPPER_WORD`
 - dict way: `app.config['UPPER_WORD']`

we recommend that using object way to access it is better than dict way, for nougat will return `None` if the attribute you access is not existed.

If you wanna use dict way, please use `app.config.get("UPPER_WORD", None)` to avoid raising KeyError Exception.

## Routing
Routing, a group of routes, is one of key classes in nougat, it can be considered as Context in the handler of route.

routes must be defined in routing, here is a sample:
```python
class OneRouting(Routing):
    
    @get('/')
    async def index_page(self):
        return 'hello world'

```
Here, we define an `OneRouting` class inheriting the basic routing `Routing`, and a route with method `GET` and handler `index_page`

the decorator `get` would wrap this handler as the `Route` instance, so when this routing was registered to app, Nougat can find out all Route instance in routing.

**NOTICE: the handler must be an asynchronous function which only `self` parameter.**

### Functions & Attributes in Routing
#### self.prefix = 
set the prefix for all route in this routing.
#### self.redirect(url)
redirect to `url`

actually this function raises an HTTPException with 302 code, then Nougat catch it and send back to client
#### self.abort(code: int, message: str = None)

send a custom http code to client with custom message. and it would abort this connection.
### Method Decorators
There are several decorators to implement HTTP methods: `get`, `post`, `delete`, `put`, `patch`, all of them have only one parameter - the rule of route.

and it's legal to bind a lots rule to one handler. If you want, you can do like that:
```python
class MultipleRule(Routing):
    
    @get('/')
    @post('/')
    @get('/index')
    async def index_page(self):
        return 'hello world'
```
### Dynamic Rule For Route
Nougat provide an straightforward way to use dynamic rule. And there are several type rules in Nougat:
 - Static Rule: one of common rule
 - Unnamed Regex type: it is allowed to write regex directly in url, but the parameter can not be accessed in handler / controller
     - Example: `/articles/[0-9]+`
     - this type rule is provided for advanced developer
 - Simple type: it is the simplest way to identify a parameter in url using `:PARAM_NAME`, it would match all character except `/`
     - Example: `/articles/:id`
     - this example can match all characters(except /)
     - and in handler, it can be accessed by `self.request.url_dict.get('id')`
 - Named Regex type: combining Simple type and Unnamed Regex Type whose structure is `:PARAMETER<REGEX_RULE>`
     - Example: `/articles/:id<[0-9]+>`
     - it can also be accessed in `self.request.url_dict`

you can choose the best type for different route.

### Request & Response
Request and Response class are two attributes in Routing
```python
class AccessContext(Routing):
    @get('/')
    async def test(self):
        
        # self.request
        # self.response
        pass
```
in handler(controller is better), `self` means Context. So you can access request by `self.request` and response by `self.response`.

#### Request
There are some attributes in request you nay need to know
##### request.app
the Nougat instance reference
##### request.method
the http method
##### request.version
the http version
##### request.url
the request url, the instance of `yarl.URL`

here is sample of `yarl.URL`
```python
url = yarl.URL("https://example.com/foo/bar?hello=world")
print(url.host)  # example.com
print(url.path)  # /foo/bar
print(url.query)  # <MultiDictProxy('hello': 'world')>
print(url.query.get('hello'))  # world
```
##### request.url_dict
the dictionary containing all parameters defining in route rule
```python
@get('/articles/:id<[0-9]+>')
async def get_one_article(self):
    return self.request.url_dict.get('id')
```
##### request.content_type
the content type of request

##### request.query
the alias of `request.url.query`
##### request.form
the http data dictionary, which has two type fields: text field and `File` field.
##### request.ip
the client ip.

if `app.config.X_FORWARD_IP` is set and True, the ip would be loaded from header `X-Forwarded-For`, or it would be loaded from the socket connection

if your application is behind CDN or other load balancers, please set the `X_FORWARD_IP` setting in config.
##### request.headers
headers of request
##### request.cookies
cookies of reuqest
#### Response
Response instance

##### response.status = 
http status of response whose default value is `200`
##### response.res = 
the content of response which should be str or bytes type.

##### response.type = 
the content type of response whose default value is `text/html`
##### response.charset =
the content charset of response whose default value is `utf-8`

the `response.res` will be converted to this charset.
##### response.set_header(key, value)
add response header
##### response.set_cookies(self, name, value, expires=None, domain=None, path=None, secure=False, http_only=False, same_site=None)
add cookies
 - `name`: cookies name
 - `value`: cookies value
 - `expires`: number of seconds until the cookie expires
 - `domain`: specifies those hosts to which the cookie will be sent
 - `path`: indicates a URL path that must exist in the requested resource before sending the Cookie header
 - `secure`: a secure cookie will only be sent to the server when a request is made using SSL and the HTTPS protocol
 - `http_only`:
 - `same_site`:

## Middleware
```python
async def middleware(context, next):
    # doing before controller
    await next()
    # doing after controller
```
middleware function must be a asynchronous function with two parameters `context` and `next`.

`context` is the Routing instance reference, `next` is the next function in middleware chain.
### Sample about Logging the process time
```python
async def logging_time(context, next):
    start_time = time()
    await next()
    process_time = time() - start_time
    context.response.set_header("Time": "{}s".format(process_time))

```