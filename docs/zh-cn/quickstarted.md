# 快速入门
## 安装
!> PYTHON3 ONLY: misuzu 只支持 Python 3.5 及以后的版本

misuzu 寄托在 pypi 上，因此可以使用 `pip` 进行安装
```bash
pip install misuzu
```

### windows 下的 misuzu 
因为 misuzu 是基于 `uvloop` 的，`uvloop` 又是 linux only 的，因此在 windows 环境下，会使用 `asyncio` 来代替 `uvloop`。 性能会下降，因此不建议在 windows 的生产环境下部署 misuzu。

## 最小的使用

```python
from misuzu import Misuzu

app = Misuzu(__name__)

@app.get('/<name>')
@app.param('name', str)
async def index(request):
    return {'hello': request.params.name}

app.run()
```

## 调试模式
 TODO: watchdog and signal on windows

## 路由系统
在编写 API 时，权限是比较重要的一部分，尤其是在设计 RESTFUL API 时，因此 misuzu 提供了精准、优雅的路由定义方法。

在 misuzu 中，允许用户定义大部分请求方法： `HEAD`, `GET`, `POST`, `PUT`, `DELETE`, `HEAD`, `PATCH`, `OPTIONS`。 每一种请求方法都对应着一个装饰器来绑定 URL
```python

@app.get('/')
async def index(request):
    return text("hello, world.")

@app.post('/')
async def index_post(request):
    return text("hello world with post method")
```

### 带参数的路由
简单来说，不同于那些实用正则表达式作为路由项目的 web 框架来说，misuzu 提供了一个简单的路由定义方式，只需要在路由中以尖括号`<param_name>`括起来，然后使用`@app.param()`装饰器对该变量进行详细的描述即可。（当然，如果你只定义不使用该变量，那么不需要使用`@app.param()`描述该变量）

以下是一个简单的例子（如同 HELLO WORLD）
```python
@app.get('/<name>')
@app.param('name', str)
async def index(request):
    return {'hello': request.params.name}
```
以上例子，在 URL 中接受一个叫`name`的参数，并且尝试格式化为 `str` 类型，如果格式化成功（没有报异常），那么可以使用`request.params.name` (通用的是`request.params.param_name`) 得到参数内容。
## 参数定义
不同于其他 web 框架， misuzu 把参数的定义提到了 handler 前面，并且使用`@app.param()`装饰器语法来实现，这样可以：
 - 逻辑代码和参数定义代码分离，更加清晰明了
 - 代码更加 Pythonic

`param()` 方法的使用方法是装饰在 handler 处理函数上的，其主要的参数有：
 - `name` 参数名称。可以通过`request.params.name`来读取对应的函数
 - `type` 参数类型。 需要传入一个 `callable` 的方法，支持 Python 内置的 `str`, `int`, `float`, `bool`
 - `location` 参数来源。告知需要从哪里读取该参数。默认值为 `query` 即从 URL 的参数的读取。 可选值有 `query`, `form`, `header`, `cookie`。 允许从多个地方读取，即传入 list , e.g. `['query', 'form']`
 - `optional` 参数是否可选。 默认值为 `False`
 - `default` 参数默认值。 默认值为 `None`，当参数 `optional` 为 `True` 时， 默认值才会生效
 - `action` 参数别名。默认值为 `None`，当设定该值时，参数的读取名字便改为 `request.params.action`
 - `append` 参数是否可为列表。 默认值为 `False`， 当为 `True` 时，读取到的参数将以 `list` 的形式返回
 - `description` 参数描述。 用于自动生成文档功能

其中对于路由上的参数， `location` 将失效。原因是对于所有参数，都会先从路由中读取，若读取不到，再根据 `location` 读取。

** `name` 和 `type` 是必须的，其他都是可选的。 **
## 重定向 和 HTTP 错误

### 如何返回自定义的 HTTP CODE
misuzu 提供了 `abort` 来返回自定义 HTTP CODE

`abort` 接受两个参数：
 - `status` 是返回的 HTTP CODE
 - `body` 是可选的，返回在页面中显示的内容。若不传入 `body` 则在常用的 HTTP CODE 中寻找对应的文字，例如 `404` 对应 `Not Found`。 对于那些不存在的，则返回 `User Definition Code`

## 请求类

## 响应类

內部提供了三个常用的响应函数 `text`, `html`, `json`。 其对应的设定如下：
 - `text` 默认设置 `content_type` 为 `text/plain; charset=utf-8`
 - `html` 默认设置 `content_type` 为 `text/html; charset=utf-8`
 - `json` 默认设置 `content_type` 为 `application/json`, 并且调用`json.dumps`方法对`body` 进行格式化

有了这几个常用的函数，就可以直接在处理函数中 `return json(body)` 即可完成返回

若需要返回其他类型的响应，可以引入 `Response` 类，直接设定 `Response` 的返回内容

### 更好的 JSON 的返回
对于 JSON 的返回内容， misuzu 提供了另外一种更加简便的返回方式
```python
@app.get("/")
async def index(request):
    return {"hello":"world"}
```
如上述代码，你可以直接返回 `dict` 或 `list` 类型的内容。

misuzu 在处理返回值时，会判断返回值是否`Response`的实例，若不是，将会调用上述描述的 `json` 方法进行格式化返回值

## 使用 nginx 部署