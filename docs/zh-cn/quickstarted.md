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
from misuzu.response import Response
app = Misuzu(__name__)

@app.get("/")
@app.param('')
async def test(request):
    return Response("hello world.", content_type="text/html")

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
    return Response("hello world.", content_type="text/html")

@app.post('/')
async def index_post(request):
    return Response("hello world with post mothod.", content_type="text/html")
```

### 带变量的路由
lalalal
## 参数定义

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
 - `json` 默认设置 `content_type` 为 `application/json`

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

misuzu 在处理返回值时，会判断返回值是否`Response`的实例，若不是，将会调用上述描述的 `json` 进行格式化返回值

## 使用 nginx 部署