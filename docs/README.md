# Misuzu

an asynchronous framework which focus on best writing experience of API. The key features are the human friendly definition of parameters, which is divided from the method's logic, and the automatic documents.



# Installation

misuzu only support python 3.5 and newer, so you can use `pip` or `pip3` to install

```bash
pip install misuzu
```

## better async supported

`uvloop`  is better than `asyncio`, so in Linux and macOS, please install `uvloop` to improve  performance

# Application

The Misuzu application is a object which contains global middlewares and sections registering

## hello world

```python
from misuzu import Misuzu, Section
app = Misuzu()
main = Section("main")

@main.get("/")
async def index(ctx):
    return "hello"

app.use(main)
app.run()
```

## app.use(middleware_or_section)

Add a given middleware or section to the application

### use middleware

```python
async def middleware(ctx, next):
    # request time
    # doing something before handler ...
    await next()
    # response time
    # doing something after handler ...

app.use(middleware)
```

### use section

```python
one_section = Section("one_section")

# add routing or middleware to one_section
# ...

app.use(one_section)
```

## app.run(...)

create a HTTP server

#### Params

- `host`  with default value is `127.0.0.1` .  mostly you needn't change it
- `port` with default value is `8000` . define the port that server listen
- `debug` with default vaule is `False` . determine to create a development mode server or not
- `loop` specialize the asynchronous even loop. if you don't know what it is, please DO NOT change it.

#### Example

```python
# in production
app.run(port=8000)

# in develop
app.run(port=8000, debug=True)
```

## app.config

the `Config` object is used to store the variable for you project. and misuzu only support and suggest to use `TOML` file to store you configurations.

toml (Tom's Obvious, Minimal Language) is very simple, slight, but powerful.

Please [read this article](https://github.com/toml-lang/toml) to know more about toml file.

a sample for toml

```toml
# This is a TOML document.

title = "TOML Example"

[owner]
name = "Tom Preston-Werner"
dob = 1979-05-27T07:32:00-08:00 # First class dates

[database]
server = "192.168.1.1"
ports = [ 8001, 8001, 8002 ]
connection_max = 5000
enabled = true

[servers]

  # Indentation (tabs and/or spaces) is allowed but not required
  [servers.alpha]
  ip = "10.0.0.1"
  dc = "eqdc10"

  [servers.beta]
  ip = "10.0.0.2"
  dc = "eqdc10"

[clients]
data = [ ["gamma", "delta"], [1, 2] ]

# Line breaks are OK when inside arrays
hosts = [
  "alpha",
  "omega"
]
```

which is the same as the json as follow:

```json
{
    "title": "TOML Example",
    "owner": {
        "name": "Tom Preston-Werner",
        "dob": "1979-05-27T07:32:00-08:00"
    },
    "database": {
        "server": "192.168.1.1",
        "ports": [8001, 8001, 8002],
        "connection_max": 5000,
        "enabled": true
    },
    "servers": {
        "alpha": {
            "ip": "10.0.0.1",
            "dc": "eqdc10"
        },
        "beta": {
            "ip": "10.0.0.2",
            "dc": "eqdc10"
        }
    },
    "clients": {
        "data": [
            ["gamma", "delta"],
            [1, 2]
        ]
    },
    "hosts": ["aplha", "omega"]
}
```

### app.config.load(file)

load configurations from file, and access them by this way:

```python
# load config
app.config.load("config.toml")

# access them
app.config['title']
app.config['database']['server']
```

### load environment variable

misuzu provide a special way to load environment variable

in case of there is a environment variable

```bash
export TEST_VARIABLE="HELLO WORLD"
```

then in file `config.toml` , we wanna  varible`test` can get `TEST_VARIABLE` from environment, just write down like this:

```toml
test = "ENV::TEST_VARIABLE::STR::HELLO NULL"
```

while loading, misuzu will automatically read `TEST_VARIABLE` from `ENV` . if this variable is not contained in environment now, `HELLO NULL` would be read, finally the variable will be tried to parse as `STR` type.

apparently, there is a pattern that loading variable from environment, which is `ENV::{ENVIRONMENT_VARIABLE_NAME}::{EXPECTATIVE_TYPE}::{DEFAULT_VALUE}`. if the value of one parameter in configuration file is matched on this pattern, it works.

```python
app.config.load("config.toml")
app.config['test']  # HELLO WORLD
```

it is very useful when misuzu project is deployed with docker.

### add more type for environment variable

`app.config.use(TYPE, TYPE_FORMATE_FUNC)`

```python
app.config.use("DOUBLE", double_func)

def double_func(content):
    try:
        return float(content)
    except:
        raise Exception()
```



# Section

Section is parts of application, just like blueprint in flask. Adding routes in section, and registering section in application.

```python
# define
section_name = Section("section_name")

# define routing and middlewares

# register in app
app.use(section_name)
```

## routing in section

when designing API, specially the RESTFULAPI, the limits of authority are very important. misuzu provide precise definition of routing.

misuzu allow section to define mostly HTTP method: `HEAD`, `GET`, `POST`, `PUT`, `DELETE`, `HEAD`, `PATCH`, `OPTIONS`, which has a decorator to bind a url:

```python
@section.get('/')
async def index(ctx):
    return "hello, world."

@section.post('/')
async def index_post(ctx):
    return "hello world with post method"
```

**handler must is a asynchronous function with one parameter name ctx**

## Params on route

In short, rather than those using regex to define a url, misuzu provide a simple way.  `<param_name>` in url represent as a parameter, then use decorator `@section.param(...)` to optimize this parameter. When in handler, you can access this parameter using `ctx.params.{param_name}`

sample here

```python
@section.get("/{name}")
@section.param("name", str)
async def index(ctx):
    return "hello {}".format(ctx.params.name)
```

## section.use(middleware)

add middleware in section

## section.param(...)

unlike other frameworks, misuzu use decorator to define parameters

- split between definition and using of parameter
- much more pythonic

```python
@section.get("/")
@section.param("page", int, optional=True, default=1)
@section.param("per-page", int, optional=True, default=10)
async def index(ctx):
    nowpage = ctx.params.page
    ....
```



### params
 - `name` the name of parameter。it can use `ctx.params.{name}` to access.
 - `type` the type of parameter。 a callable function is needed which support python standard `str`, `int`,  `float`, `bool`
 - `location` the source of parameter。the place where the parameter is read, the option values are  `query`, `form`, `header`, `cookie`. it can be a list containing some of them, e.g. `['query', 'form']` (the former is priority)
 - `optional`  determine whether this parameter is optional, whit default value is `False`
 - `default`  the default value of parameter, it active only if the `optional` is `True`
 - `action` the alias of parameter, when action is set, the way accessing parameter is changed from `ctx.params.{name}` into `ctx.params.{action}`
 - `append`  allow parameter store multiple value as list from one or different location
 - `description` description of parameter, using in the automatic document module




for those parameters in the url, `location` is invalid, cause those parameters only can be gotten in the url.

**`name` and `type`are necessary, others are optional**

# Middleware

middleware is an asynchronous function, which would executed before and after handler.

the prototype of middleware is like that:

```python
async def {middleware_name}(ctx, next):
    # doing before handler
   	await next()
    #doing after handler
```

`await next()` is not necessary, only if you do not wanna handler running. a case is that user authentication is doing before handler, and it do not pass the authentication, then you can use `ctx.abort(401)` instead of `await next()`

## difference using in between app and section

middleware in app would be executed every request. but middleware in section is executed, if and only if the request's url is defined in the same section.

this mechanism is very useful. there are two sections named `main` and `admin`.

- the middleware of logging access information can be registered in app.
- the authentication middleware should be registered in section `admin`. cause section `main` need not authenticate user information.

## a demo to take the waiting time down

```python
import time
async def time_marker(ctx, next):
    start = time.time()
    await next()
    end = time.time()
    ctx.set("x-handle-time", end - start)
```

# Context

Context is object of per request including `request` and `response` , and is referenced in middleware as the receiver.

## ctx.app

Application instance reference.

## ctx.path

the full request url. e.g. `http://example.com/foo/bar?a=1&b=1`

## ctx.url

the main path of url. e.g. `/foo/bar`

## ctx.query_string

the raw request string e.g. `a=1&b=1`

## ctx.method

request method.

## ctx.headers

the dict of request headers.

## ctx.cookies

the dict of request cookies

## ctx.ip

request remote address

### X-Forward-To

if `X-FORWARD-IP` is `True` in configuration. then `ctx.ip` would return `X-Forwarded-For` in header

## ctx.params

the parameters of routing.

## ctx.content_type

Get request `Content-Type`

## ctx.status=

set HTTP status for response

## ctx.type=

set response type.

## ctx.res =

set response body

**NOTICE: WE DO NOT SUGGEST THAT USE THIS WAY TO SET RESPONSE BODY IN HANDLER, IT SHOULD BE USED IN MIDDLEWARE ONLY**

you should use `return "something"` in handler to set response body

## ctx.set(key, value)

set response header.

if `key` has already existed, the `value` would be updated.

## ctx.url_for(name, ...)

get the url of handler in the same or different section

name should be `{section_name}.{handler_name}` , parameters should send as a dict.

```
main = Section("main")

@main.get("/")
async def index(ctx):
	pass

@main.get("/<id>")
@main.param("id", str)
async def index_id(ctx):
	pass


ctx.url_for("main.index")  # /
ctx.url_for("main.index", a=1)  # /?a=1
ctx.url_for("main.index_id")  # raise Exception: missing parameter in url
ctx.url_for("main.index_id", id=1)  # /1
ctx.url_for("main.index_id", id=1, a=1)  /1?a=1

```

## ctx.set_cookies(...)

set cookies.

#### Param

- `name`  cookies name
- `value`  cookies value
- `expires`  number of seconds until the cookie expires (second)
- `domain`  specifies those hosts to which the cookie will be sent
- `path ` indicates a URL path that must exist in the requested resource before sending the Cookie header
- `secure ` a secure cookie will only be sent to the server when a request is made using SSL and the HTTPS protocol
- `http_only`
- `same_site`

## ctx.redirect(url)

redirect to url with 302.

## ctx.abort(status, body)

abort http status

- `status` http code
- `body` optional http body. if it is empty, it will return default content of http code. e.g. the default content of `404` is `Not Found`. if the code is defined by user, return `User Definition Code`