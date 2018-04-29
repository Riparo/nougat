# Nougat

基于 Python 3.6 的异步框架。Nougat 使用中间件的形式来处理逻辑。

![PyPI](https://img.shields.io/pypi/pyversions/nougat.svg) ![PyPI](https://img.shields.io/pypi/status/nougat.svg) ![PyPI](https://img.shields.io/pypi/v/nougat.svg) ![PyPI](https://img.shields.io/pypi/l/nougat.svg) [![Build Status](https://travis-ci.org/Kilerd/nougat.svg?branch=master)](https://travis-ci.org/Kilerd/nougat)

## 安装

Nougat 目前仅支持 Python3.6，所以你可以通过 PYPI 来安装：

```bash
pip3 install nougat  # or pip install nougat
```

或者你可以通过 pipenv 来安装(推荐)：

```bash
pipenv install nougat
```

### 开发版本

如果你想使用 Nougat 的新特性，可以选择使用开发版本。**注意这同时也意味着框架会存在着更多的BUG** ：

```bash
pip3 install git@github.com:Kilerd/nougat.git@develop
```

### Uvloop 支持

Nougat 依赖于 asyncio，所以如果你打算把 Nougat 运行在 Linux 上，可以选择使用更好的异步库来运行

首先安装 `uvloop`:

```bash
pip3 install uvloop
```

然后在项目中添加以下代码以使用 uvloop:

```python
import asyncio
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
```

## 快速上手

```python
from nougat import Nougat

app = Nougat()

async def middleware(response):

    response.content = 'Hello world'

app.use(middleware)
app.run()
```

上述代码描述了 Nougat 的最基本使用过程：

- 引用 `Nougat` 类
- 定义中间件
- 把中间件倒入到 `Nougat` 中
- 运行 `Nougat`

### Nougat 类

框架中最重要的便是 Nougat 类。它储存了所有注册的中间件和信号处理函数，同时用于启动和停止服务器

```
app = Nougat()
```

在 Nougat 类中，最重要的便是注册中间件和添加信号处理函数

#### 注册中间件 `app.use(middleware...)`

`use` 方法可以同时传入多个中间件，注册顺序跟传入顺序一致

```python
async def one_middleware():
    pass

async def another_middleware(response):
    response.content = 'Hello World'
   
app.use(one_middleware)
app.use(one_middleware, another_middleware)
```

约定的中间件必须是异步函数，同时可选的参数有四个：`app`, `request`, `response`, `next` 。参数都是可选的，可根据自己的需求选择

具体的中间件定义和执行流程在下文会继续描述

### 配置

Nougat 类中的 `config` 变量用于管理配置信息

#### 从 Python 对象中读取配置信息

`app.config` 中有一个方法`load_from_object(object_name)` 用于读取指定对象中所有的大写字母组成的变量

```
class DefaultConfig:
    UPPER_WORD = 1
    normal = 2

app.config.load_from_object(DefaultConfig)
```

在这个例子中，`UPPER_WORD`会被加载进配置`app.config`中，但是`normal` 不会

#### 访问配置信息

`app.config` 中的信息可以通过 `object` 的方式访问，也可以通过`dict`的方式访问：

- 对象访问方式: `app.config.UPPER_WORD`
- 字典访问方式: `app.config['UPPER_WORD']`

我们推荐使用对象访问方式，因为 Nougat 在处理不存在的信息时，会返回`None`，而不会报错

如果你执意要用字典访问方式，请使用`app.config.get("UPPER_WORD", None)`来避免触发 KeyError 异常

### 中间件

在 Nougat 中，中间件必须是一个异步函数（或者在类中实现`async def __call__` 方法），同时参数只能先定在`app`, `request`, `response`, `next` 里面，按需定义

```Python
async def middleware(app, request, response, next):
    # doing before request
    await next()
    # doing after after
```

- `app` 为 `Nougat` 的实例
- `request` 为 `Request` 实例，当前请求上下文的请求对象
- `response` 为 `Response`实例，当前请求上下文的响应对象
- `next` 为中间件链的下一个中间件，经由包装后的无参数方法，可直接`await next() ` 调用

**注意，为了可以得到更好的代码提示，建议在编写中间件参数时，使用 Type Hints。 `async def middleware(app: Nougat, request: Request, response: Response, next)`**

```python
async def middleware(app, request, next):
    if request.headers.get('Authentication'):
        print('get user token')
    await next()

app.use(middleware)
```

上述中间件使用了三个参数，并没有使用到`response`

或者，我们可以编写一个类作为中间件

```python
class Middleware:
    
    async def __call__(next): 
        await next()

app.use(Middleware())
```

#### 中间件执行顺序

```


                      Request
              +                 ^
              |                 |
       +------|-----------------|-------+
       |      |                 |       |
       |      |   middleware 1  |       |
       |      |                 |       |
       +------|-----------------|-------+
              |                 |
       +------|-----------------|-------+
       |      |                 |       |
       |      |   middleware 2  |       |
       |      |                 |       |
       +------|-----------------|-------+
              |                 |
              |                 |
              +-----------------+
```

`await next()` 把一个中间件分成两个部分（当找不到该语句时，整个中间件默认被理解为上半部分），Nougat 在处理中间件时，会正向处理中间件链的上半部分，逆向处理下半部分

```python
v = []
async def m1(next):
    v.append(1)
    await next()
    v.append(2)
    
async def m2(next):
    v.append(3)
    await next()
    v.append(4)
    
app.use(m1, m2)
```

当经历过一次HTTP请求后，v的内容为`[1, 3, 4, 2]` 

#### 记录处理时间的例子

```Python
async def logging_time(response, next):
    start_time = time()
    await next()
    process_time = time() - start_time
    response.set_header("Time": "{}s".format(process_time))
```

### 信号

信号用于 Nougat 服务器启动前后处理的事情，例如建立数据库连接，数据的预处理等等

目前，Nougat 只支持两种信号，启动服务器前信号 `before_start` 和 关闭服务器后信号`after_start`

```python
@app.signal('before_start')
async def handle(app):
    pass
```

使用 `app.signal` 装饰器可以完成该工作，参数为信号值。 装饰器函数可以为异步函数，也可以为普通函数。参数为 `app`，其类型为 Nougat 类的实例

信号的具体应用请自行想象

## 高级使用说明

### 请求类 Request

Request 类用于储存 HTTP 请求的相关信息

#### request.method
HTTP 访问方法，为大写字符串 `GET`, `POST` 等
#### request.version
HTTP 协议版本
#### request.url

HTTP 请求的URL，为 `yarl.URL` 实例，以下是一些操作实例

```Python
url = yarl.URL("https://example.com/foo/bar?hello=world")
print(url.host)  # example.com
print(url.path)  # /foo/bar
print(url.query)  # <MultiDictProxy('hello': 'world')>
print(url.query.get('hello'))  # world
```

#### request.content_type
HTTP 的 `Content-Type`

#### request.query
`request.url.query` 的快捷访问方式
#### request.form
HTTP 非 GET 方法中 FORM 数据储存。

#### request.ip
HTTP 访问者的 IP
#### request.headers
HTTP 请求头部信息
#### request.cookies
HTTP 请求的 Cookies

### 响应类 Response

#### response.code = 

响应的HTTP CODE， 默认为 200

#### response.status = 
对应HTTP CODE的文本信息，200 对应 OK，默认会从表中查询出默认值。

#### response.content =

响应内容

#### response.type = 
响应内容的类型，默认为`text/html`

#### response.charset =
响应内容的编码，默认为 `utf-8`

#### response.set_header(key, value)
添加响应头
#### response.set_cookies(self, name, value, expires=None, domain=None, path=None, secure=False, http_only=False, same_site=None)
添加 Cookie
 - `name`: 名字
 - `value`: 值
 - `expires`: 过期时间，单位秒

### 用HttpException中断中间件链

在中间件处理业务逻辑时，在某些情况下，我们希望提前中断中间件链的执行，例如当用户认证失败时，直接返回  HTTP 401 Unauthorized。 Nougat 提供了`nougat.exceptions.HttpException` 来实现这个功能

```python
async def login_required(request, next):
    if request.headers.get('Authentication'):
        ...
    if not is_auth:
        raise HttpException(401, 'you need to login first')
    ...        
```

`HttpException` 接受两个参数：

- `code` HTTP CODE
- `body` HTTP 响应内容

### 如何写单元测试

Nougat 提供了一个非常方便的库，用于执行单元测试。当然了，我们依赖于`pytest` 和 `pytest-asyncio` 来提供基础配件

```python
import pytest
from app import app
from nougat import TestClient

@pytest.mark.asyncio
async def test_app(unused_tcp_port):
    # doing before test
    
    async with TestClient(app, unused_tcp_port) as client:
        res = await client.get('/')
        assert res.text == 'Hello world'
```

## 相关应用

- [Nougat Router](https://github.com/Kilerd/nougat-router) 一个适用于 Restful API 并且带参数格式化的路由器
- [Nougat Utils](https://github.com/Kilerd/nougat-utils) 提供了 CLI 支持和调试模式等适用于开发时的工具库

## 开源协议

本项目使用 MIT 开源，详情请查看 [LICENSE](https://github.com/NougatWeb/nougat/blob/master/LICENSE) 文件